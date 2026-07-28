"""Validation of requested and runtime-realized module maps."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from .backend import ModuleAssignment
from .contract import Precision


@dataclass(frozen=True)
class RealizedModule:
    """Runtime observation for one module after backend construction."""

    realized_precision: Precision | None
    scheme: str | None
    module_class: str | None
    kernel: str | None
    device: str | None
    excluded: bool = False


@dataclass(frozen=True)
class PrecisionMapComparison:
    """Machine-readable differences between requested and realized maps."""

    missing: tuple[str, ...]
    extra: tuple[str, ...]
    wrong_precision: tuple[str, ...]
    unexpected_exclusions: tuple[str, ...]
    fallback_dispatches: tuple[str, ...]

    @property
    def exact_match(self) -> bool:
        return not any(
            (
                self.missing,
                self.extra,
                self.wrong_precision,
                self.unexpected_exclusions,
                self.fallback_dispatches,
            )
        )


def compare_precision_maps(
    requested: Sequence[ModuleAssignment],
    realized: Mapping[str, RealizedModule],
) -> PrecisionMapComparison:
    """Compare every requested module with its runtime observation."""

    requested_by_path = {assignment.module_path: assignment for assignment in requested}
    requested_paths = set(requested_by_path)
    realized_paths = set(realized)
    missing = tuple(sorted(requested_paths - realized_paths))
    extra = tuple(sorted(realized_paths - requested_paths))

    wrong_precision: list[str] = []
    unexpected_exclusions: list[str] = []
    fallback_dispatches: list[str] = []
    for path in sorted(requested_paths & realized_paths):
        assignment = requested_by_path[path]
        observation = realized[path]
        if observation.realized_precision is None or observation.excluded:
            unexpected_exclusions.append(path)
        elif observation.realized_precision is not assignment.requested_precision:
            wrong_precision.append(path)
        kernel = (observation.kernel or "").lower()
        device = (observation.device or "").lower()
        if "fallback" in kernel or "cpu" in kernel or not device.startswith("cuda"):
            fallback_dispatches.append(path)

    return PrecisionMapComparison(
        missing=missing,
        extra=extra,
        wrong_precision=tuple(wrong_precision),
        unexpected_exclusions=tuple(unexpected_exclusions),
        fallback_dispatches=tuple(fallback_dispatches),
    )
