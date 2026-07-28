"""Configuration-driven Phase 1 manifest and run-contract entry points."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import traceback
from pathlib import Path
from typing import Any

from .manifest import json_yaml_compatible, load_config, manifest_records, resolve_candidate_manifest
from .execution import ExecutionFailure, execute_capability_preflight
from .run_contract import RunDirectory, create_run_directory


def _assignment_lines(manifest: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for schedule in manifest["schedules"]:
        for assignment in schedule["requested_precision_map"]:
            lines.append(
                "\t".join(
                    (
                        schedule["schedule_id"],
                        assignment["module_path"],
                        f"layer={assignment["layer_index"]}",
                        f"group={assignment["group_id"]}",
                        f"requested={assignment["requested_precision"]}",
                    )
                )
            )
    return lines


def _git_record(repo_root: Path) -> str:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "status", "--short"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        diff = subprocess.run(
            ["git", "diff", "HEAD", "--binary"],
            cwd=repo_root,
            check=True,
            capture_output=True,
        ).stdout
        return json.dumps(
            {
                "commit": commit,
                "working_tree_dirty": bool(status),
                "status": status.splitlines(),
                "tracked_diff_sha256": hashlib.sha256(diff).hexdigest(),
            },
            indent=2,
        ) + "\n"
    except (OSError, subprocess.CalledProcessError) as error:
        return json.dumps({"status": "unavailable", "reason": str(error)}) + "\n"


def _record_planned_run(
    run: RunDirectory,
    config: dict[str, Any],
    manifest: dict[str, Any],
    *,
    command: list[str],
    repo_root: Path,
) -> None:
    assignment_lines = _assignment_lines(manifest)
    run.write_artifact("resolved_config.yaml", json_yaml_compatible(config))
    run.write_artifact("command.txt", " ".join(command) + "\n")
    run.write_artifact("git_commit.txt", _git_record(repo_root))
    run.write_artifact(
        "environment.json",
        json.dumps(
            {
                "status": "recorded_without_backend_execution",
                "python": sys.version,
                "python_prefix": sys.prefix,
                "cuda_version": "unknown_not_run",
                "gpu_type": "unknown_not_observed",
                "quantization_backend": config["backend"],
                "model": config["model"],
                "dataset": {"status": "not_used_in_phase1"},
                "config_schema": config["schema_version"],
                "timing_conditions": {"status": "not_run"},
            },
            indent=2,
        )
        + "\n",
    )
    run.write_artifact(
        "hardware.json",
        json.dumps(
            {
                "status": "not_observed",
                "declared_target": config["hardware_target"],
                "gpu_work_launched": False,
            },
            indent=2,
        )
        + "\n",
    )
    run.write_artifact("random_seeds.json", json.dumps({"seed": config.get("seed", 0)}) + "\n")
    run.write_artifact(
        "metrics.json",
        json.dumps(
            {
                "status": "planned",
                "capability_evidence": "not_run",
                "schedule_count": len(manifest["schedules"]),
                "module_assignments_per_schedule": len(manifest["schedules"][0]["requested_precision_map"]),
            },
            indent=2,
        )
        + "\n",
    )
    run.write_artifact(
        "predictions.jsonl",
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in manifest_records(manifest)),
    )
    run.write_artifact("stdout.log", "\n".join(assignment_lines) + "\n")
    run.write_artifact("stderr.log", "")
    run.write_artifact(
        "report.md",
        "# Planned Phase 1 run\n\n"
        "Status: planned; no model, package, quantizer, or GPU was loaded.\n\n"
        "Configuration generation is not backend capability evidence. Realized precision, kernel dispatch, export/reload, and resource gates remain `not_run`.\n",
    )



def _record_executed_run(
    run: RunDirectory,
    config: dict[str, Any],
    manifest: dict[str, Any],
    *,
    command: list[str],
    repo_root: Path,
    result: dict[str, Any],
) -> None:
    conditions = {
        str(condition["schedule_id"]): condition
        for condition in result.get("conditions", [])
        if isinstance(condition, dict) and condition.get("schedule_id")
    }
    selected = set(result.get("selected_schedule_ids", []))
    records: list[dict[str, Any]] = []
    for planned in manifest_records(manifest):
        schedule_id = planned["schedule_id"]
        condition = conditions.get(schedule_id)
        if condition is None:
            records.append(planned | {"status": "not_run"})
            continue
        records.append(
            {
                "record_schema": "qcb.schedule_probe.v1",
                "schedule_id": schedule_id,
                "status": condition.get("status", "failed"),
                "capability_evidence": condition.get("kernel_validation", {}).get(
                    "status", "failed"
                ),
                "requested_precision_map": condition.get(
                    "requested_precision_map", planned["requested_precision_map"]
                ),
                "realized_precision_map": condition.get("realized_precision_map"),
                "vllm_realized_precision_map": condition.get(
                    "vllm_realized_precision_map"
                ),
                "map_validation": condition.get("map_validation", {}),
                "kernel_validation": condition.get("kernel_validation", {}),
                "export_reload_validation": condition.get(
                    "export_reload_validation", {}
                ),
                "generation": condition.get("generation", {}),
            }
        )
    environment = dict(result.get("environment") or {})
    environment.update(
        {
            "status": "recorded_after_execution",
            "selected_schedule_ids": sorted(selected),
            "calibration_path": str(result.get("calibration_path", "")),
        }
    )
    hardware = dict(result.get("hardware") or {})
    hardware["selected_device_index"] = result.get("device_index")
    run.write_artifact("resolved_config.yaml", json_yaml_compatible(config))
    run.write_artifact("command.txt", " ".join(command) + "\n")
    run.write_artifact("git_commit.txt", _git_record(repo_root))
    run.write_artifact("environment.json", json.dumps(environment, indent=2) + "\n")
    run.write_artifact("hardware.json", json.dumps(hardware, indent=2) + "\n")
    run.write_artifact(
        "random_seeds.json",
        json.dumps({"seed": config.get("seed", 0), "calibration_seed": config.get("seed", 0)})
        + "\n",
    )
    run.write_artifact(
        "metrics.json",
        json.dumps(
            {
                "status": result.get("status", "failed"),
                "capability_claim": bool(result.get("capability_claim", False)),
                "selected_schedule_count": len(selected),
                "condition_results": [
                    {
                        "schedule_id": condition.get("schedule_id"),
                        "status": condition.get("status"),
                        "map_status": condition.get("map_validation", {}).get("exact_match"),
                        "kernel_status": condition.get("kernel_validation", {}).get("status"),
                        "reload_status": condition.get("export_reload_validation", {}).get(
                            "status"
                        ),
                        "generation_status": condition.get("generation", {}).get("status"),
                    }
                    for condition in result.get("conditions", [])
                ],
                "error": result.get("error"),
            },
            indent=2,
        )
        + "\n",
    )
    run.write_artifact(
        "predictions.jsonl",
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
    )
    run.write_artifact("stdout.log", str(result.get("stdout", "")))
    run.write_artifact("stderr.log", str(result.get("stderr", "")))
    run.write_artifact(
        "report.md",
        "# Phase 1 capability preflight\n\n"
        f"Status: {result.get('status', 'failed')}. "
        f"Capability claim: {bool(result.get('capability_claim', False))}.\n\n"
        "This run used the real Qwen model, calibration data, LLM Compressor, "
        "compressed-tensors export/reload, and vLLM serving path. "
        "A capability claim is true only when every selected condition passed "
        "the requested-versus-realized map, kernel, reload, and generation gates.\n\n"
        f"Error: {result.get('error')}\n",
    )

def _resolve_command(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config))
    manifest = resolve_candidate_manifest(config)
    if args.format == "json":
        print(json.dumps(manifest, indent=2, sort_keys=True))
    else:
        print(json.dumps({"manifest_status": manifest["manifest_status"], "schedule_count": len(manifest["schedules"]), "capability_claim": manifest["capability_claim"]}, sort_keys=True))
        for line in _assignment_lines(manifest):
            print(line)
    return 0


def _preflight_command(args: argparse.Namespace) -> int:
    config_path = Path(args.config)
    config = load_config(config_path)
    manifest = resolve_candidate_manifest(config)
    run = create_run_directory(Path(args.run_root), run_id=args.run_id)
    if not args.execute:
        _record_planned_run(run, config, manifest, command=sys.argv, repo_root=Path.cwd())
        validation = run.validate_artifacts()
        if not validation.valid:
            raise RuntimeError(f"created run contract is invalid: {validation}")
        print(json.dumps({"run_directory": str(run.path), "manifest_status": manifest["manifest_status"], "capability_claim": False}, sort_keys=True))
        return 0

    result: dict[str, Any]
    try:
        if args.device_index is None or not args.model_cache or not args.calibration_dir:
            raise ExecutionFailure(
                "--execute requires --device-index, --model-cache, and --calibration-dir"
            )
        result = execute_capability_preflight(
            config,
            run_path=run.path,
            config_path=config_path,
            model_cache=Path(args.model_cache),
            calibration_dir=Path(args.calibration_dir),
            device_index=args.device_index,
            sample_count=args.sample_count,
            model_source=args.model_source or None,
        )
        result["device_index"] = args.device_index
        result["calibration_path"] = args.calibration_dir
    except Exception as error:
        result = {
            "status": "failed",
            "capability_claim": False,
            "conditions": [],
            "environment": {"status": "execution_failed_before_condition"},
            "hardware": {"gpu_work_launched": False},
            "stdout": "",
            "stderr": traceback.format_exc(),
            "error": f"{type(error).__name__}: {error}",
            "device_index": args.device_index,
            "calibration_path": args.calibration_dir,
        }
        print(result["error"], file=sys.stderr)
    _record_executed_run(
        run,
        config,
        manifest,
        command=sys.argv,
        repo_root=Path.cwd(),
        result=result,
    )
    validation = run.validate_artifacts()
    if not validation.valid:
        raise RuntimeError(f"created run contract is invalid: {validation}")
    payload = {
        "run_directory": str(run.path),
        "manifest_status": manifest["manifest_status"],
        "capability_claim": bool(result.get("capability_claim", False)),
        "status": result.get("status"),
    }
    print(json.dumps(payload, sort_keys=True))
    return 0 if result.get("status") == "completed" and result.get("capability_claim") else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m qcb.cli")
    subparsers = parser.add_subparsers(dest="command", required=True)
    resolve = subparsers.add_parser("resolve-manifest")
    resolve.add_argument("--config", required=True)
    resolve.add_argument("--format", choices=("text", "json"), default="text")
    resolve.set_defaults(handler=_resolve_command)
    preflight = subparsers.add_parser("preflight")
    preflight.add_argument("--config", required=True)
    preflight.add_argument("--run-root", required=True)
    preflight.add_argument("--run-id")
    preflight.add_argument("--execute", action="store_true")
    preflight.add_argument("--device-index", type=int)
    preflight.add_argument("--model-cache")
    preflight.add_argument("--model-source")
    preflight.add_argument("--calibration-dir")
    preflight.add_argument("--sample-count", type=int)
    preflight.set_defaults(handler=_preflight_command)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
