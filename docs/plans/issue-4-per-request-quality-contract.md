# Issue #4: Per-request quality contract

Status: AUTHORITATIVE DECISION LEDGER

This ledger records the human-in-the-loop resolution of “Define the
per-request quality contract.” The normative contract is in
`docs/research-spec.md`; this file records the decisions, alternatives,
rationale, rejected options, and edge-case interpretations. It does not define
model, backend, hardware, block-group, schedule-codebook, predictor,
uncertainty, batching, serving, or experiment choices.

## Scientific objective

Define a reproducible per-request and per-component quality label that can
support later quality-safe schedule selection and empirical violation-risk
measurement without conflating absolute quality, BF16-relative degradation,
evaluator failures, performance, or hardware feasibility.

## Locked inputs and assumptions

The evaluator/component families, pinned registry and metric directions,
mandatory MuSiQue answer/evidence components, allowed composition signatures,
leakage and split grouping, normalized statuses, primary/auxiliary evaluator
roles, and the 804-request first-profile cap are accepted Issue #7 inputs.
This ledger does not change them. No model output, evaluator run, dataset
download, experiment, GPU job, or final-test outcome was inspected or run.

## Decision ledger

### A. Contract semantics

**Accepted decision.** Preserve separate labels for `absolute_pass`,
`BF16-noninferior`, `quality_safe`, `violation`, and
`not_assessable`. Absolute pass requires a valid scored component result
meeting its frozen absolute criterion. BF16-noninferior is an inclusive
higher-is-better relative condition. Request safety is a deterministic
conjunction over mandatory components. A violation requires an assessable,
deterministic scored candidate/reference judgment that fails an applicable
absolute or BF16-relative condition. Missing, invalid, evaluator-failed,
execution-failed, or nondeterministic required judgments are
`not_assessable`, never silent passes or measured violations.

**Rationale.** Absolute task success and schedule-induced degradation answer
different scientific questions. Keeping them separate preserves useful BF16
failure cases and makes denominators auditable.

**Rejected alternatives.** A single quality score, BF16 agreement as quality,
treating every non-safe result as a violation, or treating every evaluator
failure as a pass were rejected because each hides whether the failure was
scientific quality, reference availability, or infrastructure.

### B. BF16 reference condition

**Accepted decision.** Pair BF16 and candidate executions on the same immutable
prompt, context, output contract/template, tokenizer, extraction,
normalization, evaluator version/protocol, field mapping, decoding controls,
seed policy, stopping rule, and maximum output length. Only the weight
precision schedule differs. Use one predeclared primary seed; any robustness
seed list is frozen separately. For higher-is-better metrics:

\[
m_c(q,s)\ge m_c(q,\mathrm{BF16})-\delta_c.
\]

The inequality is inclusive. A candidate improvement satisfies the relative
condition and is recorded separately. If BF16 is valid but absolutely wrong,
judge the candidate against the absolute criterion and mark the BF16 reference
failure; the relative condition is inapplicable. If BF16 is unscorable or has
an evaluator, execution, or nondeterminism failure, retain any candidate
absolute result but label the complete pair `not_assessable`.

**Rationale.** The paired reference isolates schedule-induced change while
preventing a wrong or unavailable BF16 result from becoming ground truth.

**Rejected alternatives.** Requiring candidate \(\le\) BF16, allowing a
candidate improvement to waive absolute quality, using a different seed or
generation configuration, or imputing a failed BF16 result were rejected.

### C. Component criteria and margins

**Accepted decision.**

| Component | Absolute criterion | BF16 margin |
| --- | --- | ---: |
| MATH numeric equivalence | `equivalent = 1` | 0 |
| HumanEval+ code generation | `plus_pass = 1` | 0 |
| MuSiQue answer | `answer_f1 >= 0.80` | 0.05 |
| MuSiQue supporting evidence | `support_f1 >= 0.80` | 0.05 |

MATH and HumanEval+ are exact binary gates. MuSiQue uses inclusive continuous
floors. MuSiQue exact match and group-sufficiency metrics remain auxiliary
diagnostics. Invalid or missing MATH extraction is
`unscorable_output`, with `equivalent` null or absent; evaluator/parser
infrastructure failure is `evaluator_error`, with the metric null or absent.
A candidate-caused HumanEval+ exception or timeout is a scored
`plus_pass=0` failure with native status retained. No threshold or margin is
selected from final-test outcomes.

**Rationale.** The criteria preserve native evaluator meaning, require both
MuSiQue answer and evidence quality, and use margins only where continuous
degradation is meaningful.

**Rejected alternatives.** Averaging MuSiQue components, using exact match
alone, allowing binary partial credit, treating malformed MATH extraction as
`equivalent=0`, or choosing floors after final testing were rejected.

### D. Component-to-request aggregation

**Accepted decision.** Every mandatory component must pass. The request-level
rule is:

\[
\operatorname{quality\_safe}(q,s)
\iff
\bigwedge_{c\in M(q)}\operatorname{component\_safe}_c(q,s).
\]

Native MuSiQue requires both answer and supporting evidence. A
numeric-final-answer-to-code composite requires both numeric and code
components. Auxiliary components are reported but cannot compensate for a
mandatory failure.

