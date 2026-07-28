"""Materialize frozen real calibration text for the Phase 1 run."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .manifest import load_config


def prepare_calibration(
    config: Mapping[str, Any],
    *,
    output_dir: Path,
    cache_dir: Path,
    sample_count: int | None = None,
) -> dict[str, Any]:
    if output_dir.exists():
        raise FileExistsError(f"calibration output already exists: {output_dir}")
    calibration = config["calibration"]
    count = sample_count or int(calibration["samples"])
    if count < 8:
        raise ValueError("at least eight calibration samples are required")
    from datasets import load_dataset
    from transformers import AutoTokenizer

    dataset = load_dataset(
        str(calibration["dataset_id"]),
        revision=str(calibration["dataset_revision"]),
        split="train",
        cache_dir=str(cache_dir),
        # This pinned revision publishes a test split although its dataset
        # metadata declares only train. Train is selected explicitly; disabling
        # split verification avoids rejecting that source-level metadata drift.
        verification_mode="no_checks",
    )
    if len(dataset) < count:
        raise ValueError(f"dataset has {len(dataset)} rows, requires {count}")
    dataset = dataset.shuffle(seed=int(config.get("seed", 0))).select(range(count))
    tokenizer = AutoTokenizer.from_pretrained(
        config["model"]["id"],
        revision=config["model"]["revision"],
        cache_dir=str(cache_dir),
        use_fast=True,
    )
    output_dir.mkdir(parents=True)
    rows: list[dict[str, Any]] = []
    for row in dataset:
        problem = row.get("problem") or row.get("question") or row.get("text")
        if not isinstance(problem, str) or not problem.strip():
            raise ValueError("calibration source row has no text-bearing field")
        text = tokenizer.apply_chat_template(
            [{"role": "user", "content": problem}],
            tokenize=False,
            add_generation_prompt=True,
        )
        rows.append({"text": text})
    train_path = output_dir / "train.json"
    with train_path.open("x", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    digest = hashlib.sha256(train_path.read_bytes()).hexdigest()
    manifest = {
        "schema_version": "qcb.calibration.v1",
        "dataset_id": calibration["dataset_id"],
        "dataset_revision": calibration["dataset_revision"],
        "dataset_split": "train",
        "dataset_verification_mode": "no_checks",
        "dataset_verification_reason": (
            "pinned revision publishes an extra test split; train selected explicitly"
        ),
        "model_id": config["model"]["id"],
        "model_revision": config["model"]["revision"],
        "sample_count": count,
        "sequence_length": calibration["sequence_length"],
        "chat_template_applied": True,
        "train_json_sha256": digest,
    }
    with (output_dir / "manifest.json").open("x", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return manifest


def _main(args: argparse.Namespace) -> int:
    config = load_config(Path(args.config))
    result = prepare_calibration(
        config,
        output_dir=Path(args.output_dir),
        cache_dir=Path(args.cache_dir),
        sample_count=args.sample_count,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m qcb.calibration")
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--cache-dir", required=True)
    parser.add_argument("--sample-count", type=int)
    return parser


if __name__ == "__main__":
    raise SystemExit(_main(build_parser().parse_args()))
