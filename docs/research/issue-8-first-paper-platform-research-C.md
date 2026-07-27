# Issue 8 hardware/runtime research (subagent C)

**Scope.** Hardware and runtime evidence only: RTX 3090/SM86 support, CUDA and
PyTorch compatibility, memory feasibility, compilation, and fallback risks for
plausible weight-only backends. This note does not select a model, launch model
work, download anything, or claim a completed capability preflight.

**Evidence labels.** `Documented` means the owning primary source states the
claim. `Directly verified` means observed read-only on this checkout/host.
`Inferred—preflight required` is a calculation or compatibility inference that
must not be treated as execution evidence. `Unknown` means not established.

## Hardware and CUDA

- **Documented:** NVIDIA lists GeForce RTX 3090 under compute capability 8.6;
  the RTX 3090 product page lists 24 GB GDDR6X memory. Sources: [NVIDIA CUDA
  GPU compute capability table](https://developer.nvidia.com/cuda/gpus),
  [NVIDIA RTX 3090 specifications](https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3090-3090ti/).
- **Documented:** NVIDIA's Ampere guide identifies SM 8.6, recommends compiling
  explicitly for 8.6, and documents BF16 Tensor Core support plus signed/unsigned
  8-bit and 4-bit integer MMA instructions. Source: [Ampere GPU Architecture
  Tuning Guide](https://docs.nvidia.com/cuda/ampere-tuning-guide/index.html).
- **Directly verified (2026-07-27, read-only):** all eight visible devices are
  `NVIDIA GeForce RTX 3090`, compute capability `8.6`, with `24576 MiB` each;
  the host driver reports `580.159.03`. Observed free memory was 5,847–17,815
  MiB and GPU utilization was 32–100%, so this is not an availability claim and
  no device was selected for work.
- **Documented:** CUDA 12.4 lists Linux driver >=550.54.14 as its toolkit
  driver and >=525.60.13 for minor-version compatibility; NVIDIA also states
  that newer drivers retain backward compatibility. Source: [CUDA 12.4 release
  notes](https://docs.nvidia.com/cuda/archive/12.4.0/cuda-toolkit-release-notes/).
- **Inferred—preflight required:** the observed 580.159.03 driver is newer than
  the CUDA 12.4 requirement, so a CUDA-12.4-linked PyTorch process should be a
  viable compatibility candidate on SM86. This does not prove that every
  quantization extension or kernel in the installed environment loads.

## Local software inventory and compatibility

The following is directly verified from Python package metadata and `nvidia-smi`;
it is an environment snapshot, not a proposed pin set:

| Component | Observed version | Relevant result |
| --- | --- | --- |
| Python | 3.12.3 | Directly verified |
| PyTorch | 2.4.0+cu124 | Directly verified; `torch.version.cuda == 12.4`, CUDA available, 8 devices |
| Transformers | 5.12.1 | Directly verified |
| bitsandbytes | 0.49.2 | Directly verified; its diagnostic found CUDA 12.4, SM 8.6, and returned `SUCCESS!` |
| compressed-tensors | 0.12.2 | Directly verified |
| vLLM | 0.11.2 | Directly verified, but its installed metadata requires `torch==2.9.0` and `transformers<5` |
| Triton | 3.0.0 | Directly verified |
| flash-attn | 2.8.3.post1 | Directly verified; wheel URL identifies CUDA 12 / torch 2.4 / CPython 3.12 |

- **Documented:** the official PyTorch previous-version page publishes a Linux
  CUDA 12.4 install for PyTorch 2.4.0. Source: [PyTorch 2.4.0 previous
  versions](https://pytorch.org/get-started/previous-versions/).
- **Directly verified:** `python -m bitsandbytes` completed its CUDA check with
  `PyTorch: 2.4.0+cu124`, `CUDA: 12.4`, `Highest Compute Capability: (8, 6)`,
  and `SUCCESS!`. This verifies library import/CUDA callability only; it does
  not verify a full model, W8A16/W4A16 semantics, or a mixed schedule.
- **Directly verified:** the present vLLM installation is not a reproducible
  vLLM runtime tuple: its package metadata requires `torch==2.9.0` and
  `transformers<5`, conflicting with the installed torch 2.4.0 and Transformers
  5.12.1. Do not use this environment as vLLM preflight evidence. A synchronized
  vLLM environment must be created only after approval; no install was attempted.

## Quantization semantics and backend evidence

- **Documented:** `compressed-tensors` explicitly distinguishes weight-only
  `W4A16`, `W8A16`, and `WnA16` from activation quantization `W8A8` and KV-cache
  quantization, and states that different layers can use different schemes.
  Sources: [compressed-tensors project source/README](https://github.com/vllm-project/compressed-tensors),
  [quantization scheme source](https://github.com/vllm-project/compressed-tensors/blob/main/src/compressed_tensors/quantization/quant_scheme.py).
- **Documented:** the LLM Compressor project lists W4A16/W8A16 mixed precision,
  GPTQ, AWQ, and AutoRound, and provides INT4 weight-only examples that save
  checkpoints for vLLM. Source: [LLM Compressor repository](https://github.com/vllm-project/llm-compressor).
- **Documented:** the vLLM 0.11.2 INT4 guide defines an INT4 W4A16 path, requires
  `llmcompressor` for quantization, uses integer weights with grouped scales in
  its GPTQ example, and says INT4 computation is supported for compute capability
  >8.0. SM86 therefore meets this documented threshold. Source: [vLLM 0.11.2
  INT4 W4A16 guide](https://docs.vllm.ai/en/v0.11.2/features/quantization/int4/).
- **Documented:** vLLM 0.11.2's compatibility table marks AWQ, GPTQ, Marlin
  (GPTQ/AWQ/FP8), BitBLAS, and bitsandbytes as supported on Ampere (SM8.0/8.6).
  The same page marks FP8 W8A8 unsupported on Ampere. Source: [vLLM 0.11.2
  quantization hardware table](https://docs.vllm.ai/en/v0.11.2/features/quantization/).
- **Documented:** bitsandbytes supports NVIDIA CC 6.0+, but its LLM.int8()
  feature requires CC 7.5+; NF4/FP4 requires CC 6.0+. Its published Linux
  wheels include `sm86` targets for CUDA 11.8–13.0 ranges. Sources: [official
  bitsandbytes installation requirements](https://huggingface.co/docs/bitsandbytes/installation),
  [official bitsandbytes overview](https://huggingface.co/docs/bitsandbytes/index).
- **Documented:** bitsandbytes' 4-bit choices are NF4 or FP4, while LLM.int8()
  uses vector-wise 8-bit quantization with separate 16-bit outlier matmuls.
  Consequently, bitsandbytes is not automatically evidence for the study's
  exact integer `INT4` or simple uniform `INT8` definition. Source: [official
  bitsandbytes documentation](https://huggingface.co/docs/bitsandbytes/index).
- **Inferred—preflight required:** the compressed-tensors/LLM Compressor path is
  the clearest source-supported candidate for true integer W8A16/W4A16 with
  export/reload and non-uniform module schemes. It still requires a selected
  model-specific quantization recipe, exact version/commit pins, and runtime
  inspection proving that requested contiguous transformer-block assignments
  execute as quantized kernels rather than dequantized or CPU paths.

## Candidate joint runtime tuples (not decisions)

| Candidate tuple | What primary sources support | Current status / gate |
| --- | --- | --- |
| Transformers + bitsandbytes 0.49.2 + PyTorch 2.4.0+cu124 + one RTX 3090 | CUDA importability on SM86; 8-bit and 4-bit primitives; vLLM docs also list bnb on Ampere | **Incomplete.** Direct bnb diagnostic passed, but NF4/FP4 and LLM.int8 semantics do not establish integer INT4/INT8 or block-contiguous mixed assignment. Full-model preflight required. |
| LLM Compressor + compressed-tensors 0.12.2 + vLLM 0.11.2 + PyTorch-compatible RTX 3090 environment | W4A16/W8A16, GPTQ/AWQ, non-uniform layer schemes, export/reload direction, Ampere vLLM support | **Source-supported but locally mismatched.** The installed vLLM metadata conflicts with the installed torch/Transformers. Rebuild/pin a coherent environment only with approval, then preflight. |
| GPTQ/AWQ checkpoint + vLLM Marlin on RTX 3090 | vLLM documents Marlin and GPTQ/AWQ support on Ampere | **Incomplete.** Exact quantizer, group size, excluded modules, checkpoint revision, and mixed contiguous-block construction are not fixed or verified here. |

No tuple is selected by this note. The tuples must be judged lexicographically:
official support; immutable pins and license/access; one-GPU BF16; true integer
W8A16 and W4A16; activation/KV quantization off; contiguous block assignment;
inspectable map; export/reload; exact SM86/software compatibility; and memory and
disk headroom. Any missing gate is a rejection or an explicit preflight blocker,
not a weighted-score trade-off.

## Memory and headroom

- **Documented:** each RTX 3090 has 24 GB device memory. Source: [NVIDIA RTX
  3090 specifications](https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3090-3090ti/).
- **Inferred—preflight required:** for a model with `P` parameters, raw dense
  weight storage is approximately `2P` bytes in BF16, `P` bytes at 8-bit, and
  `P/2` bytes at 4-bit, before scales, zero-points, unquantized modules,
  allocator/workspace, activations, and KV cache. For the provisional 3B–8B
  range this is approximately:

  | Parameter count | BF16 raw | W8 raw | W4 raw |
  | ---: | ---: | ---: | ---: |
  | 3B | 6.0 GB / 5.59 GiB | 3.0 GB / 2.79 GiB | 1.5 GB / 1.40 GiB |
  | 8B | 16.0 GB / 14.90 GiB | 8.0 GB / 7.45 GiB | 4.0 GB / 3.73 GiB |

  These are lower-bound arithmetic estimates, not measured footprints. They
  suggest that a conventional 3B–8B dense model may fit on one 24-GB card in
  BF16 and leaves substantially more weight headroom in W8/W4, but long context,
  generation length, model architecture, temporary quantization buffers, and
  runtime cache allocation can invalidate that inference. Exact model load and
  short neutral generation are hard gates.
- **Unknown:** usable disk headroom, model-specific parameter counts, peak
  conversion memory, KV-cache policy, and maximum preflight context/generation
  have not been established. No model or dataset was downloaded.

## Compilation and fallback risks

- **Documented:** NVIDIA recommends explicit SM86 compilation for Ampere; the
  vLLM package metadata requires `ninja`, and vLLM exposes multiple custom CUDA
  kernel families (including Marlin/BitBLAS). Sources: [NVIDIA Ampere guide](https://docs.nvidia.com/cuda/ampere-tuning-guide/index.html),
  [vLLM source tree](https://github.com/vllm-project/vllm/tree/v0.11.2).
- **Inferred—preflight required:** a successful Python import, checkpoint load,
  or reported quantization method is insufficient. The preflight must inspect
  actual module/block dtypes and packed parameters, capture kernel/backend
  selection, and fail the tuple if an unsupported kernel silently falls back to
  dequantized dense matmul, CPU execution, or activation/KV quantization.
- **Documented:** the vLLM INT4 guide requires calibration data for grouped INT4
  scales and shows `lm_compressor` as the quantization tool; this is a build/
  preparation requirement, not a runtime benchmark. Source: [vLLM INT4 guide](https://docs.vllm.ai/en/v0.11.2/features/quantization/int4/).
- **Unknown:** whether any selected backend can serialize and reload one model
  containing BF16, INT8, and INT4 contiguous transformer-block ranges without
  model-specific exclusions or a custom runtime path. This is the central
  hardware capability preflight gap and must remain open until measured.

## Required next empirical gate (after tuple approval and resource approval)

On one explicitly available RTX 3090, with a fresh coherent environment and no
final-test data: load/generate BF16, uniform integer W8A16, uniform integer
W4A16, and one nontrivial contiguous BF16/INT8/INT4 schedule. Record exact
package versions, driver/CUDA, GPU index, peak memory, commands, stdout/stderr,
requested-versus-observed module precision map, kernel path, and export/reload
results under the repository run contract. This note provides no execution
evidence for those gates.

## Reproducibility and scope limits

The local observations came from read-only `nvidia-smi`, Python/Torch device
properties, package metadata, and `python -m bitsandbytes`; no model was loaded,
no dependency was installed, no GPU job was launched, and no shared lab host was
assumed. No final-test model output, evaluator result, or target-suite result
informed these hardware/runtime findings.
