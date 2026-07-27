# Research Specification

## Status

The adaptation unit, routing decision point, task/evaluator registry, and
per-request quality contract are resolved through the current preregistration
decisions. The model, quantization backend, block-group boundaries, schedule
codebook, and exact router inputs remain open under their separate decisions.

## Research objective

Evaluate whether a representation of an incoming composite request can predict
its quantization-sensitivity profile well enough to select a quality-safe
mixed-precision schedule and support precision-compatible batching.

## Resolved initial-suite purpose

Establish whether query-conditioned quantization sensitivity varies across
coherent composite requests and whether request representations predict
quality-safe schedules beyond trivial, task-label, length, difficulty, and
generic-semantic baselines. The suite prioritizes deterministic component
judgments and held-out compositional generalization over benchmark breadth.

This purpose is the initial-suite commitment; the per-request quality contract
is specified in the normative section below.

## Resolved suite priority

- Primary: deterministic measurement of absolute task quality and
  schedule-induced change using reproducible evaluators.
- Required validation axis: held-out compositional generalization on coherent
  composite requests with jointly necessary components.
- Secondary: capability breadth beyond the selected component families.

The per-request quality contract is specified in the normative section below.

## Resolved initial component-family count

Use exactly three independently scorable capability families:

- numerical or mathematical reasoning;
- executable code generation;
- fixed-context evidence-grounded question answering.

Structured-output validity is cross-cutting and is not a fourth semantic family.

## Resolved request-component definition

A request component is an independently scorable mandatory or auxiliary
requirement within a request. A component is not merely a topic, domain, or
task-family label.

Examples:

- math.final_answer with a mathematical-equivalence evaluator;
- qa.supporting_evidence with an evidence-support evaluator.

## Resolved mandatory and auxiliary component roles

Mandatory component:
An independently scorable requirement included in the primary request-level
quality gate. Every mandatory component must pass; auxiliary results cannot
compensate for mandatory failure.

Auxiliary component:
An independently scorable requirement recorded for diagnosis or secondary
analysis but excluded from the primary request-level quality gate. Its failure
does not compensate for or invalidate mandatory-component judgments.

## Resolved composite-request definition

A composite request is a single-turn request containing two or more components
that are jointly necessary within a shared scenario, context, dependency
structure, or output contract. Each component has a separate quality judgment,
and the complete request retains one traceable request-level identity.

Unrelated benchmark prompts concatenated together are not composite requests.

## Resolved composition signature

A versioned canonical representation of a request’s component types, roles,
mandatory/auxiliary flags, directed dependencies, and required output-field
relationships. Its serialization is deterministic and defines the composition
group for split assignment and held-out-composition evaluation.

## Resolved request identity

An immutable single-turn evaluation unit containing a query, any fixed supplied
context, a required output contract, an atomic or composite component
structure, and source/template/split/leakage identities.

A request is distinct from a request–precision-schedule pair. Live retrieval,
conversation history, and post-routing adaptation are not part of the initial
request identity.

## Resolved ground truth and evaluator distinction

Ground truth:
A pre-existing target or behavioral reference independent of model output and
precision schedule. It may be an exact answer, equivalence target, executable
test contract, answer label, or evidence-support label.

Evaluator:
A versioned procedure that consumes a candidate output and ground truth,
performs extraction/normalization/scoring, and emits raw metric outputs.
Evaluator output is not ground truth.

## Resolved metric definition

Metric:
A named raw output of a pinned evaluator with a declared native value, range,
direction, and status semantics. Component metrics remain distinct from the
request-level Boolean quality judgment. No implicit cross-component averaging
is permitted.

## Resolved unscorable-output policy

Unscorable output:
A candidate output exists, but the frozen evaluator cannot produce a valid
judgment under its declared scoring protocol. It is not quality-safe and is
reported separately from scored failure, evaluator failure, and execution
failure. It remains visible in attempted counts and is not silently dropped.

## Resolved request–component registry schema

The authoritative registry has one row per request–component pair. A composite
request repeats request-level identity fields across its component rows and
varies component-level fields.

Required fields:

- request_id
- source_dataset
- source_revision
- source_instance_id
- prompt_template_id
- composition_signature
- component_id
- component_type
- mandatory
- target_or_reference
- evaluator_id
- required_output_field_or_extraction_rule
- split
- leakage_group_id


## Resolved task-family definition

A task family is a named, evaluator-homogeneous population of request
components sharing ground-truth semantics, output contract, primary evaluator,
raw metric definitions, and scoring protocol.

A task family is narrower than a component family and is not a topic label.
The registry’s component_type identifies the evaluator-compatible task-family
and component type.

## Resolved numeric task family

- component_type: numeric.math.equivalence
- scientific role: atomic mathematical reasoning with deterministic answer
  checking
- source_dataset: MATH
- source_revision: hendrycks/math@985bdc1696e88e8643f081a0ff4719da39f2ae2a
- license/access: MIT repository; public source access
- provided_splits: 7,500 train and 5,000 test; validation is carved from train
  before prompt variants or composites are generated
- ground_truth: target answer plus worked solution
- evaluator_id: math.equivalence.v1
- evaluator_revision: hendrycks/math@985bdc1696e88e8643f081a0ff4719da39f2ae2a
- raw_metric: equivalent in {0,1}
- metric_direction: higher is better
- primary construction: atomic source requests; later composites require
  separately traceable derived requests and the accepted composition rules

## Resolved numeric evaluator protocol

- evaluator_id: math.equivalence.v1
- evaluator_source: `hendrycks/math`, pinned to commit
  `985bdc1696e88e8643f081a0ff4719da39f2ae2a`
