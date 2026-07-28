"""Real Phase 1 capability-preflight execution adapter.

The module imports heavyweight ML dependencies only inside the child condition
runner. The parent process orchestrates one condition at a time and records
the existing immutable run contract.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.metadata
import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Any, Mapping, Sequence

from .backend import ModuleAssignment
from .contract import Precision
from .manifest import load_config, resolve_candidate_manifest
from .validation import RealizedModule, compare_precision_maps


class ExecutionFailure(RuntimeError):
    """Raised when a real capability condition cannot be measured."""


def _json_write_once(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def _assignment_objects(schedule: Mapping[str, Any]) -> tuple[ModuleAssignment, ...]:
    return tuple(
        ModuleAssignment(
            module_path=str(item["module_path"]),
            layer_index=int(item["layer_index"]),
            group_id=str(item["group_id"]),
            requested_precision=Precision.from_value(str(item["requested_precision"])),
        )
        for item in schedule["requested_precision_map"]
    )


def _schedule(manifest: Mapping[str, Any], schedule_id: str) -> Mapping[str, Any]:
    for schedule in manifest["schedules"]:
        if schedule["schedule_id"] == schedule_id:
            return schedule
    raise ExecutionFailure(f"schedule is not present in resolved manifest: {schedule_id}")


def _requested_precisions(assignments: Sequence[ModuleAssignment]) -> tuple[Precision, ...]:
    return tuple(dict.fromkeys(assignment.requested_precision for assignment in assignments))


def _comparison_payload(comparison: Any) -> dict[str, Any]:
    return comparison.__dict__ | {"exact_match": comparison.exact_match}


def _precision_from_module(module: Any, torch: Any) -> Precision | None:
    scheme = getattr(module, "quantization_scheme", None)
    if scheme is None:
        scheme = getattr(module, "scheme", None)
    method = getattr(module, "quant_method", None)
    if scheme is None and method is not None:
        scheme = getattr(method, "scheme", None)
    weights = getattr(scheme, "weights", None) if scheme is not None else None
    if weights is None and method is not None:
        weights = getattr(getattr(method, "scheme", None), "weights", None)
    bits = getattr(weights, "num_bits", None)
    if bits is None and isinstance(weights, Mapping):
        bits = weights.get("num_bits")
    if bits is None:
        quant_type = getattr(scheme, "quant_type", None) if scheme is not None else None
        bits = getattr(quant_type, "size_bits", None)
    if bits == 8:
        return Precision.W8A16
    if bits == 4:
        return Precision.W4A16
    parameters = list(module.parameters(recurse=False))
    if parameters and parameters[0].dtype is torch.bfloat16:
        return Precision.BF16
    return None


def _scheme_text(module: Any) -> str | None:
    scheme = getattr(module, "quantization_scheme", None)
    if scheme is None:
        scheme = getattr(module, "scheme", None)
    if scheme is None:
        return None
    return type(scheme).__module__ + "." + type(scheme).__name__


def _kernel_text(module: Any) -> str | None:
    scheme = getattr(module, "scheme", None)
    for owner in (scheme, getattr(module, "quant_method", None), module):
        if owner is None:
            continue
        for attribute in ("kernel", "kernel_type", "backend", "kernel_name"):
            value = getattr(owner, attribute, None)
            if value is not None:
                if isinstance(value, str):
                    return value
                return type(value).__module__ + "." + type(value).__name__
    method = getattr(module, "quant_method", None)
    if method is not None:
        return type(method).__module__ + "." + type(method).__name__
    return None


def _module_device(module: Any) -> str:
    parameters = list(module.parameters(recurse=False))
    if parameters:
        return str(parameters[0].device)
    buffers = list(module.buffers(recurse=False))
    if buffers:
        return str(buffers[0].device)
    return "unknown"


def _observed_map(
    model: Any,
    assignments: Sequence[ModuleAssignment],
    torch: Any,
    *,
    kernel_required: bool,
) -> dict[str, RealizedModule]:
    modules = dict(model.named_modules())
    observed: dict[str, RealizedModule] = {}
    for assignment in assignments:
        module = modules.get(assignment.module_path)
        if module is None:
            continue
        observed[assignment.module_path] = RealizedModule(
            realized_precision=_precision_from_module(module, torch),
            scheme=_scheme_text(module),
            module_class=type(module).__module__ + "." + type(module).__name__,
            kernel=_kernel_text(module) if kernel_required else None,
            device=_module_device(module),
        )
    return observed


def _inspect_model_for_vllm(model: Any) -> dict[str, dict[str, Any]]:
    """Return serializable module observations from inside a vLLM worker."""

    import torch

    return {
        path: {
            "realized_precision": (
                precision.value
                if (precision := _precision_from_module(module, torch)) is not None
                else None
            ),
            "scheme": _scheme_text(module),
            "module_class": type(module).__module__ + "." + type(module).__name__,
            "kernel": _kernel_text(module),
            "device": _module_device(module),
        }
        for path, module in model.named_modules()
    }


def _observed_vllm_map(
    llm: Any,
    assignments: Sequence[ModuleAssignment],
    *,
    kernel_required: bool,
    packed_aliases: Mapping[str, str],
) -> dict[str, RealizedModule]:
    """Inspect vLLM's worker-owned model through its supported API."""

    apply_model = getattr(llm, "apply_model", None)
    if not callable(apply_model):
        raise ExecutionFailure("vLLM apply_model inspection API is unavailable")
    inventories = apply_model(_inspect_model_for_vllm)
    inventory = inventories[0] if isinstance(inventories, list) else inventories
    if not isinstance(inventory, Mapping):
        raise ExecutionFailure("vLLM model inspection returned no module inventory")

    observed: dict[str, RealizedModule] = {}
    for assignment in assignments:
        value = inventory.get(assignment.module_path)
        if not isinstance(value, Mapping):
            for source_suffix, fused_suffix in packed_aliases.items():
                marker = "." + source_suffix
                if assignment.module_path.endswith(marker):
                    fused_path = assignment.module_path[: -len(source_suffix)] + fused_suffix
                    value = inventory.get(fused_path)
                    if isinstance(value, Mapping):
                        break
        if not isinstance(value, Mapping):
            continue
        observed[assignment.module_path] = RealizedModule(
            realized_precision=(
                Precision.from_value(str(value["realized_precision"]))
                if value.get("realized_precision") is not None
                else None
            ),
            scheme=value.get("scheme"),
            module_class=value.get("module_class"),
            kernel=value.get("kernel") if kernel_required else None,
            device=value.get("device"),
        )
    return observed


