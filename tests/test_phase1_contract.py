import pytest

from qcb.backend import build_backend_config, planned_module_assignments
from qcb.contract import (
    BlockGroup,
    BlockPartition,
    ConfigurationError,
    Precision,
    PrecisionSchedule,
    validate_contiguous_partition,
)


def test_partition_must_cover_all_layers_once_and_contiguously() -> None:
    groups = (
        BlockGroup("g00", 0, 6),
        BlockGroup("g01", 7, 13),
        BlockGroup("g02", 14, 20),
        BlockGroup("g03", 21, 27),
    )

    assert validate_contiguous_partition(groups, layer_count=28) == groups


def test_partition_rejects_a_gap() -> None:
    groups = (
        BlockGroup("g00", 0, 6),
        BlockGroup("g01", 8, 13),
        BlockGroup("g02", 14, 20),
        BlockGroup("g03", 21, 27),
    )

    with pytest.raises(ConfigurationError, match="contiguous"):
        validate_contiguous_partition(groups, layer_count=28)


def test_schedule_is_canonical_and_has_a_stable_id() -> None:
    partition = BlockPartition(
        "g4-equal7",
        28,
        (
            BlockGroup("g00", 0, 6),
            BlockGroup("g01", 7, 13),
            BlockGroup("g02", 14, 20),
            BlockGroup("g03", 21, 27),
        ),
    )

    from_symbols = PrecisionSchedule.parse(partition, ["BF16", "W8A16", "W4A16", "W4A16"])
    from_compact = PrecisionSchedule.parse(partition, "B844")

    assert from_symbols == from_compact
    assert from_compact.canonical_symbols == "B844"
    assert from_compact.schedule_id == "qcb.v1/g4-equal7/B844"


def test_backend_targets_are_deterministic_and_bf16_is_excluded() -> None:
    partition = BlockPartition(
        "g4-equal7",
        28,
        (
            BlockGroup("g00", 0, 6),
            BlockGroup("g01", 7, 13),
            BlockGroup("g02", 14, 20),
            BlockGroup("g03", 21, 27),
        ),
    )
    schedule = PrecisionSchedule.parse(partition, "B844")

    assignments = planned_module_assignments(partition, schedule)
    config = build_backend_config(assignments, group_size=128)

    assert assignments[0].module_path == "model.layers.0.self_attn.q_proj"
    assert assignments[0].requested_precision is Precision.BF16
    assert assignments[7 * 7].module_path == "model.layers.7.self_attn.q_proj"
    assert assignments[7 * 7].requested_precision is Precision.W8A16
    assert config["config_groups"]["g01"]["targets"][:7] == [
        "model.layers.7.self_attn.q_proj",
        "model.layers.7.self_attn.k_proj",
        "model.layers.7.self_attn.v_proj",
        "model.layers.7.self_attn.o_proj",
        "model.layers.7.mlp.gate_proj",
        "model.layers.7.mlp.up_proj",
        "model.layers.7.mlp.down_proj",
    ]
    assert len(config["config_groups"]["g01"]["targets"]) == 49
    assert "g00" not in config["config_groups"]
    assert config["ignore"][-1] == "lm_head"
