# AGENTS.md

## Project Purpose

This repository studies compositional, query-adaptive block-group
mixed-precision LLM inference and precision-compatible request batching.

The research question is whether a multidimensional representation of a
composite request can predict its block-group quantization-sensitivity profile,
so the system can select a quality-safe mixed-precision schedule and batch
requests with compatible schedules.

The repository is an early-stage research project. The model, dataset,
quantization backend, serving runtime, lab connection command, and build/test
toolchain are unknown until documented or verified. Do not invent them.

## Current Research Scope

The following is the initial, provisional scope. Treat it as authoritative only
after it is recorded in `docs/research-spec.md`:

- One open decoder-only language model.
- Weights-only quantization.
- BF16, INT8, and INT4.
- Four to eight contiguous transformer block groups.
- A finite codebook of hardware-executable precision schedules.
- Single-turn requests.
- Offline routing before live serving.
- Batch simulation before continuous-batching implementation.

The initial study excludes:

- Pure transformer block, layer, token, or attention-head pruning.
- Arbitrary per-layer schedule search over the full combinatorial space.
- Activation or KV-cache quantization.
- Multi-node placement.
- Internal mixture-of-experts routing unless directly relevant.
- Changing evaluation metrics after viewing final test results.

## Scientific Assumptions and Integrity

- Task composition, task difficulty, and quantization sensitivity are distinct
  concepts and must be evaluated separately.
- A generic semantic embedding is not evidence of quantization sensitivity
  unless predictive performance is measured.
- KL divergence from BF16 is an auxiliary signal, not the sole quality
  measurement.
- BF16 output is a reference condition, not automatically ground truth.
- Preserve negative, null, unfavorable, and failed results with their reasons.
- Never fabricate measurements, completed runs, citations, hardware results,
  or statistical significance.
- Never silently discard failed runs or unfavorable seeds.
- Do not tune models, thresholds, schedules, or decision rules using the final
  test set.
- Any change to a preregistered metric, split, hypothesis, or schedule
  definition must be recorded in `docs/decisions.md` before running the
  altered experiment.
- Keep raw experiment outputs immutable. Never overwrite them.

## Implementation Rules

- Implement the real end-to-end path: real data, real model outputs, real
  quantization effects, real quality targets, and real serving or batch
  measurements.
- Establish sensitivity labels from the actual model before training or
  claiming a sensitivity predictor.
- Use configuration-driven experiments and avoid undocumented constants in
  source code.
- Type public functions.
- Do not create placeholder, mock-only, diagnostic-only, toy-objective,
  random-label, stub, unused-helper, duplicate, or parallel demo
  implementations unless explicitly requested. If a temporary placeholder is
  unavoidable, mark it `NOT COMPLETE`, document why, and do not report the task
  as complete.
- Keep evaluation logic separate from training logic.
- Keep timing logic separate from quality scoring.
- Do not use notebook-only implementations.
- Synthetic data or mock models may be used for unit tests only. They are not
  completion evidence for the research implementation.
- Prefer modifying existing project paths over creating parallel paths that
  bypass the real system.
- Add unit tests for routing, schedule validation, and metric computation.
- Add an integration test for the smallest executable real experiment.
- Save and reload checkpoints when training is part of the experiment.
- Do not add production dependencies unless necessary. Check for an existing
  equivalent, update lockfiles when required, and verify installation/build
  behavior before adding one.

## Required Evaluation and Baselines

Unless explicitly declared out of scope in `docs/research-spec.md`, comparisons
must include:

- Always BF16.
- Always INT8.
- Always INT4.
- Static mixed precision.
- Average-profile routing or scheduling.
- Input-length heuristic.
- Expected-output-length heuristic.
- Task-label classifier.
- Generic semantic embedding.
- Scalar difficulty predictor.
- Multidimensional predictor.
- Oracle sensitivity or profile.
- Oracle schedule selected from measured outcomes.

