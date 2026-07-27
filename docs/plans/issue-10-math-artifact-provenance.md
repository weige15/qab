# Issue #10 — MATH artifact provenance plan

## Scientific objective

Determine which immutable, publicly retrievable MATH artifact realizes the
accepted 7,500-train/5,000-test source split, and identify the immutable
metadata, bytes, schema, split, and source-instance manifest fields that must
be frozen for reproducible use by issue #8.

## Assumptions

- The accepted issue #7 evaluator and issue #4 split/change-control semantics
  are fixed inputs, not subjects of this research.
- The authoritative research-spec revision is
  `1acbd40de0bf3fdda0b6162c76b3a58bb4716e7d`.
- No model, inference, GPU, or final-test output will be used.
- Artifact downloads are limited to the minimum required files and remain
  below the 100 MB task limit.

## Proposed design

Trace the original MATH paper and `hendrycks/math` history, inspect Berkeley
archive metadata if recoverable, compare Hugging Face current main with the
specified historical revision, and download only the smallest necessary data
files after recording expected sizes and free disk space. Verify file identity,
hashes, row counts, schema, overlap, and split correspondence. Record verified,
inferred, and unknown findings in one report.

## Affected files

- `docs/research/issue-10-math-artifact-provenance.md`
- This plan file; no changes to `docs/research-spec.md`.

## Validation approach

- Use primary-source paper, repository, commit, archive, and Hugging Face
  metadata.
- Use independent local byte inspection only for required row, schema, split,
  overlap, and digest checks.
- Re-run the exact documented verification commands and inspect the resulting
  metadata before handoff.

## Risks

- The original Berkeley archive may be unavailable or lack a recoverable
  checksum.
- A mirror’s historical files may preserve counts without proving byte- or
  membership-level equivalence to the original release.
- Hugging Face storage metadata may expose LFS/Xet identifiers without making
  a public content hash equivalent to the downloaded-file SHA-256.

## Milestones

1. Claim ticket and establish authoritative repository context.
2. Trace primary-source provenance and immutable revision/file metadata.
3. Preflight disk/size limits; download only necessary artifact files.
4. Verify counts, schema, hashes, overlap, and split correspondence.
5. Write and inspect the report; post the evidence summary and resolve only
   issue #10 if the repository workflow permits.

## Decisions during implementation

- `gh` is unavailable in the environment; issue assignment was performed with
  the configured first-party GitHub connector’s equivalent assignee endpoint.
- No issue #8 decision will be made in this ticket.
