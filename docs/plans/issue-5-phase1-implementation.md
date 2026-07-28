# Issue #5 Phase 1 implementation plan

## Scientific objective

Create the smallest reusable, configuration-driven measurement contract for the
frozen schedule-codebook preflight. Phase 1 resolves candidate intent and
artifact seams only; it does not establish backend capability or run a model.

## Assumptions

- The frozen model, schedule family, and module suffixes are configuration data.
- BF16 modules are excluded from integer target groups and remain visible in the
  requested map.
- No package installation, model/data download, quantization, model load, or
  GPU action is authorized in this phase.
- Runtime capability remains unknown until the version conflict and remote
  environment are resolved.

## Design and affected files

- `qcb/contract.py`: contiguous partition and canonical schedule contracts.
- `qcb/backend.py`: deterministic explicit module-target and candidate scheme
  generation; it does not import a quantization backend.
- `qcb/manifest.py` and `configs/issue-5-phase1.json`: real config-driven
  candidate manifest resolution.
- `qcb/validation.py`: requested-versus-realized map comparison.
- `qcb/run_contract.py`: exclusive run directories and artifact validation.
- `qcb/benchmark.py`: matched-condition result schema and validation.
- `qcb/cli.py`: no-GPU manifest and planned run-contract entry points.
- `tests/`: six seam tests plus the no-GPU CLI integration check.
- `docs/research/issue-5-phase1-backend-contract-research.md`: pinned-source
  findings and unresolved runtime claims.
- `docs/runbook.md`: verified local commands and remote unknowns.

## Validation approach

Run each focused seam test after its minimal implementation, then run the full
CPU-only suite, syntax checks, the no-GPU manifest CLI, and the planned
run-contract CLI in a temporary artifact root. Inspect all required run files.

## Risks and decisions

- Qwen module names and vLLM fusion are not runtime-verified; suffixes remain
  config-driven and all planned paths are marked requested, not realized.
- The pinned LLM Compressor metadata requires compressed-tensors 0.13.0 while
  vLLM 0.11.2 requires 0.12.2. No installation or preflight may proceed until
  this is resolved by a dated decision.
- JSON is used as the input format and as JSON-compatible YAML for the required
  resolved_config.yaml artifact so Phase 1 adds no dependency.
- Planned artifacts explicitly use `not_run` and `capability_claim: false`.

## Milestones

1. Green the six approved TDD seams.
2. Resolve and print the complete frozen candidate manifest without model load.
3. Record a validated planned run contract.
4. Stop before backend installation or GPU execution.
