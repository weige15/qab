# Query-Conditioned Quantization

This context defines the terms used to study query-conditioned weight
precision for decoder-only language-model inference.

## Language

**Request**:
An immutable single-turn evaluation unit containing a query, any fixed supplied
context, a required output contract, an atomic or composite component
structure, and source/template/split/leakage identities.
A request is distinct from a request–precision-schedule pair. Live retrieval,
conversation history, and post-routing adaptation are not part of the initial
request identity.

**Ground truth**:

A pre-existing target or behavioral reference independent of model output and
precision schedule. It may be an exact answer, equivalence target, executable
test contract, answer label, or evidence-support label.

**Evaluator**:

A versioned procedure that consumes candidate output and ground truth, performs
extraction/normalization/scoring, and emits raw metric outputs. Evaluator output
is not ground truth.

**Metric**:

A named raw output of a pinned evaluator with declared native value, range,
direction, and status semantics. Component metrics remain distinct from the
request-level Boolean quality judgment; no implicit cross-component averaging
is permitted.

**Unscorable output**:

A candidate output exists, but the frozen evaluator cannot produce a valid
judgment under its protocol. It is not quality-safe and is reported separately
from scored failure, evaluator failure, and execution failure; it remains in
attempted counts and is not silently dropped.

**Registry row**:

One authoritative request–component record. Composite requests reuse request
identity fields across rows while each component retains its own scoring fields.

**Task family**:

A named, evaluator-homogeneous population of request components sharing
ground-truth semantics, output contract, primary evaluator, raw metric
definitions, and scoring protocol. It is narrower than a component family and
is not a topic label.

**Block group**:
A contiguous group of transformer layers treated as one adaptation unit for
weight precision assignment.
_Avoid_: tensor block, when referring to the numerical sub-blocks used inside a
quantizer.

**Precision schedule**:
The per-request assignment of one allowed weight precision to each block group.

**Pre-prefill routing**:
The routing decision point at which a complete precision schedule is selected
once, after request arrival and before model prefill begins.
_Avoid_: partial-prefill routing, decode-time routing, for this study.

**Query-conditioned**:
A precision decision that can change as the natural-language query or its
model-derived representation changes.
_Avoid_: workload-conditioned, when the decision depends only on length,
batching, hardware, or other system properties.

**Initial task suite**:

The minimum decisive set of coherent request components and composites used to
test whether query-conditioned quantization sensitivity varies and whether
request representations predict quality-safe schedules beyond trivial and
semantic baselines. It prioritizes deterministic judgments and held-out
compositional generalization over benchmark breadth.

**Suite priority**:

Deterministic absolute-quality measurement is primary; held-out compositional
generalization on coherent, jointly necessary composites is required; broader
capability coverage is secondary.

**Component family**:

An independently scorable capability family represented in the initial suite:
numeric/mathematical reasoning, executable code generation, or fixed-context
evidence-grounded question answering.

**Request component**:
An independently scorable mandatory or auxiliary requirement within a request.
A component is not merely a topic, domain, or task-family label.

**Mandatory component**:
An independently scorable requirement included in the primary request-level
quality gate. Every mandatory component must pass; auxiliary results cannot
compensate for mandatory failure.

**Auxiliary component**:
An independently scorable requirement recorded for diagnosis or secondary
analysis but excluded from the primary request-level quality gate. Its failure
does not compensate for or invalidate mandatory-component judgments.

**Composite request**:

A single-turn request containing two or more components that are jointly
necessary within a shared scenario, context, dependency structure, or output
contract. Each component has a separate quality judgment, and the complete
request retains one traceable request-level identity.

Unrelated benchmark prompts concatenated together are not composite requests.

**Composition signature**:

A versioned canonical representation of component types, roles, mandatory or
auxiliary flags, directed dependencies, and required output-field relationships
used for deterministic composition grouping and split assignment.

**Split allocation**:

