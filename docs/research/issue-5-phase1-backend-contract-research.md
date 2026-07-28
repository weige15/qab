# Issue #5 Phase 1: pinned backend contract research

**Status:** source-level evidence packet for Phase 1 implementation. No package
was installed, no model or dataset was downloaded, no model was loaded or
quantized, and no GPU workload was run.

**Date:** 2026-07-28

**Method:** one read-only research pass inspected only official upstream source
code, package metadata, and first-party NVIDIA/PyTorch documentation at the
pinned revisions in the Issue #5 plan.

## Evidence labels

- **Documented:** directly stated or implemented by the linked pinned primary source.
- **Inferred; preflight required:** follows from source behavior but requires a
  real approved model/runtime execution for Qwen and RTX 3090.
- **Unknown:** not established without loading the real model or frozen runtime.

## Findings

### Configuration-group semantics

**Documented.** config_groups maps scheme configurations to target modules.
The effective quantization target set is the union of targets in all groups; a
module matching no target is not quantized. ignore excludes a module even when
it matches a target. Group keys are labels for scheme assignments, not
transformer block ranges.

[LLM Compressor quantization mixin](https://github.com/vllm-project/llm-compressor/blob/129c793fdabfd9bc486f85c444bdec6b713978fe/src/llmcompressor/modifiers/quantization/quantization/mixin.py#L67-L76),
[effective target collection](https://github.com/vllm-project/llm-compressor/blob/129c793fdabfd9bc486f85c444bdec6b713978fe/src/llmcompressor/modifiers/quantization/quantization/mixin.py#L184-L217),
[compressed-tensors scheme model](https://github.com/vllm-project/compressed-tensors/blob/2dd1b627950b4a068f2c1af19bc6f31b7fbb3316/src/compressed_tensors/quantization/quant_scheme.py#L36-L53),
[scheme application](https://github.com/vllm-project/compressed-tensors/blob/2dd1b627950b4a068f2c1af19bc6f31b7fbb3316/src/compressed_tensors/quantization/lifecycle/apply.py#L111-L149).

Overlapping targets should be avoided because applying configuration creates a
target-to-scheme map. [Pinned apply implementation](https://github.com/vllm-project/compressed-tensors/blob/2dd1b627950b4a068f2c1af19bc6f31b7fbb3316/src/compressed_tensors/quantization/lifecycle/apply.py#L111-L149)

### BF16 exclusion

**Documented.** There is no separate BF16 quantization scheme for an unquantized
block. BF16 modules are represented by leaving paths out of integer target
groups; explicit exclusions such as lm_head use ignore. vLLM returns an
unquantized method when no compressed-tensors scheme matches a layer.

[Target matching and ignore](https://github.com/vllm-project/compressed-tensors/blob/2dd1b627950b4a068f2c1af19bc6f31b7fbb3316/src/compressed_tensors/utils/match.py#L39-L75),
[vLLM unmatched-layer behavior](https://github.com/vllm-project/vllm/blob/275de34170654274616082721348b7edd9741d32/vllm/model_executor/layers/quantization/compressed_tensors/compressed_tensors.py#L633-L724),
[pinned W4A16 recipe](https://github.com/vllm-project/llm-compressor/blob/129c793fdabfd9bc486f85c444bdec6b713978fe/tests/e2e/vLLM/recipes/actorder/recipe_w4a16_actorder_group.yaml#L1-L14).

**Implementation consequence.** Phase 1 retains BF16 in the requested map but
emits no BF16 integer config_group; BF16 module paths and frozen lm_head are
listed in ignore. This is a plan, not proof of runtime retention.

### W8A16 and W4A16 encoding

**Documented.** W8A16 is INT8, channel strategy, symmetric, static weights, with
no input-activation quantization arguments. W4A16 is INT4, group strategy,
normally group size 128, symmetric, static weights, also with no input-activation
quantization arguments. INT4 and INT8 packed schemes use pack_quantized.

[Scheme definitions](https://github.com/vllm-project/compressed-tensors/blob/2dd1b627950b4a068f2c1af19bc6f31b7fbb3316/src/compressed_tensors/quantization/quant_scheme.py#L185-L225),
[packed-format inference](https://github.com/vllm-project/compressed-tensors/blob/2dd1b627950b4a068f2c1af19bc6f31b7fbb3316/src/compressed_tensors/config/format.py#L31-L81),
[vLLM WNA16 mapping](https://github.com/vllm-project/vllm/blob/275de34170654274616082721348b7edd9741d32/vllm/model_executor/layers/quantization/compressed_tensors/compressed_tensors.py#L511-L566).

**Inference.** A16 denotes the 16-bit activation path; it is not evidence that
the real model ran in BF16 until runtime dtypes are inspected.

### Contiguous transformer-block target naming

**Documented.** Target matching supports exact module names, regular expressions,
and module classes. It is not recursive prefix matching, so model.layers.0
must not be assumed to target descendant projections. Official non-uniform
examples use regexes for projection paths, and vLLM handles full paths such as
model.layers.0.self_attn.qkv_proj.

[Pinned match implementation](https://github.com/vllm-project/compressed-tensors/blob/2dd1b627950b4a068f2c1af19bc6f31b7fbb3316/src/compressed_tensors/utils/match.py#L121-L156),
[matching details](https://github.com/vllm-project/compressed-tensors/blob/2dd1b627950b4a068f2c1af19bc6f31b7fbb3316/src/compressed_tensors/utils/match.py#L223-L286),
[official non-uniform example](https://github.com/vllm-project/llm-compressor/blob/129c793fdabfd9bc486f85c444bdec6b713978fe/examples/quantization_non_uniform/quantization_int4_int8.py#L50-L82),
[vLLM path utilities](https://github.com/vllm-project/vllm/blob/275de34170654274616082721348b7edd9741d32/vllm/model_executor/layers/quantization/compressed_tensors/utils.py#L85-L131).

**Inferred; preflight required.** A contiguous group must expand into explicit
projection paths or equivalent regexes. The exact Qwen module layout and any
vLLM fusion/renaming are Unknown because Qwen loading was prohibited. The
planner therefore keeps projection suffixes configuration-driven and records
the resulting exact paths for later comparison.

### Export/reload preservation

**Documented.** Compressor save hooks write compressed weights and update model
configuration. compressed-tensors reload reconstructs compressors and schemes
from serialized qconfig_data, including groups, formats, ignored modules, and
status. vLLM reconstructs a per-target scheme map from config_groups.

[Compressor save hooks](https://github.com/vllm-project/llm-compressor/blob/129c793fdabfd9bc486f85c444bdec6b713978fe/src/llmcompressor/transformers/compression/compressed_tensors_utils.py#L27-L107),
[reload reconstruction](https://github.com/vllm-project/compressed-tensors/blob/2dd1b627950b4a068f2c1af19bc6f31b7fbb3316/src/compressed_tensors/compressors/model_compressors/model_compressor.py#L87-L105),
[serialized qconfig](https://github.com/vllm-project/compressed-tensors/blob/2dd1b627950b4a068f2c1af19bc6f31b7fbb3316/src/compressed_tensors/compressors/model_compressors/model_compressor.py#L678-L820),
[vLLM per-target reconstruction](https://github.com/vllm-project/vllm/blob/275de34170654274616082721348b7edd9741d32/vllm/model_executor/layers/quantization/compressed_tensors/compressed_tensors.py#L205-L263).

**Inferred; preflight required.** Mixed W4A16/W8A16 assignments are designed to
survive serialization, but no successful export/reload of the frozen Qwen
artifact has been demonstrated. pack_quantized at the top level does not prove
every mixed target retained its individual scheme.

### vLLM kernel selection and inspection

**Documented.** vLLM selects CompressedTensorsLinearMethod for a supported
matched scheme. WNA16 requires compute capability 8.0 or higher. Kernel
selection checks device capability, disabled-kernel settings, and each backend's
can_implement constraints, then chooses the first passing backend.

[Method selection](https://github.com/vllm-project/vllm/blob/275de34170654274616082721348b7edd9741d32/vllm/model_executor/layers/quantization/compressed_tensors/compressed_tensors.py#L129-L162),
[WNA16 capability gate](https://github.com/vllm-project/vllm/blob/275de34170654274616082721348b7edd9741d32/vllm/model_executor/layers/quantization/schemes/compressed_tensors_wNa16.py#L74-L77),
[mixed-precision backend selection](https://github.com/vllm-project/vllm/blob/275de34170654274616082721348b7edd9741d32/vllm/model_executor/layers/quantization/kernels/mixed_precision/__init__.py#L35-L105).

For each loaded module, inspect layer.scheme, quant_type.size_bits, strategy,
group size, symmetry, has_g_idx, and layer.scheme.kernel; also inspect packed
parameter names/dtypes/devices and backend logs.
[Scheme assignment](https://github.com/vllm-project/vllm/blob/275de34170654274616082721348b7edd9741d32/vllm/model_executor/layers/quantization/compressed_tensors/compressed_tensors.py#L633-L724),
[WNA16 scheme/kernel fields](https://github.com/vllm-project/vllm/blob/275de34170654274616082721348b7edd9741d32/vllm/model_executor/layers/quantization/schemes/compressed_tensors_wNa16.py#L38-L109).

**Inferred; preflight required.** Configuration generation cannot establish the
realized kernel, no CPU fallback, or actual dtype/device.

### RTX 3090 / SM86 restrictions

**Documented.** NVIDIA identifies RTX 3090 as compute capability 8.6. WNA16's
8.0 minimum makes SM86 source-level eligible for that family, subject to shape,
group-size, build, and environment checks. Cutlass W4A8 and Machete require
compute capability 9.0 and are not SM86 paths. AllSpark and Marlin declare
minimum capability 8.0 and may be candidates. ExLlama requires FP16 activations
and is not automatically compatible with BF16 activations.

[NVIDIA GPU table](https://developer.nvidia.com/cuda/gpus),
[Cutlass gate](https://github.com/vllm-project/vllm/blob/275de34170654274616082721348b7edd9741d32/vllm/model_executor/layers/quantization/kernels/mixed_precision/cutlass.py#L17-L68),
[Machete gate](https://github.com/vllm-project/vllm/blob/275de34170654274616082721348b7edd9741d32/vllm/model_executor/layers/quantization/kernels/mixed_precision/machete.py#L24-L64),
[AllSpark gate](https://github.com/vllm-project/vllm/blob/275de34170654274616082721348b7edd9741d32/vllm/model_executor/layers/quantization/kernels/mixed_precision/allspark.py#L18-L37),
[Marlin gate](https://github.com/vllm-project/vllm/blob/275de34170654274616082721348b7edd9741d32/vllm/model_executor/layers/quantization/kernels/mixed_precision/marlin.py#L28-L60),
[ExLlama gate](https://github.com/vllm-project/vllm/blob/275de34170654274616082721348b7edd9741d32/vllm/model_executor/layers/quantization/kernels/mixed_precision/exllama.py#L17-L63).

PyTorch 2.9.0 source treats CUDA devices with major capability at least 8 as
BF16-supported, but that architecture check is not a successful model run.
[PyTorch v2.9.0 CUDA source](https://github.com/pytorch/pytorch/blob/0fabc3ba44823f257e70ce397d989c8de5e362c1/torch/cuda/__init__.py#L185-L218)

### Coherent package/runtime versions

**Documented.** vLLM 0.11.2 supports Python 3.10–3.13, uses PyTorch 2.9.0,
pins compressed-tensors==0.12.2, and requires Transformers >=4.56.0,<5.
[vLLM package metadata](https://github.com/vllm-project/vllm/blob/275de34170654274616082721348b7edd9741d32/pyproject.toml#L1-L34)
[vLLM common requirements](https://github.com/vllm-project/vllm/blob/275de34170654274616082721348b7edd9741d32/requirements/common.txt#L1-L52)

**Blocking conflict.** The requested LLM Compressor revision's release metadata
requires compressed-tensors==0.13.0, not 0.12.2. Thus the exact LLM Compressor
0.9.0 revision and frozen compressed-tensors 0.12.2 pin are not demonstrably
metadata-coherent. The non-quantization intersection is approximately Python
>=3.10,<3.14, PyTorch 2.9.0, and Transformers >=4.56.0,<5; the
compressor/backend conflict requires a dated decision before installation or
GPU preflight.

[LLM Compressor setup metadata](https://github.com/vllm-project/llm-compressor/blob/129c793fdabfd9bc486f85c444bdec6b713978fe/setup.py#L112-L153),
[compressed-tensors setup metadata](https://github.com/vllm-project/compressed-tensors/blob/2dd1b627950b4a068f2c1af19bc6f31b7fbb3316/setup.py#L90-L117).

## Consequences for Phase 1

- The planner expands contiguous ranges into explicit module paths and does not
  treat a configuration-group key as a transformer group.
- BF16 paths stay in the requested map but are omitted from integer target groups.
- W8A16/W4A16 metadata is a candidate compressed-tensors-style configuration;
  no capability, kernel, export/reload, or resource result is inferred.
- Runtime implementation must resolve the version conflict before package
  installation and must inspect layer.scheme, layer.scheme.kernel, parameter
  dtype/device, CPU fallback, export digest, and fresh-process reload.
- Exact Qwen module layout, fused names, runtime kernel, memory fit, generation,
  and successful mixed export/reload remain Unknown.
