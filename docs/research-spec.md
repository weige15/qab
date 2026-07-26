# Research Specification

## Status

The adaptation unit and routing decision point are resolved. The quality
contract structure is resolved through the current preregistration decisions,
but its exact task/evaluator metric registry and numeric thresholds remain
blocked by issue #7. The model, dataset, quantization backend, and schedule
count also remain open.

## Research objective

Evaluate whether a representation of an incoming composite request can predict
its quantization-sensitivity profile well enough to select a quality-safe
mixed-precision schedule and support precision-compatible batching.

## Resolved adaptation unit and routing decision point

- The adaptation unit is a **block group**: a contiguous group of transformer
  layers.
- A request receives a **precision schedule** assigning one weight precision to
  each block group.
- The initial precision choices are **BF16, INT8, and INT4**, weights only.
- The complete precision schedule is selected at **pre-prefill routing**: once
  per request, before model prefill begins.
- The initial study does not adapt weight precision after partial prefill or
  during decoding.

The number and boundaries of block groups, hardware-executable schedule
codebook, model, dataset, and backend remain open decisions. The exact router
inputs beyond the routing-time boundary are also not fixed by this decision.

## Resolved quality judgment unit

- The quality contract records judgments at both levels: each declared
  mandatory request component is an atomic judgment unit, and the complete
  request is a request-level judgment over those component judgments.
- The evaluated object is a request–precision-schedule pair.
- The rule aggregating component judgments into the request-level Boolean
  outcome is specified separately under composite-request aggregation.

## Resolved quality references

- Declared ground truth or a task evaluator is the primary absolute-quality
  reference and determines task or component success.
- BF16 output generated under identical decoding conditions is a comparative
  reference for schedule-induced change or degradation.
- BF16 is not ground truth. A BF16 failure is not automatically a quantized
  failure, and BF16-only comparison cannot establish quantized success.
- Components without a declared ground truth or task evaluator remain
  unscorable for absolute-quality safety until their evaluator is specified.
- A BF16 failure is recorded as a BF16 reference failure. It does not
  determine the quantized schedule's quality judgment, which is evaluated
  against the declared absolute-quality reference.
- When both BF16 and a quantized schedule fail the absolute-quality reference,
  the quantized schedule is a quality-constraint violation for safety
  purposes, while BF16 is separately marked with a reference failure.
  Relative comparison to BF16 cannot excuse the quantized schedule, and the
  result must not be attributed to quantization without additional evidence.
- When BF16 fails the absolute-quality reference and a quantized schedule
  passes it, the candidate may be quality-safe if it satisfies its
  preregistered absolute-quality contract. Record the BF16 reference failure
  and the candidate's reference-comparative improvement separately; do not
  generalize the result as evidence that quantization improves quality.

## Resolved output-validity default

- Empty output is an observed candidate output, not missing data, and is passed
  to the declared component evaluator.
- Unless the component contract explicitly permits empty output, it fails the
  component quality criterion and makes the request unsafe.
- If the evaluator cannot score empty output, the result follows the
  separately defined evaluator-failure or unscorable-output policy; it must
  not silently pass.

## Resolved truncation handling

- Output ending because the declared generation limit or stopping rule occurs
  before the required response is complete remains a candidate output and is
  judged by the component evaluator.
- Output shortened or lost by an inference, transport, or recording failure
  independent of the model's declared stopping rule is recorded as an
  execution failure, not as a quality judgment.
- Neither form of truncation may silently enter the safe schedule set.
- An intentional model refusal is evaluated as a candidate output against the
  component's preregistered contract. It passes only when refusal is the
  declared correct behavior for that component; otherwise it fails the
  component quality criterion. A runtime abort before an output is produced
  remains an execution failure.
- An output that the declared evaluator cannot score under its preregistered
  protocol is recorded as unscorable. It is not quality-safe, but is kept
  separate from a measured quality-constraint violation. An evaluator
  implementation failure is recorded separately as evaluator failure.
- Missing ground truth is permitted only when a declared task evaluator
  independently defines absolute success. If neither ground truth nor a task
  evaluator exists, the component is unscorable and any request requiring it
  is not quality-safe. BF16 agreement and KL divergence cannot substitute.

## Resolved no-safe-schedule handling

- When no candidate precision schedule satisfies every mandatory component's
  preregistered quality contract, the request is classified as having no
  quality-safe schedule.
- The contract must not relax its thresholds, select a least-bad schedule, or
  substitute BF16 unless BF16 itself satisfies the contract.
- This outcome is distinct from hardware infeasibility; any later fallback
  behavior must be separately preregistered.

## Resolved request–schedule Boolean rule

For request q, candidate schedule s, and mandatory component set M(q),
quality_safe(q, s) is true if and only if every component has a valid
deterministic candidate evaluation, passes its absolute-quality criterion, and
either:

1. BF16 passes absolute quality and the candidate is within the
   preregistered BF16 non-inferiority margin; or
2. BF16 has a recorded reference failure.

A quality-constraint violation is true only when a valid deterministic
candidate evaluation fails an applicable absolute or BF16-relative criterion.
Unscorable output, evaluator failure, hardware execution failure, and
nondeterminism make the pair not quality-safe but are recorded separately from
measured quality violations. BF16 reference failure is recorded separately and
does not itself imply a violation.

The exact absolute criteria, BF16-relative criteria, metric directions, floors,
margins, and evaluator versions remain blocked by issue #7.

## Resolved overall risk target

- The overall tolerated quality-violation probability is alpha = 0.05 for the
  declared evaluation population.
- This is a predeclared risk target, not a threshold selected from final-test
  outcomes.
- Observed rates must be assessed with the separately preregistered
  confidence-bound procedure.