**Rationale.** Jointly necessary requirements define whether the complete
request succeeds; compensation would permit an invalid answer or program to be
hidden by another score.

**Rejected alternatives.** Weighted averages, majority voting, and
compensation across components were rejected.

### E. Status and denominator policy

**Accepted decision.** Retain native statuses and normalize to
`scored`, `unscorable_output`, `evaluator_error`,
`execution_error`, or `nondeterministic`. A scored result may pass or fail
its component criterion. Candidate-caused code exceptions/timeouts are scored
failures. MATH invalid extraction is unscorable. Evaluator/parser
infrastructure failures are evaluator errors; inference/backend/transport
failures are execution errors. Conflicting repeated outcomes are
nondeterministic. Non-quality statuses are not safe and are not violations.

Report these layers separately:

| Denominator | Definition |
| --- | --- |
| Manifest | All frozen eligible request identities and mandatory components. |
| Attempted | Manifest request–schedule evaluations submitted for execution or scoring. |
| Scored | Records for which the primary evaluator emitted valid raw metrics. |
| Assessable | Complete request–schedule pairs with valid deterministic scored mandatory components and required BF16 reference conditions. |

**Rationale.** Separate denominators prevent missing or failed judgments from
disappearing while keeping raw metric rates distinct from request-level risk.

**Rejected alternatives.** Counting all attempts as scored, dropping
unscorable outputs, or treating hardware/evaluator failures as quality
violations were rejected.

### F. Non-quality exclusions

**Accepted decision.** Pre-execution exclusions are allowed only for frozen,
precision-independent manifest predicates such as invalid registry or ground
truth identity, leakage or duplicate violations, invalid split assignment, or
unsupported composition. They are reported in manifest and exclusion
denominators, not attempted or assessable quality denominators. Hardware
eligibility remains a separate feasibility filter. Latency, memory,
throughput, energy, batching, serving behavior, and schedule compatibility
cannot alter the quality-safe label.

**Rationale.** Eligibility and infrastructure are not model-quality evidence.
Freezing predicates before outputs prevents output-dependent denominator
engineering.

**Rejected alternatives.** Filtering by output length, predicted difficulty,
schedule, speed, or quality outcome was rejected.

### G. Violation-risk budget

**Accepted decision.** Keep deterministic pair labels separate from policy risk:

\[
\operatorname{violation}(q,s)\in\{0,1\},
\qquad
R(\pi)=
\Pr_q[\operatorname{violation}(q,\pi(q))
\mid \operatorname{assessable}(q,\pi(q))].
\]

The non-assessable rate is reported separately and cannot be hidden by the
conditional risk denominator.

Use \(\alpha=0.05\), one-sided 95% familywise confidence, Bonferroni across
predeclared primary groups, and the exact one-sided Clopper–Pearson upper bound:

\[
U_{\mathrm{CP}}(k,n;\gamma)
=
\operatorname{Beta}^{-1}(\gamma;k+1,n-k),
\qquad
\gamma=1-\alpha/K.
\]

The gate passes only when every supported group's upper bound is at most
\(\alpha\). The Issue #7 planned group caps are \(128,164,256,128,128\).
For planning comparison only, the largest allowed \(k\) under a 99%-per-group
upper bound is:

| Group size | CP at 1% | CP at 5% | CP at 10% | Wilson at 1% | Wilson at 5% | Wilson at 10% | Jeffreys at 1% | Jeffreys at 5% | Jeffreys at 10% |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 128 | none | 0 | 5 | none | 0 | 4 | none | 1 | 5 |
| 164 | none | 1 | 7 | none | 1 | 7 | none | 2 | 8 |
| 256 | none | 4 | 14 | none | 4 | 14 | none | 5 | 15 |

“None” means zero violations still cannot meet the stated upper-bound gate.
The accepted estimator is CP because it gives an exact conservative
one-sided bound with transparent finite-sample behavior. With \(K=5\) and
\(\alpha=0.05\), zero violations require:

\[
n_{\min}(K)
=
\left\lceil
\frac{\log(\alpha/K)}{\log(1-\alpha)}
\right\rceil
=90.
\]

A group below this support is underpowered, cannot pass the gate, is not itself
a violation, and cannot be merged or waived post hoc. Additional primary
intersections increase \(K\) and require recalculation. Average risk cannot
compensate for a failing group.

**Rationale.** The 1% budget is infeasible at the planned supports, while 10%
allows materially more violations; 5% is the accepted compromise. CP,
Bonferroni, and worst-group reporting make the claim auditable and conservative.

**Rejected alternatives.** Selecting \(\alpha\) after outcomes, using an
average-only gate, using Wilson or Jeffreys as the primary estimator, treating
underpowered groups as safe, or silently excluding difficult groups were
rejected.

### H. Worst-group safety gate