Train and validation use source-disjoint atomic and seen-composition instances;
IID final uses the same signatures; held-out final uses unseen signatures.
Assign source instances before generating derivatives and keep all derivatives in
their source split.

**Leakage group**:

The transitive set of source and derived records that could reveal the same
solution, context, tests, or prompt structure. A leakage group is assigned to
one split; cross-split parent unions are invalid, and near duplicates are
merged before split assignment.

**Quality contract**:
The preregistered rule that determines whether a request–precision-schedule
pair is quality-safe or violates a quality constraint.

**Quality judgment unit**:
The object for which quality is recorded. This study uses both the individual
mandatory request component and the complete request; the component-to-request
aggregation rule is defined separately in the quality contract.

**Absolute-quality reference**:
The declared ground truth or task evaluator used to determine whether a
request component or request succeeds.

**BF16 reference condition**:
The BF16 output produced under identical decoding conditions, used to measure
schedule-induced change or degradation. It is not ground truth.

**BF16 reference failure**:
A failure of the BF16 output against the absolute-quality reference. It is
recorded separately and does not determine the quantized schedule's quality
judgment.

**Quality-constraint violation**:
The safety classification assigned when a candidate request–precision-schedule
pair fails an applicable, preregistered quality condition. It is distinct from
a BF16 reference failure, evaluator failure, or hardware execution failure.

**Quality-safe pair**:
A request–precision-schedule pair for which every mandatory request component
passes the applicable absolute and BF16-relative conditions without a
disqualifying non-quality status.

**Violation-risk budget**:
The predeclared maximum tolerated probability of a quality-constraint
violation for the declared evaluation population. The initial target is
alpha = 0.05.

**Risk stratum**:
A predeclared subset of the evaluation population defined here by task type
and mandatory request-component composition.

**Worst-group risk gate**:
The safety requirement that every predeclared risk stratum satisfies the
violation-risk budget. Overall average risk cannot compensate for a failing
stratum.

**Minimum feasible stratum size**:
The smallest predeclared number of valid quality judgments required for a risk
stratum to support the confidence-bound safety gate.

**Quality-evaluable pair**:
A request–precision-schedule pair with a valid, scorable, deterministic
candidate quality evaluation.

**Non-quality exclusion rate**:
The rate of evaluator failure, hardware execution failure, unscorable output,
or nondeterminism among all attempted request–precision-schedule pairs.

**Reference-comparative improvement**:
A candidate result that meets the absolute-quality reference when the BF16
reference condition fails. It is recorded as a comparative result and is not
by itself evidence that quantization improves quality generally.

**Invalid output**:
A candidate output that violates a component's explicitly declared output
format or validity requirements. It is evaluated as a candidate failure,
unless the evaluator itself cannot operate for an independent implementation
reason.

**Generation truncation**:
An output that ends because the declared generation limit or stopping rule
occurred before the required response was complete. It remains a candidate
output and is judged by the component evaluator.

**Execution truncation**:
An output shortened or lost by an inference, transport, or recording failure
independent of the model's declared stopping rule. It is an execution failure,
not a quality judgment.

**Refusal output**:
An intentional model response declining to provide the requested content. It
is evaluated as a candidate output against the component's preregistered
contract; it is not automatically a success or a failure.

**Evaluator failure**:
The declared evaluator cannot produce a valid judgment because of an evaluator
implementation, configuration, or availability failure, distinct from an
unscorable candidate output.

**Hardware execution failure**:
The model or schedule cannot produce a usable candidate output because the
inference backend or hardware execution failed. It is not itself a quality
judgment.

**Unscorable output**:
A candidate output for which the declared evaluator cannot produce a valid
quality judgment under its preregistered scoring protocol. It is not safe, but
is recorded separately from a measured quality-constraint violation.

**No quality-safe schedule**:
The condition in which no candidate precision schedule satisfies every
mandatory component's preregistered quality contract for a request. It is
distinct from hardware infeasibility.

