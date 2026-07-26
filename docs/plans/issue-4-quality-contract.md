# Issue #4: Per-request quality contract

## Scientific objective

Define an executable, preregistered rule for classifying a request–precision
schedule pair as quality-safe or a quality-constraint violation.

## Assumptions

- The resolved issue #3 scope is authoritative: a request receives one
  pre-prefill precision schedule over contiguous block groups using BF16, INT8,
  or INT4 weights.
- Quality, hardware executability, and serving cost remain separate.
- Decisions are made interactively and are not filled in from unspecified
  task, evaluator, or dataset details.

## Proposed design

Resolve the contract in the dependency order stated by issue #4, recording
resolved terms in `CONTEXT.md` and the complete scientific contract in
`docs/research-spec.md`.

## Affected files

- `CONTEXT.md`
- `docs/research-spec.md`
- `docs/decisions.md` only if an existing commitment must be changed; the file
  is currently absent.
- GitHub issues #1 and #4 after the contract is complete and explicitly
  confirmed.

## Validation approach

- Audit every required contract field for an executable definition.
- Check that no final-test outcome can select or tune the contract.
- Verify the request-level Boolean rule distinguishes quality, reference,
  evaluator, and hardware failures.
- Review the final diff and issue/map state; no GPU or evaluator runs are in
  scope for this ticket.

## Risks

- The task suite, ground truth, evaluator versions, and sample-size feasibility
  may be too unspecified to complete exact metric and risk choices.
- A scalar composite score could hide mandatory-component failures.
- BF16 may be incorrect or nondeterministic and must not be treated as truth by
  default.

## Milestones

1. Resolve the ten issue #4 dependencies one at a time.
2. Update the glossary immediately when terms become settled.
3. Accumulate the full contract in `docs/research-spec.md`.
4. Audit completeness and obtain explicit shared-understanding confirmation.
5. Only then comment/close #4 and update the map.

## Decisions made during implementation

- Judgment unit: both the individual mandatory request component and the
  complete request; aggregation remains a separate decision.
- Quality reference: ground truth/task evaluator for absolute quality, plus
  BF16 under identical decoding as a comparative reference; BF16 is not truth.
- Exact metric registry prerequisite: issue #7 specifies the initial task
  suite and evaluator registry; issue #4 remains blocked for exact metrics and
  thresholds until then.
- Composite aggregation: whole-request safety is the conjunction of all
  mandatory component decisions; no scalar compensation.
- BF16 failure: record a BF16 reference failure separately; judge the
  quantized schedule against the absolute-quality reference.
- Joint failure: a quantized candidate failing alongside BF16 is unsafe and
  is a quality-constraint violation; do not infer causality from this result.
- Candidate improvement over failed BF16: judge the candidate by absolute
  quality, record the BF16 reference failure, and avoid general improvement
  claims.
- Empty output: treat as an observed candidate output; it fails by default
  unless the component contract explicitly permits it.
- Truncation: distinguish generation-limit/stopping-rule truncation, which is
  evaluated as candidate output, from infrastructure truncation, which is an
  execution failure; neither silently passes.
- Refusal: evaluate intentional refusal against the component contract;
  refusal is safe only when explicitly correct for that component.
- Unscorable output: exclude it from the safe set and record a separate
  unscorable status; do not silently count it as a pass or measured violation.
- Missing ground truth: require an independent declared task evaluator;
  otherwise record the component as unscorable and unsafe.
- No safe schedule: emit an explicit no-quality-safe-schedule outcome; do not
  relax the contract or select a least-bad schedule.
- Primary decoding: deterministic greedy decoding, sampling disabled,
  temperature 0, fixed tie-breaking, and identical decoding conditions.
- Seeds: record explicitly predeclared seeds; any stochastic robustness seed
  list is separate and frozen before evaluation.
- Output limits: use frozen task/component-specific maximum lengths and stop
  rules; numeric values remain an issue #7 prerequisite.
- Repetitions: one canonical execution for primary judgments plus three fixed
  repeatability executions on the preregistered repeatability set.
- Nondeterminism: any same-condition disagreement is non-safe and separately
  recorded; no majority vote or cherry-picking.
- Boolean rule: all mandatory components must pass absolute quality and,
  when BF16 passes, the BF16 non-inferiority condition; non-quality failures
  make the pair non-safe without being measured quality violations.
- Risk target: overall tolerated quality-violation probability alpha = 0.05.
- Risk strata: predeclared task type × mandatory-component composition,
  frozen before validation and final testing.
- Risk aggregation: worst-group risk is the gate; overall average risk is
  secondary and cannot compensate for a failing stratum.
- Confidence/sample size: one-sided exact Clopper–Pearson upper bounds with
  Bonferroni-adjusted 95% familywise confidence; each stratum must meet the
  formula-based minimum size before a final safety claim.
- Risk denominator: quality violations use valid, scorable, deterministic
  evaluations; all other non-quality exclusions are separately reported over
  attempted pairs and never count as safe.
- Optimization boundary: quality-safe schedules are intersected with
  hardware-feasible schedules later; serving cost and regret stay separate.
- Split roles: train fits predeclared parameters, validation calibrates
  allowed non-final choices, and final test evaluates the frozen contract.
- Change control: freeze before final test; post-freeze changes require a
  dated decisions entry and invalidate/rerun affected results in new immutable
  runs.
