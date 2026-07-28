# Define and measure the first hardware-realizable schedule codebook — Phase 0 plan

## Status and scope

This is the Phase 0 orientation and experiment-contract plan for the Wayfinder
ticket **Define and measure the first hardware-realizable schedule codebook**.
It does not resolve the ticket, freeze a schedule family, or authorize a GPU
run. The plan inherits the accepted platform decision
qab.first_paper_platform_freeze.v1 and the authoritative text in
docs/research-spec.md, docs/decisions.md, and CONTEXT.md.

Phase 0 is documentation and inspection only. It must not install packages,
download a model or dataset, launch a GPU process, quantize the model, create
benchmark outputs, close the ticket, edit the map's Decisions-so-far, commit,
or push.

## Scientific objective

Determine, for the frozen Qwen2.5-7B-Instruct / LLM Compressor →
compressed-tensors → vLLM platform and one eligible RTX 3090, whether a small,
predeclared set of contiguous transformer-block partitions and BF16/W8A16/W4A16
schedules can be loaded, executed, exported, and reloaded with the requested
precision map intact and with matched hardware-cost observables.

The decision is about hardware realizability, reproducible schedule identity,
and coverage of coarse precision cost and group position. It is not a task-
quality result. A schedule is not accepted because it looks fast, small, or
promising on a task-quality outcome; it must first pass the declared platform
and measurement gates.

### Non-goals

- Do not change the model, tokenizer, quantization backend, quantization
  semantics, calibration contract, runtime target, or hardware target frozen by
  qab.first_paper_platform_freeze.v1.
- Do not select schedules from request quality, evaluator outputs, BF16
  agreement, KL divergence, predictor performance, or final-test outcomes.
- Do not enumerate arbitrary 3^G per-group schedules, search arbitrary layer
  boundaries, or optimize a schedule on observed quality.
- Do not implement prediction, routing, batching, continuous serving, or live
  serving.
- Do not make a claim about the usefulness or learnability of query-conditioned
  sensitivity. That is downstream of this hardware codebook decision.
- Do not make hardware claims from the local RTX 4050 or from the current
  unaccepted Torch/Transformers environment.

## Frozen platform inputs

The later execution phase must use these exact identities unless a dated
scientific amendment is approved before execution:

| Item | Frozen value |
| --- | --- |
| Model/tokenizer | Qwen/Qwen2.5-7B-Instruct@a09a35458c702b33eeacc393d103063234e8bc28, same revision and chat template |
| Model shape | 28 transformer layers, indexed 0..27 |
| Quantization path | LLM Compressor 0.9.0@129c793fdabfd9bc486f85c444bdec6b713978fe → compressed-tensors 0.12.2@2dd1b627950b4a068f2c1af19bc6f31b7fbb3316 → vLLM 0.11.2@275de34170654274616082721348b7edd9741d32 |
| Quantization | Integer GPTQ weight-only W8A16/W4A16, BF16 activations, group size 128, symmetric static scales, actorder=weight, dampening_frac=0.01, lm_head excluded |
| Calibration | 512 varied non-final samples, sequence length 2048, frozen chat template |
| Hardware | One explicitly available NVIDIA GeForce RTX 3090, SM86, 24,576 MiB; exact GPU index recorded per run |
| Runtime constraint | Torch 2.9.0 and Transformers >=4.56.0,<5 requirements from the accepted vLLM path; observed Torch 2.4/Transformers 5.12 is not accepted |

The platform decision explicitly says that capability preflight remains unrun.
No current evidence may be promoted to a passed gate.

## Mandatory capability preflight

Before any request-quality or profile measurement, run four distinct
full-model capability conditions on the approved remote RTX 3090. The preflight
is a platform gate, not a quality experiment:

1. **BF16 full model:** load the complete frozen model and produce a short
   deterministic generation without CPU fallback.
2. **Uniform W8A16:** quantize/load the complete model with every eligible
   quantized linear target at W8A16 and produce the same kind of short
   generation.
3. **Uniform W4A16:** repeat with W4A16.
4. **Contiguous mixed full model:** load at least one nontrivial schedule using
   contiguous BF16, W8A16, and W4A16 transformer-block ranges, then generate.

Every condition must record the requested map, realized module map, dispatched
kernel path, CPU-fallback status, export artifact, reload result, disk
headroom, host RSS, GPU resident/peak memory, and exact environment. The
uniform conditions establish the backend primitives; the mixed condition
establishes that range-level composition is real. A bitsandbytes diagnostic,
an import test, a CLI startup, or a mock model is not a pass.