- input: the complete candidate response and the target answer
- output_extraction: the pinned repository extraction helper in
  modeling/dataset/util.py at the evaluator commit
- output_normalization: pinned math_equivalence normalization; comparison is
  exact normalized-string equality, not symbolic equivalence
- target_representation: the normalized target answer
- raw_metric: `equivalent` in `{0,1}`; higher is better
- deterministic_settings: CPU evaluation with no random seed
- timeout: 5 seconds per candidate response
- malformed_output: adapter records missing or invalid extraction as
  unscorable_output; it does not treat missing values as a valid equivalence
  result
- evaluator_error: a separate evaluator-error status, not a task failure
- unscorable_policy: a separate unscorable status when no valid judgment can
  be produced; it remains in attempted and exclusion reporting, not the
  scored metric or assessable safety denominator


## Resolved executable-code task family

- component_type: code.humaneval_plus.function_behavior
- scientific role: atomic executable program behavior
- source_dataset: HumanEval+
- source_revision: EvalPlus release v0.1.10, commit
  200defce9e3429d28ca215b6dd061c0f7f31c18b
- license/access: original HumanEval terms and EvalPlus release terms
- provided_splits: test-only; any validation carve occurs before variants
- ground_truth: reference behavior encoded by base and augmented tests
- evaluator_id: evalplus.humaneval.v0.3.1
- evaluator_revision: e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2
- raw_metrics: base_pass, plus_pass, and per-test statuses
- metric_direction: higher pass rate is better
- primary construction: atomic function contracts; later composites require
  jointly necessary program interfaces and tests

## Resolved executable-code evaluator protocol

- evaluator_id: evalplus.humaneval.v0.3.1
- evaluator_source: `evalplus/evalplus`, pinned to commit
  `e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2`
- dataset_release: HumanEval+ v0.1.10, pinned to commit
  `200defce9e3429d28ca215b6dd061c0f7f31c18b`
- input: one candidate function solution, the pinned task prompt, and the
  pinned base and augmented tests
- output_extraction: require one complete function solution; use the pinned
  EvalPlus solution-ingestion/parser behavior and retain the raw response
- output_normalization: no semantic normalization; execute the extracted
  solution under the pinned evaluator
- target_representation: reference behavior encoded by base and augmented
  tests
- primary_raw_metric: `plus_pass` in `{0,1}`
- auxiliary_raw_metrics: `base_pass`, per-test pass statuses, and failed-test
  identifiers; no averaging across these metrics
- metric_direction: higher pass is better

- deterministic_settings: pinned Python/dependencies, one evaluator worker,
  and explicit test_details=true; any disposable sandbox or network isolation
  is a separately pinned run control, not a guarantee of EvalPlus itself
- native_status: pass, fail, or timeout; candidate exceptions are fail and
  process timeouts are timeout; plus_pass requires base and plus pass
- timeout: EvalPlus official per-test rule max(1.0 seconds, 4 × reference
  runtime), with task-level process timeout and corresponding flags pinned
- malformed_output: deterministic scored failure with a reason and no execution
- evaluator_error: separate status for evaluator or infrastructure failures;
  candidate exceptions are scored failures and candidate process timeouts retain
  native timeout with normalized scored status
- unscorable_policy: separate status only when the evaluator cannot validly
  judge; it remains in attempted and exclusion reporting, not the scored metric
  or assessable safety denominator

## Resolved fixed-context QA task family

- component_type: qa.musique_full.answer_and_support
- scientific role: fixed-context 2–4 hop answer plus evidence selection
- source_dataset: MuSiQue-Full
- source_revision: official MuSiQue v1.0 archive
- license/access: CC BY 4.0; official archive access
- provided_splits: train, dev, and test for Ans and Full variants
- ground_truth: answer, supporting paragraphs, and answerability/contrast labels
- evaluator_id: musique.full.v1
- evaluator_revision: 24cc5b297acc2abfc5fb3d0becb6ef7b73d03717
- raw_metrics: answer_em, answer_f1, support_f1,
  group_answer_sufficiency_f1, and group_support_sufficiency_f1
- metric_direction: higher is better
- protocol: fixed supplied context; retrieval disabled
- primary construction: native coherent multi-hop requests; later cross-family
  composites require shared context/dependencies and separately traced fields

## Resolved fixed-context QA evaluator protocol

- evaluator_id: musique.full.v1
- evaluator_source: `StonyBrookNLP/musique`, pinned to commit
  `24cc5b297acc2abfc5fb3d0becb6ef7b73d03717`
- dataset_release: official MuSiQue v1.0 archive; archive identity is pinned
  in the final manifest
- input: the question, fixed supplied context, gold answer/support labels, and
  the candidate prediction; retrieval is disabled
- output_extraction: adapter requires the official prediction fields for answer
  and paragraph support; the registry stores supporting paragraph IDs, and
  schema-invalid candidate fields are classified before calling the evaluator
- output_normalization: official evaluate_v1.0.py normalization and scoring
  behavior at the pinned evaluator commit; missing fields or row alignment
  failures are evaluator errors, not native scored failures
- target_representation: gold answer, gold supporting paragraphs, and official
  answerability/contrast labels
- answer_component: mandatory; primary raw `answer_f1` in `[0,1]`; auxiliary
  `answer_em` and `group_answer_sufficiency_f1`
- support_component: mandatory; primary raw `support_f1` in `[0,1]`; auxiliary

  `group_support_sufficiency_f1`
- auxiliary_raw_metrics: answer and support metrics remain distinct; no
  cross-component averaging
