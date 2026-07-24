# AGENTS.md

## Project Context

This repository investigates whether a compositional representation of an incoming
query can predict its blockwise quantization-sensitivity profile. The intended
system uses that profile to select a hardware-efficient mixed-precision schedule,
batch requests with compatible schedules, and satisfy per-request quality
constraints.

The repository is currently an early-stage research project. The model,
dataset, quantization backend, serving runtime, lab connection command, and
build/test toolchain are not yet established. Treat those as unknown until they
are documented or verified.

## Research Completion Rules

- Implement the real end-to-end path: real data, real model outputs, real
  quantization effects, real quality targets, and real serving measurements.
- Establish sensitivity labels from the actual model before training or claiming
  a sensitivity predictor.
- Evaluate both prediction quality and system utility. At minimum, report
  profile error, schedule regret versus an oracle profile, quality-constraint
  violations, latency or throughput, and memory use.
- Compare against static-precision, average-profile, and oracle-sensitivity
  baselines where applicable.
- Save and reload checkpoints when training is part of the experiment.
- Record the command, git revision, configuration, seed, data version, hardware,
  software environment, and output artifact paths for every reported run.
- Synthetic data or mock models may be used for unit tests only. They are not
  completion evidence for the research implementation.

## Execution Environments

### Local workstation

- The local GPU is an RTX 4050.
- Use the local environment for editing, syntax checks, linting, formatting,
  unit tests, and small diagnostic runs.
- Do not run large-model training, inference, evaluation, benchmarks, or
  hardware claims on the local RTX 4050.

### Remote lab

- The lab (basic1 or basic2) has up to eight RTX 3090 GPUs, but availability must be checked for
  every experiment; never assume all eight are free or usable.
- Before scheduling a GPU job, run and record an availability check on the lab
  host, for example:

  ```bash
  nvidia-smi --query-gpu=index,name,memory.total,memory.free,utilization.gpu --format=csv
  ```

- The lab hostname, scheduler, environment setup, storage paths, and GPU
  allocation command are unknown until documented. Do not invent them or
  hardcode private paths. Add verified details to `docs/runbook.md` when known.
- Ask for confirmation before launching expensive remote jobs, installing
  dependencies, or consuming shared lab resources.
- Pin or explicitly select visible devices for multi-GPU jobs and record the
  selected GPU indices. Do not assume `CUDA_VISIBLE_DEVICES=0,1,...,7` is valid.

## Working Method

- Inspect the repository and relevant documentation before editing.
- Keep the research design in `docs/research-spec.md` and operational commands
  in `docs/runbook.md`; keep this file focused on durable project rules.
- Prefer the existing project structure and libraries once established.
- Make small, reviewable changes with focused tests and a runnable command for
  the changed real path.
- When a command fails, record the exact command and error, identify whether the
  cause is code, data, dependency, environment, hardware, permission, or path,
  then fix and rerun the failing command.

## Commands and Quality Gates

- Build, test, lint, format, type-check, package-manager, and experiment
  commands are currently **Unknown**. Discover them from repository files and
  document verified commands before relying on them.
- Do not report completion from CLI startup, argument parsing, mock objects,
  checkpoint writing alone, or a tiny synthetic example.
- Use this verification order when applicable: focused unit tests, real-data
  integration test, end-to-end experiment command, lint/type/format checks, then
  benchmark or evaluator checks.
- Do not weaken or delete tests to make an incorrect implementation pass.

## Data, Artifacts, and Secrets

- Do not commit model weights, large datasets, generated benchmark dumps, or
  temporary debug output unless explicitly required and documented.
- Keep generated artifacts in documented, reproducible locations and add only
  required metadata to version control.
- Never commit API keys, tokens, credentials, private hostnames, or
  machine-specific absolute paths.
- Make train/validation/test separation explicit and prevent query leakage
  between splits.

## Editing and Git Rules

- Use `apply_patch` for manual edits and keep changes scoped to the task.
- Do not revert existing user changes or use destructive commands such as
  `git reset --hard`, `git clean -fd`, or force-push commands.
- Do not create parallel demo scripts that bypass the real implementation path.
- Update documentation when behavior, commands, configuration, or output
  formats change.
- Before committing, inspect `git diff`, `git status`, and the relevant tests;
  commits and pushes require explicit user direction.

## Uncertainty Protocol

- State assumptions explicitly and mark unverified infrastructure details as
  **Unknown**.
- If a required model, dataset, quantization backend, evaluator, or lab access
  detail is missing, identify the smallest concrete decision needed before
  implementation.
- If the real intended path is not working, report **NOT COMPLETE** and name the
  next verification or implementation step.
