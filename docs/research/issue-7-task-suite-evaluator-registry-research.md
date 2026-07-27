# Issue #7 research note: initial task suite and evaluator registry

Status: evidence packet for human design decisions; not the final registry.
Prepared from the repository’s issue-7 research subagents and primary dataset,
paper, benchmark, evaluator, and official documentation sources. No dataset was
downloaded and no model, evaluator, or GPU experiment was run.

## Executive finding

The recommended starting point remains a minimum decisive suite with roughly
three independently scorable capability families: numerical reasoning,
executable code generation, and fixed-context evidence-grounded question
answering. The evidence supports deterministic primary evaluators and fixed
context. It does not support selecting a benchmark solely for popularity, or
using an LLM judge as the sole primary evaluator.

Candidate short list for the design discussion:

- Numeric: GSM8K is the cheapest deterministic pilot; MATH-500 is a compact
  harder development set; full MATH is a broader primary candidate.
- Code: HumanEval+ with EvalPlus is the strongest small primary candidate;
  MBPP+ is a complementary source with broader task style.
- Fixed-context QA: MuSiQue-Full is the strongest evidence-grounded candidate;
  HotpotQA distractor is a simpler supporting-evidence alternative; SQuAD 2.0
  is a useful answer-only control but weak as the sole evidence-grounded task.

These are recommendations to test in the grilling loop, not accepted choices.

## Cross-candidate interpretation

### Task or component type and scientific role

Numeric candidates test exact final-answer reasoning. Code candidates test
whether a generated program satisfies executable behavioral requirements. QA
candidates test answer production under supplied context; HotpotQA and MuSiQue
also test support selection. These are component types, not topic labels: each
must have an independently scorable requirement.

### Coherent composites

MuSiQue and HotpotQA are intrinsically multi-hop or answer-plus-support tasks,
so their internal components are coherent. A math-plus-code-plus-QA request is
not supplied by any candidate dataset. If cross-family composites are selected,
they require a task-specific template with a shared scenario, a jointly
necessary output contract, and separately scorable fields. Unrelated prompts
must not be concatenated. Every derived request must retain all source IDs and
one leakage group.

### Structured output

Format validity is cross-cutting. Each request must declare required output
fields and an extraction rule; malformed output is passed to the evaluator when
possible and otherwise receives the declared unscorable status. This does not
require a fourth semantic family.

## Candidate records

Every record below uses the same fields: component type; scientific role;
coherent-composite support; dataset/source and exact revision; license/access;
splits; ground truth; evaluator and exact revision; raw metrics and direction;
determinism; parsing/scoring ambiguity; unscorable cases; leakage risk; cost;
and suitability for repeated scheduled evaluation.

### Numeric: GSM8K

- Component type: grade-school mathematical word problem; atomic exact-answer
  reasoning.
- Scientific role: low-cost deterministic numeric sensitivity component and
  parser/evaluator pilot.
- Coherent composite support: native items are atomic. Cross-family composites
  require a new template and cannot reuse the item as an unrelated subprompt.