## Resolved risk strata

- Risk is reported within strata formed by predeclared task type and mandatory
  request-component composition.
- Stratum definitions and membership are frozen before validation and final
  testing.
- No stratum may be created, split, merged, or redefined using final-test
  outcomes. Exact labels are specified by the issue #7 evaluator registry.

## Resolved risk aggregation

- The primary risk gate is worst-group risk: every predeclared task/composition
  stratum must satisfy alpha = 0.05 under the preregistered confidence
  procedure.
- Overall average violation risk is reported as a secondary summary and
  cannot compensate for a failing stratum.

## Resolved confidence and sample-size feasibility

- For each predeclared risk stratum, estimate violation probability with a
  one-sided exact Clopper–Pearson upper confidence bound.
- Use Bonferroni adjustment across the predeclared strata to provide 95%
  familywise confidence.
- The worst-group risk gate passes only when every stratum's upper bound is at
  most 0.05.
- For K strata, the minimum per-stratum sample size is the smallest integer
  satisfying the zero-violation upper-bound condition:
  n_min(K) = ceil(log(0.05 / K) / log(1 - 0.05)).
- A stratum below n_min(K) is underpowered and cannot support a final safety
  claim. It must not be silently merged, waived, or declared safe.
- Issue #7 supplies K and the actual stratum counts; until then, exact
  feasibility remains unresolved.

## Resolved risk denominators

- Quality-violation risk is computed over valid, scorable, deterministic
  candidate evaluations.
- Evaluator failures, hardware execution failures, unscorable outputs, and
  nondeterministic outcomes are excluded from that numerator and denominator.
- Those non-quality exclusions are reported separately over all attempted
  request–precision-schedule pairs and never count as safe.
- Exclusion rates cannot be hidden or used to claim serving readiness.

## Resolved quality and optimization boundary

- The quality contract defines the quality-safe schedule set independently of
  hardware executability and serving cost.
- Later routing may select only from the intersection of quality-safe and
  hardware-feasible schedules.
- Latency, throughput, memory, energy, and schedule regret are reported or
  optimized separately and are not folded into the quality score.

## Resolved split roles

- Training data may fit predeclared model or evaluator parameters.
- Validation data may calibrate or select only predeclared non-final modeling
  choices.
- The final-test split is reserved for evaluating the frozen quality contract
  and predictor.
- No final-test outcome may select or tune metrics, tolerances, strata,
  schedules, thresholds, or decision rules.

## Resolved validation calibration

- Validation data may calibrate predeclared predictor uncertainty,
  probability/interval calibration, and operating thresholds from a
  predeclared candidate set.
- Validation may not alter metric definitions, evaluator versions, absolute
  floors, BF16 margins, risk budget, strata, aggregation, or violation rules.

## Resolved final-test change control

- Before final-test evaluation, freeze the quality contract, evaluator
  registry, strata, thresholds, decoding/repeatability conditions, risk rules,
  and split policy.
- A post-freeze contract change requires a dated entry in
  docs/decisions.md before any new run. The entry must state the old and new
  rule, reason, affected artifacts, and required reruns.
- Changes to metrics, evaluators, floors, margins, reference rules,
  aggregation, decoding/repeatability, risk budget, strata, split policy, or
  violation rules invalidate affected quality, safety, risk, and schedule
  selection results. Recompute them in new immutable runs; never overwrite
  old artifacts.
- A change only to a separately reported serving-cost objective invalidates
  affected cost/utility results, not quality results, unless it changes the
  quality-safe schedule definition.
- Changes made before the final-test freeze require updating the specification
  and rerunning affected validation/calibration work before final testing.

## Resolved primary decoding condition

- The primary quality contract uses deterministic greedy decoding with
  sampling disabled and temperature 0.
- Token ties use a fixed documented tie-break rule.
- BF16 and candidate schedules use the same tokenizer, decoding algorithm,
  tie-break rule, stopping rules, and output-length limit.
- The random seed is recorded even though sampling is disabled.
- Every run and request records an explicitly predeclared random seed. The
  primary greedy result is expected to be seed-invariant. Any later stochastic
  robustness evaluation must use a predeclared seed list separate from the
  primary Boolean quality contract.
- Each task or request-component type has a predeclared maximum output length
  and stopping rule, frozen before validation and final testing. Reaching the
  maximum before a valid stop is generation truncation. Numeric limits and
  task-specific stop sequences remain blocked on issue #7.
- Each primary judgment uses one canonical execution, with three
  predeclared repeatability executions on the repeatability set under identical
  conditions. Repetitions and membership are fixed before evaluation.
- If executions with identical request, precision schedule, decoding
  condition, and seed produce different outputs or quality judgments, the pair
  is recorded as nondeterministic and is not quality-safe. No majority vote or
  cherry-picking is allowed. The result remains separate from a measured
  quality-constraint violation and execution failure unless a distinct cause
  is identified.

## Open prerequisite for exact quality metrics

The repository does not yet define the initial task suite, mandatory
request-component schema, ground-truth availability, evaluator
implementations/versions, or scoring outputs. These are tracked in [issue #7](https://github.com/weige15/qab/issues/7),
which blocks the metric registry and exact quality thresholds in issue #4.
This specification must not fill those fields with placeholders, BF16
agreement, KL divergence, or post hoc evaluator choices.

## Resolved composite-request aggregation

- The whole-request quality decision is the logical conjunction of its
  mandatory component decisions.
- Every mandatory component must be scorable and pass its preregistered
  component-level contract.
- No scalar weighting is used for the safety decision, and improvement on one
  mandatory component cannot compensate for failure on another.
- Any scalar utility used later for optimization is separate from the quality
  contract.