- metric_direction: higher is better for every raw metric
- deterministic_settings: CPU evaluation, no random seed, fixed input order,
  and one evaluator process
- timeout: 5 seconds per prediction record
- malformed_output: adapter records candidate missing or invalid fields as
  scored failure; the official evaluator is called only for schema-valid rows
- evaluator_error: separate status for evaluator failure or prediction/gold
  alignment failure; candidate answer/support failure is not evaluator error
- unscorable_policy: separate status only when the frozen evaluator cannot
  validly judge the task; it remains in attempted and exclusion reporting, not
  the scored metric or assessable safety denominator

## Resolved allowed initial composition set

- atomic.numeric
- atomic.code
- native.qa.answer_and_support with MuSiQue hop composition
- numeric.final_answer -> code.program

The initial suite does not permit code->QA, numeric->QA, or three-way
cross-family composites without a separately specified construction and scoring
protocol.

## Resolved composition-signature split allocation

- Train: atomic numeric, code, and QA requests; MuSiQue 2-hop and 3-hop
  compositions.
- Validation: source-disjoint atomic requests and MuSiQue 2-hop/3-hop
  compositions.
- IID final test: source-disjoint instances with the same seen signatures.
- Held-out-composition final test: MuSiQue 4-hop compositions and
  numeric.final_answer -> code.program composites.
- Assign source instances to splits before prompt variants or composites; keep
  every derivative in its source split and freeze the final-test manifest before
  threshold, schedule-codebook, predictor, or router tuning.

## Resolved leakage-group closure

leakage_group_id is the transitive closure of source and derived records that
could reveal the same solution, context, tests, or prompt structure. The closure
includes:
- source instances and all prompt variants;
- paraphrases and formatting variants of one source item;
- QA questions sharing a document, evidence graph, or source article;
- code problems with their reference implementation, base tests, augmented tests,
  and variants;
- derived/composite requests, whose group is the union of all parent groups;
- content-bearing template versions, which stay within one split;


- near duplicates merged by normalized exact hashes, text 5-gram Jaccard >= 0.90,
  or identical normalized code AST plus test-set hashes;
- source-provided leakage IDs reviewed as mandatory links.

Every leakage group is assigned to exactly one split before variants or
composites are generated. A cross-split parent union is invalid.
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
codebook, model, and quantization backend remain open decisions. The Issue #7
task-suite dataset sources are resolved; archive checksums and final manifests
are preflight artifacts. Exact router inputs beyond the routing-time boundary
are also not fixed by this decision.

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

The normative Issue #4 contract is recorded in the section
“Normative per-request quality contract” below. In summary, for request \(q\),
candidate schedule \(s\), and mandatory component set \(M(q)\), quality safety
is a conjunction over components; it is not an average or compensatory score.

A component's absolute label is:

\[
\operatorname{absolute\_pass}_c(q,s)
\iff
\operatorname{status}_c(q,s)=\operatorname{scored}
\land
m_c(q,s)\ \text{meets the frozen absolute criterion}.
\]

For higher-is-better component metrics, the BF16-relative label is separate:

\[
\operatorname{BF16\mbox{-}noninferior}_c(q,s)
\iff
\operatorname{status}_c(q,\mathrm{BF16})=\operatorname{scored}
\land
m_c(q,s)\ge m_c(q,\mathrm{BF16})-\delta_c.
\]

A candidate whose BF16 reference is itself an absolute-quality failure is judged
against the absolute criterion; the BF16-relative condition is inapplicable and
the reference failure is reported separately. Missing or invalid required
judgments, evaluator or execution errors, and nondeterminism are
`not_assessable`, never silent passes or measured violations. The exact
component criteria, status mapping, denominators, risk gate, and change
control are normative below. Issue #7 remains authoritative for evaluator
versions, raw metric outputs, and normalized statuses.

## Resolved overall risk target

- The overall tolerated quality-violation probability is alpha = 0.05 for the
  declared evaluation population.
- This is a predeclared risk target, not a threshold selected from final-test
  outcomes.
- Observed rates must be assessed with the separately preregistered
  confidence-bound procedure.

## Resolved risk strata

- Risk strata are predeclared request-level populations:
  - `math.atomic` (MATH atomic);
  - `code.atomic` (HumanEval+ atomic);
  - `qa.native.2_3hop` (native MuSiQue 2/3-hop);
  - `qa.heldout.4hop` (held-out MuSiQue 4-hop);
  - `numeric.final_answer->code.program` (numeric-to-code composite).
- Each request–schedule pair contributes one observation to exactly one base
  stratum. MuSiQue answer and support remain component judgments inside one
  QA request stratum.
- Split identity, composition signature, evaluator family, and hop regime are
  part of the frozen membership predicates.
- Additional legitimate intersections enter the primary gate only when
  predeclared before outcomes and sufficiently supported; otherwise they are
  diagnostic only. Any added gate group increases K and triggers recalculation
  of the confidence adjustment and minimum support.
- No group may be created, split, merged, or redefined using outcomes.

## Resolved risk aggregation

- The primary risk gate is worst-group risk: every predeclared task/composition
  stratum must satisfy alpha = 0.05 under the preregistered confidence
  procedure.
- Overall average violation risk is reported as a secondary summary and
  cannot compensate for a failing stratum.

## Resolved confidence and sample-size feasibility

- The accepted violation-risk budget is \(\alpha=0.05\), with one-sided 95%
  familywise confidence across the five predeclared base strata.
