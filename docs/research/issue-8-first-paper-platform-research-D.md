# Issue #8 research subnote D: frozen data and evaluator provenance

Status: evidence packet only. This note verifies source metadata and source
code; it does not download benchmark data, install dependencies, run an
evaluator, inspect model outputs, inspect final-test results, or use a
leaderboard. `Directly verified` means checked against the cited primary URL or
source. `Documented` means already frozen by the accepted Issue #7 ledger or
normative specification. `Inferred; preflight required` is not closure evidence.

## Frozen source matrix

| Family | Frozen source and license | Evaluator availability | Split/data identity and checksum status |
| --- | --- | --- | --- |
| MATH | **Directly verified:** `hendrycks/math@985bdc1696e88e8643f081a0ff4719da39f2ae2a`; the commit exists and its README says the repository contains loaders/evaluation code and links the dataset distribution. The repository `LICENSE` is MIT. [commit](https://github.com/hendrycks/math/commit/985bdc1696e88e8643f081a0ff4719da39f2ae2a), [README](https://github.com/hendrycks/math/blob/985bdc1696e88e8643f081a0ff4719da39f2ae2a/README.md), [license](https://github.com/hendrycks/math/blob/985bdc1696e88e8643f081a0ff4719da39f2ae2a/LICENSE) | **Directly verified:** `modeling/math_equivalence.py` supplies the equivalence implementation; `modeling/eval_math_gpt.py` imports it. The loader reads JSON records with `problem`, `solution`, and source filename and uses a globbed local data root. [equivalence source](https://github.com/hendrycks/math/blob/985bdc1696e88e8643f081a0ff4719da39f2ae2a/modeling/math_equivalence.py), [loader](https://github.com/hendrycks/math/blob/985bdc1696e88e8643f081a0ff4719da39f2ae2a/modeling/dataset/MATH.py), [evaluation entry point](https://github.com/hendrycks/math/blob/985bdc1696e88e8643f081a0ff4719da39f2ae2a/modeling/eval_math_gpt.py) | **Documented:** Issue #7 froze 7,500 train and 5,000 test items, with validation carved from train before variants/composites. **Directly verified:** the pinned repository does not contain the benchmark JSON records or a release archive; its README points to the `qwedsacf/competition_math` Hugging Face distribution. That mirror currently exposes revision `e839825f9ec5c6cfa585c654a59610969ec13993`, but its card presents one converted `train` split, so it is not by itself a substitute for the frozen train/test identity. No SHA-256 archive/file checksum is published by the pinned source. [dataset card](https://huggingface.co/datasets/qwedsacf/competition_math) |
| HumanEval+ | **Directly verified:** `evalplus/humanevalplus_release@200defce9e3429d28ca215b6dd061c0f7f31c18b` exists and is the `bump to v0.1.10` commit. Its release repository is Apache-2.0; upstream HumanEval terms must also be retained. [frozen commit](https://github.com/evalplus/humanevalplus_release/commit/200defce9e3429d28ca215b6dd061c0f7f31c18b), [release license](https://github.com/evalplus/humanevalplus_release/blob/200defce9e3429d28ca215b6dd061c0f7f31c18b/LICENSE), [upstream HumanEval](https://github.com/openai/human-eval/blob/master/LICENSE) | **Directly verified:** EvalPlus evaluator `evalplus/evalplus@e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2` exists. Its loader hard-codes HumanEval+ `v0.1.10`, loads base and plus inputs, and the evaluator retains base/plus statuses and failed-test details. The pinned evaluator declares minimum dependencies rather than a lockfile. [evaluator commit](https://github.com/evalplus/evalplus/commit/e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2), [loader](https://github.com/evalplus/evalplus/blob/e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2/evalplus/data/humaneval.py), [evaluator](https://github.com/evalplus/evalplus/blob/e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2/evalplus/evaluate.py) | **Documented:** source is test-only; Issue #7 requires any project validation carve before variants. **Directly verified:** release `v0.1.10` publishes `HumanEvalPlus.jsonl.gz`, `HumanEvalPlus-OriginFmt.jsonl.gz`, `HumanEvalPlus-Mini.jsonl.gz`, and `HumanEvalPlus-NoExtreme.jsonl.gz`; the full EvalPlus asset is 925,932 bytes. The API reports `digest: null` for each asset. **Material identity nuance:** the annotated `v0.1.10` tag target is commit `68cd26d53a0dec69f85eafe1f82a2a74155a2bd6`; frozen commit `200def…` is its child and contains the release blobs. The manifest must record both the frozen commit and exact asset URL/name; SHA-256 is **unknown** until approved acquisition. [release](https://github.com/evalplus/humanevalplus_release/releases/tag/v0.1.10), [tag object](https://github.com/evalplus/humanevalplus_release/tree/68cd26d53a0dec69f85eafe1f82a2a74155a2bd6), [release commit tree](https://github.com/evalplus/humanevalplus_release/tree/200defce9e3429d28ca215b6dd061c0f7f31c18b) |
| MuSiQue-Full | **Directly verified:** official `StonyBrookNLP/musique@24cc5b297acc2abfc5fb3d0becb6ef7b73d03717` exists. The README states that MuSiQue is CC BY 4.0 and warns about seed-dataset leakage. [commit](https://github.com/StonyBrookNLP/musique/commit/24cc5b297acc2abfc5fb3d0becb6ef7b73d03717), [README](https://github.com/StonyBrookNLP/musique/blob/24cc5b297acc2abfc5fb3d0becb6ef7b73d03717/README.md) | **Directly verified:** `evaluate_v1.0.py` is present at the frozen commit and checks prediction/ground-truth length and ID order, then computes answer EM/F1, support F1, and Full answerability group-sufficiency metrics. [evaluator](https://github.com/StonyBrookNLP/musique/blob/24cc5b297acc2abfc5fb3d0becb6ef7b73d03717/evaluate_v1.0.py), [answer metric](https://github.com/StonyBrookNLP/musique/blob/24cc5b297acc2abfc5fb3d0becb6ef7b73d03717/metrics/answer.py), [support metric](https://github.com/StonyBrookNLP/musique/blob/24cc5b297acc2abfc5fb3d0becb6ef7b73d03717/metrics/support.py) | **Directly verified:** the official download script names the archive `musique_v1.0.zip` and uses Google Drive file ID `1tGdADlNjWFaHLeZZGShh2IRcpO6Lv24h`; the README says the archive contains Ans/Full train, dev, and test sets plus `dev_test_singlehop_questions_v1.0.json`. No SHA-256 checksum is published in the pinned README/script or repository metadata; checksum is **unknown** until approved acquisition. [download script](https://github.com/StonyBrookNLP/musique/blob/24cc5b297acc2abfc5fb3d0becb6ef7b73d03717/download_data.sh), [official archive URL](https://drive.google.com/file/d/1tGdADlNjWFaHLeZZGShh2IRcpO6Lv24h/view?usp=sharing) |

The accepted local specification records MuSiQue-Full as 49,628 rows (39,876
train, 4,834 dev, 4,918 test). This count is **Documented** by the accepted
Issue #7 ledger; it was not independently recounted here because doing so
would require downloading the archive, which this subtask forbids.

## Split, manifest, and leakage controls

The following are **Documented** by the accepted Issue #7 ledger and
`docs/research-spec.md`, not new decisions in this subnote:

1. Assign source instances to train, validation, IID-final, or
   held-out-composition-final before creating prompt variants, paraphrases, or
   cross-family composites. Every derivative inherits its source split.
2. The manifest must retain source dataset/revision, archive/file identity,
   checksum, split role, source IDs, evaluator commit and source files,
   adapter/parser, prompt/composition identity, and a leakage-group identity;
   hash the resulting split manifest before model-output runs.
3. A transitive leakage group includes source items, variants/paraphrases,
   shared evidence/documents, code prompts/tests, content-bearing templates,
   and derived composites. Exact normalized duplicates, text-Jaccard >= 0.90
   duplicates, and code AST/test-hash duplicates cannot cross splits.
4. MuSiQue's own README specifically releases
   `dev_test_singlehop_questions_v1.0.json` and instructs users not to use
   those single-hop IDs if using the seed datasets. The project must preserve
   and apply that exclusion; fixed supplied context does not authorize seed
   corpus reuse.
5. Registry, evaluator, prompt, split, and leakage identities are frozen
   before validation/model-output runs; the final-test manifest is frozen
   before calibration, threshold, codebook, predictor, or router tuning. No
   final-test output/result/leaderboard can inform this selection.

## Non-final calibration and capability-preflight allowance

This is a mapping of the already accepted split roles, not a new split choice:

- **MATH:** use only the predeclared train partition and its source-disjoint
  validation carve for fitting/calibration. A neutral capability preflight may
  use a train/validation item or separately authored neutral prompt that is
  recorded outside the final manifest. The original test partition is not
  calibration or preflight data.
- **HumanEval+:** there is no official train/dev split. Partition the 164
  source tasks into project train/validation/final roles before generating any
  variants or composites. Calibration and preflight may use only tasks assigned
  to non-final roles; the asset's base/plus tests and all task IDs remain part
  of the leakage group. The accepted 164-task first-profile cap does not permit
  selecting a model/backend from final-test outcomes.
- **MuSiQue:** use only source-disjoint train/dev-derived requests for fitting,
  calibration, and neutral capability preflight. The accepted 2/3-hop native
  requests are the non-final/native calibration population; 4-hop requests and
  numeric-to-code composites are held-out-composition final populations and
  are not preflight selection data. Apply the released seed single-hop ID
  exclusion before any seed-data reuse.

No evaluator was run, no archive was downloaded, and no checksum was computed
in this subtask. Exact archive/file checksums, extracted file lists, row counts,
schema validation, dependency-lock hashes, and final split-manifest hashes are
**Inferred; preflight required** or **Unknown**, and must be retained as
immutable artifacts after approved acquisition.

## Source conclusion

The three frozen evaluator paths are publicly available and source-pinned.
MATH has no archive identity in its pinned repository; HumanEval+ has an
explicit release asset but no published digest and a tag/commit relationship
that must be recorded; MuSiQue has an explicit `musique_v1.0.zip` Google Drive
identity but no published checksum. This subnote supports later manifest
construction and approved preflight; it does not close Issue #8 or select the
model/backend/runtime/hardware tuple.
