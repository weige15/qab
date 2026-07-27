# Issue #10 — MATH artifact provenance

**Research date:** 2026-07-28 (Asia/Taipei)  
**Repository checkout:** `qab@538ea8c336b72b9507badb6b306cc32f86d5dceb`  
**Scope:** provenance and reproducibility only; no model, inference, GPU, or
final-test output was used. `docs/research-spec.md` was not modified.

## Answer in brief

The immutable artifact that directly exposes the accepted source split is
`qwedsacf/competition_math@d9afe06952835e34b5a148b90043bc04aa09e519`, using
these two files:

| source split | file | bytes | SHA-256 / HF LFS OID |
| --- | --- | ---: | --- |
| train | `data/train-00000-of-00001-48a8135a22c541f2.parquet` | 2,991,536 | `c0cb0bb1c60d04e9f38e65059a1fd93685efb1b4602912a761257cab09d476e2` |
| test | `data/test-00000-of-00001-8381d31b2d187522.parquet` | 1,855,255 | `79f372afea6bedd226750eab23ba54dddede047670446d85178e3e5d0627c191` |

The historical revision’s first-party metadata names the two files, and its
dataset card declares a 7,500-row train split. Independent Parquet inspection
finds 7,500 train rows and 5,000 test rows, the expected four fields, no nulls,
no exact duplicate rows within either split, and no exact overlap between the
two splits.

The current default branch, `e839825f9ec5c6cfa585c654a59610969ec13993`, is
not an adequate canonical split reference by itself. It exposes one
`data/train-00000-of-00001-7320a6f3aba8ebd2.parquet` file with 12,500 rows and
no train/test split field. The downloaded current-main bytes are, however,
exactly the historical train rows followed by the historical test rows under
the canonical four-field comparison below. This establishes content
correspondence between the two HF states, not independent proof that either
state is byte-equivalent to the unavailable Berkeley `MATH.tar` release.

The scientifically defensible recommendation is therefore to freeze the
historical HF revision and both file digests, while recording the original
Berkeley-split equivalence as **strongly supported but not cryptographically
proved**. Do not freeze current main as the source-split identity.

## 1. Provenance chain

### 1.1 Original paper

