from qcb.benchmark import (
    BenchmarkCondition,
    BenchmarkResult,
    validate_matched_conditions,
)


def _condition(**overrides):
    values = {
        "runtime_id": "vllm-0.11.2",
        "hardware_id": "RTX3090-sm86",
        "gpu_index": 2,
        "batch_size": 1,
        "input_length": 128,
        "output_length": 32,
        "warmup_count": 2,
        "repetition_count": 5,
        "cuda_synchronized": True,
        "prompt_order_id": "probe-v1",
        "decoding_id": "greedy-v1",
    }
    values.update(overrides)
    return BenchmarkCondition(**values)


def test_benchmark_result_has_a_stable_schema_and_summary():
    result = BenchmarkResult(
        schedule_id="qcb.v1/g4-equal7/B844",
        condition=_condition(),
        status="completed",
        elapsed_ms=(10.0, 20.0, 30.0, 40.0, 50.0),
    )

    record = result.to_record()

    assert record["schema_version"] == "qcb.benchmark_result.v1"
    assert record["summary"]["p50_ms"] == 30.0
    assert record["summary"]["p95_ms"] == 50.0
    assert record["condition"]["cuda_synchronized"] is True


def test_matched_condition_validation_rejects_shape_or_runtime_differences():
    first = BenchmarkResult("qcb.v1/g4-equal7/B844", _condition(), "completed", (10.0,))
    second = BenchmarkResult("qcb.v1/g4-equal7/8888", _condition(), "completed", (12.0,))
    different = BenchmarkResult(
        "qcb.v1/g4-equal7/4444",
        _condition(input_length=256),
        "completed",
        (14.0,),
    )

    assert validate_matched_conditions((first, second)).valid
    validation = validate_matched_conditions((first, different))
    assert not validation.valid
    assert "input_length" in validation.differences
