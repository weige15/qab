"""Matched-condition benchmark result records."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from math import ceil
from statistics import fmean
from typing import Any


@dataclass(frozen=True)
class BenchmarkCondition:
    runtime_id: str
    hardware_id: str
    gpu_index: int
    batch_size: int
    input_length: int
    output_length: int
    warmup_count: int
    repetition_count: int
    cuda_synchronized: bool
    prompt_order_id: str
    decoding_id: str

    def to_record(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BenchmarkResult:
    schedule_id: str
    condition: BenchmarkCondition
    status: str
    elapsed_ms: tuple[float, ...]

    def __post_init__(self) -> None:
        if self.status not in {"completed", "failed", "excluded"}:
            raise ValueError(f"unsupported benchmark status: {self.status}")
        if any(value < 0 for value in self.elapsed_ms):
            raise ValueError("elapsed timings must be non-negative")
        if self.status == "completed" and not self.elapsed_ms:
            raise ValueError("completed benchmark results require observations")

    @staticmethod
    def _quantile(values: tuple[float, ...], probability: float) -> float:
        ordered = sorted(values)
        rank = max(1, ceil(probability * len(ordered)))
        return ordered[rank - 1]

    def to_record(self) -> dict[str, Any]:
        summary: dict[str, float | int] = {"count": len(self.elapsed_ms)}
        if self.elapsed_ms:
            summary.update(
                {
                    "mean_ms": fmean(self.elapsed_ms),
                    "p50_ms": self._quantile(self.elapsed_ms, 0.50),
                    "p95_ms": self._quantile(self.elapsed_ms, 0.95),
                }
            )
        return {
            "schema_version": "qcb.benchmark_result.v1",
            "schedule_id": self.schedule_id,
            "condition": self.condition.to_record(),
            "status": self.status,
            "elapsed_ms": list(self.elapsed_ms),
            "summary": summary,
        }


@dataclass(frozen=True)
class MatchedConditionValidation:
    differences: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.differences


def validate_matched_conditions(
    results: tuple[BenchmarkResult, ...],
) -> MatchedConditionValidation:
    """Ensure all schedules were measured under one identical condition."""

    if not results:
        return MatchedConditionValidation(("results",))
    baseline = results[0].condition.to_record()
    differences: set[str] = set()
    for result in results[1:]:
        current = result.condition.to_record()
        differences.update(
            field for field, value in baseline.items() if current[field] != value
        )
    return MatchedConditionValidation(tuple(sorted(differences)))