**Quality-safe schedule set**:
The set of candidate precision schedules that satisfy the quality contract
for a request, without implying hardware executability.

**Hardware-feasible schedule**:
A precision schedule that the declared hardware and quantization backend can
execute. Hardware feasibility is separate from quality safety.

**Final-test freeze**:
The point before final-test evaluation after which the quality contract,
evaluator registry, all judgment-affecting registry artifacts, strata,
thresholds, and decision rules cannot be changed without invalidating results.

**Contract change**:
A post-freeze change to any quality-contract field, evaluator, decoding
condition, split rule, risk rule, or other preregistered condition that can
alter a quality or safety result. It requires a dated scientific decision
record and affected-result invalidation or rerun.

**Primary decoding condition**:
The fixed decoding setup used for the primary quality contract: deterministic
greedy decoding with sampling disabled, temperature 0, and a documented
deterministic tie-break.

**Generation limit**:
The predeclared maximum output length and valid stopping conditions for a task
or request-component type. The same limit applies to BF16 and candidate
schedules.

**Nondeterministic outcome**:
A difference in output or quality judgment across executions with identical
declared request, precision schedule, decoding condition, and seed. It is
recorded as a separate non-safe status unless a distinct execution failure is
identified.

**Evaluator registry**:
The preregistered mapping from each initial task or request-component type to
its ground truth availability, evaluator implementation and version, metric
outputs, and scoring protocol.

**Composite-request aggregation**:
The rule that combines mandatory request-component judgments into the
whole-request quality judgment. This study uses logical conjunction for
quality safety, with no cross-component compensation.

**Native evaluator status**:

The status emitted by a pinned evaluator before the repository's normalized
status mapping. Native status and failure kind remain visible in the registry.

**Normalized evaluation status**:

The cross-evaluator status used for reporting: scored, unscorable_output,
evaluator_error, execution_error, or nondeterministic. It does not erase the
evaluator-native status.

**Metric denominator**:

The count of scored evaluations used for one named raw metric. It is distinct
from the attempted-evaluation reporting population and from any later quality-
risk denominator.

**Attempted-evaluation denominator**:

The count of frozen request–schedule–component evaluations submitted for
execution or scoring, including non-quality statuses. Exclusions and
unscorable results remain visible in this denominator's reporting.

**Evaluator adapter**:

The pinned boundary that maps candidate-output extraction, evaluator-native
statuses, and evaluator errors into the normalized registry status without
averaging, fallback, or output-dependent filtering.

**Versioned registry**:

The immutable set of dataset, evaluator, dependency, adapter, template,
composition, test, split, and adjudication identities required to reproduce
the same quality judgments.

**Registry freeze**:

The point before validation or model-output runs after which the versioned
registry is the source for all derived requests and evaluator runs.


**Scientific change record**:

A dated record of a post-freeze change, its reason, affected artifacts, and
required reruns. It preserves the old result rather than overwriting it.

**Documentation-only change**:

A change that cannot affect execution, extraction, scoring, split membership,
or interpretation of recorded results and therefore does not reopen the task
suite decision.

**Profile feasibility budget**:

The predeclared cap and source-grouped population for the first profile
experiment. It estimates repeated request–schedule measurement without claiming
final safety power.

**Profile experiment**:

The first schedule-measurement study using the feasibility budget. It is
distinct from full-source evaluation and from the later Issue #4 safety claim.

**Source population cap**:

The fixed number of source instances eligible for the first profile experiment.
Derived variants and composites remain within the source instance's split and
leakage group.

**Feasibility envelope**:

An assumption-based estimate of request counts, repeated schedule executions,
evaluator work, and artifact storage. It is not a measured runtime or hardware
claim.

**Statistical-power limitation**:

A documented source or split constraint that limits the strength of a safety or
generalization claim without invalidating the profile measurement itself.
