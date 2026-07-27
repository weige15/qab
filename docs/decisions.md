# Scientific Decisions

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