- For each stratum, use the exact one-sided Clopper–Pearson upper bound:
  \(U_{\mathrm{CP}}(k,n;\gamma)=
  \operatorname{Beta}^{-1}(\gamma;k+1,n-k)\), with
  \(\gamma=1-\alpha/K=0.99\) for \(K=5\). The worst-group gate passes only
  when every \(U_{\mathrm{CP}}\le\alpha\).
- The planned Issue #7 caps are \(n=(128,164,256,128,128)\). The largest
  allowed violation counts \(k\) under the CP gate are:

  | Planned group size | \(\alpha=0.01\) | \(\alpha=0.05\) | \(\alpha=0.10\) |
  | ---: | ---: | ---: | ---: |
  | 128 | none | 0 | 5 |
  | 164 | none | 1 | 7 |
  | 256 | none | 4 | 14 |

  “None” means that even zero observed violations cannot meet the stated
  99%-per-group upper bound. This planning table uses only the declared counts,
  not model outputs.
- With \(K\) predeclared strata, zero observed violations require
  \(n_{\min}(K)=\left\lceil
  \log(\alpha/K)/\log(1-\alpha)\right\rceil\). For \(K=5\) and
  \(\alpha=0.05\), \(n_{\min}=90\). A group below this support is underpowered:
  it cannot pass the safety gate, is not counted as a violation merely for being
  underpowered, and must not be silently merged, waived, or redefined.
- Adding a primary intersection group increases \(K\), so the Bonferroni level
  and minimum-support calculation must be recomputed before outcomes.

## Resolved risk denominators

- The frozen manifest denominator contains every eligible request identity and
  its declared mandatory components.
- The attempted denominator contains every manifest request–schedule pair
  submitted for execution or scoring, including non-quality statuses.
- The scored denominator is evaluator-specific: it contains records for which
  that primary evaluator emitted valid raw metrics. The assessable denominator
  contains complete request–schedule pairs whose mandatory components are
  valid, deterministic, scored judgments and whose required BF16 reference
  conditions are available.
- Violation risk is estimated only over assessable request–schedule pairs.
  `unscorable_output`, `evaluator_error`, `execution_error`, and
  `nondeterministic` are retained in status and exclusion reporting, never
  count as safe, and are not silently converted into violations.
- Manifest, attempted, assessable, and scored counts are reported together;
  component metric denominators are not substituted for the request-level
  safety denominator. Exclusion rates cannot be hidden or used to claim
  serving readiness.

## Resolved quality and optimization boundary

- The quality contract defines the quality-safe schedule set independently of
  hardware executability and serving cost.
- Later routing may select only from the intersection of quality-safe and
  hardware-feasible schedules.
- Latency, throughput, memory, energy, and schedule regret are reported or
  optimized separately and are not folded into the quality score.

## Resolved split roles

- Train may fit only the learned predictor/representation parameters and
  train-derived normalization under the preregistered fitting procedure. It
  may not fit evaluator semantics or quality labels.
- Validation may tune or calibrate only preregistered predictor, uncertainty, or
  operating choices. It may not alter the contract, evaluator registry,
  thresholds, margins, statuses, denominators, risk budget, groups, or split
  definitions.
- The contract, evaluator pins and adapters, prompt/composition identities,
  decoding configuration, exclusion predicates, denominator policy, risk rule,
  and group definitions must be frozen and hashed before validation quantized
  outputs are inspected.
- IID final and held-out-composition final are each evaluated once under the
  same frozen contract and policy, and are reported separately. No tuning or
  refitting occurs between them.
- No final-test outcome may select or tune metrics, tolerances, strata,
  schedules, thresholds, denominators, groups, or decision rules.

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
  task-specific stop sequences are part of the predeclared execution
  configuration and are not chosen by Issue #7.
- Each primary judgment uses one canonical execution. Any repeatability
  evaluation, including its seed list and membership, must be predeclared and
  frozen separately from the primary judgment.
- If executions with identical request, precision schedule, decoding
  condition, and seed produce different outputs or quality judgments, the pair
  is recorded as nondeterministic and is not quality-safe. No majority vote or
  cherry-picking is allowed. The result remains separate from a measured
  quality-constraint violation and execution failure unless a distinct cause
  is identified.

## Boundary with Issue #4 exact quality metrics

The initial task suite, request-component schema, ground-truth availability,
evaluator implementations and versions, scoring outputs, split rules, and
leakage controls are defined by the resolved Issue #7 registry. The exact
per-request quality contract is now defined in the normative Issue #4 section
below, while Issue #7 remains authoritative for raw evaluator metrics and
normalized evaluator statuses. The registry must not be replaced by BF16
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

## Resolved evaluator-disagreement and denominator policy

- Each evaluator result retains its own raw outputs, extraction trace, status,
  and pinned version.
- The declared primary evaluator controls the primary component metric.
  Auxiliary evaluators and metrics are diagnostic only; scores are never
  averaged and cannot override the primary evaluator.
- No fallback evaluator is used in the primary study. Manual adjudication is
  permitted only for a frozen audit/error-analysis sample and cannot alter
  primary scores, thresholds, or schedule labels.
- Pre-execution filtering is permitted only for source-defined validity or
  leakage reasons independent of model outputs. Filtering cannot depend on
  BF16, INT8, or INT4 outcomes.
- The canonical evaluation statuses are scored, unscorable_output,
  evaluator_error, execution_error, and nondeterministic.
- Scored means that the evaluator produced valid raw metrics; a raw metric of
  zero does not by itself imply that the Issue #4 quality contract passes or
  fails.
- Evaluator disagreement is represented as metadata while retaining every
  evaluator result. Its fields are present, kind,
  primary_result_retained, and manual_adjudication. A disagreement does
  not trigger averaging or fallback.
