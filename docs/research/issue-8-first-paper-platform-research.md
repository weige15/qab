# Issue #8: First-paper platform research

**Status:** evidence packet for the human decision sequence; not an accepted
model, backend, hardware, or data decision.

**Date:** 2026-07-27

**Scope:** choose one first-paper joint tuple consisting of model, tokenizer,
quantization backend and method, software runtime, hardware target, and the
already-selected data/evaluator sources. This packet does not define the
schedule codebook, query-by-schedule pilot, predictor, batching, or serving.

No model or dataset was downloaded, no dependency was installed, no model or
evaluator was run, no GPU job was launched, and no final-test output,
evaluator result, or target-suite leaderboard result informed this packet.

## Evidence labels and method

- **Documented:** stated by the primary source linked with the claim.
- **Directly verified:** observed from immutable repository metadata or the
  current local environment without model work.
- **Inferred; preflight required:** a consequence of documented facts that is
  not execution evidence.
- **Unknown:** not established without an approved acquisition, environment
  setup, or real-model preflight.

The research subnotes A–D were produced against official model cards,
repositories, release metadata, framework/backend documentation, and source
code. Their claims were consolidated here and are retained only when their
status and primary source are explicit.

## Existing accepted constraints

Issue #7 already froze the initial task/evaluator registry and split roles:

| Family | Frozen source/evaluator | Accepted role |
|---|---|---|
| Numeric reasoning | MATH `hendrycks/math@985bdc1696e88e8643f081a0ff4719da39f2ae2a`; evaluator `math.equivalence.v1` at the same commit | 128 atomic profile requests; validation carved from train before variants/composites; MIT repository and public source access. [source commit](https://github.com/hendrycks/math/commit/985bdc1696e88e8643f081a0ff4719da39f2ae2a) |
| Code generation | HumanEval+ v0.1.10 release commit `200defce9e3429d28ca215b6dd061c0f7f31c18b`; EvalPlus evaluator `e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2` | 164 public source tasks; any project validation partition is created before variants/composites; base/plus/per-test statuses retained. [release commit](https://github.com/evalplus/humanevalplus_release/commit/200defce9e3429d28ca215b6dd061c0f7f31c18b) [evaluator commit](https://github.com/evalplus/evalplus/commit/e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2) |
| Fixed-context QA | Official MuSiQue-Full v1.0 archive; evaluator `24cc5b297acc2abfc5fb3d0becb6ef7b73d03717` | Retrieval disabled; answer and support are separate mandatory components; native 2/3-hop, held-out 4-hop, and leakage-control files remain in the accepted split plan. [evaluator commit](https://github.com/StonyBrookNLP/musique/commit/24cc5b297acc2abfc5fb3d0becb6ef7b73d03717) |

The accepted Issue #4 contract is unchanged: deterministic greedy decoding,
paired BF16 reference conditions, mandatory-component conjunction, frozen
thresholds/margins/statuses/denominators, and final-test change control. No
platform choice may alter it.

## Model candidates

The screen is limited to open decoder-only text models in the frozen 3B–8B
range. The listed model and tokenizer revisions are intended to be pinned to
the same immutable snapshot; exact downloaded-file checksums remain a
preflight artifact.

| Candidate | Primary-source facts | Joint-tuple implication and status |
|---|---|---|
| **Qwen/Qwen2.5-7B-Instruct** at `a09a35458c702b33eeacc393d103063234e8bc28` | **Documented:** `Qwen2ForCausalLM`, 7.61B parameters, 28 transformer layers, GQA, `apply_chat_template`, and configured `max_position_embeddings=32768`; Apache-2.0 and API reports `gated:false`. The pinned tree reports roughly 15.2 GB of BF16 safetensor files. [API/revision](https://huggingface.co/api/models/Qwen/Qwen2.5-7B-Instruct) [config](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/blob/a09a35458c702b33eeacc393d103063234e8bc28/config.json) [pinned tree](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/tree/a09a35458c702b33eeacc393d103063234e8bc28) | **Inferred; preflight required:** 28 indexed layers, public ungated access, and the model-side footprint make this the clearest joint candidate for one 24-GiB card. BF16 loading, short generation, actual quantized kernels, block assignment, and memory headroom are unverified. |
| **mistralai/Mistral-7B-Instruct-v0.3** at `c170c708c41dac9275d15a8fff4eca08d52bab71` | **Documented:** `MistralForCausalLM`, 32 layers, 32 query/8 KV heads, configured 32,768-token context, tokenizer chat template, Apache-2.0, and `gated:false`. The pinned tree contains a 14.5 GB consolidated BF16 file; Mistral’s official inference repository publishes archive MD5 `80b71fcb6416085bcb4efad86dfb4d52`. [API/revision](https://huggingface.co/api/models/mistralai/Mistral-7B-Instruct-v0.3) [config](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3/blob/c170c708c41dac9275d15a8fff4eca08d52bab71/config.json) [pinned tree](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3/tree/c170c708c41dac9275d15a8fff4eca08d52bab71) [inference source](https://github.com/mistralai/mistral-inference) | **Inferred; preflight required:** 32 indexed layers and a public Apache-2.0 snapshot are strong candidates. The archive MD5 is not a substitute for the exact selected snapshot/file manifest; backend support, load/generation, and memory headroom remain unverified. |
| **microsoft/Phi-3.5-mini-instruct** at `2fe192450127e6a83f7441aef6e3ca586c338b77` | **Documented:** Microsoft describes a 3.8B dense decoder-only Transformer, `apply_chat_template`, 128K model-card context, MIT license, and two BF16 shards totaling roughly 7.64 GB. The documented integration uses `trust_remote_code=True` and custom Phi-3 code. [revision](https://huggingface.co/microsoft/Phi-3.5-mini-instruct/commit/2fe192450127e6a83f7441aef6e3ca586c338b77) [model card/tree](https://huggingface.co/microsoft/Phi-3.5-mini-instruct/tree/2fe192450127e6a83f7441aef6e3ca586c338b77) | **Inferred; preflight required:** lower memory pressure is attractive, but custom remote code and backend layer enumeration create higher integration risk. The advertised context length is not a project preflight context setting. |
| **meta-llama/Llama-3.1-8B-Instruct** at `0e9e39f249a16976918f6564b8830bc894c89659` | **Documented:** decoder-only Llama architecture, GQA, 128K model-card context, chat template, and roughly 16.07 GB of BF16 weight files. Access is manually gated and governed by the Llama 3.1 Community License and AUP. [revision/API](https://huggingface.co/api/models/meta-llama/Llama-3.1-8B-Instruct) [Meta card](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/MODEL_CARD.md) [license](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE) | **Conditional only:** technically plausible on a 24-GiB card, but reproducible public access and license eligibility are hard-gate risks. It is excluded by the recommended gate policy unless the human explicitly accepts gated access as reproducible. |

**Lower-boundary lead:** Qwen/Qwen2.5-3B-Instruct is technically small and
documents a 3.09B decoder-only model, 36 layers, chat template, and about
6.18 GB of BF16 files, but its official Qwen Research License is
non-commercial and this pass did not recover a full immutable revision for
the current page. [model card](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct)
[license](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/blob/main/LICENSE)
It is a fallback lead only until license and revision gates pass.

## Backend and quantization evidence

### Meaning established by primary sources

**Documented:** LLM Compressor and compressed-tensors describe `W4A16` and
`W8A16` as 4-/8-bit weights with 16-bit activations, distinguish them from
activation-quantized W8A8 and KV-cache quantization, expose GPTQ/AWQ-style
weight quantization, and support non-uniform schemes/config groups. The
weight-only recipe must explicitly leave activation and KV-cache schemes null.
[scheme guide](https://docs.vllm.ai/projects/llm-compressor/en/stable/steps/choosing-scheme/)
[quantization API](https://docs.vllm.ai/projects/llm-compressor/en/stable/api/llmcompressor/modifiers/quantization/)
[compressed-tensors source](https://github.com/vllm-project/compressed-tensors/tree/0.12.2)

The exact algorithm, scale granularity, group size, excluded modules,
calibration subset, and A16 activation dtype remain decisions. They must not
be silently inherited from a backend default.

### Candidate backend tuples

These are complete joint candidates for the matrix, not accepted choices. The
model anchor used by backend documentation is Qwen2.5-7B-Instruct at the
immutable revision above; the same backend family must later be checked against
any selected model.

| Joint tuple | Exact pins and hardware | Evidence, gate status, and blocking unknown |
|---|---|---|
| **Qwen2.5-7B + LLM Compressor → compressed-tensors → vLLM** | LLM Compressor `0.9.0` @ `129c793fdabfd9bc486f85c444bdec6b713978fe`; compressed-tensors `0.12.2` @ `2dd1b627950b4a068f2c1af19bc6f31b7fbb3316`; vLLM `0.11.2` @ `275de34170654274616082721348b7edd9741d32`; a coherent PyTorch/Transformers environment; one RTX 3090 SM86 | **Documented:** W4A16/W8A16 schemes, GPTQ/AWQ/config groups, saved compressed representations, and Qwen2 runtime support. **Not directly executable as the current installed stack:** vLLM metadata requires `torch==2.9.0` and `transformers<5`, conflicting with locally observed torch 2.4.0 and Transformers 5.12.1. The coherent runtime pin is therefore **unknown and requires approval/preflight**. Contiguous block construction, map inspection, kernel path, export/reload, and no silent dequantization are also **unknown**. [non-uniform example](https://docs.vllm.ai/projects/llm-compressor/en/latest/examples/quantization_non_uniform/) [vLLM support](https://docs.vllm.ai/en/v0.11.2/models/supported_models/) |
| **Mistral-7B + LLM Compressor → compressed-tensors → vLLM** | Same backend family, with Mistral revision above; coherent runtime to be pinned; one RTX 3090 SM86 | **Documented/inferred:** backend family and vLLM support direction are plausible. Model-specific quantizer support, contiguous block assignment, exact runtime compatibility, and preflight are **unknown**. |
| **Qwen2.5-7B + TensorRT-LLM** | TensorRT-LLM `1.2.1` @ `376f7e1bd8ed543f75014309e3fd4b237e9b0e73`; Model Optimizer/TensorRT/CUDA build pins unresolved; one RTX 3090 SM86 | **Documented:** official quantization docs define `int8_wo`, `int4_wo`, and per-layer `MIXED_PRECISION` configuration; **inferred:** consecutive layer ranges are expressible. Conversion, engine build, precision-map inspection, reload, and exact SM86 stack are **unknown**. [quantization README](https://github.com/NVIDIA/TensorRT-LLM/blob/v1.2.1/examples/quantization/README.md) [support matrix](https://docs.nvidia.com/deeplearning/tensorrt/latest/getting-started/support-matrix.html) |
| **Qwen2.5-7B + torchao eager/compiled PyTorch** | torchao `v0.17.0` @ `02105d46c61dc80a8c9d39d5836e827ba3af8439`; PyTorch `2.4.0+cu124`; Transformers 5.12.1; one RTX 3090 SM86 | **Documented:** `Int8WeightOnlyConfig`, groupwise `Int4WeightOnlyConfig`, and FQN-to-config maps. **Inferred:** contiguous layer FQNs could express ranges. **Unknown:** exact torchao/PyTorch compatibility, Qwen path, kernels, save/reload, and runtime map. [quantization API](https://docs.pytorch.org/ao/stable/api_reference/api_ref_quantization.html) [FqnToConfig](https://docs.pytorch.org/ao/stable/api_reference/generated/torchao.quantization.FqnToConfig.html) |
| **Qwen2.5-7B + bitsandbytes/Transformers** | bitsandbytes `0.49.2` @ `f0e6ca31b32c4744a9cee4e31610b25796cbf778`; PyTorch `2.4.0+cu124`; Transformers 5.12.1; Accelerate 1.14.0; one RTX 3090 SM86 | **Directly verified:** bitsandbytes CUDA diagnostic succeeded on the visible SM86 environment. **Documented:** Transformers exposes `Linear8bitLt`/`Linear4bit`, but 4-bit is NF4/FP4 and LLM.int8 uses outlier handling; this is not automatically the strict integer W8A16/INT4 definition, nor does it establish contiguous mixed blocks, map inspection, or export/reload. [integration docs](https://huggingface.co/docs/transformers/main/quantization/bitsandbytes) [bnb docs](https://huggingface.co/docs/bitsandbytes/index) |
| **Qwen2.5-7B + HQQ/Transformers** | HQQ `v0.2.8` @ `f62d06e45d0ad0327a045ade383f92b258e0ca27`; exact PyTorch/Transformers/CUDA tuple unresolved; one RTX 3090 SM86 | **Documented:** layer-specific dynamic configurations and `save_pretrained`/reload direction. **Unknown:** Qwen support, intended CUDA backend, true execution semantics, and deploy/runtime path. [HQQ source](https://github.com/dropbox/hqq/tree/v0.2.8) |

**Provisional evidence ordering:** the LLM Compressor/compressed-tensors path
has the strongest primary-source support for the required W4A16/W8A16,
non-uniform schemes, and serialized quantized representations. This is an
inference requiring a coherent environment and the real preflight, not a
selection. TensorRT-LLM has explicit per-layer configuration but greater build
unknowns. bitsandbytes is locally available but does not establish the strict
format or block-schedule requirements.

## Hardware and runtime

### Directly observed environment

On 2026-07-27, read-only inspection reported eight `NVIDIA GeForce RTX 3090`
devices, compute capability 8.6, 24,576 MiB each, driver `580.159.03`, Python
3.12.3, PyTorch `2.4.0+cu124` with CUDA 12.4, and CUDA availability. The
observed free memory ranged from 5,847 to 17,815 MiB and utilization was high;
this is neither a reservation nor a clean-device guarantee. The local package
inventory additionally reported Transformers 5.12.1, Accelerate 1.14.0,
bitsandbytes 0.49.2, compressed-tensors 0.12.2, vLLM 0.11.2, Triton 3.0.0,
and flash-attn 2.8.3.post1. The bitsandbytes diagnostic returned `SUCCESS!`.

**Documented:** NVIDIA identifies RTX 3090 as SM86 with 24 GB memory and
Ampere support for BF16 and 4-/8-bit integer MMA; CUDA 12.4 requires Linux
driver >=550.54.14 and the observed 580.159.03 driver is newer. PyTorch
publishes a CUDA 12.4 installation for 2.4.0. These establish compatibility
direction, not model execution. [NVIDIA GPU table](https://developer.nvidia.com/cuda/gpus)
[RTX 3090 specifications](https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3090-3090ti/)
[Ampere guide](https://docs.nvidia.com/cuda/ampere-tuning-guide/index.html)
[CUDA 12.4 notes](https://docs.nvidia.com/cuda/archive/12.4.0/cuda-toolkit-release-notes/)
[PyTorch versions](https://pytorch.org/get-started/previous-versions/)

**Directly verified compatibility warning:** installed vLLM 0.11.2 metadata
requires torch 2.9.0 and Transformers <5, so the visible local environment is
not a coherent vLLM runtime. A synchronized runtime must be approved and
created before preflight. No installation was attempted.

### Memory and kernel implications

**Inferred; preflight required:** dense BF16 weights require approximately
`2P` bytes, W8 `P` bytes, and W4 `P/2` bytes before scales, unquantized
modules, workspaces, activations, and KV cache. At 8B this is about 16.0 GB
(14.90 GiB) raw BF16, 8.0 GB W8, and 4.0 GB W4. Thus one 24-GiB card is
plausible for short-context full-model loading, but exact peak memory,
conversion scratch space, context/generation limits, and disk headroom are
unknown. No memory claim is closure evidence.

**Documented:** vLLM’s quantization table lists AWQ, GPTQ, Marlin, BitBLAS,
and bitsandbytes on Ampere; FP8 W8A8 is marked unsupported on Ampere. Its INT4
guide documents W4A16 and a compute-capability threshold that SM86 satisfies.
This does not prove a mixed schedule for the selected model. [hardware table](https://docs.vllm.ai/en/v0.11.2/features/quantization/)
[INT4 guide](https://docs.vllm.ai/en/v0.11.2/features/quantization/int4/)

Compilation may require explicit SM86 targets, compatible CUDA/toolkit/
compiler versions, and build tools such as `ninja`. **Unknown:** exact target
host/toolkit, kernel compilation, whether unsupported kernels fall back to
dequantized dense matmul or CPU, and whether mixed checkpoint/engine reload
preserves the map.

## Frozen data-source and evaluator provenance

### Exact source/archive matrix

| Family | Identity/access/license facts | Checksum and artifact status |
|---|---|---|
| MATH | **Directly verified:** pinned repository commit exists, is MIT, and contains loaders/evaluation code; its README points to a separate dataset distribution. [commit](https://github.com/hendrycks/math/commit/985bdc1696e88e8643f081a0ff4719da39f2ae2a) [README](https://github.com/hendrycks/math/blob/985bdc1696e88e8643f081a0ff4719da39f2ae2a/README.md) | The pinned repository does not contain the benchmark JSON/archive and publishes no SHA-256. The current `qwedsacf/competition_math` mirror exposes revision `e839825f9ec5c6cfa585c654a59610969ec13993` and one converted train split; it cannot yet be treated as the accepted train/test identity. **Unknown:** approved acquisition identity and checksum. [mirror card](https://huggingface.co/datasets/qwedsacf/competition_math) |
| HumanEval+ | **Directly verified:** release repository commit `200defc...` exists, release materials are Apache-2.0, and upstream HumanEval terms must also be retained. EvalPlus commit `e5d0ed0...` exists and its loader/evaluator expose v0.1.10 base/plus inputs and per-test status. [release commit](https://github.com/evalplus/humanevalplus_release/commit/200defce9e3429d28ca215b6dd061c0f7f31c18b) [release license](https://github.com/evalplus/humanevalplus_release/blob/200defce9e3429d28ca215b6dd061c0f7f31c18/LICENSE) [evaluator](https://github.com/evalplus/evalplus/commit/e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2) | v0.1.10 publishes `HumanEvalPlus.jsonl.gz`, `HumanEvalPlus-OriginFmt.jsonl.gz`, `HumanEvalPlus-Mini.jsonl.gz`, and `HumanEvalPlus-NoExtreme.jsonl.gz`; API digest is null. The annotated tag target differs from frozen release commit: tag target `68cd26d53a0dec69f85eafe1f82a2a74155a2bd6`, frozen commit is a child. Record both exact tag/commit and selected asset URL/name. **Unknown:** SHA-256 until approved acquisition. [release](https://github.com/evalplus/humanevalplus_release/releases/tag/v0.1.10) |
| MuSiQue-Full | **Directly verified:** official commit exists, README states CC BY 4.0, and evaluator checks aligned IDs/length then computes answer/support/group-sufficiency metrics. The pinned download script names `musique_v1.0.zip` and uses Google Drive file ID `1tGdADlNjWFaHLeZZGShh2IRcpO6Lv24h`. [README](https://github.com/StonyBrookNLP/musique/blob/24cc5b297acc2abfc5fb3d0becb6ef7b73d03717/README.md) [download script](https://github.com/StonyBrookNLP/musique/blob/24cc5b297acc2abfc5fb3d0becb6ef7b73d03717/download_data.sh) [evaluator](https://github.com/StonyBrookNLP/musique/blob/24cc5b297acc2abfc5fb3d0becb6ef7b73d03717/evaluate_v1.0.py) | No SHA-256 is published in the pinned source. **Unknown:** archive checksum until approved acquisition. Preserve the released `dev_test_singlehop_questions_v1.0.json` leakage-control file. [archive](https://drive.google.com/file/d/1tGdADlNjWFaHLeZZGShh2IRcpO6Lv24h/view?usp=sharing) |

### Split and manifest construction

These are already accepted Issue #7 rules, recorded here as implementation
inputs rather than new decisions:

1. Assign source instances to train, validation, IID-final, or
   held-out-composition-final before prompt variants, paraphrases, or
   cross-family composites. Every derivative inherits its source split.
2. Retain dataset/revision, archive or asset name, checksum, source IDs,
   evaluator commit/source files, adapter/parser, prompt/composition identity,
   split role, and leakage-group identity; hash the resulting manifest before
   model outputs.
3. Close leakage transitively over source items, prompt variants/paraphrases,
   shared documents/evidence, code prompts/tests, templates, and derived
   composites. Merge exact normalized duplicates, text-Jaccard >=0.90, and
   code AST/test-hash duplicates before split assignment.
4. Apply MuSiQue’s released single-hop leakage-control IDs; fixed supplied
   context means retrieval is disabled, not that seed-data leakage is allowed.
5. Freeze registry/evaluator/prompt/split/leakage identities before validation
   outputs and freeze the final-test manifest before calibration, codebook,
   predictor, or router tuning.

Non-final calibration and neutral capability preflight may use only MATH
train/validation records, HumanEval+ tasks assigned to non-final roles before
variants, and MuSiQue source-disjoint train/dev native 2/3-hop requests. Do
not use MATH test, held-out MuSiQue 4-hop, numeric-to-code held-out composites,
or any final-test outputs to choose this tuple. Exact extracted file lists,
row counts, checksums, dependency locks, and split-manifest hashes remain
preflight artifacts.

## Complete joint-tuple matrix

The matrix is deliberately lexicographic. A tuple with an unknown hard gate is
not promoted by a weighted score.

| Tuple | Model/tokenizer | Backend/method | Software/runtime | Hardware | Current conclusion |
|---|---|---|---|---|---|
| Qwen-7B / compressed-tensors path | Qwen2.5-7B-Instruct @ `a09a...bc28`; same-revision tokenizer/chat template | LLM Compressor 0.9.0 + compressed-tensors 0.12.2; GPTQ/AWQ candidate; explicit W8A16/W4A16 weight-only recipe | vLLM 0.11.2 with a yet-to-be-created coherent PyTorch/Transformers environment; current torch 2.4/Transformers 5.12 environment is incompatible | One RTX 3090 SM86 | **Primary preflight candidate, not selected.** Strongest source support; runtime coherence, real BF16/W8/W4, mixed map, kernel path, reload, and headroom unknown. |
| Mistral-7B / compressed-tensors path | Mistral-7B-Instruct-v0.3 @ `c170...ab71`; same-revision tokenizer | Same candidate backend/method | Coherent vLLM environment unresolved | One RTX 3090 SM86 | **Secondary preflight candidate.** Native 32-layer model and public license; model-specific backend/preflight unknown. |
| Qwen-7B / TensorRT-LLM | Qwen2.5-7B-Instruct @ `a09a...bc28`; tokenizer same revision | TensorRT-LLM 1.2.1; `int8_wo`/`int4_wo` and per-layer mixed config | Model Optimizer, TensorRT, CUDA, compiler pins unresolved | One RTX 3090 SM86 | **Technically expressible but not locally prepared.** Build/conversion/engine reload unknown. |
| Qwen-7B / torchao | Qwen2.5-7B-Instruct @ `a09a...bc28`; tokenizer same revision | torchao 0.17.0; `Int8WeightOnlyConfig`/`Int4WeightOnlyConfig`/FQN map | PyTorch 2.4.0+cu124; exact torchao compatibility unresolved | One RTX 3090 SM86 | **Module-control candidate, not closure-ready.** Kernel, Qwen path, serialization, and map execution unknown. |
| Qwen-7B / bitsandbytes | Qwen2.5-7B-Instruct @ `a09a...bc28`; tokenizer same revision | bitsandbytes 0.49.2; Transformers `Linear8bitLt`/`Linear4bit` | PyTorch 2.4.0+cu124, Transformers 5.12.1, Accelerate 1.14.0 | One RTX 3090 SM86 | **Uniform-baseline candidate only until semantics are resolved.** NF4/FP4 and LLM.int8 outlier behavior do not by themselves establish strict integer W4A16/W8A16 or mixed contiguous blocks. |
| Phi-3.5-mini / backend TBD | Phi-3.5-mini-instruct @ `2fe...8b77`; tokenizer same revision | Backend must support custom remote code and strict W8/W4; no eligible backend yet | Transformers example uses `trust_remote_code`; coherent quantizer/runtime unresolved | One RTX 3090 SM86 | **Memory fallback lead, not a complete eligible tuple.** |
| Llama-3.1-8B / backend TBD | Llama-3.1-8B-Instruct @ `0e9...9659`; tokenizer same gated revision | Backend TBD | Access and runtime unresolved | One RTX 3090 SM86 | **Rejected by recommended reproducibility gate** because access is manually gated; no final-test evidence involved. |

## Proposed lexicographic hard gates

The recommendation is to apply these gates in order, with evidence rather than
an arbitrary weighted score:

1. **Scope:** open, decoder-only, text model in the frozen 3B–8B range with
   an inspectable transformer-layer count; no MoE or architecture outside the
   accepted scope.
2. **Reproducibility/access:** immutable model and tokenizer revisions,
   reproducible public acquisition, acceptable research license, and recorded
   file/archive checksums. Recommended policy: manually gated models fail this
   gate rather than becoming a hidden access dependency.
3. **Baseline execution:** on one explicitly available RTX 3090, the full
   pinned model loads and generates in BF16 with short neutral/non-final
   prompts, without CPU fallback; peak memory and headroom are recorded.
4. **Format semantics:** the backend performs true weight-only W8A16 and
   W4A16: INT8/INT4 weights, 16-bit activation path as later resolved, no
   activation quantization, and no KV-cache quantization.
5. **Schedule expressivity:** different precisions can be assigned to
   contiguous transformer-block ranges, not merely to tensor-internal
   quantizer groups.
6. **Inspection and persistence:** the requested module/block precision map is
   inspectable after construction and matches the request; export/save and
   reload preserve the map wherever the experimental path uses serialization.
7. **Runtime/hardware:** exact GPU architecture, driver, CUDA, PyTorch,
   backend, compiler/kernel path, model architecture, and runtime versions are
   mutually compatible; unsupported kernels, CPU fallback, or dequantized
   execution fail the gate rather than silently passing.
8. **Resource headroom:** enough VRAM, disk, conversion scratch space, and
   short-generation runtime headroom are observed on the selected target.
9. **Scientific integrity:** no final-test prompt, output, evaluator result,
   leaderboard result, or target-suite quality outcome informs selection.

## Remaining decision dependencies

The required grilling order keeps these separate from facts:

1. Eligibility policy, including whether any gated model is excluded.
2. One RTX 3090 versus homogeneous multi-GPU target; visible inventory is not
   a reservation.
3. Exact A16 meaning: BF16 or FP16 activations, quantization algorithm, scale
   granularity, group size, excluded modules, calibration data, and whether
   these belong in this ticket. Any scientifically material field not covered
   elsewhere should become a new decision ticket rather than a backend default.
4. Primary joint tuple.
5. Deterministic fallback tuple and exact trigger.
6. Exact data/archive/checksum/manifest/calibration/split pins.
7. Minimum empirical preflight.

No tuple currently reaches the Issue #8 closure gate. The missing evidence is
the approved coherent runtime and real full-model capability preflight, not
the schedule codebook or any final-test outcome.

## Primary sources

Model and data sources are linked in the matrices above. Additional primary
backend/runtime sources:

- [LLM Compressor 0.9.0](https://github.com/vllm-project/llm-compressor/releases/tag/0.9.0)
- [compressed-tensors 0.12.2](https://github.com/vllm-project/compressed-tensors/tree/0.12.2)
- [vLLM 0.11.2 supported models](https://docs.vllm.ai/en/v0.11.2/models/supported_models/)
- [vLLM 0.11.2 quantization hardware](https://docs.vllm.ai/en/v0.11.2/features/quantization/)
- [vLLM 0.11.2 INT4 guide](https://docs.vllm.ai/en/v0.11.2/features/quantization/int4/)
- [TensorRT-LLM 1.2.1 quantization](https://github.com/NVIDIA/TensorRT-LLM/blob/v1.2.1/examples/quantization/README.md)
- [torchao quantization API](https://docs.pytorch.org/ao/stable/api_reference/api_ref_quantization.html)
- [bitsandbytes installation/overview](https://huggingface.co/docs/bitsandbytes/installation)
- [HQQ 0.2.8](https://github.com/dropbox/hqq/tree/v0.2.8)

## Researcher note

The official sources support investigating Qwen2.5-7B and Mistral-7B first,
with LLM Compressor/compressed-tensors as the leading backend candidate. This
is a recommendation for the decision conversation only. Until the human
answers the decision questions and authorizes the required runtime setup and
one-GPU preflight, Issue #8 remains open and no tuple is accepted.