- Dataset/source and exact revision: `openai/grade-school-math`, commit
  `3101c7d5072418e28b9008a6636bde82a006892c`; 7,473 train and 1,319 test
  examples. [Official repository](https://github.com/openai/grade-school-math/tree/3101c7d5072418e28b9008a6636bde82a006892c).
- License/access: MIT repository license; public Git access. Preserve the
  source license and record any mirror revision separately.
- Splits: train and test; no supplied validation split. A validation subset
  would have to be carved from train before prompt generation.
- Ground truth: final answer embedded after `####`, with worked solutions.
- Evaluator implementation: official `grade_school_math/dataset.py`, same
  source commit; it extracts the final answer, removes commas, and compares
  exact normalized strings.
- Raw metrics/direction: `exact_match` in `{0,1}`, higher is better; retain
  parser status and extracted answer as raw fields.
- Determinism: deterministic CPU scoring; generation remains potentially
  stochastic, so primary model decoding must be separately frozen.
- Ambiguity: only the last/marked `####` answer is used; formatting, units,
  alternate equivalent forms, and an absent marker can be mishandled. Exact
  final-answer correctness does not establish solution validity.
- Unscorable: missing required target, absent/unparseable answer under the
  declared extraction rule, or evaluator error; distinguish evaluator failure
  from an output that is merely wrong.
- Leakage risk: public training and test data are widely reproduced and may
  be present in pretraining; source-instance and near-duplicate grouping are
  required.
- Approximate evaluation cost: one lightweight parse/compare per output; CPU
  cost is negligible relative to generation, making repeated schedules cheap.
- Repeated-schedule suitability: high for a pilot and atomic component; lower
  scientific difficulty and contamination resistance limit its role as the
  only numeric family.

### Numeric: MATH

- Component type: competition mathematics with proof-style solutions; atomic
  exact-answer reasoning at substantially higher difficulty than GSM8K.
- Scientific role: broader primary numeric component for sensitivity across
  algebra, counting, geometry, number theory, and other subdomains.
- Coherent composite support: native items are atomic. Cross-family composition
  needs an explicit shared scenario and separate final-answer fields.
- Dataset/source and exact revision: `hendrycks/math`, commit
  `985bdc1696e88e8643f081a0ff4719da39f2ae2a`; 7,500 train and 5,000 test
  items, with no supplied validation split. [Official repository](https://github.com/hendrycks/math/tree/985bdc1696e88e8643f081a0ff4719da39f2ae2a).
- License/access: MIT repository license; public access. Check any mirror or
  extracted artifact terms before redistribution.
- Splits: train and test only; validation must be declared and carved before
  deriving templates or composites.
- Ground truth: target answer and worked solution, represented as normalized
  LaTeX-compatible answer strings.
- Evaluator implementation: repository `modeling/math_equivalence.py` and
  its evaluation scripts at the pinned commit. [Evaluator source](https://github.com/hendrycks/math/blob/985bdc1696e88e8643f081a0ff4719da39f2ae2a/modeling/math_equivalence.py).
- Raw metrics/direction: `equivalent`/accuracy in `{0,1}`, higher is better;
  retain extracted answer, normalization trace, and evaluator status.
- Determinism: deterministic local equivalence checking when dependencies and
  timeout settings are fixed; no stochastic judge is required.
- Ambiguity: extraction commonly searches for a final boxed/fbox expression;
  LaTeX normalization and symbolic equivalence can accept or reject forms
  unexpectedly. Full solution correctness is not measured by final answer.
- Unscorable: no extractable answer, evaluator timeout/error, or missing
  target; do not convert parser failure to zero without a separate status.
- Leakage risk: public benchmark and solution text are contamination-prone;
  group source items, variants, and derived composites together.
- Approximate evaluation cost: more parsing and symbolic work than GSM8K but
  still CPU-cheap compared with model generation; repeated schedules are
  feasible for a compact subset and costlier for all 5,000 test items.
- Repeated-schedule suitability: high evaluator reliability and useful
  difficulty; exact subset and validation policy remain human decisions.

### Numeric: MATH-500

- Component type: 500 curated MATH problems; atomic harder numeric reasoning.
- Scientific role: compact development or calibration set for evaluator and
  prompt design, not a replacement for a frozen broad final test.
- Coherent composite support: native items are atomic; cross-family composites
  must be generated only after source split assignment.
- Dataset/source and exact revision: `openai/prm800k`, `math_splits/test.jsonl`,
  repository commit `7ecc794703b2877f63226f2477a49b34f9b25163`; the canonical
  LFS artifact SHA-256 is
  `35dc41080a3680858b27fa7e0533d2d547825316fc5dafe5d316f4ccc5a06132`.
  [PRM800K source](https://github.com/openai/prm800k/tree/7ecc794703b2877f63226f2477a49b34f9b25163).
- License/access: repository license and Git LFS access apply; pin the LFS
  object and retain its checksum in the manifest.
- Splits: test-only 500-item artifact; no train or validation split supplied.
- Ground truth: final mathematical answer and PRM800K grading annotations.
- Evaluator implementation: `prm800k/grading/grader.py` and
  `math_normalize.py` at the pinned repository revision.
- Raw metrics/direction: binary answer equivalence in `{0,1}`, higher is
  better; retain normalization and parse outcomes.
- Determinism: deterministic local grading when the dependency environment is
  pinned; evaluator dependencies do not provide a complete lock by default.
- Ambiguity: LaTeX/SymPy normalization and extraction of the final answer can
  disagree with a human proof judgment; no separate official unscorable field
  is provided.
- Unscorable: malformed/missing target, no extractable answer, or grader error;
  record each reason explicitly.
- Leakage risk: curated public benchmark likely overlaps MATH training or
  model pretraining; do not use it as an independent final test if related
  MATH sources cross splits.
- Approximate evaluation cost: CPU-cheap for 500 items; symbolic dependencies
  make it heavier than string exact match but suitable for many schedules.
- Repeated-schedule suitability: very high for pilot and validation; limited
  sample size and test-only provenance make it unsuitable as the sole final
  numeric population.

### Numeric: RIMO-N

- Component type: 335 high-difficulty mathematical reasoning problems.
- Scientific role: optional stress test for tail difficulty, not a first-suite
  primary component.
- Coherent composite support: native items are atomic; no cross-family
  composition protocol is supplied.
- Dataset/source and exact revision: official `ziye2chen/RIMO` commit
  `af7cb3d5e9b01fed7ccf23cdc6371762c1f1c6db`; Hugging Face artifact revision
  `a6fb235...` must be pinned in any later use. [Official repository](https://github.com/ziye2chen/RIMO/tree/af7cb3d5e9b01fed7ccf23cdc6371762c1f1c6db).
- License/access: dataset card states Apache-2.0; public access subject to
  the pinned artifact terms.
- Splits: no complete train/validation/test split supplied; 335-item release.
- Ground truth: final boxed mathematical answers and problem statements.
- Evaluator implementation: no complete official evaluator; the repository
  extracts a final boxed answer but does not provide a sufficiently specified
  primary scoring package.
- Raw metrics/direction: no complete canonical raw metric registry; any
  exact-match wrapper would be a new evaluator and must not be silently
  treated as official.
- Determinism: extraction is deterministic, but evaluator equivalence and
  malformed-output policy are underspecified.
- Ambiguity: last-box extraction, answer normalization, and lack of a full
  evaluator make false negatives and unscorable cases hard to classify.
- Unscorable: evaluator cannot establish a valid target judgment under the
  incomplete official protocol.
- Leakage risk: public release and likely overlap with other math corpora;
  no split/group manifest is supplied.
- Approximate evaluation cost: generation dominates; a new wrapper would add
  low CPU cost but high scientific specification cost.
- Repeated-schedule suitability: low as a primary component; propose a
  narrowly scoped research dependency if this candidate is required.

### Code: HumanEval

- Component type: Python function synthesis evaluated by execution tests.
- Scientific role: small executable code component and historical comparability
  control.
- Coherent composite support: native tasks are atomic function contracts. A
  coherent composite would need a shared program interface and jointly needed
  tests, not concatenated functions.
- Dataset/source and exact revision: `openai/human-eval`, commit
  `6d43fb980f9fee3c892a914eda09951f772ad10`; 164 test-only problems.
  [Official repository](https://github.com/openai/human-eval/tree/6d43fb980f9fee3c892a914eda09951f772ad10).
- License/access: MIT; evaluator runs generated code in a sandbox and requires
  local execution access.
- Splits: test only; no train or validation split supplied.
- Ground truth: function signature, prompt, reference tests, and expected
  behavior encoded in the task tests.
- Evaluator implementation: `human_eval/execution.py` and evaluation scripts
  at the pinned commit; package setup version is 1.0.
- Raw metrics/direction: per-task `passed` Boolean and `result` status such
  as passed, failed, or timed out; aggregate pass@k is higher-is-better but
  must not replace raw task status.
- Determinism: execution scoring can be deterministic for a fixed completion,
  timeout, environment, and seed; generation and code behavior can vary.
- Ambiguity: official sandbox warns it is not a security boundary; timeout
  behavior and imports can differ by environment. Public prompts invite
  contamination.
- Unscorable: execution infrastructure failure, malformed completion that
  cannot be extracted, or timeout policy that cannot produce a declared status.
- Leakage risk: public benchmark is widely memorized; group prompt, tests, and
  derived variants together.
- Approximate evaluation cost: roughly one sandboxed execution per task per
  candidate output; 164 executions for a greedy pass, plus process startup.
- Repeated-schedule suitability: high operationally, but low coverage and
  fragile sandbox isolation argue for a stronger test suite.

### Code: HumanEval+ with EvalPlus

- Component type: HumanEval function synthesis with augmented hidden-style
  tests; atomic executable requirement.
- Scientific role: recommended compact primary code component because extra tests
  reduce overfitting to the original visible tests.
- Coherent composite support: native tasks remain atomic; a cross-family
  composite requires a new interface and tests that jointly exercise all
  required behaviors.
- Dataset/source and exact revision: HumanEval+ data release `v0.1.10`,
  commit `200defce9e3429d28ca215b6dd061c0f7f31c18b`; 164 tasks with base and
  extra tests. [EvalPlus project](https://github.com/evalplus/evalplus).
- License/access: EvalPlus release materials use Apache-2.0; retain the
  original HumanEval license and any task-specific terms.
- Splits: test-only; no train or validation split. Split any prompt variants
  before derived test generation.
- Ground truth: reference implementation plus base and augmented executable
  tests.
- Evaluator implementation: EvalPlus evaluator `v0.3.1`, commit
  `e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2`; retain separate base and extra
  statuses and failed-test indices.
  [EvalPlus release](https://github.com/evalplus/evalplus/releases/tag/v0.3.1).
- Raw metrics/direction: `base_pass`, `plus_pass`, per-test pass/fail and
  failed-test indices; pass rate is higher-is-better. No averaging across
  base and plus should hide a plus failure.
- Determinism: deterministic for fixed completion, pinned dependencies,
  timeout, and test order; execution still depends on the runtime environment.
- Ambiguity: special oracles and tolerances exist for some tasks; timeouts are
  approximately `max(1 second, 4 × reference runtime)` with a task-level
  timeout around 60 seconds. These settings must be frozen in the registry.
- Unscorable: completion extraction failure, evaluator/runtime error, timeout
  classified outside the declared pass/fail policy, or missing test result.
- Leakage risk: public prompts/tests and model-training contamination remain;
  augmented tests reduce test overfitting but do not solve contamination.
- Approximate evaluation cost: tens of thousands of test executions across all
  candidates and schedules; still CPU-feasible but materially costlier than
  numeric exact match.
- Repeated-schedule suitability: high evaluator reliability and good small-suite
  coverage; preferred primary code candidate.

### Code: MBPP+ with EvalPlus

- Component type: short Python program synthesis with multiple assertions;
  atomic executable requirement.
- Scientific role: complementary code style and broader task distribution.
- Coherent composite support: native tasks are atomic; composite construction
  needs a shared program contract and jointly necessary tests.
- Dataset/source and exact revision: MBPP+ release `v0.2.0`, commit
  `64fc4195b858a17cdfdb3324f0baf37939144e14`; 378 released tasks.
  [EvalPlus project](https://github.com/evalplus/evalplus).
- License/access: original MBPP data is CC BY 4.0 and code is Apache-2.0;
  retain both terms and the EvalPlus release terms.
- Splits: original MBPP task IDs define train 601–974, validation 511–600,
  test 11–510, and few-shot 1–10; MBPP+ release coverage is 378 tasks, so
  the exact final manifest must pin the mapping rather than assume all IDs.
- Ground truth: reference code and assertion tests, augmented by EvalPlus.
- Evaluator implementation: EvalPlus `v0.3.1`, commit
  `e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2`; retain per-test outcomes.
- Raw metrics/direction: base/plus pass, per-test pass/fail, and failed-test
  indices; higher pass rate is better; do not average away plus failures.
- Determinism: deterministic for fixed completion and pinned execution
  environment, but task-specific oracles and timeouts must be frozen.
- Ambiguity: task-specific tests/oracles, release task selection, and the
  relationship between original and augmented tests can change results.
- Unscorable: extraction, runtime, timeout, or missing-test failures under the
  declared policy; retain excluded/unscorable counts.
- Leakage risk: public prompts, reference tests, and code are contamination
  risks; group original task, augmented tests, and all variants.
- Approximate evaluation cost: tens of thousands of test executions across
  candidates and schedules; higher than HumanEval+ for the released suite.
- Repeated-schedule suitability: good complement; added coverage may be worth
  the cost, but it should not force a benchmark zoo.

### Code: APPS

- Component type: programming problems with input/output tests; atomic program
  synthesis ranging from introductory to competitive programming.
- Scientific role: later coverage or stress component, not recommended for the
  minimum decisive suite because evaluator and source choices are more complex.
- Coherent composite support: native problems are atomic; a coherent composite
  needs a shared input/output contract and jointly necessary tests.
- Dataset/source and exact revision: `hendrycks/apps`, commit
  `362aedc3c71cd7d9bd2fc96a6c80e11dbc38c7a5`; 5,000 train and 5,000 test
  problems. [Official repository](https://github.com/hendrycks/apps/tree/362aedc3c71cd7d9bd2fc96a6c80e11dbc38c7a5).
- License/access: repository and mirrored dataset terms are not uniform enough
  to treat a mirror label as authoritative; pin and review official terms
  before use. This unresolved access ambiguity is itself a reason to defer it.
- Splits: train and test; no supplied validation split.
- Ground truth: input/output test cases and expected program behavior.
- Evaluator implementation: official `eval/test_one_solution.py` at the pinned
  repository revision.
- Raw metrics/direction: per-test statuses including True/False and timeout or
  execution-error sentinels; Test Case Average and Strict Accuracy are higher
  is better. Preserve raw status vectors.
- Determinism: test execution can be deterministic after pinning runtime and
  timeout, but the evaluator has fallback behavior and environment sensitivity.
- Ambiguity: timeout fallback vectors, language/runtime setup, and sentinel
  meanings complicate denominator and unscorable handling.
- Unscorable: missing executable, timeout/error sentinel, malformed output, or
  evaluator failure; status semantics must be frozen before use.
- Leakage risk: public solutions and problem statements create severe
  contamination risk; source and solution grouping is required.
- Approximate evaluation cost: potentially many tests per problem and much more
  process/runtime cost than exact-match tasks.
- Repeated-schedule suitability: technically repeatable but expensive and noisy;
  defer unless a later research ticket resolves licensing and evaluator policy.

### Fixed-context QA: SQuAD 2.0

- Component type: extractive answer question answering from supplied paragraphs,
  including answerable and unanswerable questions.
- Scientific role: deterministic answer-only control for context grounding;
  not sufficient alone to establish evidence selection.
- Coherent composite support: each item is atomic. Multi-field composites need
  a shared context and a new jointly necessary answer/evidence contract.
- Dataset/source and exact revision: canonical `rajpurkar/SQuAD` evaluator/data
  commit `09eac9971f46889fa057ff2c870bf71092ba9d55`; train JSON SHA-256
  `68dcfbb9...` and dev JSON SHA-256 `80a522...` must be recorded in any
  final manifest. [Official repository](https://github.com/rajpurkar/SQuAD/tree/09eac9971f46889fa057ff2c870bf71092ba9d55).
- License/access: CC BY-SA 4.0; public download. Hidden official test is
  server-evaluated, so dev must be used for a local frozen evaluation.
- Splits: train/dev, with hidden test service; no local public test labels.
- Ground truth: answer spans or declared no-answer labels; no evidence-support
  labels beyond the paragraph context.
- Evaluator implementation: official `evaluate-v2.0.py` at the pinned commit.
- Raw metrics/direction: `exact`, `f1`, `HasAns_exact`, `HasAns_f1`,
  `NoAns_exact`, and `NoAns_f1`, percentages from 0 to 100, higher is better.
  Missing predictions must remain visible because the official script can omit
  them from some denominators.
- Determinism: deterministic normalization and scoring on CPU.
- Ambiguity: answer normalization, no-answer thresholding, and missing-prediction
  denominator behavior; answer EM/F1 does not prove context use.
- Unscorable: missing target, invalid prediction JSON, absent prediction under
  the chosen policy, or evaluator error; report denominator impact explicitly.
- Leakage risk: public train/dev and paragraphs are widely used; group context,
  question, answer variants, and any generated paraphrases.
- Approximate evaluation cost: seconds to minutes on CPU for about 11,873 dev
  items; repeated scoring is cheap relative to generation.
- Repeated-schedule suitability: high as a control, low as the sole
  evidence-grounded primary component.

### Fixed-context QA: HotpotQA distractor

- Component type: multi-hop question answering with supplied paragraphs and
  supporting-fact labels; distractor setting has 2 support and 8 distractor
  paragraphs.
- Scientific role: evidence-grounded QA component with separately scorable
  answer and support requirements.
- Coherent composite support: native multi-hop questions are coherent; an
  answer-plus-support output has jointly necessary fields.
- Dataset/source and exact revision: `hotpotqa/hotpot` commit
  `3635853403a...`; use `hotpot_train_v1.1` and the pinned distractor dev
  artifact. The evaluator source revision is `fa3a36370899e1d85822de61e58c85ea19993154`.
  [Official repository](https://github.com/hotpotqa/hotpot).
- License/access: data CC BY-SA 4.0; code Apache-2.0; public download.
- Splits: train and distractor/fullwiki dev/test variants; use distractor
  fixed-context data and pin the exact artifact. Hidden test labels are not
  assumed available locally.
- Ground truth: answer string plus supporting paragraph/sentence facts.
- Evaluator implementation: official HotpotQA evaluator at the pinned
  evaluator revision.
- Raw metrics/direction: answer EM/F1/precision/recall, support EM/F1/precision/
  recall, and joint scores, all fractions in [0,1], higher is better.
- Determinism: deterministic token normalization and set scoring on CPU.
- Ambiguity: support scoring is label-set comparison, not full logical
  entailment; missing predictions use the full intended denominator; distractor
  context and fullwiki retrieval are different tasks.
- Unscorable: malformed prediction, missing answer/support field, missing gold
  item, or evaluator error; retain answer-scored but support-unscored status.
- Leakage risk: public multi-hop questions and source paragraphs; group all
  supporting context, variants, and derived composites.
- Approximate evaluation cost: linear CPU scoring over a few thousand items;
  answer and support fields are cheap to score repeatedly.
- Repeated-schedule suitability: high if the fixed distractor artifact and
  output schema are frozen; stronger than SQuAD for evidence, smaller and
  simpler than MuSiQue.

### Fixed-context QA: MuSiQue-Full v1.0

- Component type: 2–4 hop compositional QA with supplied paragraphs, answer
  labels, support paragraphs, and answerable/unanswerable contrasts in Full.
- Scientific role: recommended primary fixed-context component because the
  dataset's intended task is coherent composition and evidence use.
- Coherent composite support: native multi-hop questions are coherent and
  jointly require their hops; Full also supplies answerability contrasts.
- Dataset/source and exact revision: MuSiQue v1.0 archive from the official
  Google Drive release, owner repository commit
  `922ac98...`; answerable split paper counts are 19,938 train, 2,417 dev,
  and 2,459 test. The official repository also provides leakage-control files
  such as `dev_test_singlehop_questions_v1.0.json`. [Official repository](https://github.com/StonyBrookNLP/musique).
- License/access: dataset CC BY 4.0; official archive access and Google Drive
  download must be recorded by immutable archive checksum before use.
- Splits: train/dev/test for answerable (`Ans`) and Full variants; preserve
  the supplied single-hop leakage-control grouping and split before variants.
- Ground truth: answer text, supporting paragraph indices, and for Full the
  answerability/contrast structure.
- Evaluator implementation: `evaluate_v1.0.py`, commit
  `24cc5b297acc2abfc5fb3d0becb6ef7b73d03717`.
  [Evaluator source](https://github.com/StonyBrookNLP/musique/blob/24cc5b297acc2abfc5fb3d0becb6ef7b73d03717/evaluate_v1.0.py).
- Raw metrics/direction: `answer_em`, `answer_f1`, `support_f1`, and Full
  `group_answer_sufficiency_f1` and `group_support_sufficiency_f1`, fractions
  in [0,1], higher is better. Retain answer and support scores separately.
- Determinism: deterministic normalization and set/F1 scoring on CPU when
  JSONL ordering and dependency versions are pinned.
- Ambiguity: support F1 is paragraph-index set scoring, not sentence-level or
  full logical entailment; Full evaluation requires matching JSONL ordering and
  length and can assert on malformed or missing predictions.
- Unscorable: malformed output, missing answer/support field, mismatched paired
  ordering/length, missing gold, or evaluator error; never silently drop a
  failed Full pair.
- Leakage risk: official paper and repository provide explicit single-hop
  overlap controls; retain those groups and keep all source paragraphs,
  paraphrases, and composites in one split.
- Approximate evaluation cost: linear CPU scoring for roughly 25,000 answerable
  items before any subset decision; repeated scoring is cheap, but model
  generation dominates.
- Repeated-schedule suitability: high evaluator value for fixed-context
  composition; full-scale repeated schedules may require a predeclared subset
  to stay within the first experiment budget.

## Evaluator and protocol implications

- Primary evaluators should be deterministic and versioned by repository commit,
  dependency lock, parser version, test cases, timeout, and random seed policy.
- Store raw evaluator outputs, extraction traces, per-test statuses, and
  exclusion/unscorable reasons. Aggregate metrics must not replace them.
- Numeric exact/equivalence, code execution, and QA answer/support scores have
  different ranges and directions; the registry must preserve native raw values
  and declare whether higher is better.
- A component may be filtered before model execution only for a source-defined
  validity or leakage reason independent of model outputs. Favorable INT4, INT8,
  or BF16 outcomes must never determine filtering.
- Multiple metrics should remain distinct unless a later decision explicitly
  declares a deterministic aggregation. No LLM judge is a sole primary
  evaluator in this initial go/no-go study.
- BF16 comparison and KL divergence may be auxiliary/reference signals; neither
  substitutes for absolute task quality.

## Provisional recommendation and open decisions

Use the evidence above to grill, in order, on suite purpose, priority, size,
ontology, request schema, family selection, composite construction, splits,
registry behavior, disagreement/unscorable policy, freeze policy, and
feasibility. The accepted purpose is recorded separately in the research spec;
the family, dataset, exact final manifest, and evaluator registry remain
unresolved until the user confirms them.

## Primary sources

- GSM8K repository and evaluator: https://github.com/openai/grade-school-math/tree/3101c7d5072418e28b9008a6636bde82a006892c
- MATH repository and equivalence evaluator: https://github.com/hendrycks/math/tree/985bdc1696e88e8643f081a0ff4719da39f2ae2a
- PRM800K repository and grading code: https://github.com/openai/prm800k/tree/7ecc794703b2877f63226f2477a49b34f9b25163
- RIMO repository: https://github.com/ziye2chen/RIMO/tree/af7cb3d5e9b01fed7ccf23cdc6371762c1f1c6db
- HumanEval repository: https://github.com/openai/human-eval/tree/6d43fb980f9fee3c892a914eda09951f772ad10
- EvalPlus project and release: https://github.com/evalplus/evalplus/releases/tag/v0.3.1
- APPS repository: https://github.com/hendrycks/apps/tree/362aedc3c71cd7d9bd2fc96a6c80e11dbc38c7a5
- SQuAD repository/evaluator: https://github.com/rajpurkar/SQuAD/tree/09eac9971f46889fa057ff2c870bf71092ba9d55
- HotpotQA repository: https://github.com/hotpotqa/hotpot
- MuSiQue repository and evaluator: https://github.com/StonyBrookNLP/musique/tree/24cc5b297acc2abfc5fb3d0becb6ef7b73d03717

## Source-verification addendum

The pinned evaluator sources were checked again after the registry decision.
This addendum supersedes any earlier shorthand that conflicts with the source.

- MATH extraction is in the repository extraction helper, separate from
  math_equivalence.py. The pinned equivalence implementation normalizes strings
  and applies exact normalized-string equality; it is not symbolic equivalence.
  Missing extraction and evaluator exceptions must be represented by the
  adapter's normalized status rather than silently treated as a valid match.
  [equivalence source](https://github.com/hendrycks/math/blob/985bdc1696e88e8643f081a0ff4719da39f2ae2a/modeling/math_equivalence.py#L69-L152),
  [extraction source](https://github.com/hendrycks/math/blob/985bdc1696e88e8643f081a0ff4719da39f2ae2a/modeling/dataset/util.py#L5-L41).
- EvalPlus emits native pass, fail, and timeout outcomes; candidate exceptions
  are failures and process timeouts retain timeout status. The pinned evaluator
  uses a max(1.0 seconds, 4 times reference runtime) per-test floor, and full
  per-test details require test_details=true. Its reliability guard is not a
  security sandbox, so external isolation and network policy must be pinned as
  separate run controls.
  [evaluation source](https://github.com/evalplus/evalplus/blob/e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2/evalplus/evaluate.py#L79-L124),
  [timeout source](https://github.com/evalplus/evalplus/blob/e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2/evalplus/eval/__init__.py#L87-L108),
  [sandbox warning](https://github.com/evalplus/evalplus/blob/e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2/evalplus/eval/utils.py#L102-L112).
- MuSiQue requires aligned prediction/gold rows and raises on missing or
  malformed fields. The adapter therefore classifies candidate schema failure
  before invoking the official evaluator, while input alignment or evaluator
  errors remain evaluator_error. Answer/support denominators and question-group
  sufficiency denominators are retained separately.
  [official evaluator](https://github.com/StonyBrookNLP/musique/blob/24cc5b297acc2abfc5fb3d0becb6ef7b73d03717/evaluate_v1.0.py#L18-L97),
  [group metrics](https://github.com/StonyBrookNLP/musique/blob/24cc5b297acc2abfc5fb3d0becb6ef7b73d03717/metrics/group.py#L23-L39).

## Feasibility source-count addendum

The bounded primary-source audit corrected the MuSiQue population description.
MuSiQue-Full v1.0 contains 49,628 rows: 39,876 train, 4,834 dev, and 4,918
test. The earlier approximately-25,000 figure described answerable rows and
must not be used as the Full-suite denominator.

For the accepted 804-request profile cap, the audit's smaller 300-request
illustration remains a useful lower-bound comparison but does not replace the
accepted cap. Its transparent example uses 75 MATH atomic rows, 60 HumanEval+
atomic rows, 100 MuSiQue rows representing 50 paired Full question groups, and
65 numeric-to-code composites. At S=8 it produces 2,400 model outputs and 3,720
component records before any additional baseline conditions.

Conservative evaluator envelopes for that illustration are approximately 1.6
single-worker CPU hours for MATH, 34.4 hours for HumanEval+ if every test phase
reaches its timeout bound, and 2.2 hours for MuSiQue under the registered
adapter timeout. These are bounds, not measurements; model-generation time,
hardware, and the eventual schedule count remain unmeasured.

The normalized-artifact storage estimate is approximately 40 MiB, or 55 MiB
with detailed code-test traces, for the 300-request illustration at S=8 under
the stated assumptions. The specification retains a deliberately conservative
1–3 GiB envelope for the larger accepted cap and S=8–16 range.

Primary sources: [MuSiQue paper](https://direct.mit.edu/tacl/article/doi/10.1162/tacl_a_00475/110996/MuSiQue-Multihop-Questions-via-Single-hop-Question),
[pinned MuSiQue repository](https://github.com/StonyBrookNLP/musique/tree/24cc5b297acc2abfc5fb3d0becb6ef7b73d03717),
[pinned HumanEval+ release](https://github.com/evalplus/humanevalplus_release/tree/200defce9e3429d28ca215b6dd061c0f7f31c18b).