Evaluate both prediction quality and system utility. At minimum, report profile
error, schedule regret versus an oracle, quality-constraint violations,
latency or throughput, and memory use where applicable. Keep denominator,
inputs, batch conditions, and quality constraints consistent across methods.

The oracle may use measured outcomes only for the intended oracle role. It must
not leak final-test outcomes into predictor training, threshold selection, or
schedule-codebook design.

## Experiment Run Contract

Every attempted experiment must create a unique, immutable, documented run
directory containing:

- `resolved_config.yaml`
- `command.txt`
- `git_commit.txt`
- `environment.json`
- `hardware.json`
- `random_seeds.json`
- `metrics.json`
- `predictions.parquet` or `predictions.jsonl`
- `stdout.log`
- `stderr.log`
- `report.md`

Use one explicitly selected prediction format per experiment and document its
schema. If a run fails before an artifact can be produced, retain the run,
record the failure and reason, and mark the missing artifact rather than
fabricating it or silently skipping the run.

The environment record must include relevant package versions, Python version,
CUDA version, GPU type, quantization backend, model identifier and revision,
dataset identifier and revision, and any other settings needed to reproduce
the run. Record batch size, input length, output length, schedule, repetitions,
and warm-up count for timing experiments.

Reported results must identify the exact git revision. A clean working tree is
required for reproducible or publishable results. Development runs from a
dirty tree must record the working-tree state and exact diff, and must be
clearly marked as non-release evidence.

## GPU Execution and Resource Rules

- Implement a CPU or mocked dry run where practical, but do not treat it as
  completion evidence for the real research path.
- Run unit tests before launching GPU work.
- Run a 5–10 request smoke test before a full experiment. A smoke test only
  proves early health; it is not sufficient completion evidence.
- Do not run large-model training, inference, evaluation, or benchmarks on the
  local RTX 4050.
- Do not launch a job expected to run longer than ten minutes without explicit
  approval.
- Do not download a new model or dataset without explicit approval.
- Before a large run, report estimated disk, memory, GPU, and runtime
  requirements.
- Never terminate another process without approval.

### Local workstation

Use the local environment for editing, syntax checks, linting, formatting, unit
tests, and small diagnostic runs. Do not make hardware-performance claims from
the local RTX 4050.

### Remote lab

The documented lab hosts are currently referred to as `basic1` and `basic2`
and may provide up to eight RTX 3090 GPUs, but availability must be checked for
every experiment. Never assume all GPUs are free or usable. Before scheduling a
GPU job, run and record an availability check such as:

```bash
nvidia-smi --query-gpu=index,name,memory.total,memory.free,utilization.gpu --format=csv
```

The lab hostname, scheduler, environment setup, storage paths, and GPU
allocation command remain unknown until verified. Do not invent or hardcode
private paths. Add verified operational details to `docs/runbook.md`.

Ask for confirmation before launching expensive remote jobs, installing
dependencies, or consuming shared lab resources. Pin or explicitly select
visible devices for multi-GPU jobs and record the selected GPU indices.

## Timing Requirements

For GPU latency measurements:

- Include warm-up iterations.
- Synchronize the device around timed regions.
- Separate prefill and decode measurements where possible.
- Report the number of repetitions.
- Report median and tail latency, not only the mean.
- Record batch size, input length, output length, schedule, and hardware.
- Do not compare configurations measured under different conditions.
- Keep timing and quality measurements separately identifiable.

## Working Method and Commands

- Inspect the repository structure, relevant documentation, real entry points,
  build commands, run commands, and tests before editing code.
- Keep the research design in `docs/research-spec.md` and operational commands
  in `docs/runbook.md`; keep this file focused on durable project rules.
- Prefer the existing project structure and libraries once established.
- Make small, reviewable changes with focused tests and a runnable command for
  the changed real path.
- Build, test, lint, format, type-check, package-manager, and experiment
  commands are currently `Unknown` until discovered from repository files and
  documented after verification.
- Do not weaken or delete tests to make an incorrect implementation pass.

## Planning and Documentation

