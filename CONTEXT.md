# Query-Conditioned Quantization

This context defines the terms used to study query-conditioned weight
precision for decoder-only language-model inference.

## Language

**Request**:
An incoming single-turn inference item whose query may affect the selected
precision schedule.

**Block group**:
A contiguous group of transformer layers treated as one adaptation unit for
weight precision assignment.
_Avoid_: tensor block, when referring to the numerical sub-blocks used inside a
quantizer.

**Precision schedule**:
The per-request assignment of one allowed weight precision to each block group.

**Pre-prefill routing**:
The routing decision point at which a complete precision schedule is selected
once, after request arrival and before model prefill begins.
_Avoid_: partial-prefill routing, decode-time routing, for this study.

**Query-conditioned**:
A precision decision that can change as the natural-language query or its
model-derived representation changes.
_Avoid_: workload-conditioned, when the decision depends only on length,
batching, hardware, or other system properties.