- Report separate counts for the frozen manifest, attempted evaluations,
  scored evaluations, unscorable outputs, evaluator errors, execution errors,
  nondeterministic outcomes, and pre-execution exclusions.
- Raw metric denominators use scored evaluations only. The Issue #4 quality
  risk denominator is the assessable request-level denominator: complete,
  valid, scorable, deterministic candidate/reference pairs. Non-quality
  statuses remain visible in attempted-count and exclusion-rate reporting and
  never count as safe.

The registry records the policy as:

Policy fields:
  evaluator_disagreement_policy:
    primary_evaluator_is_authoritative: true
    auxiliary_metrics_are_diagnostic: true
    aggregate_scores: false
    fallback_evaluator_in_primary_study: false
    manual_adjudication: audit_only
    model_output_dependent_filtering: forbidden
    raw_outputs_and_statuses_retained: true
    nonquality_statuses_never_count_as_safe: true

- Each result also retains evaluator-native status, failure kind, evaluator
  identifier, and extraction/error trace; normalization never erases native
  evaluator behavior.
- The pinned evaluator mappings are: MATH extraction/equivalence outputs,
  EvalPlus pass/fail/timeout with per-test details, and MuSiQue adapter schema
  validation plus official evaluator alignment errors.
- Component-specific native statuses are retained even when the normalized
  status is scored, unscorable_output, evaluator_error, execution_error, or
  nondeterministic.

## Resolved registry versioning and freeze policy

- Every artifact that can change a quality judgment is pinned: dataset release,
  commit or archive checksum; evaluator repository commit and source files;
  dependency lock and runtime version; evaluator-adapter/parser version;
  prompt-template content hash; composite-generation procedure, inputs, and
  seed; test cases and test-harness version; split-manifest hash; and
  manual-label/adjudication artifact version when present.
- A registry freeze occurs before any validation or model-output run. The
  frozen registry is the source for all derived requests and evaluator runs.
- A final-test freeze occurs before threshold, schedule-codebook, predictor, or
  router calibration. The final-test manifest and every artifact that can alter
  its judgments are immutable after this point.
- After final-test freeze, a change affecting task identity, evaluator
  behavior, parsing, dependencies, templates, tests, splits, composites, or
  labels requires a dated scientific change record, invalidation of affected
  results, and new immutable runs. Old artifacts are never overwritten.
- Before final-test freeze, an affected change requires the specification and
  registry hashes to be updated and affected validation/calibration work to be
  rerun before final testing.
- Documentation-only changes that cannot affect execution do not reopen Issue
  #7. The Issue #4 quality contract separately freezes the interpretation of
  evaluator outputs, request-level safety labels, risk denominators, and
  confidence procedures.

Versioned registry fields are:

  registry_schema_version
  dataset_revision
  dataset_archive_checksum
  evaluator_commit
  evaluator_dependency_lock_hash
  adapter_parser_version
  prompt_template_version_and_hash
  composite_procedure_version_and_hash
  test_case_version_and_hash
  split_manifest_hash
  manual_adjudication_version
  final_test_manifest_hash

## Resolved first-profile feasibility budget

- The first profile experiment uses a capped, source-grouped subset rather than
  the full MATH or MuSiQue populations: 128 MATH atomic requests, all 164
  HumanEval+ source tasks, 256 native MuSiQue 2/3-hop requests, 128 held-out
  MuSiQue 4-hop requests, and 128 numeric.final_answer -> code.program
  composites.
- The resulting estimate is 804 request identities. HumanEval+ source tasks
  used as composite parents remain in the same split as their atomic
  derivatives; source groups are assigned before variants and composites.
- If S is the schedule count selected under Issue #5, the profile estimate is
  804*S request-schedule executions. At the current 8–16 schedule scope this is
  6,432–12,864 executions. Additional baseline conditions are reported as
  804*B and do not determine the schedule codebook here.
- Composite requests add component-level evaluator rows but not additional
  model generations. MATH and MuSiQue scoring are linear CPU work; HumanEval+
  execution is the dominant evaluator cost and retains native test statuses.
- Assuming 100–250 KiB per request-schedule record for raw output, traces,
  metrics, and code test details, the expected raw artifact envelope is roughly
  1–3 GiB. This is a planning assumption, not a measured result.
- Full-source MATH or MuSiQue repeated across schedules is outside the first
  profile budget. Exact runtime and archive checksums require an approved later
  data/evaluator preflight; no download or GPU run is part of Issue #7.
- The 164-task HumanEval+ source population is a recorded statistical-power
  limitation. The first profile experiment must not overstate independent code
  family safety evidence. This feasibility budget is separate from quality
  semantics; the risk planning table in the normative Issue #4 contract uses
  these declared group caps without inspecting model outputs.

The registry records the budget as:

feasibility_budget:
  first_profile_request_cap: 804
  math_atomic_requests: 128
  humaneval_plus_source_tasks: 164
  musique_native_requests: 256
  musique_held_out_4hop_requests: 128
  numeric_code_composites: 128
  schedule_count: issue_5_parameter
  estimated_request_schedule_executions: 6432_to_12864
  full_source_population_in_first_profile: false
  local_gpu_execution: forbidden
  exact_runtime_status: unmeasured_until_approved_preflight
  statistical_power_limitations: recorded

- Source-count correction: the official MuSiQue-Full v1.0 population is 49,628
  rows (39,876 train, 4,834 dev, 4,918 test). Earlier approximately-25,000
  wording referred to answerable rows rather than the Full population and is
  not the suite-size denominator. The accepted 804-request profile cap remains
  unchanged and samples only a declared subset.

