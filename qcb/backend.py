"""Deterministic backend-target planning without importing a quantizer."""

from __future__ import annotations

from dataclasses import dataclass

from .contract import BlockPartition, ConfigurationError, Precision, PrecisionSchedule


QWEN_LINEAR_SUFFIXES: tuple[str, ...] = (
    "self_attn.q_proj",
    "self_attn.k_proj",
    "self_attn.v_proj",
    "self_attn.o_proj",
    "mlp.gate_proj",
    "mlp.up_proj",
    "mlp.down_proj",
)


@dataclass(frozen=True)
class ModuleAssignment:
    """Requested precision for one eligible linear module."""

    module_path: str
    layer_index: int
    group_id: str
    requested_precision: Precision


def planned_module_assignments(
    partition: BlockPartition,
    schedule: PrecisionSchedule,
    *,
    module_prefix: str = "model.layers",
    linear_suffixes: tuple[str, ...] = QWEN_LINEAR_SUFFIXES,
) -> tuple[ModuleAssignment, ...]:
    """Expand a block schedule into stable, explicit linear-module targets."""

    if partition.partition_id != schedule.partition_id:
        raise ConfigurationError("schedule and partition identifiers do not match")
    if not linear_suffixes or len(set(linear_suffixes)) != len(linear_suffixes):
        raise ConfigurationError("linear module suffixes must be non-empty and unique")

    assignments: list[ModuleAssignment] = []
    for group, precision in zip(partition.groups, schedule.precisions, strict=True):
        for layer_index in range(group.start_layer, group.end_layer + 1):
            for suffix in linear_suffixes:
                assignments.append(
                    ModuleAssignment(
                        module_path=f"{module_prefix}.{layer_index}.{suffix}",
                        layer_index=layer_index,
                        group_id=group.group_id,
                        requested_precision=precision,
                    )
                )
    return tuple(assignments)


def _weight_scheme(precision: Precision, *, group_size: int) -> dict[str, object]:
    if precision is Precision.W8A16:
        return {
            "num_bits": 8,
            "type": "int",
            "strategy": "channel",
            "symmetric": True,
            "dynamic": False,
            "input_activations": None,
            "format": "pack_quantized",
        }
    if precision is Precision.W4A16:
        return {
            "num_bits": 4,
            "type": "int",
            "strategy": "group",
            "group_size": group_size,
            "symmetric": True,
            "dynamic": False,
            "input_activations": None,
            "format": "pack_quantized",
        }
    raise ConfigurationError(f"BF16 cannot be encoded as an integer weight scheme")


def build_backend_config(
    assignments: tuple[ModuleAssignment, ...], *, group_size: int
) -> dict[str, object]:
    """Build a deterministic compressed-tensors-style candidate configuration.

    BF16 modules are deliberately omitted from ``config_groups``. They remain
    in the requested assignment map and are listed in ``ignore`` so that the
    later runtime adapter can audit the exclusion explicitly.
    """
    if group_size <= 0:
        raise ConfigurationError("group_size must be positive")
    config_groups: dict[str, dict[str, object]] = {}
    ignored: list[str] = []
    for assignment in assignments:
        if assignment.requested_precision is Precision.BF16:
            ignored.append(assignment.module_path)
            continue
        group = config_groups.setdefault(
            assignment.group_id,
            {
                "targets": [],
                "weights": _weight_scheme(
                    assignment.requested_precision, group_size=group_size
                ),
            },
        )
        targets = group["targets"]
        assert isinstance(targets, list)
        targets.append(assignment.module_path)

    return {
        "config_groups": config_groups,
        "ignore": [*ignored, "lm_head"],
    }


