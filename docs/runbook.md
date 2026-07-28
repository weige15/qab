# Issue #5 Phase 1 runbook

## Local no-GPU manifest check

The repository has no installed quantization runtime or verified remote lab
command. The dependency-free Phase 1 path resolves the frozen JSON-compatible
configuration, expands the candidate schedules into explicit module paths, and
prints each planned assignment. It does not load Qwen, import a backend, or
launch GPU work.

```bash
python -m pytest -q
python -m qcb.cli resolve-manifest \
  --config configs/issue-5-phase1.json
```

The output must report `resolved_without_execution` and
`capability_claim: false`. For the frozen g4-equal7 config it contains 14
schedules and 196 module assignments per schedule.

## Planned run-contract recording

Use a temporary or documented artifact root outside tracked source:

```bash
python -m qcb.cli preflight \
  --config configs/issue-5-phase1.json \
  --run-root /path/to/run-root \
  --run-id planned-phase1
```

This records all required AGENTS.md files, validates their structure, and marks
capability, realized maps, kernels, export/reload, and hardware observations as
`not_run`. `--execute` intentionally refuses in Phase 1 because no real backend
execution adapter has been verified.

## Remote execution status

The remote host, scheduler, environment installation command, GPU allocation,
and coherent package resolution are **Unknown**. Do not install packages,
download Qwen, query or consume a shared GPU, or launch a preflight until the
LLM Compressor `0.9.0` metadata conflict with frozen compressed-tensors `0.12.2`
is resolved in a dated decision and human approval is recorded.

A future real preflight must record the exact RTX 3090 availability query,
selected device, runtime lock, model revision, module map, realized scheme and
kernel fields, CPU-fallback status, export digest, fresh-process reload result,
resource measurements, and matched timing conditions in a new immutable run.