For work involving multiple modules, new experiment architecture, or more than
approximately one hour of implementation, create and maintain an execution
plan under `docs/plans/` before editing code. The plan must contain:

- Scientific objective.
- Assumptions.
- Proposed design.
- Affected files.
- Validation approach.
- Risks.
- Milestones.
- Decisions made during implementation.

Keep the research design in `docs/research-spec.md`, operational commands and
environment details in `docs/runbook.md`, and scientific changes in
`docs/decisions.md`. Update documentation when behavior, commands, config, or
output formats change. Document expected inputs, outputs, common failure
modes, and known limitations concisely.

## Verification and Completion

Use the smallest relevant verification first, then broaden it as appropriate:

1. Focused unit tests for changed logic.
2. Integration test for the real path.
3. End-to-end command.
4. Lint, type, and format checks.
5. Benchmark, evaluator, or submission checks.

A coding or research task is complete only when all applicable conditions hold:

- The real implementation path exists.
- The real command runs.
- Relevant tests or checks pass.
- A minimal real-path smoke run succeeds.
- The output format matches the requirement.
- The change is integrated into the existing project flow.
- Generated outputs have been inspected.
- The diff has been reviewed for leakage, metric errors, timing errors,
  inconsistent baselines, and accidental scope expansion.
- Exact reproduction commands are documented.
- No unrelated generated junk files remain.
- No hardcoded local paths, secrets, or machine-specific assumptions were
  introduced.
- Remaining limitations are stated explicitly.

For ML, training, routing, evaluation, quantization, retrieval, or benchmark
work, do not claim completion unless the implementation includes:

1. Real data loading or a documented real-data subset.
2. A real objective, loss, metric, or evaluator matching the design.
3. Real targets, labels, rewards, or distillation signals.
4. A real training or evaluation command.
5. Evidence that outputs or metrics behave as expected; training must also
   demonstrate parameter or output change when applicable.
6. Checkpoint save and reload when checkpoints are part of the feature.
7. A validation metric or evaluation artifact.
8. A reproducible run record.

A tiny run is acceptable only when it uses the same real data format, objective,
and code path as the intended full run. A synthetic diagnostic path is not a
substitute for a real implementation.

Do not say “all tests pass” unless tests were actually run. If the real intended
path is not working, report `NOT COMPLETE` and name the next concrete step.

## Data, Artifacts, Secrets, and Git

- Make train/validation/test separation explicit and prevent query leakage
  between splits.
- Do not commit model weights, large datasets, generated benchmark dumps, or
  temporary debug output unless explicitly required and documented.
- Keep generated artifacts in documented, reproducible locations and add only
  required metadata to version control.
- Never commit API keys, tokens, credentials, private hostnames, or
  machine-specific absolute paths.
- Use `apply_patch` for manual edits and keep changes scoped to the task.
- Do not revert existing user changes or use destructive commands such as
  `git reset --hard`, `git clean -fd`, or force-push commands.
- Before committing, inspect `git diff`, `git status`, and relevant tests.
  Commits and pushes require explicit user direction.

## Debugging and Uncertainty

When a command fails:

1. Capture the exact command and error.
2. Identify whether the cause is code, data, dependency, environment,
   hardware, permission, or path related.
3. Make the smallest root-cause fix.
4. Re-run the failing command.

State assumptions explicitly and mark unverified infrastructure details as
`Unknown`. If a required model, dataset, quantization backend, evaluator, or
lab-access detail is missing, identify the smallest concrete decision needed
before implementation.

## Completion Report

When handing off work, report:

### Result

Whether the task is complete or `NOT COMPLETE`.

### Changed

Changed files.

### Verification

Commands run and what each command proves.

### Evidence

Evidence that the real intended path works.

### Limitations

Remaining risks and unverified assumptions.

### Next Step

The next concrete step only when work remains.

## Agent skills

### Issue tracker

Issues for this repo live on GitHub; use the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the canonical labels `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repo using root `CONTEXT.md` and `docs/adr/`. See `docs/agents/domain.md`.
