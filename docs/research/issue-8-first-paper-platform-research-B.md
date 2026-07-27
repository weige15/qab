# Issue #8 backend research: quantization backends

**Subagent:** B (quantization backends)  
**Date:** 2026-07-27  
**Scope:** backend and runtime evidence only. No model/data download, package
installation, model inference, GPU job, benchmark, or final-test outcome was
used. This note does not select the Issue #8 tuple.

## Evidence labels

- **Documented:** stated by the cited primary documentation or source.
- **Directly verified:** observed read-only in the current environment.
- **Inferred; preflight required:** a direct engineering consequence of a
  documented API, but not evidence of a working full-model path.
- **Unknown:** not established by the sources or local inspection.

## Common model/hardware anchor for joint tuples

To compare backends as complete tuples rather than retrofit a backend after
model selection, the rows below use the same candidate model: `Qwen/Qwen2.5-7B-
Instruct` at immutable revision
[`a09a35458c702b33eeacc393d103063234e8bc28`](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/tree/a09a35458c702b33eeacc393d103063234e8bc28).
The repository contains the tokenizer and chat-template files at that same
revision. **Documented:** the model is a Qwen2 decoder-only causal-LM family
checkpoint; the exact model architecture and tokenizer behavior must still be
checked after obtaining the pinned snapshot. The vLLM 0.11.2 supported-model
table lists `Qwen2ForCausalLM` and Qwen2-7B examples
([primary source](https://docs.vllm.ai/en/v0.11.2/models/supported_models/)).

**Directly verified:** the visible host has eight `NVIDIA GeForce RTX 3090`
devices, each reporting 24,576 MiB and compute capability `8.6`; free memory
at inspection was 17,609, 6,697, 15,155, 5,847, 17,403, 13,594, 17,815, and
14,137 MiB respectively. This is an environment observation, not a resource
reservation or availability guarantee. **Documented:** NVIDIA lists the RTX
3090 as Ampere with 24 GB GDDR6X
([specification](https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3090-3090ti/));
NVIDIA's CUDA documentation identifies RTX 3090-class Ampere as SM86
([CUDA GPU table](https://developer.nvidia.com/cuda/gpus)).

## Local software observations

**Directly verified, read-only:** Python is `3.12.3`; installed packages are
`torch==2.4.0+cu124`, `transformers==5.12.1`, `accelerate==1.14.0`,
`bitsandbytes==0.49.2`, `compressed-tensors==0.12.2`, and `vllm==0.11.2`.
`torchao`, `hqq`, `llmcompressor`, and `tensorrt_llm` were not present in the
package listing. No imports that load weights and no GPU computation were run.

The exact source tag commits queried from the official repositories are:

| Component | Release/tag | Commit |
|---|---|---|
| PyTorch | `v2.4.0` | `d990dada86a8ad94882b5c23e859b88c0c255bda` |
| vLLM | `v0.11.2` | `275de34170654274616082721348b7edd9741d32` |
| compressed-tensors | `0.12.2` | `2dd1b627950b4a068f2c1af19bc6f31b7fbb3316` |
| bitsandbytes | `0.49.2` | `f0e6ca31b32c4744a9cee4e31610b25796cbf778` |
| LLM Compressor | `0.9.0` | `129c793fdabfd9bc486f85c444bdec6b713978fe` |
| torchao | `v0.17.0` | `02105d46c61dc80a8c9d39d5836e827ba3af8439` |
| HQQ | `v0.2.8` | `f62d06e45d0ad0327a045ade383f92b258e0ca27` |
| TensorRT-LLM | `v1.2.1` | `376f7e1bd8ed543f75014309e3fd4b237e9b0e73` |

The tag-to-commit mappings were obtained with read-only `git ls-remote` calls
against the official repositories. Source/release links: [PyTorch](https://github.com/pytorch/pytorch/tree/v2.4.0),
[vLLM](https://github.com/vllm-project/vllm/tree/v0.11.2),
[compressed-tensors](https://github.com/vllm-project/compressed-tensors/tree/0.12.2),
[bitsandbytes](https://github.com/bitsandbytes-foundation/bitsandbytes/tree/0.49.2),
[LLM Compressor](https://github.com/vllm-project/llm-compressor/tree/0.9.0),
[torchao](https://github.com/pytorch/ao/tree/v0.17.0),
[HQQ](https://github.com/dropbox/hqq/tree/v0.2.8), and
[TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM/tree/v1.2.1).

The local pins are not a compatibility proof: `llmcompressor` and TensorRT-LLM
are absent, and the installed vLLM/compressed-tensors pair has not loaded a
checkpoint. **Unknown:** the target lab's driver, host CUDA toolkit, Python
environment, compiler, and package compatibility beyond the observations above.

## Semantics required by Issue #8

**Documented:** LLM Compressor defines `W4A16/W8A16` as 4- or 8-bit weights
with 16-bit activations, with the scheme targeting weights; its scheme table
lists Ampere as suitable and vLLM minimum compute capability 7.5
([scheme guide](https://docs.vllm.ai/projects/llm-compressor/en/stable/steps/choosing-scheme/)).
The quantization API documents `input_activations: null` for weight-only
configurations and `kv_cache_scheme: null` as the no-KV-quantization setting
([API](https://docs.vllm.ai/projects/llm-compressor/en/stable/api/llmcompressor/modifiers/quantization/)).
The selected recipe must explicitly set those fields and exclude activation and
KV-cache quantization; a backend's general ability to quantize activations or
KV cache is not evidence that the study path does so.

**Documented:** LLM Compressor exposes PTQ modifiers including GPTQ and AWQ;
release 0.9.0 documents AutoRound and generalized AWQ support
([release notes](https://github.com/vllm-project/llm-compressor/releases/tag/0.9.0)).
GPTQ exposes weight bit width, type, symmetric/asymmetric choice, strategy,
group size, targets, and ignore patterns in its configuration
([GPTQ API](https://docs.vllm.ai/projects/llm-compressor/en/stable/api/llmcompressor/modifiers/quantization/)).
The exact algorithm, scale granularity, group size, excluded modules, and
calibration subset remain a decision dependency for Issue #8; they must not be
silently taken from a backend default.

## Candidate complete tuples

All rows use the Qwen checkpoint and RTX 3090/SM86 anchor above. “Mixed block
groups” means the project's contiguous transformer-block ranges, not the
smaller tensor quantizer groups.

| Tuple | Exact backend/runtime pins | What primary sources establish | Mixed contiguous block-group status | Main risk |
|---|---|---|---|---|
| **A: LLM Compressor → compressed-tensors → vLLM** | LLM Compressor `0.9.0` @ `129c793`; compressed-tensors `0.12.2` @ `2dd1b62`; vLLM `0.11.2` @ `275de34`; PyTorch `2.4.0+cu124` @ `d990dad`; Transformers `5.12.1`; RTX 3090 SM86 | **Documented:** W4A16/W8A16, GPTQ/AWQ/RTN-style weight schemes, config groups, targets/ignore patterns, and compressed checkpoint saving are supported by LLM Compressor/compressed-tensors. Mixed formats are recorded in `config.json`; local formats are recorded per config group. The resulting compressed model is intended to load in vLLM ([non-uniform example](https://docs.vllm.ai/projects/llm-compressor/en/latest/examples/quantization_non_uniform/), [compressed-tensors source](https://github.com/vllm-project/compressed-tensors/tree/0.12.2)). **Documented:** vLLM 0.11.2 lists Qwen2 causal-LM support. | **Inferred; preflight required:** target patterns can name the linear modules within a contiguous set of `model.layers.N...`; selecting BF16 by leaving other groups unquantized is expressible. The sources do not prove construction of a complete BF16/INT8/INT4 transformer-block schedule, map inspection, reload, or execution for this exact Qwen revision. | Compatibility between these exact package pins, Qwen revision, group size, kernel, and SM86 is **unknown**. LLM Compressor 0.9.0 also supports KV/activation quantization, so the no-activation/no-KV recipe must be checked. |
| **B: TensorRT-LLM** | TensorRT-LLM `1.2.1` @ `376f7e1`; its Model Optimizer dependency/revision is **unknown**; PyTorch/Transformers conversion environment and CUDA/TensorRT versions are **unknown**; RTX 3090 SM86 | **Documented:** the official quantization README defines `int8_wo` and `int4_wo` and shows `MIXED_PRECISION` with per-layer `quant_cfg.json`; unlisted layers remain unquantized. It documents W4A16 AWQ/GPTQ metadata and engine/checkpoint deployment ([README at pinned tag](https://github.com/NVIDIA/TensorRT-LLM/blob/v1.2.1/examples/quantization/README.md)). NVIDIA documents TensorRT support for SM 7.5+ and CUDA/driver prerequisites ([support matrix](https://docs.nvidia.com/deeplearning/tensorrt/latest/getting-started/support-matrix.html)). | **Inferred; preflight required:** `quantized_layers` can be generated for consecutive transformer-layer ranges, giving a strong schedule representation. The source does not prove the Qwen checkpoint conversion, actual contiguous mixed engine, post-build precision-map inspection, or reload on this host. | Engine build is required; serialized engines are hardware/build sensitive. Exact Model Optimizer, TensorRT, CUDA, driver, Qwen architecture, and SM86 kernel support are **unknown**. This is the most explicit per-layer representation but the least locally prepared tuple. |
| **C: torchao eager/compiled PyTorch** | torchao `v0.17.0` @ `02105d4`; PyTorch `2.4.0+cu124` @ `d990dad`; Transformers `5.12.1`; RTX 3090 SM86 | **Documented:** `Int8WeightOnlyConfig` is symmetric per-channel weight-only; `Int4WeightOnlyConfig` is groupwise weight-only. `quantize_` changes linear modules in place, and `FqnToConfig` maps different configs or `None` to fully-qualified module names ([API](https://docs.pytorch.org/ao/stable/api_reference/api_ref_quantization.html), [FqnToConfig](https://docs.pytorch.org/ao/stable/api_reference/generated/torchao.quantization.FqnToConfig.html), [inference workflows](https://docs.pytorch.org/ao/stable/workflows/inference.html)). | **Inferred; preflight required:** FQN mapping can assign INT4, INT8, or no quantization to linear modules selected by transformer-layer index, so contiguous block ranges are expressible at module level. It is not documented as a ready-made Qwen schedule/export/runtime path. Safetensors support exists in torchao release notes, but exact mixed-checkpoint save/reload and runtime map inspection for Qwen are **unknown**. | The local PyTorch 2.4.0 pin is not shown by the torchao 0.17 documentation as a compatible pair; torchao is absent locally. CUDA/SM86 kernel coverage for these exact configs and Qwen architecture is **unknown**. |
| **D: bitsandbytes + Transformers** | bitsandbytes `0.49.2` @ `f0e6ca3`; PyTorch `2.4.0+cu124`; Transformers `5.12.1`; Accelerate `1.14.0`; RTX 3090 SM86 | **Documented:** Transformers replaces linear layers with `Linear8bitLt` for `load_in_8bit` and `Linear4bit` for `load_in_4bit`; 4-bit exposes NF4/FP4 and a BF16 compute dtype. The integration exposes module skipping for 8-bit and documents checkpoint loading/saving flows ([Transformers integration](https://huggingface.co/docs/transformers/main/quantization/bitsandbytes), [BitsAndBytesConfig](https://huggingface.co/docs/transformers/main_classes/quantization)). bitsandbytes documents NVIDIA CUDA support and hardware requirements ([installation](https://huggingface.co/docs/bitsandbytes/main/en/installation)). | **Not documented; high-risk inference:** module replacement could be manually extended to selected layer ranges, but the official integration does not provide a single model containing BF16, W8, and W4 contiguous transformer-block ranges, nor a schedule manifest/map inspection API. Uniform W4A16 is the closest documented path. `load_in_8bit` is LLM.int8 with outlier handling, not automatically equivalent to the study's strict W8A16 definition; this requires an explicit semantic decision and preflight. | Best local availability, but no documented mixed schedule construction. Peak memory, pure weight-only semantics for W8, export/reload of a manually mixed model, and kernel path on SM86 are **unknown**. |
| **E: HQQ + Transformers/PyTorch** | HQQ `v0.2.8` @ `f62d06e`; PyTorch/Transformers versions and optional CUDA backend **unknown**; RTX 3090 SM86 | **Documented:** HQQ supports 1–8-bit weight quantization and its Transformers integration accepts `HqqConfig(dynamic_config=...)` for layer-specific configurations. The project documents `save_pretrained`/`from_pretrained` reload of quantized Transformers models ([official HQQ README](https://github.com/dropbox/hqq/tree/v0.2.8)). | **Inferred; preflight required:** dynamic per-layer configs can encode contiguous layer ranges and leave other ranges BF16. No primary source inspected here proves one mixed BF16/INT8/INT4 Qwen model executing with the intended CUDA kernel or a precision-map audit. | HQQ has no established vLLM/TensorRT serving path in the cited sources; exact CUDA/SM86 optimized backend, Qwen support, and serialization of a heterogeneous schedule are **unknown**. |

## Backend comparison and provisional ordering

**Inferred; preflight required:** Tuple A is the strongest first capability
preflight candidate because it is the only candidate whose primary sources
jointly document the required W4A16/W8A16 schemes, mixed config groups, saved
compressed representation, and a deployment engine that explicitly lists the
Qwen2 architecture. Tuple B has the strongest explicit per-layer serialized
schedule representation but the heaviest unverified conversion/build stack.
Tuple C is attractive for inspectable Python-level FQN control but has a local
version mismatch risk. Tuple D is locally installed and useful as a uniform
baseline, but does not establish mixed contiguous block groups and its W8 path
needs semantic scrutiny. Tuple E has attractive layer-specific configuration
and reload, but no established deployment/runtime path.

This ordering is not a final selection and must not be converted into a
weighted score. A tuple fails Issue #8 closure unless it reaches the required
real full-model BF16, W8A16, W4A16, and one contiguous mixed-schedule preflight.

## Hard gates for backend eligibility

1. Open decoder-only model in the frozen 3B–8B range; immutable model and
   tokenizer revisions.
2. Reproducible public access and acceptable license; gated access is excluded
   unless separately approved as reproducible before selection.
3. One RTX 3090 must load the full pinned model and generate in BF16.
4. The backend must implement true **weight-only** W8A16 and W4A16: weights
   are INT8/INT4, activations remain BF16/FP16, activation quantization is
   disabled, and KV-cache quantization is disabled.
5. The backend must assign different precisions to contiguous transformer-block
   ranges, not merely use tensor-internal quantizer groups; this must be
   inspectable after construction.
6. The selected path must export/save and reload schedule variants when the
   experimental execution path uses serialized checkpoints or engines.
7. Exact SM86, CUDA, driver, PyTorch, backend, compiler/kernel, and model
   architecture compatibility must be verified on the target host.
8. There must be measured memory and disk headroom for BF16 source weights,
   quantization intermediates, quantized artifacts, runtime state, and short
   preflight generation.
9. No final-test prompt, output, evaluator result, or leaderboard outcome may
   inform backend/model selection.

## Required empirical checks before treating a backend as eligible

For the selected tuple, the real-hardware preflight must record the immutable
run contract and verify BF16, uniform W8A16, uniform W4A16, and one nontrivial
BF16/INT8/INT4 contiguous-block schedule. It must inspect every targeted module,
the serialized metadata, and the reloaded artifact where applicable. It must
also prove that no activation/KV quantization, CPU fallback, unsupported-kernel
fallback, or dequantized execution path invalidates the claimed format. This is
capability evidence only; it is not latency, quality, codebook, predictor, or
final-test work.

## Unresolved backend decisions

- Exact A16 activation dtype (BF16 versus FP16), algorithm, scale granularity,
  group size, excluded modules, calibration data, and whether these belong in
  Issue #8 or a newly surfaced decision ticket remain unresolved.
- Exact target driver/CUDA/PyTorch/backend compatibility and resource
  allocation remain unknown; the current `nvidia-smi` output is not a booking.
- The exact Qwen tokenizer/chat-template behavior and model snapshot checksum
  must be retained when the approved model is obtained.
- No backend in this note has passed the real full-model closure gate. No
  final-test outcome informed any claim.