def _kernel_validation(
    assignments: Sequence[ModuleAssignment],
    observed: Mapping[str, RealizedModule],
    *,
    quantized: bool,
) -> dict[str, Any]:
    if not quantized:
        return {"status": "not_applicable", "module_classes": [], "dispatches": []}
    missing = sorted(
        assignment.module_path
        for assignment in assignments
        if assignment.module_path not in observed
    )
    unknown = sorted(
        path
        for path, observation in observed.items()
        if not observation.kernel or observation.kernel.lower() == "unknown"
    )
    fallback = sorted(
        path
        for path, observation in observed.items()
        if "fallback" in (observation.kernel or "").lower()
        or "cpu" in (observation.kernel or "").lower()
        or not (observation.device or "").lower().startswith("cuda")
    )
    dispatches = [
        {
            "module_path": path,
            "module_class": observation.module_class,
            "kernel": observation.kernel,
            "device": observation.device,
        }
        for path, observation in sorted(observed.items())
    ]
    return {
        "status": "pass" if not missing and not unknown and not fallback else "failed",
        "missing_modules": missing,
        "unknown_kernel": unknown,
        "fallback_dispatches": fallback,
        "module_classes": sorted(
            {observation.module_class for observation in observed.values() if observation.module_class}
        ),
        "dispatches": dispatches,
    }


def _resource_snapshot(torch: Any, export_dir: Path | None = None) -> dict[str, Any]:
    resource_path = export_dir if export_dir and export_dir.exists() else (
        export_dir.parent if export_dir and export_dir.parent.exists() else Path.cwd()
    )
    usage = shutil.disk_usage(resource_path)
    result: dict[str, Any] = {
        "disk_free_bytes": usage.free,
        "disk_total_bytes": usage.total,
        "rss_bytes": None,
        "cuda_memory_allocated_bytes": None,
        "cuda_memory_reserved_bytes": None,
        "cuda_max_memory_allocated_bytes": None,
    }
    try:
        import psutil

        result["rss_bytes"] = psutil.Process().memory_info().rss
    except ImportError:
        pass
    if torch.cuda.is_available():
        result["cuda_memory_allocated_bytes"] = torch.cuda.memory_allocated()
        result["cuda_memory_reserved_bytes"] = torch.cuda.memory_reserved()
        result["cuda_max_memory_allocated_bytes"] = torch.cuda.max_memory_allocated()
    return result