## Normative per-request quality contract

**Contract identifier:** `qab.per_request_quality_contract.v1`

This section is the authoritative resolution of “Define the per-request quality
contract.” It defines request-level quality semantics, component criteria,
reference pairing, status and denominator interpretation, risk gates, split
roles, and change control. Issue #7 remains authoritative for the evaluator
registry, evaluator versions, raw metric outputs, native statuses, and
normalized status mapping. No threshold, evaluator, dataset, composition
signature, or split grouping is selected from final-test outcomes.

### Contract semantics

Let \(q\) be a frozen request, \(s\) a candidate precision schedule, and
\(M(q)\) its set of mandatory components. Let \(m_c(q,s)\) be the primary raw
metric for component \(c\), and let \(\mathcal A_c\) be its frozen absolute
criterion. For a deterministic scored component result:

\[
\operatorname{absolute\_pass}_c(q,s)
\iff
\operatorname{status}_c(q,s)=\mathrm{scored}
\land
m_c(q,s)\in\mathcal A_c.
\]

For each higher-is-better component, the BF16-relative label is separate from
the absolute label:

\[
\operatorname{BF16\mbox{-}noninferior}_c(q,s)
\iff
\operatorname{status}_c(q,\mathrm{BF16})=\mathrm{scored}
\land
m_c(q,s)\ge m_c(q,\mathrm{BF16})-\delta_c.
\]

The inequality is inclusive. A candidate improvement over BF16 satisfies the
relative condition and is recorded separately as an improvement; it does not
change the absolute criterion or establish a general quantization-improvement
claim.

If BF16 is scored but fails its absolute criterion, it is a BF16 reference
failure. The candidate is still judged against \(\mathcal A_c\), and the
BF16-relative condition is inapplicable for that component. If the BF16
reference is unscorable, an evaluator error, an execution error, or
nondeterministic, the candidate's independently available absolute result is
retained, but the complete request–schedule pair is \(\mathrm{not\_assessable}\).

Define \(\operatorname{assessable}(q,s)\) to require a valid, deterministic,
scored candidate judgment for every mandatory component and either a scored
BF16 reference or a scored BF16 reference failure for every mandatory
component. Then:

\[
\operatorname{quality\_safe}(q,s)
\iff
\operatorname{assessable}(q,s)
\land
\bigwedge_{c\in M(q)}
\operatorname{absolute\_pass}_c(q,s)
\land
\bigwedge_{\substack{c\in M(q)\\
  \operatorname{absolute\_pass}_c(q,\mathrm{BF16})}}
\operatorname{BF16\mbox{-}noninferior}_c(q,s).
\]

Here \(\operatorname{component\_safe}_c(q,s)\) means the candidate absolute
pass plus the BF16-relative pass when the BF16 component is absolutely
successful; it is satisfied by an absolute candidate pass alone when BF16 has a
recorded reference failure.

\[
\operatorname{violation}(q,s)
\iff
\operatorname{assessable}(q,s)
\land
\neg\operatorname{quality\_safe}(q,s).
\]

Thus, \(\mathrm{not\_assessable}\) is a distinct request-level outcome, not a
quality pass and not a measured violation. A \(\mathrm{violation}\) is only a
valid scored candidate/reference judgment that fails an applicable absolute or
BF16-relative condition. The labels \(\mathrm{absolute\_pass}\),
\(\mathrm{BF16\mbox{-}noninferior}\), \(\mathrm{quality\_safe}\),
\(\mathrm{violation}\), and \(\mathrm{not\_assessable}\) are retained
separately.

The quality-safe schedule set and hardware-feasible intersection are:

\[
S_{\mathrm{quality}}(q)=
\{s:\operatorname{quality\_safe}(q,s)\},
\qquad
S_{\mathrm{feasible}}(q)=
S_{\mathrm{quality}}(q)\cap S_{\mathrm{hardware}}(q).
\]

\(\operatorname{no\_quality\_safe\_schedule}(q)\) holds when
\(S_{\mathrm{quality}}(q)=\varnothing\). \(\operatorname{no\_feasible\_schedule}(q)\)
holds when \(S_{\mathrm{quality}}(q)\ne\varnothing\) but
\(S_{\mathrm{feasible}}(q)=\varnothing\). The latter is a feasibility outcome,
not a quality failure.

### BF16 reference condition

The BF16 and candidate executions use the same immutable request: prompt,
supplied context, required output contract/template, tokenizer, extraction and
normalization rules, evaluator version and protocol, field mapping, decoding
algorithm, sampling controls, temperature, top-p/top-k, repetition controls,
stop sequences, tie-break rule, stopping rule, and maximum output length. The
only intended condition difference is the weight-precision schedule. The
primary seed policy is one predeclared seed, with any additional robustness
seed list frozen separately. Reaching the maximum output length is a candidate
generation result and is evaluated under the component contract.

BF16 and candidate raw outputs, extraction traces, evaluator statuses, and
metrics are retained as paired records. Candidate improvements over a valid
BF16 result are reported, but the BF16 output remains a reference condition and
not ground truth. A wrong BF16 output does not make a correct candidate unsafe;
an equally wrong candidate fails its own absolute criterion and is a
violation when the pair is otherwise assessable.

### Component contract