The original paper, [*Measuring Mathematical Problem Solving With the MATH
Dataset*](https://arxiv.org/abs/2103.03874), describes MATH as 12,500
competition mathematics problems, each with a step-by-step solution. Its
dataset section states explicitly that MATH contains **7,500 training and
5,000 test problems** and describes the seven subjects and five difficulty
levels. This is the primary source for the target counts, not a claim about a
particular later serialization.

### 1.2 Original repository and the pinned revision

The upstream [MATH repository](https://github.com/hendrycks/math) is the
authors’ loader/evaluation repository and is MIT-licensed. At the pinned
revision [`985bdc1696e88e8643f081a0ff4719da39f2ae2a`](https://github.com/hendrycks/math/commit/985bdc1696e88e8643f081a0ff4719da39f2ae2a):

- the commit message is `Update README.md`;
- the only changed file is `README.md` (one line added and one removed);
- the README link changes from the former Berkeley URL
  `https://people.eecs.berkeley.edu/~hendrycks/MATH.tar` to the HF dataset
  `https://huggingface.co/datasets/qwedsacf/competition_math`;
- the repository tree contains loaders/evaluation code and lists of auxiliary
  data files, but does not contain the MATH benchmark JSON files or a MATH
  archive; and
- the pinned README and LICENSE blobs are respectively
  `28a259d9230c06f00325cd6f88c11b304daa5e36` (1,345 bytes) and
  `2884bd5e0ebe3af32f148e407ca9648153b6f2fa` (1,070 bytes).

The immediate parent is
[`357963a7f5501a6c1708cf3f3fb0cdf525642761`](https://github.com/hendrycks/math/tree/357963a7f5501a6c1708cf3f3fb0cdf525642761), whose README still points
to Berkeley. Therefore the known hypothesis is verified: the pinned upstream
revision changes the acquisition link, but does not pin the dataset bytes,
archive checksum, split manifest, or HF revision.

The pinned loader reads JSON objects and requires `problem` and `solution`.
The pinned evaluation entry point uses `./MATH/test/*/*.json`, providing
first-party evidence for the original archive’s test-directory convention.
The repository does not publish a byte hash for `MATH.tar`.

### 1.3 Berkeley archive access

The former first-party URL is recorded above and in the parent README. A
metadata-only `curl -fsSIL` request on 2026-07-28 returned HTTP 403 from the
Berkeley server, with no usable `Content-Length`, checksum, archive listing, or
redirect. No Berkeley bytes were downloaded. The archive’s historical
existence and URL are verified; its current byte identity is not recoverable
from this check.

### 1.4 Hugging Face historical revision

The HF API reports public, non-gated dataset revision
`d9afe06952835e34b5a148b90043bc04aa09e519`, created by `qwedsacf`, with the
two split file names above. Its historical README front matter reports the
train features and `num_examples: 7500`, `download_size: 2991536`, and
`dataset_size: 5984772` (the latter is the Arrow logical size, not the file
byte size). The historical revision is the first-party immutable source used
for the independent byte checks in this report.

### 1.5 Hugging Face current main

The HF API reports current main as
`e839825f9ec5c6cfa585c654a59610969ec13993`. Its tree contains one Parquet
file under `data/` and the current dataset card describes the MATH fields, but
it does not expose separate train/test files or a split column. The current
revision’s history shows the split files were later replaced by a combined
train-named Parquet file. The current file’s row content is exactly the
historical 7,500-train + 5,000-test sequence, as independently verified below.

## 2. Revision and file identity

The HF tree API identifies three different layers of identity for each Parquet
file:

- the tree `oid` is the Git blob identity for the LFS pointer;
- `lfs.oid` is the advertised content SHA-256 and is the value matched by the
  downloaded file’s SHA-256; and
- `xetHash` is the Xet content identifier exposed by the HF API and response
  headers.

The repository’s `.gitattributes` marks `*.parquet` as Git LFS content. The
metadata and local byte hashes are:

| HF revision | file | Git tree `oid` | LFS OID and local SHA-256 | Xet hash | size |
| --- | --- | --- | --- | --- | ---: |
| `d9afe06952835e34b5a148b90043bc04aa09e519` | `data/train-00000-of-00001-48a8135a22c541f2.parquet` | `61fcdd7c12bf7f62e55b02d2d9fe92b8da41ff29` | `c0cb0bb1c60d04e9f38e65059a1fd93685efb1b4602912a761257cab09d476e2` | `60f84c81f9f962484e1f5224ee7e51f6c0f62fba6c21644b699ae8a7a5ca3c8b` | 2,991,536 |
| `d9afe06952835e34b5a148b90043bc04aa09e519` | `data/test-00000-of-00001-8381d31b2d187522.parquet` | `95f9811bc412c8bddcf16174e58b9d920846e078` | `79f372afea6bedd226750eab23ba54dddede047670446d85178e3e5d0627c191` | `2b9528a90d449a0a859eb920980798a92fe51958f74a5f87af6454ef0d63cf1d` | 1,855,255 |
| `e839825f9ec5c6cfa585c654a59610969ec13993` | `data/train-00000-of-00001-7320a6f3aba8ebd2.parquet` | `db0dc902ccc029afdc866dd5015821627d0c5ea3` | `2325458edc03d786939ee9e1e5795efb9e2480247b6e1ed2c51f41bea7369c6a` | `25032e7230e89efcaccff6d670bce9f074cfa8043bef3027717f8a90a973c82e` | 4,848,345 |

The download response headers independently returned the same revision, linked
size, LFS OID, and Xet hash. The three files total **9,695,136 bytes**, well
below the 100 MB task limit. Their locally computed SHA-256 digests matched
the LFS OIDs exactly.

Primary metadata links:

- [historical HF tree API](https://huggingface.co/api/datasets/qwedsacf/competition_math/tree/d9afe06952835e34b5a148b90043bc04aa09e519?recursive=true&expand=false)
- [current HF tree API](https://huggingface.co/api/datasets/qwedsacf/competition_math/tree/main?recursive=true&expand=false)
- [historical HF dataset metadata](https://huggingface.co/api/datasets/qwedsacf/competition_math/revision/d9afe06952835e34b5a148b90043bc04aa09e519)
- [current HF dataset metadata](https://huggingface.co/api/datasets/qwedsacf/competition_math)
- [HF commit history](https://huggingface.co/api/datasets/qwedsacf/competition_math/commits/main?limit=100)
- [historical file](https://huggingface.co/datasets/qwedsacf/competition_math/blob/d9afe06952835e34b5a148b90043bc04aa09e519/data/train-00000-of-00001-48a8135a22c541f2.parquet)
- [historical test file](https://huggingface.co/datasets/qwedsacf/competition_math/blob/d9afe06952835e34b5a148b90043bc04aa09e519/data/test-00000-of-00001-8381d31b2d187522.parquet)
- [current combined file](https://huggingface.co/datasets/qwedsacf/competition_math/blob/e839825f9ec5c6cfa585c654a59610969ec13993/data/train-00000-of-00001-7320a6f3aba8ebd2.parquet)

## 3. Independently verified row counts and schema

All three files were read with `pyarrow.parquet` 24.0.0. The Parquet footer
row count and fully read table row count agreed:

| artifact | Parquet rows | rows read | row groups | columns and types | nulls | exact duplicate rows |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| current combined | 12,500 | 12,500 | 13 | `problem:string`, `level:string`, `type:string`, `solution:string` | 0 | 0 |
| historical train | 7,500 | 7,500 | 8 | same four columns, same order/types | 0 | 0 |
| historical test | 5,000 | 5,000 | 5 | same four columns, same order/types | 0 | 0 |

All files report `created_by=parquet-cpp-arrow version 10.0.1`. The historical
HF card’s declared four features match the independent schema. There is no
explicit split column in any of these Parquet files; the split is represented
by the immutable revision and file path.

## 4. Duplicate and overlap checks

For every row, I constructed canonical JSON from the four fields in this exact
order-independent form:

```text
json.dumps(
  {"problem": row["problem"], "level": row["level"],
   "type": row["type"], "solution": row["solution"]},
  ensure_ascii=False, sort_keys=True, separators=(",", ":")
).encode("utf-8")
```

The per-row SHA-256 of those bytes was used only for deterministic comparison.
Results:

- historical train: 7,500 unique canonical rows; 0 within-split duplicates;
- historical test: 5,000 unique canonical rows; 0 within-split duplicates;
- train/test exact canonical intersection: 0;
- current combined unique canonical rows: 12,500;
- current minus historical union: 0;
- historical union minus current: 0; and
- current row order equals historical train followed by historical test.

This is an exact field-content check, not a semantic near-duplicate or
solution-leakage analysis. Near duplicates, shared source questions, and
external contamination remain outside what can be established from these
three files alone.

## 5. Stable source-instance identifier strategy

Freeze the source identity independently of Parquet row order:

```text
record_sha256 = SHA256(canonical_json(problem, level, type, solution))
source_instance_id = "math.v1:" + record_sha256
```

The manifest must retain, for every row:

```text
dataset_id, dataset_revision, split, file, row_index,
source_instance_id, record_sha256
```

`source_instance_id` is content-stable across a storage conversion or row
reordering. `dataset_revision`, `split`, `file`, and `row_index` are retained
as provenance coordinates and must not be replaced by the content ID. A
manifest builder must reject duplicate `source_instance_id` values within a
split and reject an ID appearing in both source splits.

Using the canonical JSONL records sorted in source-file order, with sorted JSON
keys, compact separators, UTF-8, and one trailing newline per record, the
historical revision produces these reproducibility digests:

| manifest | rows | SHA-256 |
| --- | ---: | --- |
| train | 7,500 | `26748d701decbc8eadfe86cda070841fe9a9c4a55d418573e3c26f28ba0a7095` |
| test | 5,000 | `c04caf7b870997bab14262eb63348df4f84d26e9e866a76a15bb6dde92bacf7a` |
| combined train-then-test | 12,500 | `5d922af609751004ec32e02bcd4c3fb8238e1722a6dfe124a5a335b6305db446` |

These are proposed freeze-manifest digests generated from the verified bytes,
not files committed to this repository.

## 6. Evidence about correspondence to the original MATH split

### Verified

1. The original paper states 7,500 train and 5,000 test problems.
2. The original repository’s pinned evaluation path uses `MATH/test/*/*.json`
   and its loader requires the original JSON `problem` and `solution` fields.
3. The historical HF revision exposes separate files named `train` and `test`
   with exactly those counts after independent reading.
4. The historical Parquet schema contains the original problem and solution
   fields plus level and type, with no nulls.
5. The current HF combined file contains exactly the historical train/test
   canonical record union, in train-then-test order.

### Inferred

The historical HF revision is very likely a conversion of the original MATH
release rather than an independently reconstructed 12,500-row corpus. The
converging counts, split names, schema, and exact relationship to the later
combined HF file are strong provenance evidence. The HF current card also
labels its `source_datasets` as `original` and the dataset license as MIT.

### Unknown / not proved

- No original `MATH.tar` bytes, archive checksum, archive manifest, or Berkeley
  server metadata were recoverable in this session; the URL returned 403.
- No first-party statement or signed manifest maps every historical HF row to
  the original Berkeley archive path/content.
- The HF uploader’s conversion script, source checkout, and any transformations
  between JSON and Parquet are not published in the immutable metadata checked.
- Therefore the exact proposition “the historical HF split membership is
  byte-for-byte the original Berkeley split membership” cannot be proved from
  primary evidence presently available.

The correct claim is **historical HF split with exact verified counts and
internal consistency, strongly supported as the MATH split, but not
cryptographically equivalent to the unrecoverable Berkeley archive**.

## 7. Current-main versus historical-revision discrepancy

| property | historical `d9afe...` | current main `e839...` | consequence |
| --- | --- | --- | --- |
| files | separate train and test Parquet files | one train-named Parquet file | only historical revision directly preserves split identity |
| row counts | train 7,500; test 5,000 | one file with 12,500 | current card/file name alone is ambiguous |
| schema | four non-null string fields | same | content schema is compatible |
| byte identity | two LFS objects, two hashes | one different LFS object/hash | do not substitute current file digest for split-file digests |
| content relation | source split files | exact train-then-test canonical union | current main is useful corroboration, not the canonical split pin |
| card metadata | historical card declares train 7,500 | current card does not declare separate split counts | current metadata cannot independently recover split roles |

The HF history records the later combined-file upload and deletion of earlier
files. The current file’s exact content relation is verified locally, but
current main has no immutable split field and should not be used without the
historical revision and manifest.

## 8. License and access

- The original `hendrycks/math` repository is publicly accessible and contains
  an MIT LICENSE. That directly licenses the repository contents; it is not, by
  itself, a separately hashed license grant for the Berkeley archive bytes.
- HF reports the dataset as `private: false` and `gated: false` at both checked
  revisions. Anonymous `resolve` downloads succeeded for all three files.
- Current HF card metadata declares `license: mit`; the historical card does
  not carry that same license field. Preserve the current card claim and the
  upstream MIT license URL as legal provenance, but do not infer more than the
  source metadata states.
- The artifact is publicly retrievable as of this research date, but access is
  operationally dependent on the HF repository, revision, and object storage.
  Freeze the exact revision and file hashes rather than relying on `main`.

## 9. Exact reproduction commands

The following commands reproduce the metadata and byte checks. They download
only 9,695,136 expected bytes and do not download a model.

```bash
# Check disk before downloading.
df -B1 .

# Record expected sizes, LFS OIDs, and Xet hashes.
curl -fsSL \
  'https://huggingface.co/api/datasets/qwedsacf/competition_math/tree/d9afe06952835e34b5a148b90043bc04aa09e519?recursive=true&expand=false' \
  | jq .
curl -fsSL \
  'https://huggingface.co/api/datasets/qwedsacf/competition_math/tree/main?recursive=true&expand=false' \
  | jq .

issue10_dir=$(mktemp -d /tmp/qab-issue10-math-XXXXXX)
curl -fL --retry 2 --output "$issue10_dir/historical-train.parquet" \
  'https://huggingface.co/datasets/qwedsacf/competition_math/resolve/d9afe06952835e34b5a148b90043bc04aa09e519/data/train-00000-of-00001-48a8135a22c541f2.parquet?download=true'
curl -fL --retry 2 --output "$issue10_dir/historical-test.parquet" \
  'https://huggingface.co/datasets/qwedsacf/competition_math/resolve/d9afe06952835e34b5a148b90043bc04aa09e519/data/test-00000-of-00001-8381d31b2d187522.parquet?download=true'
curl -fL --retry 2 --output "$issue10_dir/current-main.parquet" \
  'https://huggingface.co/datasets/qwedsacf/competition_math/resolve/main/data/train-00000-of-00001-7320a6f3aba8ebd2.parquet?download=true'

stat -c '%n %s bytes' "$issue10_dir"/*.parquet
sha256sum "$issue10_dir"/*.parquet
```

Expected SHA-256 output is the three LFS OIDs in section 2. To reproduce the
row/schema/overlap checks and generate the manifest JSONL files, run this
complete command with the temporary directory as its argument. It uses
`pyarrow==24.0.0` (the version used here), writes only temporary manifest files
under that directory, and asserts the reported digests:

```bash
python - "$issue10_dir" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

root = Path(sys.argv[1])
dataset_id = "qwedsacf/competition_math"
dataset_revision = "d9afe06952835e34b5a148b90043bc04aa09e519"
expected_schema = [
    ("problem", pa.string()),
    ("level", pa.string()),
    ("type", pa.string()),
    ("solution", pa.string()),
]
expected_counts = {"train": 7500, "test": 5000, "current": 12500}
source_files = {
    "train": (
        "data/train-00000-of-00001-48a8135a22c541f2.parquet",
        root / "historical-train.parquet",
    ),
    "test": (
        "data/test-00000-of-00001-8381d31b2d187522.parquet",
        root / "historical-test.parquet",
    ),
    "current": (
        "data/train-00000-of-00001-7320a6f3aba8ebd2.parquet",
        root / "current-main.parquet",
    ),
}
fields = ["problem", "level", "type", "solution"]


def canonical_row(row):
    payload = {field: row[field] for field in fields}
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


tables = {}
rows = {}
keys = {}
for split, (_, path) in source_files.items():
    table = pq.read_table(path)
    schema = [(field.name, field.type) for field in table.schema]
    assert schema == expected_schema, (split, schema)
    assert table.num_rows == expected_counts[split], (split, table.num_rows)
    assert all(table[column].null_count == 0 for column in table.column_names), split
    split_rows = table.to_pylist()
    split_keys = [canonical_row(row) for row in split_rows]
    assert len(split_rows) == expected_counts[split]
    assert len(set(split_keys)) == len(split_keys), f"duplicates in {split}"
    tables[split] = table
    rows[split] = split_rows
    keys[split] = split_keys

assert not (set(keys["train"]) & set(keys["test"])), "train/test overlap"
assert keys["current"] == keys["train"] + keys["test"], "current != train + test"


def manifest_rows(split, file_name, split_rows):
    output = []
    for row_index, row in enumerate(split_rows):
        record_sha256 = hashlib.sha256(canonical_row(row)).hexdigest()
        output.append(
            {
                "dataset_id": dataset_id,
                "dataset_revision": dataset_revision,
                "split": split,
                "file": file_name,
                "row_index": row_index,
                "source_instance_id": f"math.v1:{record_sha256}",
                "record_sha256": record_sha256,
            }
        )
    return output


train_file = source_files["train"][0]
test_file = source_files["test"][0]
manifest_data = {
    "train": manifest_rows("train", train_file, rows["train"]),
    "test": manifest_rows("test", test_file, rows["test"]),
}
manifest_data["combined"] = manifest_data["train"] + manifest_data["test"]
expected_manifests = {
    "train": "26748d701decbc8eadfe86cda070841fe9a9c4a55d418573e3c26f28ba0a7095",
    "test": "c04caf7b870997bab14262eb63348df4f84d26e9e866a76a15bb6dde92bacf7a",
    "combined": "5d922af609751004ec32e02bcd4c3fb8238e1722a6dfe124a5a335b6305db446",
}

for name, manifest in manifest_data.items():
    jsonl = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
        for record in manifest
    ).encode("utf-8")
    (root / f"manifest-{name}.jsonl").write_bytes(jsonl)
    digest = hashlib.sha256(jsonl).hexdigest()
    assert digest == expected_manifests[name], (name, digest)
    print(f"{name}_manifest_sha256={digest}")
PY
```

The original source-history checks used:

```bash
curl -fsSL \
  'https://api.github.com/repos/hendrycks/math/commits/985bdc1696e88e8643f081a0ff4719da39f2ae2a' \
  | jq '{sha,parents:[.parents[].sha],message:.commit.message,files:[.files[]|{filename,status,additions,deletions}]}'
curl -fsSL \
  'https://raw.githubusercontent.com/hendrycks/math/985bdc1696e88e8643f081a0ff4719da39f2ae2a/README.md'
curl -fsSL \
  'https://raw.githubusercontent.com/hendrycks/math/357963a7f5501a6c1708cf3f3fb0cdf525642761/README.md'
curl -fsSIL --max-time 20 \
  'https://people.eecs.berkeley.edu/~hendrycks/MATH.tar'
```

The final command returned HTTP 403 in this session; it did not download the
archive.

## 10. Recommended freeze bundle for issue #8

This is a provenance recommendation, not the issue #8 model/backend/hardware
decision:

1. Freeze dataset identity as
   `qwedsacf/competition_math@d9afe06952835e34b5a148b90043bc04aa09e519`.
2. Freeze both exact relative paths, file sizes, Git tree OIDs, LFS OIDs,
   Xet hashes, and local SHA-256 values from section 2.
3. Freeze the verified schema: ordered fields
   `problem:string`, `level:string`, `type:string`, `solution:string`, with
   no nulls; retain Parquet reader/version and the row-count verification.
4. Freeze the train/test source-instance manifest using the identifier and
   canonical JSONL procedure in section 5. Retain the three manifest hashes
   reported there.
5. Freeze the upstream provenance references: the MATH paper, upstream
   repository commit `985bdc...`, its Berkeley-link parent
   `357963a...`, and the historical HF revision. Record that upstream commit
   `985bdc...` is a link change and not a dataset-byte pin.
6. Freeze the MATH evaluator/parser and split semantics already accepted in
   issues #7 and #4 separately; this report does not alter them.
7. Mark the original-archive equivalence field as
   `not_cryptographically_verified` unless Berkeley archive bytes or a
   provenance-bearing first-party manifest are later recovered.

Do not use current HF `main` as a replacement for item 1. It is suitable as an
audit cross-check because its bytes equal the historical union under the
canonical comparison, but its file naming and metadata erase the source split.

## 11. Confidence and unresolved uncertainty

- **High confidence:** paper counts; upstream README-link change; HF revision
  and file identities; LFS/Xet metadata; local SHA-256 matches; row counts;
  schema; null and exact-duplicate results; zero train/test overlap; and the
  current-main-to-historical-union content relation.
- **Moderate-to-high confidence:** `d9afe...` is the best publicly retrievable
  immutable artifact for the accepted split and is a faithful HF conversion of
  the MATH source population.
- **Low/unknown:** byte-for-byte or membership-level equivalence to the
  original Berkeley `MATH.tar`; original archive checksum; uploader conversion
  procedure; and a separately documented dataset license for the old Berkeley
  bytes.

No speculative follow-on ticket is needed. If exact primary-source equivalence
is a hard closure requirement, the smallest concrete next operation is manual
recovery of the Berkeley archive or a first-party archive manifest/checksum;
until then, issue #8 can freeze the historical HF artifact only with the
explicit provenance caveat above.

## Sources

- [MATH paper](https://arxiv.org/abs/2103.03874)
- [MATH repository](https://github.com/hendrycks/math)
- [Pinned upstream commit](https://github.com/hendrycks/math/commit/985bdc1696e88e8643f081a0ff4719da39f2ae2a)
- [Pinned README](https://github.com/hendrycks/math/blob/985bdc1696e88e8643f081a0ff4719da39f2ae2a/README.md)
- [Berkeley archive URL](https://people.eecs.berkeley.edu/~hendrycks/MATH.tar)
- [Pinned MATH loader](https://github.com/hendrycks/math/blob/985bdc1696e88e8643f081a0ff4719da39f2ae2a/modeling/dataset/MATH.py)
- [Pinned evaluation entry point](https://github.com/hendrycks/math/blob/985bdc1696e88e8643f081a0ff4719da39f2ae2a/modeling/eval_math_gpt.py)
- [HF dataset current page](https://huggingface.co/datasets/qwedsacf/competition_math)
- [HF historical revision](https://huggingface.co/datasets/qwedsacf/competition_math/tree/d9afe06952835e34b5a148b90043bc04aa09e519)
- [HF current revision](https://huggingface.co/datasets/qwedsacf/competition_math/tree/e839825f9ec5c6cfa585c654a59610969ec13993)
- [HF historical train file](https://huggingface.co/datasets/qwedsacf/competition_math/blob/d9afe06952835e34b5a148b90043bc04aa09e519/data/train-00000-of-00001-48a8135a22c541f2.parquet)
- [HF historical test file](https://huggingface.co/datasets/qwedsacf/competition_math/blob/d9afe06952835e34b5a148b90043bc04aa09e519/data/test-00000-of-00001-8381d31b2d187522.parquet)
- [HF current combined file](https://huggingface.co/datasets/qwedsacf/competition_math/blob/e839825f9ec5c6cfa585c654a59610969ec13993/data/train-00000-of-00001-7320a6f3aba8ebd2.parquet)
