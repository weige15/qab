# Issue #7: Initial task suite and evaluator registry

## Scientific objective

Specify the minimum decisive task suite and reproducible evaluator registry
needed to test query-conditioned quantization sensitivity on coherent atomic
and composite requests. Issue #4 quality thresholds and risk procedures remain
out of scope.

## Assumptions

- The issue #3 adaptation-unit and pre-prefill routing decision is authoritative.
- The initial study favors deterministic primary judgments, fixed supplied
  context, and held-out compositional generalization.
- No dataset download, model inference, evaluator implementation, or GPU run is
  in scope for issue #7.

## Proposed design

Research numeric/mathematical reasoning, executable code generation, and
fixed-context evidence-grounded question answering; then resolve the suite,
component ontology, request schema, composites, splits, evaluator registry,
unscorable policy, versioning, and feasibility one decision at a time.

## Affected files

- `docs/research/issue-7-task-suite-evaluator-registry-research.md`
- `docs/research-spec.md`
- `CONTEXT.md`
- `docs/decisions.md` only if an already recorded scientific commitment
  changes; the file is currently absent.
- GitHub issues #1, #4, and #7 only after explicit confirmation.

## Validation approach

- Compare candidates using primary dataset and evaluator sources.
- Audit every selected component for exact revisions, ground truth, metrics,
  extraction, scoring, unscorable, split, and leakage rules.
- Search final documents for unresolved placeholder language and separate issue
  #4 thresholds from issue #7 registry fields.
- Review the complete diff and GitHub map state; do not run models, evaluators,
  GPU experiments, or download data.

## Risks

- Public benchmark contamination and related-variant leakage can invalidate
  held-out compositional claims.
- Evaluator parsing, sandbox, timeout, or evidence-scoring ambiguity can mask
  the expected quantization effect.
- A suite that is too broad can spend the first experiment's budget on noisy
  or weakly scorable tasks.

## Milestones

1. Reconcile repository and Wayfinder state; claim issue #7.
2. Produce the cited candidate research packet.
3. Resolve decisions A–J interactively, updating the glossary inline.
4. Run the completeness and unresolved-language audit; obtain explicit shared
   understanding.
5. Finalize documents, resolve/close #7, update #1, and make #4 actionable;
   do not resolve #4 in this session.

## Decisions made during implementation

- Issue #7 was claimed by assigning it to `weige15` as the first GitHub write.
- Accepted initial-suite purpose: establish whether query-conditioned
  quantization sensitivity varies across coherent composite requests and
  whether request representations predict quality-safe schedules beyond
  trivial, task-label, length, difficulty, and generic-semantic baselines,
  prioritizing deterministic component judgments and held-out compositional
  generalization over benchmark breadth.
- Accepted suite priority: deterministic absolute-quality measurement is
  primary; held-out compositional generalization on coherent, jointly necessary
  composites is required; broader capability coverage is secondary.
- Accepted component-family count: exactly three independently scorable
  families—numerical/mathematical reasoning, executable code generation, and
  fixed-context evidence-grounded question answering. Structured-output
  validity is cross-cutting, not a fourth semantic family.
- Accepted request-component definition: a component is an independently
  scorable mandatory or auxiliary requirement, not merely a topic, domain, or
  task-family label. Example registry components include math.final_answer and
  qa.supporting_evidence.
- Accepted mandatory/auxiliary roles: mandatory components enter the primary
  request-level quality gate and all must pass; auxiliary components are
  reported for diagnosis/secondary analysis and do not gate primary safety.
- Accepted composite-request definition: a single-turn request with two or more
  jointly necessary components in shared scenario/context/dependency/output
  contract, separately judged with one traceable identity. Unrelated benchmark
  prompts concatenated together are not composites.
- Accepted composition signature: a versioned canonical representation of
  component types, roles, mandatory/auxiliary flags, directed dependencies, and
  required output-field relationships. Its deterministic serialization defines
  composition groups for split assignment and held-out-composition evaluation.
- Accepted request identity: an immutable single-turn unit containing query,
  fixed supplied context, output contract, component structure, and
  source/template/split/leakage identities. It is distinct from a
  request–precision-schedule pair; live retrieval and conversation history are out.
- Accepted ground truth: a pre-existing target or behavioral reference
  independent of model output and precision schedule; examples include exact
  answers, equivalence targets, executable test contracts, answer labels, and
  evidence-support labels. Evaluator output is distinct from ground truth.
- Accepted metric definition: a named raw output of a pinned evaluator with
  declared native value, range, direction, and status semantics. Component
  metrics remain distinct from request-level Boolean quality; no implicit
  cross-component averaging is permitted.
