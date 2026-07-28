# Issue #5 Phase 1 runbook

Set `ARTIFACT_ROOT` to the approved artifact storage root for the host before using the examples below. The repository does not encode a private machine path.

## Local no-GPU checks

The dependency-free path resolves the frozen JSON-compatible configuration,
expands every candidate schedule into explicit module paths, and prints the
planned assignments without importing a quantizer or loading Qwen.

```bash
python -m pytest -q
python -m qcb.cli resolve-manifest \
  --config configs/issue-5-phase1.json
```

The output must report `resolved_without_execution` and
`capability_claim: false`. The frozen g4-equal7 configuration contains 14
schedules and 196 module assignments per schedule.

## Remote runtime resolution

The approved runtime is isolated on the remote basic-1 host. The final package
set is Python 3.12.3, Torch 2.9.0, Transformers 4.57.3, LLM Compressor
0.9.0, compressed-tensors 0.13.0, and vLLM 0.11.2. vLLM 0.11.2 declares compressed-tensors 0.12.2 while LLM Compressor 0.9.0
requires compressed-tensors 0.13.0. The accepted install deliberately
solves the vLLM side first, then overrides that one metadata requirement:

```bash
uv venv /tmp/qab-issue5-venv --python 3.12
uv pip install --python /tmp/qab-issue5-venv/bin/python \
  torch==2.9.0 vllm==0.11.2 compressed-tensors==0.12.2 \
  'transformers>=4.56.0,<5'
uv pip install --python /tmp/qab-issue5-venv/bin/python \
  transformers==4.57.3 datasets==4.4.1 auto-round==0.9.2 \
  accelerate==1.12.0 requests==2.32.5 nvidia-ml-py==13.590.44 \
  pillow==12.0.0
uv pip install --python /tmp/qab-issue5-venv/bin/python --no-deps \
  llmcompressor==0.9.0 compressed-tensors==0.13.0 \
  tqdm==4.67.1 chardet==5.2.0
```

`uv pip check` is expected to report only the intentional vLLM
compressed-tensors 0.12.2 versus 0.13.0 metadata mismatch. No local package
installation is part of this runbook.

## Calibration materialization

The full calibration path uses 512 training-source MATH rows at the pinned
operational dataset revision and applies the frozen Qwen chat template. The
approved smoke used the existing `preflight-neutral-8-v3/train.json` artifact
and is not full-calibration or quality evidence. The pinned revision publishes
an extra test split despite metadata declaring only train, so the loader selects
train explicitly with `verification_mode=no_checks` and records that reason in
`manifest.json`. The materialized directory is immutable and contains
`train.json` plus `manifest.json`:

```bash
/tmp/qab-issue5-venv/bin/python -m qcb.calibration \
  --config configs/issue-5-phase1.json \
  --output-dir ${ARTIFACT_ROOT}/calibration/<run-id> \
  --cache-dir ${ARTIFACT_ROOT}/hf-cache
```

A smoke check may use `--sample-count 8`; it is not capability evidence. The
historical MATH artifact must be explicitly approved for acquisition before the
full frozen calibration is materialized.

## Real device-7 capability preflight

Check availability immediately before launch:

```bash
nvidia-smi --query-gpu=index,name,memory.total,memory.free,utilization.gpu --format=csv
```

Run the real configuration-driven preflight with an immutable run directory:

```bash
/tmp/qab-issue5-venv/bin/python -m qcb.cli preflight \
  --config configs/issue-5-phase1.json \
  --run-root ${ARTIFACT_ROOT}/runs \
  --run-id <run-id> \
  --execute --device-index 7 \
  --model-cache ${ARTIFACT_ROOT}/hf-cache \
  --calibration-dir ${ARTIFACT_ROOT}/calibration/<run-id>
```

The adapter runs BF16, uniform W8A16, uniform W4A16, and the declared
nontrivial mixed schedule in separate child processes with
`CUDA_VISIBLE_DEVICES=7`. For the pinned vLLM 0.11.2 worker inspection hook,
the adapter sets `VLLM_ALLOW_INSECURE_SERIALIZATION=1` only inside the child
serving process. It records requested and realized maps, the
compressed export digest, fresh-process reload, vLLM generation, kernel
metadata, CPU-fallback status, resources, package versions, and all required
AGENTS.md run-contract files. A configuration or import check never counts as
backend capability.

The approved 8-row B844 smoke completed its single-condition gates: HF and
vLLM maps, mixed W8A16/W4A16/BF16 realization, fused-module inspection,
AllSpark/Marlin kernel dispatch, export/reload, and 8/8 generation. This is
condition-level evidence only. The complete four-condition capability gate
must still be rerun with the alias-aware inspector before claiming the backend
codebook executable.

Quality evaluation, latency benchmarks, and schedule-codebook claims remain
blocked unless every selected capability gate passes.