| Component | Primary raw metric | Absolute criterion | BF16 margin \(\delta_c\) | Required status interpretation |
| --- | --- | --- | ---: | --- |
| MATH numeric equivalence | `equivalent` | `equivalent = 1` | 0 | Valid extraction plus equivalence is scored 1; valid non-equivalence is scored 0; invalid or missing extraction is `unscorable_output` with metric null/absent; evaluator/parser infrastructure failure is `evaluator_error` with metric null/absent. |
| HumanEval+ code behavior | `plus_pass` | `plus_pass = 1` | 0 | Candidate exception, malformed solution, or candidate-caused timeout is a scored failure with native status retained; evaluator/infrastructure failure is not a scored candidate failure. |
| MuSiQue answer | `answer_f1` | `answer_f1 >= 0.80` | 0.05 | Mandatory answer component; `answer_em` and group sufficiency are auxiliary diagnostics. |
| MuSiQue supporting evidence | `support_f1` | `support_f1 >= 0.80` | 0.05 | Mandatory evidence component; group support sufficiency is auxiliary diagnostics. |

The binary gates are exact. The MuSiQue floors are inclusive continuous-score
floors. Auxiliary metrics are retained and reported separately; they are never
averaged into a primary component score and cannot change a primary gate.
Thresholds and margins are frozen before validation quantized outputs and are
not selected from final-test outcomes.

### Component-to-request aggregation

Every mandatory component must be assessable and pass. For all allowed atomic
and composite signatures:

\[
\operatorname{quality\_safe}(q,s)
\iff
\bigwedge_{c\in M(q)}\operatorname{component\_safe}_c(q,s).
\]

Averaging, weighted averaging, scalar compensation, or offsetting one
component's failure with another component's improvement is prohibited. Native
MuSiQue requests require both answer and supporting-evidence components to pass.
A numeric final-answer-to-code-program composite requires both the numeric and
code components to pass. Auxiliary components do not alter the primary
request-level label.

### Status and denominator policy

Issue #7 defines the following normalized statuses and preserves each
evaluator-native status and failure trace:

| Normalized status | Meaning | Candidate quality label | Manifest / attempted / scored / assessable |
| --- | --- | --- | --- |
| `scored` | The primary evaluator produced valid raw metrics. | Absolute pass or scored failure, as dictated by the component criterion. | In manifest, attempted, and scored; assessable only when the complete request and required BF16 references are valid and deterministic. |
| `unscorable_output` | A candidate output exists, but the frozen evaluator cannot produce a valid judgment under its protocol. | `not_assessable`; never silently pass or become a violation. Component metric is null/absent. | In manifest and attempted; not scored or assessable. |
| `evaluator_error` | Evaluator, parser, configuration, dependency, or evaluator-service infrastructure failed independently of candidate quality. | `not_assessable`; not a violation. | In manifest and attempted; not scored or assessable. |
| `execution_error` | Inference, backend, hardware, transport, or recording failed before a usable candidate judgment. | `not_assessable`; not a violation. | In manifest and attempted; not scored or assessable. |
| `nondeterministic` | Repeated executions under identical frozen conditions conflict in output or judgment. | `not_assessable`; preserve every outcome and do not majority-vote. | In manifest and attempted; not scored or assessable. |
| Pre-execution exclusion | Frozen manifest-integrity or scientific-eligibility predicate fails before execution. | No quality label; never a safe result. | In the frozen manifest and exclusion denominator; not attempted, scored, or assessable. |

A candidate-caused HumanEval+ exception or timeout is a scored failure with
`plus_pass=0`, not an evaluator or execution error. A MATH invalid or missing
extraction follows Issue #7's `unscorable_output` rule. An evaluator or parser
infrastructure timeout follows `evaluator_error` or
`execution_error`, according to the failing layer.

The manifest denominator is all frozen eligible records; attempted is all
submitted request–schedule evaluations; scored is the valid raw-metric
denominator for a primary evaluator; assessable is the complete request-level
denominator needed for the safety gate. Component metric denominators and the
request-level assessable denominator are reported separately. Non-quality
statuses and exclusions remain visible and never count as safe.

### Non-quality exclusions and optimization boundary

Pre-execution exclusions are permitted only when their predicates are frozen
from the request manifest and independent of precision, model outputs,
predictions, schedules, or quality outcomes. Examples are missing ground truth
or evaluator identity, invalid registry rows, leakage or duplicate violations,
invalid split assignment, and unsupported composition signatures. These records
remain in manifest accounting and exclusion reporting but are not attempted
quality judgments.

Hardware eligibility and schedule compatibility are separate feasibility
predicates. Latency, memory, throughput, energy, batching, serving behavior,
and hardware choice cannot alter the quality-safe label. A faster schedule that
violates quality remains a violation; a slower schedule that is quality-safe
remains quality-safe. Later selection may use only the intersection of
quality-safe and hardware-feasible schedules.

### Violation-risk and worst-group gate

A deterministic pair label and a method's empirical risk are different objects:

\[
\operatorname{violation}(q,s)\in\{0,1\},
\qquad
R(\pi)=
\Pr_q[\operatorname{violation}(q,\pi(q))
\mid \operatorname{assessable}(q,\pi(q))].
\]

The non-assessable rate for \(\pi\) is reported separately and cannot be hidden
by the conditional risk denominator.

The accepted risk budget is \(\alpha=0.05\). The primary gate is a worst-group
gate with one-sided 95% familywise confidence. The five predeclared base groups
are:

1. MATH atomic;
2. HumanEval+ atomic;
3. native MuSiQue 2/3-hop;
4. held-out-composition MuSiQue 4-hop;
5. numeric final-answer-to-code-program composite.