**Accepted decision.** Predeclare these five base groups before outcomes:
MATH atomic; HumanEval+ atomic; native MuSiQue 2/3-hop; held-out MuSiQue
4-hop; and numeric-final-answer-to-code-program composite. Each pair belongs
to exactly one base group. Membership includes family, signature, hop regime,
split identity, and declared legitimate intersections. MuSiQue answer and
evidence remain components within one QA request group. Additional
intersections are primary only if predeclared and sufficiently supported;
otherwise diagnostic. No favorable group selection, merging, splitting, or
redefinition after outcomes.

**Rationale.** The gate tests the weakest scientifically meaningful population
and preserves the held-out compositional claim.

**Rejected alternatives.** Reporting only pooled risk, selecting favorable
groups after seeing results, or allowing average performance to rescue a
failing group was rejected.

### I. Split roles

**Accepted decision.**

| Split | Allowed | Frozen/prohibited |
| --- | --- | --- |
| Train | Predictor/representation parameters and train-derived normalization. | No evaluator semantics, contract, risk rule, or final information. |
| Validation | Preregistered model, uncertainty, calibration, and operating choices. | No contract, evaluator, threshold, margin, denominator, group, or split changes. |
| IID final | One-shot evaluation on seen signatures. | No tuning or refitting. |
| Held-out final | One-shot evaluation on held-out composition. | No tuning or refitting; report separately from IID final. |

All judgment-affecting inputs must be frozen and hashed before validation
quantized outputs. Final outcomes cannot change thresholds, margins,
denominators, groups, contract, evaluator, or split definitions.

**Rationale.** This preserves separation between learning/calibration and the
scientific quality claim.

**Rejected alternatives.** Final-test calibration, validation-driven contract
changes, and pooling IID with held-out final were rejected.

### J. Freeze and change control

**Accepted decision.** Use contract identifier
`qab.per_request_quality_contract.v1`. The freeze bundle covers the normative
specification, canonical glossary, authoritative ledger, dated decision
record, equations and tables, evaluator IDs/commits/adapters/parsers and
dependency hashes, prompt/template/composition hashes, decoding/seed/stopping/
length configuration, request/leakage/split manifests and hashes, and eventual
model/backend/block-group/schedule identities.

A semantics-preserving documentation or evaluator bug fix is distinct from a
scientific-policy change. If a bug fix changes labels, affected results are
invalidated and rerun even if the version remains unchanged. A policy change
to thresholds, margins, evaluator/extraction semantics, statuses, denominators,
exclusions, aggregation, strata, splits, confidence rules, or other
judgment-affecting fields requires a dated amendment, version bump, retained
old results, and affected reruns.

Before final-test unblinding, correct, record, rerun affected validation or
calibration work, and refreeze. After unblinding, invalidate affected final
results and do not patch or reuse the revealed set; a new untouched
confirmatory final set is required, with original and replacement results
reported separately. A documentation-only correction with no judgment effect
does not require a new final set.

**Rationale.** Versioned provenance prevents silent scientific-policy drift and
keeps invalidated results recoverable.

**Rejected alternatives.** Silent edits, overwriting affected results, and
reusing an unblinded set after a label-changing correction were rejected.

## Worked edge-case outcomes

| Case | Outcome |
| --- | --- |
| BF16 wrong; INT4 correct | BF16 reference failure; INT4 may be quality-safe if absolute quality passes; relative condition inapplicable; record comparative improvement; no violation. |
| BF16 wrong; INT4 equally wrong | INT4 scored absolute failure and violation if otherwise assessable; retain BF16 reference failure; no causality claim. |
| BF16 unscorable; candidate scored | Candidate absolute result retained; complete pair `not_assessable`; no safe or violation label. |
| Candidate unscorable | `not_assessable`; not safe and not a violation. |
| MATH passes; code fails in composite | Conjunction fails; deterministic scored pair is a violation. |
| MuSiQue answer passes; evidence fails | Conjunction fails; deterministic scored pair is a violation. |
| Candidate-generated code timeout | Candidate-caused timeout is scored `plus_pass=0`; native timeout retained; violation if otherwise assessable. |
| Evaluator infrastructure timeout | `evaluator_error` or `execution_error` by failing layer; `not_assessable`; no violation. |
| Conflicting repeated outcomes | Preserve every outcome; `nondeterministic`; `not_assessable`; no majority. |
| Faster schedule violates quality | Quality violation regardless of speed; performance is separate. |
| Group has too few examples | Underpowered; cannot pass the gate; not itself a violation; no post-hoc merge. |
| Evaluator bug before final-test unblinding | Dated amendment, affected-output classification, affected pre-final rerun, and refreeze. |
| Evaluator bug after final-test unblinding | Preserve and invalidate affected results; amend/version as required; use an untouched confirmatory final set. |

## Affected artifacts and validation

Authoritative artifacts are `docs/research-spec.md`,
`CONTEXT.md`, this ledger, and the dated entry in `docs/decisions.md`.
The pre-existing `docs/plans/issue-4-quality-contract.md` remains
non-authoritative provisional notes and is not adopted by this ledger.

Validation for this documentation resolution is limited to the documented
Markdown checks, `git diff --check`, contradiction review, and inspection of
the complete diff. No source code, implementation path, model, evaluator,
dataset, GPU job, serving path, or experiment is part of this ticket.
