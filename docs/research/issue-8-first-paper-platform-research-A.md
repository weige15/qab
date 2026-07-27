# Issue #8 model-candidate evidence

**Scope.** Model candidates only: open decoder-only models in the accepted
3B–8B range, with model/tokenizer identity, architecture, access and license,
checkpoint footprint, prompt format, context limits, and implications for a
joint backend/runtime/RTX 3090 tuple. This note does not select the model,
backend, schedule, or hardware policy. No model or dataset was downloaded; no
dependency was installed; no model inference or GPU job was run; and no
final-test output or target-suite result was inspected.

**Evidence labels.** `[documented]` means stated by the cited first-party
source; `[directly verified]` means observed from the local environment or
immutable repository metadata without running model work; `[inferred—requires
preflight]` is a consequence that still needs the approved real-model
preflight; `[unknown]` was not established by this pass.

## Candidate screen

The screen keeps instruction-tuned text-only causal models because the frozen
suite requires generated answers, code, and fixed-context QA. Model cards
explicitly show Transformers/vLLM paths for all four candidates; that is
model-loading evidence, not evidence that any backend can provide true
W8A16/W4A16 contiguous mixed-block execution. [documented]

| Candidate and immutable IDs | Architecture, tokenizer, prompt/context | Access, license, footprint | Joint-tuple implication |
|---|---|---|---|
| **Qwen/Qwen2.5-7B-Instruct**; model revision `a09a35458c702b33eeacc393d103063234e8bc28`; tokenizer ID is the same repo and revision, using its pinned `tokenizer.json`, `tokenizer_config.json`, `merges.txt`, and `vocab.json`. [documented; revision/API](https://huggingface.co/api/models/Qwen/Qwen2.5-7B-Instruct) [documented; pinned tree](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/tree/a09a35458c702b33eeacc393d103063234e8bc28) | `Qwen2ForCausalLM`; 7.61B parameters; 28 transformer layers; GQA 28 Q / 4 KV; RoPE/SwiGLU/RMSNorm with attention QKV bias. The documented chat path is `apply_chat_template`. The pinned config sets `max_position_embeddings=32768`; Qwen documents 131,072-token operation only with optional YaRN configuration and generation up to 8192. [documented](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/blob/a09a35458c702b33eeacc393d103063234e8bc28/config.json) [documented](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct) | Apache-2.0; API reports `gated:false`. The pinned HF tree reports 15.2 GB total: four BF16 safetensor shards of 3.95, 3.86, 3.86, and 3.56 GB plus tokenizer/config files. [documented](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/tree/a09a35458c702b33eeacc393d103063234e8bc28) | **Strong native-architecture candidate.** 28 layers give a direct contiguous-block index. A 15.2 GB BF16 repository footprint is below 24 GiB before runtime/KV/cache overhead, so one-3090 BF16 loading is plausible but not proven. [inferred—requires preflight] Quantizer-specific W8A16/W4A16 semantics, excluded modules, per-layer assignment, and export/reload remain unknown. |
| **mistralai/Mistral-7B-Instruct-v0.3**; model revision `c170c708c41dac9275d15a8fff4eca08d52bab71`; tokenizer ID is the same repo and revision, with `tokenizer.json`, `tokenizer.model`, and `tokenizer.model.v3`. [documented; revision/API](https://huggingface.co/api/models/mistralai/Mistral-7B-Instruct-v0.3) [documented; pinned tree](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3/tree/c170c708c41dac9275d15a8fff4eca08d52bab71) | `MistralForCausalLM`; pinned config has 32 layers, 32 attention heads / 8 KV heads, BF16 dtype, and `max_position_embeddings=32768`. The model card documents Transformers loading, chat messages, and function-calling support; its tokenizer config contains the chat template. [documented](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3/blob/c170c708c41dac9275d15a8fff4eca08d52bab71/config.json) [documented](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3) | Apache-2.0; API reports `gated:false`. The pinned tree contains a 14.5 GB consolidated BF16 file and sharded safetensors of 4.95, 5.00, and 4.55 GB; the 29 GB repository total includes duplicate checkpoint formats. Mistral’s official inference repository publishes the 7B v0.3 archive URL and MD5 `80b71fcb6416085bcb4efad86dfb4d52`. [documented](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3/tree/c170c708c41dac9275d15a8fff4eca08d52bab71) [documented](https://github.com/mistralai/mistral-inference) | **Strong native-architecture candidate.** 32 layers provide a direct contiguous-block index; the official archive checksum is useful for reproducible acquisition. A 14.5 GB BF16 payload is plausibly compatible with one 24-GiB 3090 for short contexts, but loading/generation and quantized mixed execution remain unverified. [inferred—requires preflight] |
| **microsoft/Phi-3.5-mini-instruct**; model revision `2fe192450127e6a83f7441aef6e3ca586c338b77`; tokenizer ID is the same repo and revision, with the pinned tokenizer files. [documented; full commit](https://huggingface.co/microsoft/Phi-3.5-mini-instruct/commit/2fe192450127e6a83f7441aef6e3ca586c338b77) [documented; pinned tree](https://huggingface.co/microsoft/Phi-3.5-mini-instruct/tree/2fe192450127e6a83f7441aef6e3ca586c338b77) | Microsoft describes it as a 3.8B dense decoder-only Transformer, best suited to chat format, with 128K context. The official example uses `apply_chat_template`, `trust_remote_code=True`, and the model’s custom Phi-3 code files. The model card’s example integration is Transformers 4.43.0; this is a documented example requirement, not the project’s final pin. [documented](https://huggingface.co/microsoft/Phi-3.5-mini-instruct) | MIT. The pinned HF tree reports 7.64 GB and two BF16 safetensor shards of 4.97 and 2.67 GB. [documented](https://huggingface.co/microsoft/Phi-3.5-mini-instruct/tree/2fe192450127e6a83f7441aef6e3ca586c338b77) | **Memory-friendly but higher integration risk.** The smaller BF16 footprint makes one-3090 loading plausible, but custom remote model code and an unverified block count make backend-level layer inspection and contiguous assignment less certain than native Qwen/Mistral. The 128K capability also does not imply a 128K preflight context; KV memory and project context policy still need to be fixed. [inferred—requires preflight] |
| **meta-llama/Llama-3.1-8B-Instruct**; model revision `0e9e39f249a16976918f6564b8830bc894c89659`; tokenizer ID is the same gated repo and revision; Meta describes the tokenizer family as TikToken-based. [documented; revision/API](https://huggingface.co/api/models/meta-llama/Llama-3.1-8B-Instruct) [documented; official Meta card](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/MODEL_CARD.md) | `LlamaForCausalLM`; Meta describes an autoregressive optimized Transformer with GQA and 128K context. The HF model card documents `apply_chat_template` generation. [documented](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct/tree/0e9e39f249a16976918f6564b8830bc894c89659) [documented](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/MODEL_CARD.md) | Manual-gated access requiring agreement and contact-information sharing; custom Llama 3.1 Community License and Acceptable Use Policy. The pinned HF tree exposes four BF16 shards of 4.98, 5.00, 4.92, and 1.17 GB, about 16.07 GB of weight files. [documented](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct/tree/0e9e39f249a16976918f6564b8830bc894c89659) [documented](https://github.com/meta-llama/llama-models/blob/main/models/llama3_1/LICENSE) | **Conditional only.** BF16 memory is plausibly within one 24-GiB 3090 for short contexts, but manual gating, a non-OSI custom license, access reproducibility, and the unverified block count are hard-gate risks. Excluding gated models would reject this candidate before backend scoring. [inferred—requires preflight] |

### Lower-boundary license screen

**Qwen/Qwen2.5-3B-Instruct** is in the numeric range and technically small:
Qwen documents 3.09B parameters, 36 layers, `Qwen2ForCausalLM`, 32,768-token
configured context, `apply_chat_template`, and a 6.18 GB BF16 repository
footprint. However, its official LICENSE is the **Qwen Research License**, which
grants use for non-commercial purposes only and requires a separate license for
commercial use. [documented](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct)
[documented](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/blob/main/LICENSE)

Its current mutable `main` page was sufficient to document the facts above, but
this pass did not recover a full immutable repository SHA for the current
`main` head. Therefore it is not eligible for an immutable-revision gate yet.
[unknown—requires exact revision pin] It should remain a fallback lead, not a
joint-tuple recommendation, unless the license and revision gates are
explicitly accepted.

## Local target environment

- `[directly verified]` Python 3.12.3; package metadata: PyTorch
  `2.4.0+cu124`, CUDA runtime reported by PyTorch `12.4`, Transformers `5.12.1`,
  vLLM `0.11.2`, and bitsandbytes `0.49.2`. `torch.cuda.is_available()` was
  true. These are inventory facts only; no model path was run.
- `[directly verified]` The inspected host exposes eight NVIDIA RTX 3090 GPUs,
  each with 24,576 MiB total VRAM, driver `580.159.03`; free VRAM at the
  observation ranged from 5,847 to 17,815 MiB. Availability is transient and
  must be rechecked immediately before an approved preflight.
- `[unknown]` The host’s exact CUDA driver/runtime compatibility with the
  eventual quantizer kernels, the installed vLLM build’s support for the
  selected model revision, and the availability of a clean isolated GPU are
  not established by package import or `nvidia-smi` alone.

## Joint-tuple implications, not a selection

| Model | Plausible software/runtime tuple to test | Why it is a joint candidate | Blocking unknowns |
|---|---|---|---|
| Qwen2.5-7B-Instruct | Pinned Transformers/vLLM plus the backend selected by Issue #8-B on one RTX 3090 | Native Qwen2 architecture, 28 inspectable layers, Apache-2.0, non-gated access, and pinned sharded safetensors | True W8A16/W4A16, block-range assignment, module exclusions, kernel path, export/reload, and actual BF16/quantized generation |
| Mistral-7B-Instruct-v0.3 | Pinned Transformers or official Mistral inference/vLLM plus the selected backend on one RTX 3090 | Native Mistral architecture, 32 inspectable layers, Apache-2.0, non-gated access, and an official archive checksum | Same quantization and execution questions; Mistral inference’s install/build requirements must be checked against the final runtime |
| Phi-3.5-mini-instruct | Pinned Transformers with `trust_remote_code` or a runtime/backend that natively supports Phi-3, on one RTX 3090 | Lowest BF16 footprint and MIT license | Custom code trust boundary, exact block enumeration, quantizer support, and no silent fallback |
| Llama-3.1-8B-Instruct | Pinned Transformers/vLLM plus selected backend on one RTX 3090 | Familiar native Llama family and 128K model card context | Gated access/license; exact block config and all mixed-precision capability checks; reject if reproducibility gate excludes gated models |

The model cannot be selected independently of the backend: a candidate passes
the model screen only if the same tuple can load BF16 and construct, inspect,
and execute the required weight-only W8A16/W4A16 assignments. Backend support
for those semantics, contiguous block ranges, export/reload, and absence of
activation/KV quantization is **unknown** in this model-only pass and belongs to
the backend evidence and approved real-hardware preflight.

## Proposed lexicographic model-side gates

1. The tuple names one immutable model revision and the exact tokenizer files
   at an immutable revision; acquisition records source checksums, archive
   identity, and access procedure.
2. The model is a public, open decoder-only text model in the frozen 3B–8B
   range with a license acceptable for this research. Manual-gated models are
   excluded unless reproducible access is explicitly accepted as a decision.
3. The pinned model card/config identifies a causal-LM architecture and an
   inspectable transformer-layer count; custom remote code is allowed only if
   the selected backend and audit policy explicitly support it.
4. On one approved RTX 3090, a real full-model BF16 load and short neutral
   generation succeed without CPU fallback; memory headroom is recorded.
5. The same tuple supports true weight-only W8A16 and W4A16, with activation and
   KV-cache quantization disabled, and can assign requested precisions to
   contiguous transformer-block ranges. This requires direct backend evidence
   and preflight, not model-card inference.
6. The constructed assignment is inspectable and, where the selected path
   serializes variants, export/reload preserves the requested map.
7. Exact GPU architecture, CUDA/driver/PyTorch/backend versions, disk headroom,
   and compile requirements are recorded; no final-test outcome informs any
   gate or candidate choice.

## Bottom line for the parent decision

The primary open, non-gated, immutable-revision model candidates with the
cleanest model-side joint implications are **Qwen2.5-7B-Instruct** and
**Mistral-7B-Instruct-v0.3**. That is a research prioritization for backend
preflight, not an accepted selection. Phi-3.5-mini is a lower-memory fallback
with custom-code risk. Llama 3.1 is technically plausible but gated and
license-constrained. No candidate reaches the Issue #8 closure gate without
the separate backend evidence and authorized real full-model preflight.
