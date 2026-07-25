# Novelty Boundary: Query-Conditioned Precision Selection

**Ticket:** [weige15/qab#2](https://github.com/weige15/qab/issues/2)  
**Branch:** `research/novelty-boundary-query-conditioned-precision-selection`  
**Research cutoff:** 2026-07-25  
**Scope:** primary papers and primary project pages only; the comparison is limited to query/task-conditioned precision selection and prediction of layer or block quantization sensitivity.

## Bottom line

The broad claim that an LLM can use the incoming query to select different weight precisions is not novel. The query-adaptive QAQ paper explicitly describes a trainable router that uses query-dependent hidden representations, produces a score for each block, converts those scores into probabilities over candidate bitwidths, and performs block-wise quantized inference with on-demand loading. That is direct prior art for query-conditioned, per-block precision selection and for predicting a local sensitivity-like score. ([QAQ paper](https://openreview.net/pdf?id=dpHfDasG44), [NeurIPS project page](https://neurips.cc/virtual/2025/129098))

TAQ establishes a closely related but weaker task-conditioned result: a small set of unlabeled task-calibration prompts can identify task-relevant transformer layers and drive a static weight-only mixed-precision allocation. It does not, as described by the paper, route each incoming query to its own profile. ([TAQ paper](https://arxiv.org/abs/2511.06516))

AnyBCQ establishes hardware-efficient multi-precision weights and dynamic per-request selection, but its contribution is the representation and kernel for choosing a precision level under runtime service objectives, not a semantic query-to-layer-profile predictor. IMPQ/CoopQ establishes interaction-aware *static* layerwise allocation. LLM-PQ establishes hardware- and workload-aware *offline* layerwise allocation plus heterogeneous-cluster serving. ([AnyBCQ](https://arxiv.org/abs/2510.10467), [IMPQ/CoopQ](https://arxiv.org/abs/2509.15455), [LLM-PQ](https://arxiv.org/abs/2403.01136))

The defensible novelty is therefore narrower:

> **Predict, before full inference, a calibrated quantization-sensitivity or quality-degradation profile for an incoming composite query over contiguous transformer block groups and a finite, hardware-executable weight-only schedule codebook; select a quality-safe schedule from that profile; and use feasible-schedule overlap to form precision-compatible batches.**

This is a synthesis of the boundary exposed by the sources, not a claim made by any one of them. The novelty claim must not say “first query-conditioned precision selection,” “first query-conditioned layer sensitivity,” or “first adaptive mixed precision.”

## Terms used for the comparison

- **Query-conditioned:** the natural-language input or its model-derived representation changes the precision decision. Prompt length, batch size, device memory, and a user quality scalar are workload or system inputs, not semantic query conditioning.
- **Sensitivity profile:** a vector indexed by model regions, for example (p(q)=[\Delta Q_{q,1},\ldots,\Delta Q_{q,G}]), where each component describes measured or predicted quality degradation when a block group is quantized. A router score or a chosen bitwidth is evidence of an adjacent capability, but is not automatically a calibrated profile.
- **Block group:** a contiguous group of transformer layers chosen as the scheduling unit. This is distinct from the small numerical blocks used inside a weight tensor by ordinary block/group quantizers.
- **Precision-compatible batching:** a system-level operation that finds a shared schedule safe for multiple requests, rather than merely routing each request independently.

## Related-work matrix

| System | What is conditioned on? | Quantized object and decision granularity | What the primary source establishes | What it leaves open for this ticket |
|---|---|---|---|---|
| **QAQ — Query-adaptive Mixed-precision Quantization** | Query-dependent features and hidden representation (h_j(x)). | Weight bitplanes; the method describes block-wise transformer inference and a score (s_j(x)) for each block, followed by a softmax over candidate bitwidths. | Direct prior art for a query-conditioned per-block score and per-query precision selection, with dynamic loading of selected bitplanes. ([paper](https://openreview.net/pdf?id=dpHfDasG44)) | The reviewed description does not establish contiguous block-group schedule codebooks, a separately evaluated calibrated query-by-schedule sensitivity profile, safe-schedule coverage/regret, composite capability decomposition, or compatibility-aware batching. Its existence removes the broad “first query-conditioned block precision” claim. |
| **TAQ — Task-Aware Quantization** | A small set of unlabeled prompts from a target task or task mixture. | Weight-only PTQ; higher precision is assigned to task-relevant transformer layers using activation/stability, output-KL, or oracle sensitivity signals. | Task-conditioned layer importance can improve the accuracy–memory trade-off, and the allocation can be validated on real kernels. ([paper](https://arxiv.org/abs/2511.06516)) | It is per-task calibration and allocation, not an incoming-query router. The source does not establish per-query generalization, contiguous block-group profiles, a finite shared schedule codebook, or request batching. |
| **AnyBCQ** | A runtime request’s desired precision/service objective, not semantic query content. | Weight bitplanes in one BCQ-based multi-precision model; a specialized kernel supports dynamic per-request precision selection. | A single deployable representation can support multiple precision levels with hardware-efficient bit-plane execution and monotonic quality improvement as bits are added. ([paper](https://arxiv.org/abs/2510.10467)) | It does not establish a query encoder, query-to-sensitivity prediction, heterogeneous per-layer/block-group assignment, or quality-safe batching by predicted profiles. “Per-request” is not equivalent to “query-conditioned.” |
| **IMPQ / current arXiv title CoopQ** | Static calibration/model information; no incoming-query feature is part of the stated decision. | Weight-only layerwise 2/4-bit allocation under a memory constraint; Shapley-based estimates model inter-layer interactions. | Inter-layer interaction terms can improve static mixed-precision layer allocation over isolated sensitivity metrics. ([arXiv record](https://arxiv.org/abs/2509.15455)) | No runtime query conditioning, query-profile prediction, incoming-query quality constraint, or batch formation. The record currently calls the method **CoopQ**; the earlier IMPQ name is retained here because it is the ticket’s terminology. |
| **LLM-PQ** | Model, heterogeneous device resources, candidate precisions, prompt length, generation length, batch size, and a user quality scalar. | Offline per-decoder-layer bit assignment jointly optimized with layer partition and microbatch sizing. | A variance-based layer perturbation indicator plus ILP can optimize hardware-aware mixed precision and heterogeneous-cluster serving for an offline workload. ([paper](https://arxiv.org/abs/2403.01136)) | Its “query workload” inputs are lengths and batch/runtime properties, not semantic query content. It does not predict an incoming query’s block-group sensitivity profile or batch requests by profile compatibility, although it does optimize microbatch execution. |
| **Any-Precision LLM** | A runtime-selected uniform model size/bitwidth. | One bit-plane-packed model exposes several uniform precisions through incremental upscaling and a specialized kernel. | Multi-precision model storage and execution can reduce the cost of deploying separate uniform-precision models. ([paper](https://arxiv.org/abs/2402.10517)) | No query-conditioned selector, layerwise profile, block-group schedule, or quality-safe batching. |
| **DP-LLM** | Current layer input values at each decoding iteration. | A precision selector is attached to each linear layer and chooses between high/low bitwidth using a relative-error estimate and learned thresholds. | Layer sensitivity can vary across decoding iterations, and dynamic layerwise precision can exploit that variation. ([paper](https://arxiv.org/abs/2508.06041)) | This is token/activation-state-conditioned runtime adaptation, not a pre-inference semantic incoming-query profile. It also does not establish contiguous block-group batching. |
| **Progressive Mixed-Precision Decoding (PMPD)** | Task-adaptive or prompt-adaptive precision-switching policies over the generation process. | Phase-aware and progressively lower precision deeper in the generated sequence. | Precision can be adapted across prefill/decode phases and generation depth rather than held uniform throughout decoding. ([paper](https://arxiv.org/abs/2410.13461)) | The decision axis is inference phase/generation depth, not a predicted weight sensitivity vector over transformer block groups. |
| **Prompt-Adaptive Quantization (PAQ)** | A BERT-based prompt complexity classifier. | Selects one pre-quantized whole-model variant (2/4/8/16 bits) per prompt using perplexity-guided labels. | Whole-model per-prompt precision routing can approach a higher-precision baseline while avoiding high precision for every prompt. ([paper](https://openreview.net/pdf?id=YWn5CbBSKj)) | No per-layer or block-group precision assignment, sensitivity-profile prediction, or compatible batching. It is an important adjacent precedent against claiming per-prompt routing broadly. |
| **Cocktail** | Similarity between the query and context chunks. | Query-adaptive mixed precision for **KV-cache context chunks**, with FP16/INT4/INT2 assignments and chunk reordering. | Query-conditioned quantization can preserve query-relevant context at higher precision while compressing less-relevant context. ([paper](https://arxiv.org/abs/2503.23294)) | It concerns KV-cache chunks, not model weights or transformer block groups. It is adjacent evidence that query-conditioned quantization is known outside the project’s weights-only scope. |
| **Quality-Adaptive QAQ** | Current attention/importance state during generation. | Per-token key/value-cache precision, with separate key/value sensitivity treatment and outlier handling. | KV-cache precision can be adapted to estimated token importance and the distinct sensitivity of keys versus values. ([paper](https://arxiv.org/abs/2403.04643)) | This is a different QAQ from Query-adaptive Mixed-precision Quantization and does not select weight precision or predict a weight block-group profile. |

## What is already established

The literature reviewed establishes four separate capabilities that should be treated as prior art rather than proposed novelty:

1. **Semantic or prompt-conditioned whole-model precision:** PAQ routes each prompt to a pre-quantized model variant. ([PAQ](https://openreview.net/pdf?id=YWn5CbBSKj))
2. **Query-conditioned block/layer precision:** QAQ directly describes query-dependent block scores and bitwidth routing. ([QAQ](https://openreview.net/pdf?id=dpHfDasG44))
3. **Task-conditioned layer allocation:** TAQ uses task calibration prompts and hidden/output sensitivity signals to protect task-relevant layers. ([TAQ](https://arxiv.org/abs/2511.06516))
4. **Non-semantic dynamic layer precision:** DP-LLM conditions per-layer precision on current input values during decoding, while LLM-PQ conditions offline allocation on hardware and workload characteristics. ([DP-LLM](https://arxiv.org/abs/2508.06041), [LLM-PQ](https://arxiv.org/abs/2403.01136))

The existence of these components means that “use an embedding/router to choose bitwidth,” “learn layer sensitivity,” and “make precision vary by request” are all too broad as novelty statements. The distinction between **query**, **task**, **current token state**, and **system workload** must be explicit in the paper and evaluation.

## Explicit novelty boundary

### Not defensible

The following claims would overstate the prior art boundary:

- “The first query-conditioned precision selector for LLMs.” QAQ already makes the direct query-conditioned block-routing claim. ([QAQ](https://openreview.net/pdf?id=dpHfDasG44))
- “The first system to predict which layers are sensitive to quantization.” TAQ, IMPQ/CoopQ, LLM-PQ, and DP-LLM each establish layer sensitivity signals, albeit with different conditioning and objectives. ([TAQ](https://arxiv.org/abs/2511.06516), [IMPQ/CoopQ](https://arxiv.org/abs/2509.15455), [LLM-PQ](https://arxiv.org/abs/2403.01136), [DP-LLM](https://arxiv.org/abs/2508.06041))
- “The first per-prompt adaptive quantization system.” PAQ establishes whole-model per-prompt routing, and Cocktail establishes query-conditioned KV-cache precision. ([PAQ](https://openreview.net/pdf?id=YWn5CbBSKj), [Cocktail](https://arxiv.org/abs/2503.23294))
- “The first block-wise mixed-precision inference system.” QAQ and AnyBCQ establish block/bitplane-oriented multi-precision inference, while LLM-PQ establishes layerwise mixed-precision serving. ([QAQ](https://openreview.net/pdf?id=dpHfDasG44), [AnyBCQ](https://arxiv.org/abs/2510.10467), [LLM-PQ](https://arxiv.org/abs/2403.01136))

### Defensible if demonstrated

The project can claim a narrower systems/research contribution if it implements and evaluates all of the following on held-out query instances:

- **A query-by-schedule behavioral target:** measured quality degradation relative to BF16 (or another declared reference) for each query and each finite schedule, with a profile over contiguous transformer block groups rather than only a scalar difficulty score or a local router score.
- **Compositional query conditioning:** a representation that is tested on held-out combinations of capabilities, difficulty ranges, prompt formats, and lengths. Generic semantic similarity alone is not evidence that the representation predicts quantization sensitivity.
- **Calibrated quality-safe selection:** prediction intervals or calibrated safe/unsafe probabilities used to choose a schedule under a stated quality constraint, evaluated by profile error, calibration, feasible-schedule recall, violation rate, and regret against an oracle schedule.
- **Hardware-executable group schedules:** a finite schedule codebook whose contiguous block-group assignments are actually runnable, with matched timing conditions and no claim that arbitrary per-layer assignments are free.
- **Precision-compatible batching:** a batcher or offline simulator that uses the predicted feasible schedule sets to select a shared schedule for multiple requests and measures batch fill, queueing, latency/throughput, quality violations, and memory. None of the reviewed sources establishes this combination of predicted query-specific block profiles and schedule-compatibility batching.

The strongest concise claim supported by this audit is:

> **Prior work already covers query-conditioned block precision selection, task-conditioned layer allocation, runtime-input-conditioned layer precision, whole-model prompt routing, and hardware-aware static mixed precision. The open boundary is the calibrated prediction and evaluation of an incoming query’s contiguous block-group quality-sensitivity profile, followed by quality-safe schedule selection and precision-compatible request batching.**

That claim is intentionally an intersection claim. It should be presented as “not established by the primary systems reviewed here,” not as an absolute proof that no concurrent or unpublished work exists.

## Source notes

The two papers named QAQ are distinct: **Query-adaptive Mixed-precision Quantization** is the direct weight/block-routing precedent; **Quality Adaptive Quantization for LLM KV Cache** is a KV-cache method. The matrix keeps them separate to avoid conflating weight precision selection with cache precision adaptation. ([Query-adaptive QAQ](https://openreview.net/pdf?id=dpHfDasG44), [Quality-adaptive QAQ](https://arxiv.org/abs/2403.04643))

The arXiv record for the ticket’s IMPQ name currently uses the title **CoopQ: Cooperative Game Inspired Layerwise Mixed Precision Quantization for LLMs**. The source record describes the same Shapley/SPQE line and is cited under both names above. ([arXiv:2509.15455](https://arxiv.org/abs/2509.15455))

PMPD is an important boundary correction: its learned scheduler adapts a precision schedule to each prompt before decoding, using prefill-derived features. That makes “pre-inference prompt-conditioned schedule selection” too broad as a QAB claim. PMPD’s schedule axis is phase and generation depth rather than a predicted contiguous transformer block-group quality profile, so it does not remove the narrower intersection below. ([PMPD](https://arxiv.org/abs/2410.13461))

## Audit addendum (approved 2026-07-25)

The primary-source audit adds the following corrections to the matrix above:

| Source | Boundary correction |
|---|---|
| **PMPD** | Its learned scheduler adapts a precision schedule to each prompt before decoding. Therefore “pre-inference prompt-conditioned schedule selection” is not sufficient novelty. Its schedule axis is phase and generation depth, not a contiguous transformer block-group quality profile. ([paper](https://arxiv.org/abs/2410.13461)) |
| **AnyBCQ** | Its “block-wise” procedure refers to weight-tensor reconstruction granularity; it should not be conflated with contiguous transformer block groups. Its dynamic per-request selection is not semantic query conditioning. ([paper](https://arxiv.org/abs/2510.10467)) |
| **RAMP** | Static multidimensional layer representations and learned policy transfer further weaken broad claims about multidimensional sensitivity prediction, but RAMP has no incoming-query conditioning or compatible batching. ([paper](https://arxiv.org/abs/2603.17891)) |
| **MXSens** | Recent static column/layer sensitivity-aware mixed precision is adjacent evidence against broad sensitivity-allocation novelty, but it uses a different quantization setting and is not query-conditioned. ([paper](https://arxiv.org/abs/2607.17733)) |
| **MoQAE** | A learned router selects mixed-precision KV-cache configurations for input chunks/tokens, with routing shared across LLM blocks. This remains outside the weights-only boundary. ([paper](https://aclanthology.org/2025.acl-long.531/)) |

Accordingly, the following claims are explicitly prior art or too broad: first query-conditioned precision selection; first pre-inference prompt-conditioned schedule selection; first query-conditioned layer sensitivity; first per-prompt adaptive quantization; first block-wise mixed precision; and first multidimensional sensitivity-aware precision policy.

The narrowest defensible QAB boundary remains the evaluated intersection of: (1) a calibrated pre-inference predictor of query-specific quality degradation across contiguous transformer block groups and candidate weight-only schedules; (2) quality-safe schedule selection from a finite hardware-executable codebook; and (3) precision-compatible batching based on overlap of per-request feasible schedules. This is a qualified intersection claim—“not established by the primary sources reviewed here”—not an absolute first claim.

The audit did not find a reviewed primary source that forms batches by overlapping query-specific quality-safe weight schedules. That absence is provisional and must remain qualified until a broader concurrent-literature search is completed.