def _runtime_environment(config: Mapping[str, Any], model_cache: Path) -> dict[str, Any]:
    names = (
        "torch",
        "transformers",
        "llmcompressor",
        "compressed-tensors",
        "vllm",
        "datasets",
        "accelerate",
    )
    versions: dict[str, str] = {}
    for name in names:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "not_installed"
    import torch

    return {
        "status": "observed",
        "python": sys.version,
        "python_prefix": sys.prefix,
        "cuda_version": torch.version.cuda,
        "gpu_type": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "unavailable",
        "gpu_compute_capability": (
            list(torch.cuda.get_device_capability(0)) if torch.cuda.is_available() else None
        ),
        "visible_cuda_devices": os.environ.get("CUDA_VISIBLE_DEVICES", ""),
        "package_versions": versions,
        "quantization_backend": config["backend"],
        "model": config["model"],
        "dataset": config.get("calibration", {}),
        "model_cache": str(model_cache),
    }


def _hardware_observation(device_index: int, torch: Any) -> dict[str, Any]:
    properties = torch.cuda.get_device_properties(0)
    query = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=index,name,memory.total,memory.free,utilization.gpu",
            "--format=csv",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "status": "observed",
        "physical_gpu_index": device_index,
        "visible_device_index": 0,
        "name": properties.name,
        "compute_capability": [properties.major, properties.minor],
        "memory_total_mib": properties.total_memory // (1024 * 1024),
        "nvidia_smi_inventory": query.stdout.strip(),
        "gpu_work_launched": True,
    }


def _read_prompts(calibration_dir: Path, count: int) -> list[str]:
    path = calibration_dir / "train.json"
    raw = path.read_text(encoding="utf-8")
    try:
        parsed = json.loads(raw)
        values = parsed if isinstance(parsed, list) else [parsed]
    except json.JSONDecodeError:
        values = [json.loads(line) for line in raw.splitlines() if line.strip()]
    rows = []
    for value in values:
        text = value.get("text") if isinstance(value, dict) else None
        if not isinstance(text, str) or not text.strip():
            raise ExecutionFailure(f"calibration row has no text: {path}")
        rows.append(text)
        if len(rows) == count:
            break
    if len(rows) < count:
        raise ExecutionFailure(f"calibration data has {len(rows)} rows, requires {count}")
    return rows


def _load_model(model_source: str, revision: str | None, cache_dir: Path, torch: Any) -> Any:
    from transformers import AutoModelForCausalLM

    kwargs: dict[str, Any] = {
        "cache_dir": str(cache_dir),
        "torch_dtype": torch.bfloat16,
        "low_cpu_mem_usage": True,
    }
    if revision is not None:
        kwargs["revision"] = revision
    model = AutoModelForCausalLM.from_pretrained(
        model_source,
        **kwargs,
    )
    meta_parameters = [
        name for name, parameter in model.named_parameters() if parameter.is_meta
    ]
    if meta_parameters:
        raise ExecutionFailure(
            "model loader left meta parameters before compression: "
            + ", ".join(meta_parameters[:8])
        )
    # The pinned basic pipeline dispatches the CPU model after calibration setup.
    # Pre-placing it on CUDA would make that dispatcher see less free VRAM and
    # incorrectly create CPU/meta offload placements.
    return model


def _load_tokenizer(model_source: str, revision: str | None, cache_dir: Path) -> Any:
    from transformers import AutoTokenizer

    kwargs: dict[str, Any] = {"cache_dir": str(cache_dir), "use_fast": True}
    if revision is not None:
        kwargs["revision"] = revision
    return AutoTokenizer.from_pretrained(model_source, **kwargs)


