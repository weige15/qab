"""Configuration-driven candidate schedule manifest resolution."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .backend import QWEN_LINEAR_SUFFIXES, build_backend_config, planned_module_assignments
from .contract import BlockGroup, BlockPartition, ConfigurationError, PrecisionSchedule


def _partition_from_config(raw: Mapping[str, Any]) -> BlockPartition:
    partition_raw = raw["partition"]
    groups = tuple(
        BlockGroup(
            group_id=str(group["group_id"]),
            start_layer=int(group["start_layer"]),
            end_layer=int(group["end_layer"]),
        )
        for group in partition_raw["groups"]
    )
    return BlockPartition(
        partition_id=str(partition_raw["partition_id"]),
        layer_count=int(partition_raw["layer_count"]),
        groups=groups,
    )


def load_config(path: Path) -> dict[str, Any]:
    """Load the dependency-free JSON-compatible experiment configuration."""

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ConfigurationError(f"cannot load experiment config {path}") from error
    if not isinstance(raw, dict):
        raise ConfigurationError("experiment config root must be an object")
    if raw.get("schema_version") != "qcb.phase1.config.v1":
        raise ConfigurationError("unsupported experiment config schema")
    return raw


def resolve_candidate_manifest(raw: Mapping[str, Any]) -> dict[str, Any]:
    """Resolve all schedules and explicit module assignments without model loading."""

    partition = _partition_from_config(raw)
    schedule_values = tuple(str(value) for value in raw["schedules"])
    if not 8 <= len(schedule_values) <= 16:
        raise ConfigurationError("the candidate codebook must contain eight to sixteen schedules")
    schedules: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    module_prefix = str(raw.get("module_prefix", "model.layers"))
    suffixes = tuple(str(value) for value in raw.get("linear_suffixes", QWEN_LINEAR_SUFFIXES))
    quantization = raw["quantization"]
    group_size = int(quantization["group_size"])
    for value in schedule_values:
        schedule = PrecisionSchedule.parse(partition, value)
        if schedule.schedule_id in seen_ids:
            raise ConfigurationError(f"duplicate schedule: {schedule.schedule_id}")
        seen_ids.add(schedule.schedule_id)
        assignments = planned_module_assignments(
            partition, schedule, module_prefix=module_prefix, linear_suffixes=suffixes
        )
        schedules.append(
            {
                "schedule_id": schedule.schedule_id,
                "symbols": list(schedule.canonical_symbols),
                "groups": [
                    {
                        "group_id": group.group_id,
                        "start_layer": group.start_layer,
                        "end_layer": group.end_layer,
                        "requested_precision": precision.value,
                    }
                    for group, precision in zip(partition.groups, schedule.precisions, strict=True)
                ],
                "requested_precision_map": [
                    {
                        "module_path": assignment.module_path,
                        "layer_index": assignment.layer_index,
                        "group_id": assignment.group_id,
                        "requested_precision": assignment.requested_precision.value,
                    }
                    for assignment in assignments
                ],
                "backend_config": build_backend_config(assignments, group_size=group_size),
                "realized_precision_map": None,
                "map_validation": {"status": "not_run", "differences": []},
                "kernel_validation": {"status": "not_run", "module_classes": [], "dispatches": []},
                "export_reload_validation": {"status": "not_run", "artifact_sha256": None},
                "eligibility": {"status": "pending", "exclusion_reason": None},
            }
        )

    return {
        "schema_version": "qcb.schedule_manifest.v1",
        "manifest_status": "resolved_without_execution",
        "capability_claim": False,
        "codebook_id": raw["codebook"]["codebook_id"],
        "generator_id": raw["codebook"]["generator_id"],
        "partition": {
            "partition_id": partition.partition_id,
            "layer_count": partition.layer_count,
            "groups": [
                {
                    "group_id": group.group_id,
                    "start_layer": group.start_layer,
                    "end_layer": group.end_layer,
                }
                for group in partition.groups
            ],
        },
        "model": raw["model"],
        "backend": raw["backend"],
        "quantization": raw["quantization"],
        "hardware_target": raw["hardware_target"],
        "schedules": schedules,
    }


def manifest_records(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return one prediction-record-shaped row per planned schedule."""

    return [
        {
            "record_schema": "qcb.schedule_probe.v1",
            "schedule_id": schedule["schedule_id"],
            "status": "planned",
            "capability_evidence": "not_run",
            "requested_precision_map": schedule["requested_precision_map"],
            "realized_precision_map": None,
        }
        for schedule in manifest["schedules"]
    ]


def json_yaml_compatible(value: Mapping[str, Any]) -> str:
    """Serialize JSON, which is also valid YAML 1.2, for the required artifact."""

    return json.dumps(value, indent=2, sort_keys=True) + "\n"