- Accepted unscorable policy: candidate output exists but frozen evaluator
  cannot produce a valid judgment; it is not safe, remains in attempted counts,
  and is separate from scored, evaluator, and execution failure.
- Accepted registry schema: one authoritative row per request–component pair;
  required fields are request_id, source_dataset/revision/instance, prompt
  template, composition/component identity, mandatory, target/reference,
  evaluator/extraction, split, leakage group, and stratification metadata.
- Accepted task family: a named evaluator-homogeneous population sharing
  ground-truth semantics, output contract, evaluator, raw metrics, and scoring
  protocol. It is narrower than a component family and not a topic label;
  component_type identifies the evaluator-compatible task-family/component type.
- Accepted numeric family: numeric.math.equivalence using MATH at commit
  985bdc1696e88e8643f081a0ff4719da39f2ae2a, MIT, train/test source splits,
  validation carved from train before derivatives, target-answer ground truth,
  and deterministic math equivalence with raw equivalent∈{0,1}, higher better.
- Accepted code family: code.humaneval_plus.function_behavior using HumanEval+
  release v0.1.10 commit 200defce9e3429d28ca215b6dd061c0f7f31c18b and EvalPlus
  evaluator v0.3.1 commit e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2; test-only
  source, validation carved before variants, base/plus/per-test raw statuses,
  and higher-is-better pass metrics.
- Accepted QA family: qa.musique_full.answer_and_support using the official
  MuSiQue v1.0 archive, CC BY 4.0, Ans/Full train/dev/test, answer/support/
  answerability ground truth, evaluator commit 24cc5b297acc2abfc5fb3d0becb6ef7b73d03717,
  answer/support/group-sufficiency metrics, higher better, and fixed supplied
  context with retrieval disabled.
- Accepted allowed compositions: atomic.numeric, atomic.code,
  native.qa.answer_and_support with MuSiQue hops, and
  numeric.final_answer -> code.program. code->QA, numeric->QA, and three-way
  composites require a separate construction/scoring protocol.
- Accepted split allocation: train/validation use source-disjoint atomics and
  MuSiQue 2/3-hop compositions; IID final uses those seen signatures;
  held-out final uses MuSiQue 4-hop and numeric.final_answer -> code.program.
  Assign source instances before derivatives and freeze the final manifest
  before threshold, codebook, predictor, or router tuning.
- Accepted leakage closure: source items, variants, paraphrases, shared
  documents/evidence, code problems/tests, content-bearing templates, and
  derived composites form one transitive group. Merge exact normalized,
  text-Jaccard>=0.90, AST/test-hash duplicates; cross-split unions are invalid.
- Accepted numeric evaluator protocol: `math.equivalence.v1` uses the MATH
  evaluator pinned to commit 985bdc1696e88e8643f081a0ff4719da39f2ae2a; input
  is the complete candidate response and target; official final/boxed-answer
  extraction and normalization are used; raw `equivalent∈{0,1}` is
  higher-is-better; CPU/no-seed evaluation has a 5-second candidate timeout;
  malformed output is equivalent=0 when the scorer returns a valid result;
  evaluator errors and unscorable outputs are separate statuses, and
  unscorable outputs remain in attempted and denominator counts.
- Accepted code evaluator protocol: `evalplus.humaneval.v0.3.1` uses
  HumanEval+ v0.1.10 and the pinned EvalPlus commit; `plus_pass` is primary;
  `base_pass`, per-test statuses, and failed-test IDs are auxiliary; one
  complete solution is parsed by the pinned evaluator, then executed in a
  pinned single-worker isolated sandbox with the official per-test timeout;
  malformed code is scored failure, candidate exceptions/timeouts are scored
  failure, evaluator errors are separate, and unscorable outputs remain in
  attempted and denominator counts.
- Accepted QA evaluator protocol: `musique.full.v1` uses the official
  MuSiQue v1.0 archive and evaluator commit 24cc5b297acc2abfc5fb3d0becb6ef7b73d03717;
  fixed supplied context is scored with retrieval disabled; answer and support
  are separate mandatory components with primary `answer_f1` and `support_f1`;
  exact match and group-sufficiency outputs are auxiliary and never averaged;
  official prediction-field extraction/normalization is pinned; CPU/no-seed,
  fixed-order evaluation uses a 5-second record timeout; malformed fields are
  scored failure, evaluator/alignment errors are separate, and unscorable
  outputs remain in attempted and denominator counts.
