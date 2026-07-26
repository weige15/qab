# Research Specification

## Status

The adaptation unit and routing decision point are resolved. The model,
dataset, quantization backend, schedule count, and quality contract remain
unspecified until their respective decisions are resolved.

## Research objective

Evaluate whether a representation of an incoming composite request can predict
its quantization-sensitivity profile well enough to select a quality-safe
mixed-precision schedule and support precision-compatible batching.

## Resolved adaptation unit and routing decision point

- The adaptation unit is a **block group**: a contiguous group of transformer
  layers.
- A request receives a **precision schedule** assigning one weight precision to
  each block group.
- The initial precision choices are **BF16, INT8, and INT4**, weights only.
- The complete precision schedule is selected at **pre-prefill routing**: once
  per request, before model prefill begins.
- The initial study does not adapt weight precision after partial prefill or
  during decoding.

The number and boundaries of block groups, hardware-executable schedule
codebook, request quality contract, model, dataset, and backend remain open
decisions. The exact router inputs beyond the routing-time boundary are also
not fixed by this decision.
