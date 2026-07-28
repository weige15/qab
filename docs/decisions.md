# Scientific Decisions

## 2026-07-28 - Resolve the pinned quantization-runtime dependency conflict

Accepted decision identifier: `qab.issue5_runtime_override.v2`.

The pinned metadata conflict is operationally resolved for the approved remote
experiment by using LLM Compressor `0.9.0` at
`129c793fdabfd9bc486f85c444bdec6b713978fe`, compressed-tensors `0.13.0`
at `797d3019ef6867362796f412980547c74551f369`, and vLLM `0.11.2` at
`275de34170654274616082721348b7edd9741d32`. The serving runtime is
Torch `2.9.0` and Transformers `4.57.3` on Python `3.12.3`.

LLM Compressor `0.9.0` and compressed-tensors `0.13.0` are metadata
coherent. vLLM `0.11.2` declares compressed-tensors `0.12.2`, while LLM Compressor
`0.9.0` requires compressed-tensors `0.13.0`. The experiment therefore
solves the vLLM side with its declared `0.12.2` dependency first and then
installs compressed-tensors `0.13.0` without dependency resolution. The exact
exception is recorded in the run environment and is not treated as proof of
backend capability. The no-model import/API preflight passed for the pinned
LLM Compressor GPTQ/oneshot APIs and vLLM compressed-tensors integration.

The runtime override is accepted only for the remote device-7 capability
preflight. The run must prove real Qwen loading, GPTQ W8A16/W4A16 calibration,
packed export, fresh-process reload, vLLM generation, requested-versus-realized
module maps, and compressed-tensors kernel dispatch. A failed gate blocks all
quality or benchmark claims. No package was installed locally and the local
RTX 4050 remains out of scope.

This dated execution decision supersedes the earlier compressed-tensors
`0.12.2` runtime line for Phase 1 only; it does not alter the preregistered
scientific scope. The resulting isolated environment reports one intentional
`uv pip check` incompatibility: vLLM declares `0.12.2`, but `0.13.0` is
installed.

## 2026-07-28 — Freeze the first-paper model, data, backend, and hardware

Accepted freeze identifier: `qab.first_paper_platform_freeze.v1`.

The first paper uses `Qwen/Qwen2.5-7B-Instruct` and its same-revision
tokenizer at `a09a35458c702b33eeacc393d103063234e8bc28`, with the LLM
Compressor `0.9.0` → compressed-tensors `0.12.2` → vLLM `0.11.2` path
at the pinned commits recorded in `docs/research-spec.md`. The frozen
configuration is BF16-activation, integer GPTQ W8A16/W4A16 weight-only
quantization, group size 128, symmetric static scales, weight activation
ordering, `lm_head` excluded, and no activation or KV-cache quantization.
Exact block-group boundaries and the schedule codebook remain issue #5
decisions.

The hardware target is one explicitly available RTX 3090, SM86, 24,576 MiB,
with exact GPU index and runtime conditions recorded per run. The accepted
sources are the historical split-preserving MATH artifact
`qwedsacf/competition_math@d9afe06952835e34b5a148b90043bc04aa09e519`,
HumanEval+ release `200defce9e3429d28ca215b6dd061c0f7f31c18b`, and official
MuSiQue-Full v1.0 archive at evaluator/source commit
`24cc5b297acc2abfc5fb3d0becb6ef7b73d03717`. MATH file SHA-256 values and
manifest digests are recorded in the authoritative specification; HumanEval+
and MuSiQue archive SHA-256 values, model snapshot file hashes, and the
coherent environment lock remain required acquisition/preflight artifacts
because their immutable sources publish no digest.

The historical MATH train/test mapping is high-confidence but not proven
byte-equivalent to the unavailable Berkeley archive. Validation is carved only
from training-source instances before derivatives. Issue #7 leakage grouping
and manifest freeze rules and issue #4's quality contract are inherited
unchanged. Primary documentation supports the selected formats and mixed
configuration groups, but no unrun full-model BF16/W8A16/W4A16 or contiguous
mixed-schedule result is claimed. The empirical capability preflight must pass
before model-output runs.

The authoritative specification is `docs/research-spec.md`; the platform
research packet and earlier issue plans remain evidence/provisional artifacts
and are not promoted by this decision. No model output, final-test outcome,
evaluator run, experiment, dataset download, GPU job, serving implementation,
commit, or push was performed for this decision.

## 2026-07-27 — Define the per-request quality contract

Accepted contract identifier: `qab.per_request_quality_contract.v1`.

The contract preserves separate absolute-pass and BF16-noninferior labels,
defines request safety as conjunction over mandatory components, and treats
missing or invalid required judgments, evaluator/infrastructure failures,
execution failures, and nondeterminism as `not_assessable`, not silent passes
or measured violations. The frozen component criteria are MATH
`equivalent=1`, HumanEval+ `plus_pass=1`, and MuSiQue answer/support
`answer_f1>=0.80` and `support_f1>=0.80`, with BF16 margins
0, 0, 0.05, and 0.05 respectively. The contract uses a 5% violation-risk
budget, a one-sided 95% familywise Bonferroni gate over five predeclared
worst-group strata, and exact Clopper–Pearson upper bounds.

The authoritative specification is `docs/research-spec.md`; canonical glossary
terms are in `CONTEXT.md`; the complete decision ledger is
`docs/plans/issue-4-per-request-quality-contract.md`. No model output,
final-test outcome, evaluator run, experiment, dataset download, GPU job, or
implementation was used or changed for this decision.
