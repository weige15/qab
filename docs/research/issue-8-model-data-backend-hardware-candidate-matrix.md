# Issue #8: model, data, backend, and hardware candidate matrix

**Ticket:** [Choose the first-paper model, data sources, quantization backend,
and hardware target](https://github.com/weige15/qab/issues/8)

**Research date:** 2026-07-27  
**Status:** Evidence packet only. No final stack is selected by this artifact.

## Decision boundary

Issue #8 asks for one open decoder-only model in the 3B–8B range, real request
sources and split plan, a weight-only quantization backend, and a one-GPU or
homogeneous-GPU target, with executable BF16/W8A16/W4A16 paths. The repository
also prohibits downloading models or data, installing dependencies, or running
large local experiments for this decision. The ticket must not be resolved from
final-test results. See the [ticket body](https://github.com/weige15/qab/issues/8)
and the repository's [research specification](../research-spec.md).

The matrix deliberately separates:

- **Documented:** stated by the linked first-party source.
- **Inference:** a direct engineering implication of documented module- or
  layer-level controls; it still requires a real-path test.
- **Open:** not established by the sources and must be empirically verified.

Here, W8A16 and W4A16 mean 8- or 4-bit weights with 16-bit activations. The
project's allowed precisions are BF16, INT8, and INT4 weights only; KV-cache and
activation quantization are out of scope.

## Common data candidate: D1

The data choice below is not being re-opened here: it is the dataset bundle
already recorded in the repository after the Issue #7 resolution. It is
repeated in every candidate row so that each model/backend combination has an
explicit revision set.

| Source | Exact revision and role | License / access | Reproducibility status |
|---|---|---|---|
| MATH | hendrycks/math at 985bdc1696e88e8643f081a0ff4719da39f2ae2a; 7,500 train and 5,000 test source items; validation is carved from train before variants/composites | MIT; public repository [at the pinned commit](https://github.com/hendrycks/math/tree/985bdc1696e88e8643f081a0ff4719da39f2ae2a) | Strong source revision and evaluator code. Split manifest, prompt variants, and derived-composite identities remain project artifacts to pin before model-output runs. |
| HumanEval+ | Official release v0.1.10, evalplus/humanevalplus_release at 200defce9e3429d28ca215b6dd061c0f7f31c18b; 164 test-only function contracts. Evaluator evalplus/evalplus at e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2, corresponding to EvalPlus v0.3.1 | Original HumanEval terms plus EvalPlus Apache-2.0 project terms; [release commit](https://github.com/evalplus/humanevalplus_release/commit/200defce9e3429d28ca215b6dd061c0f7f31c18b), [evaluator commit](https://github.com/evalplus/evalplus/tree/e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2) | Release and evaluator revisions are pinned. It has no upstream train/validation split; any project validation carve must be declared before derived prompts/tests and cannot be inferred from final results. |
| MuSiQue-Full | Official MuSiQue v1.0 archive; evaluator StonyBrookNLP/musique at 24cc5b297acc2abfc5fb3d0becb6ef7b73d03717; train/dev/test, fixed supplied context, retrieval disabled | CC BY 4.0; [official repository and license statement](https://github.com/StonyBrookNLP/musique/tree/24cc5b297acc2abfc5fb3d0becb6ef7b73d03717) | **Incomplete:** the official archive identity is named but its exact archive URL/filename and SHA-256 are not yet recorded. These must be pinned before reproducible use. |

The repository's feasibility plan uses a first profile subset of 804 request
identities and an estimated 6,432–12,864 request-schedule executions, depending
on the unresolved schedule count. That is planning evidence, not a completed
run; see [the Issue #7 plan](../plans/issue-7-task-suite-evaluator-registry.md).

## Hardware and software target

The common hardware target is **one NVIDIA GeForce RTX 3090**, or a set of
homogeneous RTX 3090 devices for later batch simulation. NVIDIA lists 24 GB of
GDDR6X memory for the RTX 3090, and its CUDA compute-capability table lists the
RTX 3090 as **8.6 / SM86** ([NVIDIA product information](https://www.nvidia.com/en-us/geforce/news/rtx-3090-out-september-24/),
[NVIDIA compute-capability table](https://developer.nvidia.com/cuda/gpus)).

A reproducible PyTorch starting point is a CUDA 12.1 or CUDA 11.8 wheel for
torch 2.5.1; PyTorch publishes both choices in its official
[previous-version matrix](https://docs.pytorch.org/get-started/previous-versions/).
That page proves wheel availability, not compatibility of every optional
quantization kernel. The actual driver, toolkit/runtime, PyTorch build,
backend version, and SM86 kernel path still need to be recorded on the target
machine.

The lab hosts and allocation procedure remain Unknown as required by the
repository instructions. No availability check was run during this research.

## Candidate matrix

Every row uses **D1** exactly as specified above. The model revision is an
immutable Hugging Face commit; moving main branches must not be used for a run.

| ID | Candidate combination and exact model revision | License / reproducibility | BF16, W8A16, W4A16 execution path | Contiguous block-group schedules | RTX 3090 / CUDA / PyTorch status | Memory, disk, and setup |
|---|---|---|---|---|---|---|
| C1 | Qwen/Qwen2.5-7B-Instruct at a09a35458c702b33eeacc393d103063234e8bc28; D1 = MATH 985bdc1696e88e8643f081a0ff4719da39f2ae2a, HumanEval+ 200defce9e3429d28ca215b6dd061c0f7f31c18b / evaluator e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2, MuSiQue v1.0 / evaluator 24cc5b297acc2abfc5fb3d0becb6ef7b73d03717. [Model revision](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/tree/a09a35458c702b33eeacc393d103063234e8bc28) | Apache-2.0; public and ungated at the pinned revision. The published model snapshot is 15.2 GB. [Model card/files](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/tree/a09a35458c702b33eeacc393d103063234e8bc28) | BF16: load the pinned Transformers checkpoint with BF16 weights/compute, or use the BF16 vLLM path. W8A16: LLM Compressor weight-only INT8 (W8A16) to compressed-tensors, then vLLM. W4A16: LLM Compressor INT4 (W4A16, typically GPTQ/AWQ/RTN and group size selected before evaluation), then vLLM. The official scheme guide lists both formats and the W4A16 example documents an end-to-end compressed checkpoint. [Schemes](https://docs.vllm.ai/projects/llm-compressor/en/stable/steps/choosing-scheme/), [W4A16 example](https://docs.vllm.ai/projects/llm-compressor/en/latest/examples/quantization_w4a16/) | **Documented at layer/module level; group schedule is an inference.** LLM Compressor documents mixed precision, multiple config groups, and precision assigned by layer group. Mapping complete contiguous transformer block ranges to the project's block-group schedule is still project code and must be checked after export and reload. [Non-uniform quantization](https://docs.vllm.ai/projects/llm-compressor/en/latest/examples/quantization_non_uniform/) | Strongest documented hardware fit among the candidates: the LLM Compressor guide lists Ampere as suitable for W4A16/W8A16 and vLLM's minimum capability is below SM86. Exact current vLLM/LLM Compressor/PyTorch wheel compatibility on the lab image is still open. | Weight-only floors from 15.2 GB BF16 are approximately 15.2 GB BF16, 7.6 GB W8, and 3.8 GB W4 before scales, KV cache, activations, allocator overhead, or engine state. Expect the BF16 path to be tight at long context or larger batch on 24 GB; this is an estimate, not a measurement. Setup: PyTorch, Transformers, vLLM, LLM Compressor, compressed-tensors, and calibration data for GPTQ/AWQ if chosen. |
| C2 | mistralai/Mistral-7B-Instruct-v0.3 at c170c708c41dac9275d15a8fff4eca08d52bab71; the same exact D1 revision set. [Model revision](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3/tree/c170c708c41dac9275d15a8fff4eca08d52bab71) | Apache-2.0; public and ungated. The Transformers shards total about 14.5 GB; the repository also exposes a 14.5 GB consolidated file, so a full snapshot is about 29 GB. [Model card/files](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3/tree/c170c708c41dac9275d15a8fff4eca08d52bab71) | Same LLM Compressor/vLLM BF16, W8A16, and W4A16 paths as C1. The model card documents Transformers loading and the backend documents the quantized formats. | Same status as C1: mixed precision over module/layer groups is documented; contiguous transformer block groups are not a turnkey schedule API. | Same SM86 target and PyTorch wheel options. The model's architecture is commonly supported by Transformers/vLLM, but exact current backend coverage at the pinned commit and lab environment must be preflighted. | Approximate weight floors: 14.5 GB BF16, 7.25 GB W8, 3.6 GB W4, excluding runtime state. Reserve space for the source representation actually used, compressed output, calibration files, and engine/cache artifacts; a full snapshot may retain both model formats. |
| C3 | meta-llama/Llama-3.1-8B-Instruct at 0e9e39f249a16976918f6564b8830bc894c89659; the same exact D1 revision set. [Model revision](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct/tree/0e9e39f249a16976918f6564b8830bc894c89659) | **Custom Llama 3.1 Community License**, not Apache/MIT; manual access gate and contact-information approval are required. The published model card states the model is static, but access approval is an external reproducibility dependency. [Model card/license](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct), [license text](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct/blob/main/LICENSE) | BF16: official Transformers pipeline uses torch.bfloat16. W8A16/W4A16: the LLM Compressor/vLLM weight-only paths documented for C1 can be applied if this exact model is accepted by the selected backend; the W4A16 official example uses the Llama family. This model-specific application is still to be verified. | Backend-level mixed layer/group controls are documented; exact contiguous block-group export, reload, and execution for this gated model are open. | Size and SM86 are plausible for one 24 GB card, but the gated license/access path and model-specific engine support reduce reproducibility. Current backend/PyTorch compatibility is not established by the model card alone. | Published weight files total about 16.1 GB: approximate floors are 16.1 GB BF16, 8.0 GB W8, and 4.0 GB W4 before runtime state. BF16 has less headroom than the 7B candidates. Setup additionally requires Meta/Hugging Face access approval and compliance with the community license and acceptable-use policy. |
| C4 | Qwen/Qwen2.5-7B-Instruct at a09a35458c702b33eeacc393d103063234e8bc28 + torchao/Transformers; the same exact D1 revision set. | Qwen Apache-2.0 and ungated. Backend license is the first-party PyTorch AO project license; the exact backend commit/version must be pinned before a run. | BF16: standard Transformers/PyTorch load. W8A16: TorchAO Int8WeightOnlyConfig, documented as INT8 weights with BF16 activations. W4A16: Int4WeightOnlyConfig, documented as INT4 weights with BF16 activations and groupwise quantization. [TorchAO inference workflows](https://docs.pytorch.org/ao/stable/workflows/inference.html) | **Promising but not end-to-end proven.** TorchAO's quantization API targets selected Linear modules and its configuration APIs support per-module/FQN choices. Assigning INT4, INT8, or no quantization to the linear modules inside contiguous transformer block ranges is a direct implementation inference; save/reload and kernel behavior must be tested. [TorchAO API](https://docs.pytorch.org/ao/stable/api_reference/api_ref_quantization.html) | TorchAO documents CUDA inference, but the current inference page does not establish that every INT4/INT8 kernel path works on SM86. The page explicitly gives a CUDA minimum for some FP8 workflows, not a complete RTX 3090 guarantee for INT4/INT8 weight-only. PyTorch 2.5.1 CUDA 11.8/12.1 wheels are available, but a compatible TorchAO version is not selected. | Same Qwen weight floors: 15.2/7.6/3.8 GB for BF16/W8/W4 before overhead. Setup: a pinned PyTorch + CUDA wheel, compatible TorchAO, Transformers, and a serialization/reload path. torch.compile and any generated kernel cache add unmeasured disk and setup cost. |
| C5 | Qwen/Qwen2.5-7B-Instruct at a09a35458c702b33eeacc393d103063234e8bc28 + TensorRT-LLM/Model Optimizer; the same exact D1 revision set. | Qwen Apache-2.0. TensorRT-LLM is Apache-2.0 at its [official repository](https://github.com/NVIDIA/TensorRT-LLM/blob/main/LICENSE). The TensorRT-LLM and Model Optimizer revisions are not pinned in the current ticket and must be frozen together. | BF16: TensorRT-LLM full_prec/BF16 engine path. W8A16: INT8 weight-only (int8_wo, represented as W8A16). W4A16: INT4 weight-only (int4_wo) or INT4 AWQ/GPTQ. TensorRT-LLM's official quantization README documents these weight-only choices and per-layer MIXED_PRECISION/quant_cfg.json metadata; unlisted layers remain unquantized. [Quantization README](https://github.com/NVIDIA/TensorRT-LLM/blob/main/examples/quantization/README.md), [quantization feature guide](https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/features/quantization.md) | **Best explicit schedule representation, still not a project-ready schedule.** Per-layer quantization metadata and mixed-precision checkpoint loading are documented. Generating a schedule whose assignments are contiguous transformer block groups is straightforward metadata construction, but engine build, reload, and actual outputs must be verified. | NVIDIA documents Ampere support for relevant INT4 weight-only paths and RTX 3090 is SM86. However, the current TensorRT-LLM engine/wheel/driver matrix does not establish this exact Qwen checkpoint and all three paths on the lab's RTX 3090 image. | Same Qwen weight floors, plus TensorRT checkpoint and engine copies. Setup is the heaviest: PyTorch, Transformers, TensorRT-LLM, TensorRT, Model Optimizer, engine build tools, and any calibration data. Reserve roughly 50–70 GB per candidate as a planning envelope if retaining BF16, quantized checkpoints, temporary files, and engines; measure before any large run. |
| C6 | Qwen/Qwen2.5-7B-Instruct at a09a35458c702b33eeacc393d103063234e8bc28 + bitsandbytes/Transformers; the same exact D1 revision set. | Qwen Apache-2.0 and ungated. bitsandbytes is MIT at its [official repository](https://github.com/bitsandbytes-foundation/bitsandbytes). Pin exact Transformers, Accelerate, bitsandbytes, and PyTorch versions; the moving docs page is not a lockfile. | BF16: ordinary Transformers load with BF16 weights. W8A16: BitsAndBytesConfig(load_in_8bit=True) uses Linear8bitLt and preserves some operations in higher precision. W4A16: load_in_4bit=True with bnb_4bit_compute_dtype=torch.bfloat16; the docs expose Linear4bit and NF4/FP4 paths. [Official Transformers bitsandbytes guide](https://huggingface.co/docs/transformers/main/quantization/bitsandbytes) | **Uniform paths are documented; arbitrary mixed block groups are not.** Transformers supports skipping modules for some 8-bit cases, and bitsandbytes exposes 4-/8-bit linear replacements, but one model with BF16, W8, and W4 assigned to contiguous transformer block groups is a project implementation requiring manual module replacement and validation. Treat this row as a strong uniform baseline and a high-risk mixed-schedule backend. | bitsandbytes documents NVIDIA CUDA 11.8–13.0 support; LLM.int8 requires Turing or newer and NF4/FP4 requires Pascal or newer. RTX 3090 SM86 clears those documented minimums. The exact wheel and driver combination still needs the preflight. [Hardware compatibility](https://huggingface.co/docs/bitsandbytes/main/en/installation) | Same Qwen weight floors. Setup is comparatively small: PyTorch, Transformers, Accelerate, bitsandbytes, and no calibration set for the ordinary load-time paths. Quantized module replacement can still have temporary CPU/GPU memory overhead; peak memory and reload behavior are unmeasured. |
| C7 | Qwen/Qwen2.5-7B-Instruct at a09a35458c702b33eeacc393d103063234e8bc28 + HQQ/Transformers; the same exact D1 revision set. | Qwen Apache-2.0 and ungated. HQQ's official implementation is Apache-2.0; pin its exact release or commit. [Official HQQ repository](https://github.com/dropbox/hqq) | BF16: standard Transformers load with BF16 compute. W8A16: HqqConfig(nbits=8, ...) / BaseQuantizeConfig(nbits=8, ...) and BF16 compute. W4A16: the same path with nbits=4; HQQ documents support for 8, 4, 3, 2, and 1 bits and BF16-capable TorchAO inference examples. [HQQ README](https://github.com/dropbox/hqq), [Transformers HQQ guide](https://huggingface.co/docs/transformers/main/quantization) | **Most direct mixed-schedule API among the PyTorch candidates.** Transformers' HQQ integration documents dynamic_config, where layer-name tags receive dedicated quantization configurations. Mapping those tags to contiguous block ranges and leaving BF16 ranges unquantized is an implementation inference; the resulting model must be saved, reloaded, and checked for numerical and runtime equivalence. | HQQ documents pure PyTorch and custom CUDA dequantization backends suitable for older GPUs, but it does not provide a definitive RTX 3090/SM86 compatibility statement for every optimized backend. The native PyTorch path is the conservative preflight target; optimized backends need separate verification. | Same Qwen weight floors. Setup: PyTorch matched to CUDA, Transformers, HQQ, and optional compiled CUDA/optimized kernels. Quantization can require a BF16 source model plus quantized allocations during preparation; peak CPU/GPU memory is not documented for this exact model. |

### Cross-candidate interpretation

- C1–C3 hold the backend constant and expose model/license/access tradeoffs.
- C4–C7 hold Qwen and D1 constant and expose backend tradeoffs.
- This is a candidate matrix, not a ranking. In particular, documented support
  for mixed **modules** or **layers** is not evidence that a complete mixed
  **contiguous block-group schedule** has executed.
- The source documents use different meanings of “block”: quantizer tensor
  groups, layer/module groups, and transformer block groups. The project must
  keep those distinct.

## Reproducibility and resource accounting

### Model and weight storage

The published file listings give the following source-snapshot anchors:

| Model | Published source files | Weight-only planning floors |
|---|---:|---:|
| Qwen2.5-7B-Instruct | About 15.2 GB | BF16 ≈15.2 GB; W8 ≈7.6 GB; W4 ≈3.8 GB, plus scales/metadata |
| Mistral-7B-Instruct-v0.3 | HF shards ≈14.5 GB; full repository snapshot ≈29 GB because both sharded and consolidated forms are present | BF16 ≈14.5 GB; W8 ≈7.25 GB; W4 ≈3.6 GB, plus scales/metadata |
| Llama-3.1-8B-Instruct | About 16.1 GB | BF16 ≈16.1 GB; W8 ≈8.0 GB; W4 ≈4.0 GB, plus scales/metadata |

The W8/W4 figures are arithmetic estimates from the BF16 weight bytes and do
not include scale tensors, zero points, padding, tokenizer files, runtime
buffers, KV cache, or temporary quantization allocations. A 24 GB RTX 3090
therefore has plausible short-context, batch-1 headroom for these candidates,
but no source establishes peak memory for the complete experiment. Long context,
larger batches, calibration, engine building, and retaining multiple model
copies can exceed the card.

A conservative planning reservation is **50–70 GB per model/backend candidate**
when retaining the original checkpoint, one or more quantized checkpoints,
calibration/intermediate files, and runtime/engine caches. This is a storage
planning envelope, not a measurement. Dataset archive sizes, especially the
official MuSiQue archive, must be measured and checksummed before use.

### Dependencies that must be pinned later

No dependency was installed for this artifact. Before any real run, record at
least:

- Python version and OS/architecture.
- Exact PyTorch build and CUDA runtime/driver.
- Transformers and Accelerate versions.
- Backend package and source commit/tag.
- vLLM, compressed-tensors, TensorRT, or Model Optimizer versions where used.
- HQQ/TorchAO/bitsandbytes compiled-kernel details where used.
- Model ID and full revision.
- Every D1 dataset/evaluator revision, MuSiQue archive SHA-256, split manifest,
  prompt/template revision, and calibration-data revision.
- The exact GPU indices, memory, driver, and warm-up/timing controls.

## Minimal non-mutating preflight commands

These commands are proposed for the later selected candidate. They inspect the
environment only; they do not download models/data, install packages, load a
model, or launch an experiment.

### CPU/environment preflight

~~~bash
python - <<'PY'
import platform
import sys

print("python:", sys.version)
print("platform:", platform.platform())
for name in ("torch", "transformers", "accelerate", "bitsandbytes",
             "torchao", "hqq", "llmcompressor", "vllm", "tensorrt_llm"):
    try:
        module = __import__(name)
        print(name + ":", getattr(module, "__version__", "version-unknown"))
    except Exception as exc:
        print(name + ": unavailable:", type(exc).__name__, str(exc))
PY

python -m pip check
df -h .
~~~

The import loop is intentionally diagnostic. “Unavailable” is expected before
the environment is built; it is not evidence that a candidate works.

For a prepared checkout/archive, verify immutable data identities without
fetching anything:

~~~bash
git -C <math-checkout> rev-parse --verify 985bdc1696e88e8643f081a0ff4719da39f2ae2a
git -C <evalplus-checkout> rev-parse --verify e5d0ed0bab96280b60b637ec7f15b5e4841b0cb2
git -C <musique-checkout> rev-parse --verify 24cc5b297acc2abfc5fb3d0becb6ef7b73d03717
sha256sum <musique-v1.0-archive>
~~~

The first three commands assume checkouts already exist; they are not download
commands. The archive checksum command cannot be completed until the archive
identity is resolved and the archive is explicitly obtained in a later,
approved step.

### GPU preflight

The repository requires an availability check before using the remote lab:

~~~bash
nvidia-smi --query-gpu=index,name,memory.total,memory.free,utilization.gpu,driver_version --format=csv
~~~

Then check the actual PyTorch build and SM capability:

~~~bash
CUDA_VISIBLE_DEVICES=0 python - <<'PY'
import torch

assert torch.cuda.is_available(), "CUDA is unavailable"
device = torch.cuda.current_device()
props = torch.cuda.get_device_properties(device)
print("device:", props.name)
print("capability:", torch.cuda.get_device_capability(device))
print("total_memory_bytes:", props.total_memory)
print("bf16_supported:", torch.cuda.is_bf16_supported())
print("torch:", torch.__version__)
print("torch_cuda_runtime:", torch.version.cuda)
print("compiled_arches:", torch.cuda.get_arch_list())
PY
~~~

Backend-specific import checks can follow without loading weights:

~~~bash
python -c 'import bitsandbytes; print("bitsandbytes import ok")'
python -c 'import torchao; print("torchao import ok")'
python -c 'import hqq; print("hqq import ok")'
python -c 'import llmcompressor, vllm; print("llm-compressor/vLLM imports ok")'
python -c 'import tensorrt_llm; print("TensorRT-LLM import ok")'
~~~

These checks prove only environment visibility and device capability. They do
not prove model execution, quantization correctness, mixed schedules, quality,
latency, memory safety, or checkpoint reload.

## Evidence gaps requiring empirical verification

1. **MuSiQue reproducibility:** record the official v1.0 archive URL/filename and
   SHA-256. The repository commit alone does not identify the archive bytes.
2. **Backend revisions:** choose immutable backend commits/tags and a compatible
   PyTorch/CUDA matrix. The cited documentation pages are moving targets.
3. **Actual mixed schedules:** for every candidate that claims feasibility,
   instantiate at least one schedule with contiguous groups assigned BF16, W8A16,
   and W4A16, execute it, save it, reload it, and verify module dtypes,
   outputs, and schedule metadata.
4. **Kernel compatibility on SM86:** import success is insufficient. Check
   actual BF16, W8A16, and W4A16 forward passes on an RTX 3090, including the
   chosen group size, attention implementation, and batch shape.
5. **TensorRT-LLM engine support:** verify the exact Qwen revision, current
   TensorRT-LLM/Model Optimizer pair, engine build, reload, and output path on
   RTX 3090. Do not infer this from a generic Ampere table.
6. **Calibration and leakage:** GPTQ/AWQ/Model Optimizer calibration must use
   only a predeclared train/validation source and must not use final-test
   requests or outputs. Record calibration revision and sample IDs.
7. **Peak memory and disk:** measure source load, quantization preparation,
   checkpoint save/reload, engine build, KV-cache allocation, and generation
   under the same batch/input/output conditions. The arithmetic floors above are
   not capacity guarantees.
8. **Quality:** measure absolute task quality and schedule-induced change for
   D1 using the frozen evaluators. BF16 is a reference condition, not ground
   truth, and no candidate quality result exists yet.
9. **Timing:** report warm-up, synchronized prefill/decode timings, median and
   tail latency, batch size, input length, output length, repetitions, and
   hardware. No local RTX 4050 performance claim is valid for this decision.
10. **Remote operations:** check basic1/basic2 availability and document the
    verified allocation/environment command before requesting shared GPU use.
11. **License/access:** confirm compatibility of each model/data/backend license
    with the intended paper artifacts. Llama access and license obligations are
    not interchangeable with open Apache/MIT access.
12. **Contamination:** public MATH, HumanEval+, and MuSiQue sources may overlap
    model pretraining or other evaluation corpora. Preserve the declared split
    and leakage-group rules and do not treat public availability as
    contamination-free evidence.

## Claims this artifact does not make

- It does not select C1–C7.
- It does not claim any candidate has completed a BF16/W8A16/W4A16 run.
- It does not claim a contiguous block-group schedule is executable merely
  because a backend can mix quantization at module or layer granularity.
- It does not claim RTX 3090 availability in the remote lab.
- It does not claim a final quality, latency, throughput, or memory result.
- It does not download a model or dataset, install dependencies, launch a GPU
  experiment, edit the ticket, or close the ticket.
