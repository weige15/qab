# Query-Conditioned Quantization Sensitivity and Precision-Compatible Batching

## The System Has Two Separate Levels

| Level | Examples |
|---|---|
| What the query requires | Mathematical reasoning, code generation, retrieval grounding, exact copying, instruction following, long-context synthesis |
| What the serving system optimizes | Correctness, latency, throughput, memory, energy, cost, SLO satisfaction |

A single request can require a mixture of capabilities while the serving system still has a well-defined optimization problem. For example:

> Maximize throughput subject to no more than a 1% quality loss relative to BF16 and a p95 latency limit.

For an open-ended request, the quality constraint can itself be multidimensional:

$$
Q(q,s) = [Q_{\text{correctness}}, Q_{\text{grounding}}, Q_{\text{code}}, Q_{\text{format}}]
$$

Here, $q$ is the query and $s$ is a precision schedule.

## Yes, Composite Tasks Can Be Embedded—but Not With an Arbitrary Embedding

Any text can be mapped to an embedding. The scientific question is whether the embedding captures the properties needed to predict quantization behavior.

A generic semantic embedding might recognize that a prompt concerns mathematics and retrieval, but it may not predict whether INT4 changes the answer or whether blocks 8–16 require higher precision. Your representation therefore needs to be trained against behavioral measurements obtained from multiple precision configurations.

A useful decomposition is:

$$
z_q = [z_{q,\text{skills}}, z_{q,\text{difficulty}}, z_{q,\text{structure}}, z_{q,\text{precision sensitivity}}]
$$

- $z_{q,\text{skills}}$: soft mixture of capabilities, not one task label.
- $z_{q,\text{difficulty}}$: intensity of each capability demand.
- $z_{q,\text{structure}}$: length, expected output length, syntax, context characteristics.
- $z_{q,\text{precision sensitivity}}$: expected quality degradation under lower precision.

The attached ZeroRouter paper supplies a good conceptual starting point. In the architecture diagram on page 3, it maps a query into multidimensional difficulty and discrimination vectors and separates those query properties from model profiles. The heatmaps on page 7 further motivate separating relatively general difficulty from task-specific discrimination. Your adaptation would replace the candidate-model profile with a precision-schedule profile.

A ZeroRouter-like baseline could be:

$$
P(\text{success} \mid q,s) = \sigma\left(\alpha_q^\top(\theta_s-b_q)\right)
$$

where:

- $b_q$ represents multidimensional query difficulty;
- $\alpha_q$ represents which latent capabilities matter for that query;
- $\theta_s$ represents the capability retained by precision schedule $s$.

This is a strong starting model, although the IRT monotonicity assumptions may not hold for arbitrary blockwise schedules. Two schedules with the same average bit width can affect different capabilities, so you should compare IRT against a more flexible query–schedule interaction network.

## The Likely Novelty Is Narrower Than “Use Embeddings to Choose Bit Width”

Several parts of the idea now have direct prior art:

| Research line | What is already covered | What remains open in your formulation |
|---|---|---|
| ZeroRouter | Multidimensional query characterization and separation of query properties from model capability. | It selects among models, not blockwise precision schedules, and its global ILP is not an execution-level dynamic batching system. |
| Progressive Mixed-Precision Decoding | ICLR 2025 work allocates different precision to prefill and decoding and uses prompt-adaptive switching as generation progresses. | It does not infer a compositional capability-demand representation or form precision-compatible server batches. |
| Prompt-Adaptive Quantization | An AAAI 2026 AIR-FM workshop poster routes each prompt to an appropriate pre-quantized model variant. | It operates at whole-model granularity rather than constructing a query-specific schedule over block groups. |
| Dynamic Mixed-Precision Routing | A 2026 preprint selects BF16, INT4, or INT3 at individual decision steps in long-horizon agentic tasks, using KL supervision and reinforcement learning. | It routes precision by interaction step, not by transformer block, and does not jointly optimize batch formation. |
| MorphServe | A serving framework dynamically swaps full-precision and quantized layers and resizes the KV cache in response to system pressure. | Its layer order is profiled offline and adaptation is workload-driven rather than conditioned on the semantic requirements of each query. |
| Batch-level routing | Recent work jointly optimizes model assignments across batches under cost, capacity, and concurrency constraints; RoBatch jointly considers routing and batch size. | These methods do not predict blockwise quantization sensitivity or batch according to precision-schedule compatibility. |

Therefore, the strongest prospective contribution is not merely:

> Embed a prompt and choose a bit width.

It is:

> **Learn a compositional, query-conditioned block-sensitivity representation and use it to form precision-compatible batches under calibrated quality constraints.**

That exact intersection still requires a dedicated novelty audit, especially against recent workshop submissions and preprints.

## The Most Important Conceptual Correction: Do Not Batch Only by Difficulty

Two equally difficult queries may have very different quantization sensitivity.

For example, one request may require exact copying or precise retrieval grounding, while another requires long reasoning but is robust to small logit perturbations in many blocks. Even if both receive the same scalar “difficulty” score, they might need different precision schedules.

A better batching concept is precision compatibility.

Let a block-group precision schedule be:

$$
s = (b_1,b_2,\ldots,b_G), \qquad b_g \in \{4,8,16\}
$$

where $G$ is the number of transformer block groups.

For each query, predict the set of schedules that satisfy its quality requirement:

$$
F(q) = \{s \in S : P(\Delta Q(q,s) \leq \epsilon_q) \geq 1-\alpha\}
$$

- $\Delta Q(q,s)$ is predicted degradation relative to BF16.
- $\epsilon_q$ is the permitted degradation.
- $\alpha$ controls risk or uncertainty.