The preflight is ineligible if any of these occurs: a runtime identity differs
from the freeze; the model or tokenizer revision is different; any target
silently remains BF16 or falls back to CPU; a requested integer precision is
not dispatched through the intended backend kernel; the realized map differs
from the manifest; export/reload loses or changes the map; the model exceeds
declared disk, host-memory, or GPU-memory limits; or the run cannot be tied to
an immutable run directory and exact Git working-tree state.

## Candidate block partitions

The initial candidate set is deliberately bounded to balanced, contiguous,
equal-size partitions of the frozen 28-layer model:

| Partition identifier | Groups, inclusive layer ranges | Purpose |
| --- | --- | --- |
| g4-equal7 | g00=[0-6], g01=[7-13], g02=[14-20], g03=[21-27] | Coarse four-position schedule; provisional default for the 8–16 codebook |
| g7-equal4 | g00=[0-3], g01=[4-7], g02=[8-11], g03=[12-15], g04=[16-19], g05=[20-23], g06=[24-27] | Finer seven-position capability/coverage comparison |

The set is bounded because the accepted scope is four-to-eight contiguous
groups, the model has 28 layers, equal partitions remove boundary-size and
parameter-count confounds, and the first codebook is explicitly approximately
8–16 schedules rather than a search over all boundaries. No unequal partition,
single-layer group, arbitrary boundary, or extra group count may enter after
looking at outcomes. A backend module-layout mismatch may stop the experiment,
but it may not silently redefine a partition.

g7-equal4 is a candidate partition, not an accepted second codebook. If it
survives capability inspection, its schedule list must be generated and
approved under the same bounded-template rule before timing. The first
hardware-realizable codebook hypothesis is the g4-equal7 family below.

## Predeclared schedule generator and identifiers

Use the symbols B = BF16, 8 = W8A16, and 4 = W4A16. The generator is a
template generator, not arbitrary 3^G search:

1. Emit the three uniform schedules.
2. For a declared base precision, emit one-position substitutions in ascending
   group-index order.
3. Fill only the remaining predeclared budget with named tri-level templates.
4. Canonicalize, deduplicate, sort by the generator's declared order, and fail
   if the count is outside the accepted 8–16 range.

For g4-equal7, the provisional generator output is exactly this 14-entry
family:

~~~text
BBBB, 8888, 4444,
B888, 8B88, 88B8, 888B,
8444, 4844, 4484, 4448,
B844, 448B, 8448
~~~

The stable schedule identifier is
qcb.v1/<partition_id>/<canonical_symbols>, for example
qcb.v1/g4-equal7/B844. The symbols, group order, and zero-based inclusive
layer ranges are part of the identifier's meaning; no identifier may be
reused for a changed map. The generator version, partition identifier, and
codebook identifier are recorded in every run.

### Starting-hypothesis coverage review

This review uses only the combinatorics and nominal weight-cost proxy, not any
task-quality result.

| Schedule pattern | Nominal mean weight bits/parameter | Approximate packed weight payload for 7.61B parameters, before scale/metadata overhead |
| --- | ---: | ---: |
| BBBB | 16 | 15.22 GB |
| 8888 | 8 | 7.61 GB |
| 4444 | 4 | 3.81 GB |
| any B888 position | 10 | 9.51 GB |
| any 8444 position | 5 | 4.76 GB |
| B844 or 448B | 8 | 7.61 GB |
| 8448 | 6 | 5.71 GB |

The family is a reasonable compact hardware-cost probe: it includes all
uniform endpoints, spans nominal 4/5/6/8/10/16-bit mean payload levels, and
stresses BF16 and W8 placement at every g4 position through the two one-position
sweeps. Fourteen entries remain inside the accepted 8–16 budget.

It is not adequate for a strong claim of complete positional coverage. It has
no four-position BF16/W4 sweep, no direct BF16/W4 transition sweep, and only
three hand-picked tri-level arrangements. B844 and 448B probe two local
BF16/W8 arrangements while 8448 probes symmetric endpoint W8 placement; the
other pair interactions remain unrepresented. Therefore the family is retained
as a **provisional H0 for preflight and discussion**, not accepted as the final
codebook. If the decision requires direct BF16/W4 positional coverage, the
generator must replace or add entries within the same 8–16 cap before any
quality-profile run. No quality outcome may make that choice.

## Schedule-manifest schema

The later implementation must emit one immutable manifest before quantization
or timing. The selected prediction/artifact record format for this preflight
and codebook experiment is predictions.jsonl; no second prediction format is
permitted within one run. Each schedule record must contain at least:

