# Query-Conditioned Quantization

This context defines the terms used to study query-conditioned weight
precision for decoder-only language-model inference.

## Language

**Request**:
An incoming single-turn inference item whose query may affect the selected
precision schedule.

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

**Request component**:
A declared, mandatory subtask or quality-relevant requirement within a
composite request that can receive its own quality judgment.

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
evaluator registry, strata, thresholds, and decision rules cannot be changed
without invalidating the affected results.

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