Each request–schedule pair belongs to exactly one base group. Group membership is
frozen from evaluator/component family, atomic or composite signature, MuSiQue
hop count, split identity, and any declared intersection fields before
outcomes are observed. MuSiQue answer and evidence are components within one QA
request group. Additional intersections are primary only if predeclared and
sufficiently supported; each added group increases \(K\), requiring a new
Bonferroni and minimum-support calculation. Favorable groups may not be
selected after outcomes.

For \(k\) violations among \(n\) assessable observations and \(K\) primary
groups, use the exact one-sided Clopper–Pearson upper bound:

\[
U_{\mathrm{CP}}(k,n;\gamma)
=
\operatorname{Beta}^{-1}(\gamma;k+1,n-k),
\qquad
\gamma=1-\alpha/K.
\]

The gate passes only if \(U_{\mathrm{CP}}\le\alpha\) for every sufficiently
supported primary group. With \(K=5\), \(\alpha=0.05\), and zero violations,
the minimum support is:

\[
n_{\min}(K)
=
\left\lceil
\frac{\log(\alpha/K)}{\log(1-\alpha)}
\right\rceil
=90.
\]

A group below this support is underpowered: it cannot pass the gate, is not
itself counted as a violation, and cannot be merged, waived, or redefined
post hoc. The planned Issue #7 caps are 128, 164, 256, 128, and 128; the
candidate-budget planning table appears in the preceding resolved
sample-size section and uses no model outputs. Average risk is secondary and
cannot compensate for a failing group.

### Split roles

| Split | Permitted use | Prohibited use |
| --- | --- | --- |
| Train | Fit predictor/representation parameters and train-derived normalization under the preregistered procedure. | Fitting evaluator semantics, contract thresholds, risk rules, or any final-test information. |
| Validation | Tune/calibrate preregistered predictor, uncertainty, and operating choices. | Changing evaluator pins, metrics, floors, margins, statuses, denominators, groups, splits, or the contract. |
| IID final | One-shot evaluation of the frozen predictor and contract on seen signatures. | Any tuning, refitting, threshold selection, or policy revision. |
| Held-out final | One-shot evaluation of the frozen predictor and contract on held-out composition. | Any tuning, refitting, threshold selection, or policy revision. |

All judgment-affecting contract, registry, prompt/template, composition,
decoding, exclusion, denominator, risk, group, and split inputs must be frozen
and hashed before validation quantized outputs are inspected. IID and held-out
final results are reported separately. Final outcomes cannot drive any
threshold, margin, denominator, group, evaluator, split, or contract change.

### Freeze and change control

The freeze bundle for `qab.per_request_quality_contract.v1` covers the
normative sections and equations in `docs/research-spec.md`, canonical
glossary definitions in `CONTEXT.md`, the authoritative decision ledger,
the dated scientific decision record, all component tables and formulas,
evaluator IDs, commits, adapters, parsers and dependency hashes, prompt and
composition identifiers and hashes, decoding/seed/stopping/length
configuration, request/leakage/split manifests and hashes, and the eventual
model, backend, block-group, and schedule identities.

A bug fix is a semantics-preserving correction to documentation or evaluator
implementation. If it can change a label, the affected labels and results are
invalidated and rerun even if the contract version remains unchanged. A
scientific-policy change alters thresholds, margins, evaluator or extraction
semantics, statuses, denominators, exclusions, aggregation, strata, splits,
confidence rules, or any other judgment-affecting field. It requires a dated
amendment, a version bump, retention of old results, and reruns for every
affected artifact.

Before final-test unblinding, correct the affected artifact, record the
amendment, rerun affected validation/calibration work, and refreeze all hashes.
After final-test unblinding, preserve and mark affected final results invalid;
do not patch the revealed set or reuse it as if untouched. A new untouched
confirmatory final set is required for a replacement claim, and original
invalidated and replacement results are reported separately. A documentation-
only correction with no judgment effect requires no new final set.

### Worked edge-case truth table

| Case | Result under this contract |
| --- | --- |
| BF16 wrong; INT4 correct | BF16 reference failure; INT4 can be quality-safe if its absolute gate passes; relative label is inapplicable; record reference-comparative improvement; no violation. |
| BF16 wrong; INT4 equally wrong | Both are scored absolute failures; INT4 is a violation if otherwise assessable; retain BF16 reference failure; make no causality claim. |
| BF16 unscorable; candidate scored | Retain candidate absolute result; complete pair is `not_assessable`; no safe or violation label. |
| Candidate unscorable | `not_assessable`; not quality-safe and not a violation. |
| MATH passes; code fails in composite | Conjunction fails; deterministic scored pair is a violation. |
| MuSiQue answer passes; evidence fails | Conjunction fails; deterministic scored pair is a violation. |
| Candidate-generated code times out | Candidate-caused timeout is scored `plus_pass=0`; retain native timeout; violation if the complete pair is otherwise assessable. |
| Evaluator infrastructure times out | `evaluator_error` or `execution_error` by failing layer; `not_assessable`, not a violation. |
| Conflicting repeated outcomes | Preserve all outputs; normalized status `nondeterministic`; `not_assessable`; no majority or cherry-pick. |
| Faster schedule violates quality | It is a quality violation regardless of speed; latency and throughput remain separate measurements. |
| Group has too few examples | Underpowered; cannot pass the worst-group gate; not itself a violation; no post-hoc merge or group selection. |
| Evaluator bug found before final-test unblinding | Record amendment; classify affected outputs; rerun affected pre-final work; refreeze before final testing. |
| Evaluator bug found after final-test unblinding | Preserve and invalidate affected results; amend/version as required; evaluate a new untouched confirmatory final set. |