~~~yaml
schema_version: qcb.schedule_manifest.v1
codebook_id: qcb.v1
generator_id: qcb.template.v1
partition_id: g4-equal7
schedule_id: qcb.v1/g4-equal7/B844
symbols: [B, "8", "4", "4"]
model: {id: Qwen/Qwen2.5-7B-Instruct, revision: ...}
backend: {compressor: ..., compressed_tensors: ..., vllm: ...}
hardware_target: {gpu_family: RTX3090, compute_capability: 8.6}
groups:
  - {group_id: g00, start_layer: 0, end_layer: 6, requested_precision: BF16}
  - {group_id: g01, start_layer: 7, end_layer: 13, requested_precision: W8A16}
  - {group_id: g02, start_layer: 14, end_layer: 20, requested_precision: W4A16}
  - {group_id: g03, start_layer: 21, end_layer: 27, requested_precision: W4A16}
eligibility: {status: pending, exclusion_reason: null}
requested_precision_map: ...
realized_precision_map: ...
map_validation: {status: pending, differences: []}
kernel_validation: {status: pending, module_classes: [], dispatches: []}
export_reload_validation: {status: pending, artifact_sha256: null}
~~~

The concrete file must additionally include calibration identity, environment
lock hash, source/config hashes, generation command, random seed, run ID, and
working-tree state. The manifest records schedule intent and eligibility; it
does not contain a quality label.

### Requested-versus-realized map validation

Validation must expand both maps to the complete set of targeted transformer
linear modules and compare, for every module: canonical module path, layer
index, group identifier, requested precision, realized precision, quantization
scheme, and backend module/kernel class. The result must record exact matches,
missing modules, extra modules, wrong precision, unexpected exclusions, and
fallback dispatches. A schedule is not eligible when the comparison is not
exact, except for the explicitly frozen lm_head exclusion and other
configuration exclusions recorded in the manifest.

### Kernel-path and export/reload validation

The run must prove that the intended compressed-tensors/vLLM path dispatched
the requested BF16/W8A16/W4A16 kernels for the targeted modules. Record module
classes, kernel/dispatch identifiers, and any fallback. Export each eligible
artifact, compute its digest, reload it in a fresh process, and repeat map and
kernel checks. Export/reload is a separate gate from initial generation; a
successful first load cannot hide a reload mismatch.

## Hardware eligibility and exclusion reasons

Eligibility is evaluated before timing and is independent of task quality. A
candidate is eligible only when all of the following hold:

- the exact frozen model, backend, runtime, calibration, partition, and
  schedule manifest are present;
- one explicitly available RTX 3090 is selected after recording
  nvidia-smi --query-gpu=index,name,memory.total,memory.free,utilization.gpu --format=csv;
- the full model loads and generates on that GPU without CPU fallback;
- the requested/realized precision map and intended kernel path match;
- export/reload preserves the artifact and map; and
- disk, host-memory, GPU-memory, and matched-timing conditions are satisfied.

Use explicit, machine-readable exclusion reasons rather than a generic
"failed": runtime_lock_mismatch, model_revision_mismatch,
backend_revision_mismatch, gpu_ineligible, model_load_failure, cpu_fallback,
unsupported_precision, unsupported_contiguous_map, precision_map_mismatch,
kernel_path_mismatch, export_failure, reload_map_mismatch,
disk_headroom_insufficient, host_memory_headroom_insufficient,
gpu_memory_headroom_insufficient, timing_condition_mismatch,
artifact_integrity_failure, and run_contract_incomplete. Exclusion is not a
quality violation and must not be silently removed from denominators.

## Resource and runtime estimates

These are planning estimates only; they are not hardware measurements and must
be replaced by recorded preflight observations. The payload estimate uses
7.61B parameters and excludes scales, metadata, allocator workspace, cache,
runtime libraries, and temporary files:

- BF16 payload: 7.61B × 2 bytes, approximately 15.22 GB.
- Uniform W8A16 payload: approximately 7.61 GB.
- Uniform W4A16 payload: approximately 3.81 GB.
- The 14-entry g4 family has approximately 104.64 GB of nominal packed weight
  payload if every artifact is retained separately. Scale/metadata and staging
  overhead are unknown; reserve a preflight disk budget above this total and
  record the measured requirement before building the family.
- Host memory must cover the largest serialized artifact, model/runtime staging,
  and allocator copies. The plan requires a measured peak RSS and a declared
  safety margin; no unverified host-memory number is accepted as evidence.
- GPU memory must record resident and peak allocation per condition against the
  RTX 3090's 24,576 MiB. The model payload alone is not a capacity estimate:
  runtime workspace, activations, and the fixed timing prompt/output shape must
  be included. A candidate with insufficient measured headroom is ineligible.