def _build_recipe(assignments: Sequence[ModuleAssignment], group_size: int) -> Any:
    from compressed_tensors.quantization import QuantizationArgs, QuantizationScheme
    from llmcompressor.modifiers.quantization import GPTQModifier

    grouped: dict[str, list[str]] = {}
    precisions: dict[str, Precision] = {}
    ignored: list[str] = []
    for assignment in assignments:
        if assignment.requested_precision is Precision.BF16:
            ignored.append(assignment.module_path)
            continue
        grouped.setdefault(assignment.group_id, []).append(assignment.module_path)
        previous = precisions.setdefault(assignment.group_id, assignment.requested_precision)
        if previous is not assignment.requested_precision:
            raise ExecutionFailure(f"mixed precision inside group {assignment.group_id}")

    config_groups: dict[str, Any] = {}
    for group_id, targets in grouped.items():
        precision = precisions[group_id]
        weights: dict[str, Any] = {
            "num_bits": 8 if precision is Precision.W8A16 else 4,
            "type": "int",
            "strategy": "channel" if precision is Precision.W8A16 else "group",
            "symmetric": True,
            "dynamic": False,
        }
        if precision is Precision.W4A16:
            weights["group_size"] = group_size
        config_groups[group_id] = QuantizationScheme(
            targets=targets,
            weights=QuantizationArgs(**weights),
            format="pack-quantized",
        )

    if not config_groups:
        raise ExecutionFailure("quantized condition has no integer targets")
    return GPTQModifier(
        config_groups=config_groups,
        ignore=[*ignored, "lm_head"],
        block_size=group_size,
        dampening_frac=0.01,
        actorder="weight",
        offload_hessians=True,
    )


def _serve_and_inspect(
    model_path: str,
    model_revision: str | None,
    model_cache: Path,
    prompts: Sequence[str],
    assignments: Sequence[ModuleAssignment],
    torch: Any,
    *,
    quantized: bool,
    packed_aliases: Mapping[str, str],
) -> dict[str, Any]:
    # vLLM 0.11.2's V1 engine serializes apply_model callbacks through
    # msgspec and requires this explicit opt-in for a callable inspection hook.
    os.environ["VLLM_ALLOW_INSECURE_SERIALIZATION"] = "1"
    from vllm import LLM, SamplingParams

    kwargs: dict[str, Any] = {
        "model": model_path,
        "dtype": "bfloat16",
        "tensor_parallel_size": 1,
        "gpu_memory_utilization": 0.80,
        "max_model_len": 2048,
        "enforce_eager": True,
        "disable_log_stats": True,
    }
    if model_revision is not None:
        kwargs["revision"] = model_revision
    if model_cache:
        kwargs["download_dir"] = str(model_cache)
    llm = LLM(**kwargs)
    outputs = llm.generate(
        list(prompts),
        SamplingParams(temperature=0.0, max_tokens=8),
        use_tqdm=False,
    )
    nonempty = sum(bool(output.outputs and output.outputs[0].text.strip()) for output in outputs)
    observed = _observed_vllm_map(
        llm,
        assignments,
        kernel_required=quantized,
        packed_aliases=packed_aliases,
    )
    kernel = _kernel_validation(assignments, observed, quantized=quantized)
    map_comparison = compare_precision_maps(assignments, observed)
    del llm
    gc.collect()
    torch.cuda.empty_cache()
    return {
        "generation": {
            "request_count": len(prompts),
            "nonempty_count": nonempty,
            "status": "pass" if nonempty == len(prompts) else "failed",
        },
        "vllm_realized_precision_map": {
            path: observation.__dict__ for path, observation in observed.items()
        },
        "vllm_map_validation": _comparison_payload(map_comparison),
        "kernel_validation": kernel,
    }


