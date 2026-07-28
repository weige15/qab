"""Public configuration contracts for schedule-codebook experiments."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from collections.abc import Sequence


class ConfigurationError(ValueError):
    """Raised when an experiment configuration violates a frozen contract."""


@dataclass(frozen=True)
class BlockGroup:
    """Inclusive transformer-layer range assigned as one block group."""

    group_id: str
    start_layer: int
    end_layer: int


@dataclass(frozen=True)
class BlockPartition:
    """Named partition of the complete transformer-layer index range."""

    partition_id: str
    layer_count: int
    groups: tuple[BlockGroup, ...]

    def __post_init__(self) -> None:
        groups = tuple(self.groups)
        object.__setattr__(self, "groups", groups)
        validate_contiguous_partition(groups, layer_count=self.layer_count)


class Precision(str, Enum):
    """Allowed weight precision symbols in a schedule."""

    BF16 = "BF16"
    W8A16 = "W8A16"
    W4A16 = "W4A16"

    @property
    def symbol(self) -> str:
        return {Precision.BF16: "B", Precision.W8A16: "8", Precision.W4A16: "4"}[self]

    @classmethod
    def from_value(cls, value: str | "Precision") -> "Precision":
        if isinstance(value, cls):
            return value
        aliases = {
            "B": cls.BF16,
            "8": cls.W8A16,
            "4": cls.W4A16,
            cls.BF16.value: cls.BF16,
            cls.W8A16.value: cls.W8A16,
            cls.W4A16.value: cls.W4A16,
        }
        try:
            return aliases[value]
        except KeyError as error:
            raise ConfigurationError(f"unsupported precision value: {value!r}") from error


@dataclass(frozen=True)
class PrecisionSchedule:
    """Canonical precision assignment for one named block partition."""

    partition_id: str
    precisions: tuple[Precision, ...]

    @classmethod
    def parse(
        cls,
        partition: BlockPartition,
        value: str | Sequence[str | Precision],
    ) -> "PrecisionSchedule":
        if isinstance(value, str):
            compact = value.strip()
            if len(compact) != len(partition.groups):
                raise ConfigurationError(
                    f"schedule {value!r} must contain {len(partition.groups)} symbols"
                )
            raw_values: Sequence[str | Precision] = tuple(compact)
        else:
            raw_values = value

        precisions = tuple(Precision.from_value(item) for item in raw_values)
        if len(precisions) != len(partition.groups):
            raise ConfigurationError(
                "schedule length must match the number of partition groups"
            )
        return cls(partition.partition_id, precisions)

    @property
    def canonical_symbols(self) -> str:
        return "".join(precision.symbol for precision in self.precisions)

    @property
    def schedule_id(self) -> str:
        return f"qcb.v1/{self.partition_id}/{self.canonical_symbols}"

def validate_contiguous_partition(
    groups: tuple[BlockGroup, ...], *, layer_count: int
) -> tuple[BlockGroup, ...]:
    """Validate an ordered, gap-free, non-overlapping layer partition."""

    if not 4 <= len(groups) <= 8:
        raise ConfigurationError("a block partition must contain four to eight groups")
    if layer_count <= 0:
        raise ConfigurationError("layer_count must be positive")

    expected_start = 0
    for group in groups:
        if group.start_layer != expected_start:
            raise ConfigurationError(
                "block groups must be contiguous and start at layer "
                f"{expected_start}, got {group.start_layer}"
            )
        if group.end_layer < group.start_layer:
            raise ConfigurationError(f"group {group.group_id} has an invalid range")
        expected_start = group.end_layer + 1

    if expected_start != layer_count:
        raise ConfigurationError(
            "block groups must cover every layer through "
            f"{layer_count - 1}, ended at {expected_start - 1}"
        )
    return groups