- A provisional wall-clock envelope is 10–30 minutes per capability condition
  and roughly 40–120 minutes for the four-condition preflight, excluding
  download/install time. This is unverified and is intentionally above the
  ten-minute approval threshold for a single job. Building and exporting all
  14 schedules may take several hours if each requires a separate quantization
  pass; do not launch it without an explicit approval after the first preflight
  estimates are observed.

## Matched timing and observables

Timing begins only after capability eligibility. All configurations must use
the same selected GPU, model/tokenizer revision, runtime lock, batch size,
input token length, output token limit, prompt order, decoding controls, warmup
count, repetition count, synchronization policy, and measurement process. No
configuration may be compared if it has a different failure, fallback, or
input/output condition.

For each schedule and condition, record separately:

- load time, serialized artifact size, artifact digest, and export/reload time;
- resident and peak GPU memory, host peak RSS, and allocator/workspace notes;
- prefill latency/TTFT and decode latency/TPOT;
- end-to-end latency and generated-token throughput;
- repetitions, warmups, p50, p95, mean, standard deviation or MAD, min/max,
  and per-repetition raw observations; and
- variability observables: failed repetitions, timeout count, device
  synchronization status, clock/utilization snapshot, and run-to-run spread.

Use CUDA synchronization around timed regions, separate prefill and decode
where the runtime exposes them, and report the exact batch/input/output shape.
Load time and artifact size are not folded into TTFT; quality scoring is not
folded into timing. The later timing report must make hardware eligibility,
quality status, and serving-cost observations separately identifiable.

## Immutable run-directory contract

Every attempted preflight, artifact build, or timing experiment gets a unique
never-overwritten run directory. It must contain:

~~~text
resolved_config.yaml
command.txt
git_commit.txt
environment.json
hardware.json
random_seeds.json
metrics.json
predictions.jsonl
stdout.log
stderr.log
report.md
~~~

predictions.jsonl records one row per probe/schedule with the schedule ID,
request/probe identity, output or execution status, map validation, kernel
validation, and artifact references. A failed run retains its directory and
records the failure and missing artifacts in report.md and metrics.json;
it is never overwritten or silently omitted. git_commit.txt and the working-
tree state must identify dirty development runs, including an exact diff or
content hash sufficient to reproduce them. Run directories and raw outputs are
immutable; reports may only point to new amended runs.

## Stop conditions and platform amendments

Stop without proceeding to quality/profile work when a capability gate fails,
the runtime lock is unavailable, the requested map cannot be realized, the
kernel/export/reload path is wrong, any resource headroom is insufficient, the
GPU is not explicitly eligible, or timing conditions cannot be matched. Also
stop if the proposed partition or schedule count must expand beyond this
predeclared scope, or if implementation requires changing any frozen platform
semantic.

Do not substitute bitsandbytes, another model, another GPU, another backend,
another calibration set, a CPU result, or a silent fallback. Record the exact
failure and reason in the immutable run directory. A change to model, backend,
quantization semantics, calibration, runtime, hardware, partition definition,
schedule generator, eligibility rule, timing condition, or any judgment-
affecting manifest field requires a dated entry in docs/decisions.md, a
version/hash update, invalidation of affected runs, and new immutable runs
before continuation. This Phase 0 plan itself does not make that amendment.

## Human approval gates

1. **Current HITL gate:** approve or reject this Phase 0 contract and retain
   the 14-entry g4 family only as provisional H0; no GPU or data action follows
   from this plan alone.
2. **Remote-resource gate:** after a later implementation reports package,
   model/data, disk, host-memory, GPU-memory, and runtime estimates plus the
   exact remote availability output, obtain explicit approval before installing,
   downloading, consuming shared lab resources, or launching any job expected
   to exceed ten minutes.
3. **Preflight gate:** after the four full-model capability conditions and all
   map/kernel/export/reload/resource checks are complete, obtain human review
   of the immutable artifacts and explicit acceptance or rejection of each
   partition/codebook. No task-quality result is admissible for this gate.
4. **Experiment gate:** only after the codebook and schedule manifest are
   accepted may the later profile experiment be approved. Freeze the final-test
   manifest and schedule identities before any predictor, router, threshold, or
   quality-profile tuning; do not start predictor, batching, or serving work
   here.

## Expected later changes

No runtime or test package exists in the current checkout. Later phases are
expected to update only the paths discovered after toolchain/entry-point
inspection:

- docs/research-spec.md for the accepted partition, schedule-generator,
  manifest, and eligibility definitions;
- docs/decisions.md for dated amendments or the accepted schedule decision;
- CONTEXT.md only when an accepted glossary term needs to be added;
- docs/runbook.md for verified remote host, environment, availability,
  execution, storage, and reproduction commands (the file is currently absent);
- the repository's later-discovered configuration/manifest path for the
  versioned schedule manifest;
- the repository's later-discovered quantization/preflight and timing entry
  points, with focused tests beside the real implementation; and
- documented immutable run directories outside tracked source unless the
  repository later establishes a different artifact policy.

No predictor, batching, serving, or parallel demo path is an expected change
from this ticket.

## Validation and final review procedure

Before any remote GPU action, add focused unit tests for partition coverage and
contiguity, canonical partition/schedule identifiers, bounded generator output
and deduplication, manifest/schema validation, requested-versus-realized map
comparison, explicit exclusion reasons, and timing-summary quantiles. Use only
synthetic objects in these tests; they are health checks, not completion
evidence.

The smallest real integration check is the frozen full-model four-condition
capability preflight on one approved RTX 3090, including one nontrivial
contiguous mixed schedule, map inspection, kernel-path inspection, and
export/reload. A later end-to-end check must build the accepted manifest,
produce immutable artifacts, and collect matched timing for every accepted
schedule. It must preserve failed and excluded conditions and must not invoke
predictor, batching, or serving code.

Final review must inspect git diff, git status, exact commit and dirty-tree
metadata, every run manifest and exclusion reason, artifact hashes, requested
versus realized maps, kernel dispatches, export/reload evidence, resource
headroom, timing conditions, p50/p95 calculations, variability records, and
the absence of quality-outcome leakage. Re-run the documented focused tests and
the real integration command from the recorded command.txt. Confirm that no
unrelated generated files remain and that the final ticket resolution cites
only accepted immutable artifacts and human-approved decisions.

## Milestones

1. Phase 0 orientation: confirm the ticket claim, inspect accepted decisions
   and local state, and obtain the HITL decision on this plan.
2. Later implementation preflight: discover the actual environment/entry
   points, write focused tests, and obtain remote-resource approval.
3. Run the four mandatory full-model capability conditions and retain immutable
   pass/fail artifacts.
4. Validate candidate partitions and the provisional g4 family; obtain the
   hardware-only codebook decision.
5. Run matched timing only for accepted schedules, inspect artifacts, and hand
   off the accepted codebook to later quality/predictor tickets.

## Decisions made during Phase 0

- Issue #5 was already assigned to weige15 when inspected; no assignment
  mutation was needed. The required gh executable is not installed locally,
  so the configured GitHub connector was used for read-only issue inspection.
- The current working tree already contains uncommitted authoritative freeze
  text in docs/research-spec.md and docs/decisions.md; those user changes
  were preserved and not edited.
- The accepted platform freeze is present in the current working tree but is
  absent from the two tracked local/remote branch refs currently visible; the
  GitHub issue resolution and normative working-tree documents are therefore
  the evidence sources for this Phase 0 orientation.
- The g4 14-entry family is a provisional H0: it provides compact endpoint,
  nominal-cost, and first-order position coverage, but it is not accepted as
  complete positional coverage because BF16/W4 placement is not swept.

## Phase 0 orientation record

The orientation was performed on 2026-07-28 in the following checkout state:

| Field | Recorded value |
| --- | --- |
| Branch | `research/novelty-boundary-query-conditioned-precision-selection` |
| HEAD | `8d27dc796ff5f44527f3a5a2edbb496ced0ad74e` (`claim issue 10`) |
| Working tree | Dirty before this Phase 0 work: modified `docs/decisions.md` and `docs/research-spec.md`; untracked `docs/plans/issue-5-schedule-codebook.md` |
| Visible refs | `main`=`75e772d8a3041363f2294b8fda29e9dc84103c94`; `origin/main`=`7a52a255dd3072213316344cf2a9e69b7e86c556`; feature remote ref=`8d27dc796ff5f44527f3a5a2edbb496ced0ad74e` |
| Issue #5 claim | Already assigned to `weige15`; no assignment write was required |
| Accepted Issue #8 freeze | Present in the current working-tree normative documents, absent from the visible local/remote branch refs; the GitHub default branch also lacks `docs/research-spec.md` |

No authoritative accepted freeze artifact was found only on another local or
remote branch. The accepted Issue #8 resolution remains the tracker authority;
the uncommitted normative text is preserved as pre-existing user state and is
not treated as a committed reproducibility artifact.