def _export_digest(export_dir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(p for p in export_dir.rglob("*") if p.is_file()):
        if "compressor-log" in path.parts:
            continue
        digest.update(str(path.relative_to(export_dir)).encode("utf-8"))
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def _reload_export(
    export_dir: Path,
    assignments: Sequence[ModuleAssignment],
    torch: Any,
) -> dict[str, Any]:
    from transformers import AutoModelForCausalLM

    model = AutoModelForCausalLM.from_pretrained(
        str(export_dir),
        torch_dtype="auto",
        device_map={"": "cuda:0"},
        low_cpu_mem_usage=True,
    )
    observed = _observed_map(model, assignments, torch, kernel_required=False)
    comparison = compare_precision_maps(assignments, observed)
    result = {
        "status": "pass" if comparison.exact_match else "failed",
        "fresh_process": True,
        "map_validation": _comparison_payload(comparison),
        "realized_precision_map": {path: value.__dict__ for path, value in observed.items()},
        "artifact_sha256": _export_digest(export_dir),
    }
    del model
    gc.collect()
    torch.cuda.empty_cache()
    return result


def _fresh_process_reload(
    config_path: Path,
    schedule_id: str,
    export_dir: Path,
    model_cache: Path,
    device_index: int,
) -> dict[str, Any]:
    result_path = export_dir.parent / (export_dir.name + ".reload.json")
    command = [
        sys.executable,
        "-m",
        "qcb.execution",
        "--reload",
        "--condition",
        schedule_id,
        "--config",
        str(config_path),
        "--model-cache",
        str(model_cache),
        "--export-dir",
        str(export_dir),
        "--device-index",
        str(device_index),
        "--result",
        str(result_path),
    ]
    child_env = os.environ.copy()
    child_env["CUDA_VISIBLE_DEVICES"] = str(device_index)
    completed = subprocess.run(
        command,
        cwd=str(Path.cwd()),
        env=child_env,
        capture_output=True,
        text=True,
        check=False,
    )
    if not result_path.is_file():
        raise ExecutionFailure(
            "fresh-process export reload did not create a result: "
            + completed.stderr[-2000:]
        )
    result = json.loads(result_path.read_text(encoding="utf-8"))
    result["stdout"] = completed.stdout
    result["stderr"] = completed.stderr
    if completed.returncode != 0:
        raise ExecutionFailure(f"fresh-process export reload failed: {result.get('error')}")
    return result


def _run_condition(
    config: Mapping[str, Any],
    schedule_id: str,
    config_path: Path,
    model_source: str | None,
    model_cache: Path,
    calibration_dir: Path,
    export_dir: Path,
    device_index: int,
    sample_count: int,
) -> dict[str, Any]:
    import torch

    if not torch.cuda.is_available():
        raise ExecutionFailure("CUDA is unavailable in the selected execution environment")
    torch.cuda.set_device(0)
    manifest = resolve_candidate_manifest(config)
    schedule = _schedule(manifest, schedule_id)
    assignments = _assignment_objects(schedule)
    requested = _requested_precisions(assignments)
    quantized = any(precision is not Precision.BF16 for precision in requested)
    prompts = _read_prompts(calibration_dir, min(8, sample_count))
    started = _resource_snapshot(torch, export_dir)
    environment = _runtime_environment(config, model_cache)
    environment["model_source"] = model_source or config["model"]["id"]
    environment["schedule_id"] = schedule_id
    environment["calibration_samples_used"] = sample_count
    environment["calibration_path"] = str(calibration_dir)
    hardware = _hardware_observation(device_index, torch)
    source = model_source or config["model"]["id"]
    revision = None if model_source else config["model"]["revision"]
    packed_aliases = {
        str(source_suffix): str(fused_suffix)
        for source_suffix, fused_suffix in config.get("vllm_packed_module_aliases", {}).items()
    }

    if not quantized:
        served = _serve_and_inspect(
            source,
            revision,
            model_cache,
            prompts,
            assignments,
            torch,
            quantized=False,
            packed_aliases=packed_aliases,
        )
        comparison = served["vllm_map_validation"]
        reload_result = {"status": "not_applicable", "fresh_process": False, "artifact_sha256": None}
        realized = served["vllm_realized_precision_map"]
    else:
        model = _load_model(source, revision, model_cache, torch)
        tokenizer = _load_tokenizer(source, revision, model_cache)
        recipe = _build_recipe(assignments, int(config["quantization"]["group_size"]))
        import llmcompressor

        # LLM Compressor 0.9.0 scans every JSON file in dataset_path.
        # Stage only train.json so the calibration manifest is not treated as
        # another dataset shard.
        with tempfile.TemporaryDirectory(prefix="qcb-calibration-") as staged_root:
            staged_train = Path(staged_root) / "train.json"
            shutil.copy2(calibration_dir / "train.json", staged_train)
            llmcompressor.oneshot(
                model=model,
                tokenizer=tokenizer,
                recipe=recipe,
                dataset="json",
                dataset_path=staged_root,
                splits="train",
                num_calibration_samples=sample_count,
                shuffle_calibration_samples=False,
                max_seq_length=int(config["calibration"]["sequence_length"]),
                pad_to_max_length=True,
                text_column="text",
                preprocessing_num_workers=0,
                pipeline="basic",
                model_revision=revision or config["model"]["revision"],
                precision="bfloat16",
                save_compressed=True,
                output_dir=str(export_dir),
                log_dir=str(export_dir / "compressor-log"),
                clear_sparse_session=True,
            )
        del tokenizer, model
        gc.collect()
        torch.cuda.empty_cache()
        reloaded = _fresh_process_reload(
            config_path,
            schedule_id,
            export_dir,
            model_cache,
            device_index,
        )
        realized = reloaded["realized_precision_map"]
        comparison = reloaded["map_validation"]
        served = _serve_and_inspect(
            str(export_dir),
            None,
            model_cache,
            prompts,
            assignments,
            torch,
            quantized=True,
            packed_aliases=packed_aliases,
        )
        reload_result = reloaded

    ended = _resource_snapshot(torch, export_dir)
    return {
        "status": "completed",
        "schedule_id": schedule_id,
        "requested_precision": "+".join(precision.value for precision in requested),
        "requested_precision_map": schedule["requested_precision_map"],
        "realized_precision_map": realized,
        "map_validation": comparison,
        "kernel_validation": served["kernel_validation"],
        "vllm_map_validation": served["vllm_map_validation"],
        "vllm_realized_precision_map": served["vllm_realized_precision_map"],
        "export_reload_validation": reload_result,
        "generation": served["generation"],
        "resources": {"before": started, "after": ended},
        "environment": environment,
        "hardware": hardware,
    }


def execute_capability_preflight(
    config: Mapping[str, Any],
    *,
    run_path: Path,
    config_path: Path | None = None,
    model_cache: Path,
    calibration_dir: Path,
    device_index: int,
    sample_count: int | None = None,
    model_source: str | None = None,
) -> dict[str, Any]:
    manifest = resolve_candidate_manifest(config)
    schedule_values = tuple(
        str(value)
        for value in config.get(
            "capability_preflight_schedules",
            ["BBBB", "8888", "4444", "B844"],
        )
    )
    available = {"".join(schedule["symbols"]): str(schedule["schedule_id"]) for schedule in manifest["schedules"]}
    selected = tuple(available.get(value, value) for value in schedule_values)
    valid_ids = {str(schedule["schedule_id"]) for schedule in manifest["schedules"]}
    if any(value not in valid_ids for value in selected):
        raise ExecutionFailure(
            f"capability preflight schedules are not in the manifest: {schedule_values}"
        )
    count = sample_count or int(config["calibration"]["samples"])
    if count < 8:
        raise ExecutionFailure("real capability preflight requires at least eight calibration samples")
    results: list[dict[str, Any]] = []
    stdout_parts: list[str] = []
    stderr_parts: list[str] = []
    conditions_dir = run_path / "condition_results"
    exports_dir = run_path / "exports"
    conditions_dir.mkdir(parents=True, exist_ok=True)
    exports_dir.mkdir(parents=True, exist_ok=True)
    resolved_config_path = config_path or (Path.cwd() / "configs/issue-5-phase1.json")
    for schedule_id in selected:
        result_path = conditions_dir / (schedule_id.replace("/", "_") + ".json")
        export_dir = exports_dir / schedule_id.replace("/", "_")
        command = [
            sys.executable,
            "-m",
            "qcb.execution",
            "--condition",
            schedule_id,
            "--config",
            str(resolved_config_path),
            "--model-cache",
            str(model_cache),
            "--model-source",
            str(model_source) if model_source else "",
            "--calibration-dir",
            str(calibration_dir),
            "--export-dir",
            str(export_dir),
            "--device-index",
            str(device_index),
            "--sample-count",
            str(count),
            "--result",
            str(result_path),
        ]
        child_env = os.environ.copy()
        child_env["CUDA_VISIBLE_DEVICES"] = str(device_index)
        child_env["TOKENIZERS_PARALLELISM"] = "false"
        completed = subprocess.run(
            command,
            cwd=str(Path.cwd()),
            env=child_env,
            capture_output=True,
            text=True,
            check=False,
        )
        stdout_parts.append(f"$ {' '.join(command)}\n{completed.stdout}")
        stderr_parts.append(f"$ {' '.join(command)}\n{completed.stderr}")
        if result_path.is_file():
            result = json.loads(result_path.read_text(encoding="utf-8"))
        else:
            result = {
                "status": "failed",
                "schedule_id": schedule_id,
                "error": "condition child did not create a result artifact",
            }
        results.append(result)
        if completed.returncode != 0 or result.get("status") != "completed":
            break

    capability = bool(results) and len(results) == len(selected) and all(
        result.get("status") == "completed"
        and result.get("map_validation", {}).get("exact_match", True)
        and result.get("vllm_map_validation", {}).get("exact_match", True)
        and result.get("kernel_validation", {}).get("status") in {"pass", "not_applicable"}
        and result.get("export_reload_validation", {}).get("status") in {"pass", "not_applicable"}
        and result.get("generation", {}).get("status") == "pass"
        for result in results
    )
    return {
        "status": "completed" if capability else "failed",
        "capability_claim": capability,
        "selected_schedule_ids": list(selected),
        "conditions": results,
        "environment": results[0].get("environment", {}) if results else {},
        "hardware": results[0].get("hardware", {}) if results else {},
        "stdout": "\n".join(stdout_parts),
        "stderr": "\n".join(stderr_parts),
        "error": None if capability else "one or more capability gates failed",
    }


def _child_main(args: argparse.Namespace) -> int:
    try:
        config = load_config(Path(args.config))
        result = _run_condition(
            config,
            args.condition,
            Path(args.config),
            args.model_source or None,
            Path(args.model_cache),
            Path(args.calibration_dir),
            Path(args.export_dir),
            args.device_index,
            args.sample_count,
        )
    except Exception as error:
        result = {
            "status": "failed",
            "schedule_id": args.condition,
            "error": f"{type(error).__name__}: {error}",
            "traceback": traceback.format_exc(),
        }
        print(result["error"], file=sys.stderr)
        _json_write_once(Path(args.result), result)
        return 1
    _json_write_once(Path(args.result), result)
    print(json.dumps({"schedule_id": args.condition, "status": result["status"]}, sort_keys=True))
    return 0


def _reload_main(args: argparse.Namespace) -> int:
    try:
        config = load_config(Path(args.config))
        manifest = resolve_candidate_manifest(config)
        schedule = _schedule(manifest, args.condition)
        assignments = _assignment_objects(schedule)
        import torch

        if not torch.cuda.is_available():
            raise ExecutionFailure("CUDA is unavailable during fresh-process reload")
        torch.cuda.set_device(0)
        result = _reload_export(Path(args.export_dir), assignments, torch)
        result["schedule_id"] = args.condition
        result["status"] = result.get("status", "failed")
    except Exception as error:
        result = {
            "status": "failed",
            "schedule_id": args.condition,
            "error": f"{type(error).__name__}: {error}",
            "traceback": traceback.format_exc(),
        }
        print(result["error"], file=sys.stderr)
        _json_write_once(Path(args.result), result)
        return 1
    _json_write_once(Path(args.result), result)
    print(json.dumps({"schedule_id": args.condition, "status": result["status"]}, sort_keys=True))
    return 0


def build_child_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m qcb.execution")
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--condition")
    parser.add_argument("--config", required=True)
    parser.add_argument("--model-cache", required=True)
    parser.add_argument("--model-source", default="")
    parser.add_argument("--calibration-dir")
    parser.add_argument("--export-dir", required=True)
    parser.add_argument("--device-index", required=True, type=int)
    parser.add_argument("--sample-count", type=int)
    parser.add_argument("--result", required=True)
    return parser


if __name__ == "__main__":
    arguments = build_child_parser().parse_args()
    if arguments.reload:
        raise SystemExit(_reload_main(arguments))
    if not arguments.condition or arguments.sample_count is None or not arguments.calibration_dir:
        raise SystemExit("--condition, --sample-count, and --calibration-dir are required")
    raise SystemExit(_child_main(arguments))