A batch $B$ is precision-compatible when:

$$
\bigcap_{q \in B} F(q) \neq \varnothing
$$

The scheduler can then select one shared schedule from that intersection. Requests should additionally have reasonably compatible input and expected output lengths.

This formulation has several advantages:

- It uses a set of safe schedules, rather than forcing one possibly wrong prediction.
- It naturally handles uncertainty.
- A request that tolerates INT4 can still join an INT8 batch when that reduces waiting time.
- It exposes the real systems trade-off between precision overprovisioning and queueing delay.
- It does not assume that scalar difficulty is identical to precision sensitivity.

This “feasible-schedule-set” formulation could become the central novelty of the systems component.

## Recommended First Paper

Do not begin with arbitrary per-block bit-width assignment, continuous batching, multiple model families, activation quantization, KV-cache quantization, and online adaptation simultaneously.

Begin with:

> **Predicting query-conditioned quantization sensitivity for composite LLM tasks**

### Scope

| Decision | Recommended initial choice |
|---|---|
| Base model | One open decoder-only model in the 3B–8B range |
| Precision target | Weights only |
| Precision options | BF16, W8A16, and W4A16 |
| Granularity | Four to eight contiguous transformer block groups |
| Precision schedules | A codebook of approximately 8–16 hardware-efficient schedules |
| Serving environment | One GPU or one homogeneous GPU node |
| Query setting | Single-turn composite requests initially |
| Batching | Offline simulation first; live serving after the predictor is validated |
| Out of scope | Activation precision, KV-cache precision, arbitrary per-token precision, multi-node placement, pure pruning |

The schedule codebook is important. With $L$ blocks and three precision choices, unrestricted search has $3^L$ configurations. More importantly, arbitrary schedules may not have efficient kernels or practical weight layouts.

Construct a small schedule codebook by:

1. Profiling block-group sensitivity.
2. Finding Pareto-efficient schedules.
3. Clustering schedules with similar quality and latency characteristics.
4. Retaining only schedules that have practical kernel implementations.

The router then chooses a schedule identifier, rather than independently predicting a bit width for every block.

## A Practical Model Architecture

### 1. Query Encoder

Use a frozen or lightly fine-tuned text encoder with separate heads for:

- capability mixture;
- capability-specific difficulty;
- expected output length;
- uncertainty.

For retrieval or tool-using requests, the initial text may not contain enough information. The encoder may need:

$$
q_{\text{context}} = [\text{user prompt}; \text{retrieved-context metadata}; \text{tool state}; \text{interaction history}]
$$

A static pre-retrieval embedding and a post-retrieval embedding could eventually form a hierarchical router, but that is an extension rather than the first experiment.

### 2. Schedule Encoder

Represent a schedule using:

- the bit width of each block group;
- attention versus MLP precision;
- measured latency and memory;
- static block sensitivity;
- optionally hardware-specific kernel identifiers.

### 3. Query–Schedule Predictor

Predict:

$$
\Delta Q(q,s), \quad T(q,s), \quad M(s)
$$

A bilinear latent model gives interpretability, while a small cross-attention or MLP interaction model can capture non-additive block effects.

### 4. Uncertainty Calibration

A production router should not merely predict the schedule with the best mean score. It should estimate whether the quality constraint is likely to be violated.

Suitable first approaches include:

- model ensembles;
- quantile regression;
- conformal calibration;
- calibrated classification of whether a schedule is safe.

## How to Create the Training Data

Construct a query-by-schedule response matrix:

$$
R_{q,s} = [Q(q,s), T(q,s), M(s), \text{output length}, \text{logit divergence}]
$$

For each query:

1. Run the BF16 reference.
2. Run all schedules in the initial codebook.
3. Record final task quality.
4. Record KL divergence or representation drift as auxiliary signals.
5. Record actual wall-clock prefill and decode latency.
6. Record memory and batching behavior.

Do not use KL divergence from BF16 as the only quality label. BF16 can itself be wrong; a high-KL answer can occasionally be better, and a low-KL answer can preserve the same mistake. Use task success as the primary label and KL as a sensitivity surrogate.

For open-ended composite tasks:

- prefer executable or verifiable outcomes where available;
- use component-level criteria such as retrieval grounding, numerical correctness, code execution, and format adherence;
- use an external judge only as one measurement;
- manually inspect a statistically meaningful subset.

## Evaluation Design

### Generalization Splits

A random train/test split is insufficient. Use several harder splits:

- Unseen query instances
- Unseen datasets
- Unseen capability combinations
- Unseen difficulty ranges
- Unseen prompt formats
- Unseen sequence lengths

For compositional generalization, train on individual skills and selected pairs, then test on held-out combinations. The composite examples must be coherent tasks, not unrelated prompts concatenated together.

### Predictor Metrics

- Mean absolute error in quality degradation
- AUROC or AUPRC for “requires higher precision”
- Calibration error
- Quality-constraint violation rate
- Schedule-selection regret relative to the oracle
- Top-k feasible-schedule recall

### End-to-End Metrics

- Task success or task-specific quality
- Average and effective bit width
- GPU memory consumption
- Router overhead
- Throughput
- p50, p95, and p99 TTFT
- TPOT
- SLO attainment
- Batch fill ratio
- Queueing delay
- Energy, when measurement is available

### Essential Baselines

- Always BF16
- Always INT8
- Always INT4
- Static offline mixed precision
- Whole-model prompt-adaptive routing
- Scalar-difficulty threshold
- Task-label routing
- Generic-embedding router
- Length-aware router
- Oracle schedule
- Oracle batch formation
