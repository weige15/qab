"""Immutable run-directory and artifact-contract helpers."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_ARTIFACTS: tuple[str, ...] = (
    "resolved_config.yaml",
    "command.txt",
    "git_commit.txt",
    "environment.json",
    "hardware.json",
    "random_seeds.json",
    "metrics.json",
    "predictions.jsonl",
    "stdout.log",
    "stderr.log",
    "report.md",
)


class RunContractError(ValueError):
    """Raised when a run artifact violates the immutable run contract."""


@dataclass(frozen=True)
class ArtifactValidation:
    missing: tuple[str, ...]
    invalid: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.missing and not self.invalid


@dataclass(frozen=True)
class RunDirectory:
    path: Path
    run_id: str

    def write_artifact(self, name: str, content: str | bytes) -> Path:
        if name not in REQUIRED_ARTIFACTS:
            raise RunContractError(f"unknown run artifact: {name}")
        target = self.path / name
        try:
            with target.open("xb") as handle:
                handle.write(content.encode("utf-8") if isinstance(content, str) else content)
        except FileExistsError as error:
            raise RunContractError("run artifacts are immutable and write-once") from error
        return target

    def validate_artifacts(self) -> ArtifactValidation:
        missing = tuple(name for name in REQUIRED_ARTIFACTS if not (self.path / name).is_file())
        invalid: list[str] = []
        for name in ("environment.json", "hardware.json", "random_seeds.json", "metrics.json"):
            target = self.path / name
            if target.is_file():
                try:
                    json.loads(target.read_text(encoding="utf-8"))
                except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                    invalid.append(name)
        predictions = self.path / "predictions.jsonl"
        if predictions.is_file():
            try:
                for line in predictions.read_text(encoding="utf-8").splitlines():
                    if line.strip() and not isinstance(json.loads(line), dict):
                        invalid.append("predictions.jsonl")
                        break
            except (OSError, UnicodeDecodeError, json.JSONDecodeError):
                invalid.append("predictions.jsonl")
        for name in ("resolved_config.yaml", "command.txt", "git_commit.txt", "report.md"):
            target = self.path / name
            if target.is_file() and not target.read_text(encoding="utf-8").strip():
                invalid.append(name)
        return ArtifactValidation(missing=missing, invalid=tuple(dict.fromkeys(invalid)))


def create_run_directory(root: Path, *, run_id: str | None = None) -> RunDirectory:
    """Create one never-overwritten run directory with an exclusive mkdir."""

    root.mkdir(parents=True, exist_ok=True)
    requested_id = run_id
    for _ in range(10):
        candidate_id = requested_id or (
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
            + "-"
            + uuid.uuid4().hex[:12]
        )
        if Path(candidate_id).name != candidate_id or candidate_id in {".", ".."}:
            raise RunContractError("run_id must be a single safe directory name")
        candidate = root / candidate_id
        try:
            candidate.mkdir()
        except FileExistsError:
            if requested_id is not None:
                raise
            continue
        return RunDirectory(candidate, candidate_id)
    raise RunContractError("could not allocate a unique run directory")
