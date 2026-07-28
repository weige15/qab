from qcb.backend import planned_module_assignments
from qcb.contract import BlockGroup, BlockPartition, Precision, PrecisionSchedule
from qcb.validation import RealizedModule, compare_precision_maps


def _requested():
    partition = BlockPartition(
        "g4-equal7",
        28,
        (
            BlockGroup("g00", 0, 6),
            BlockGroup("g01", 7, 13),
            BlockGroup("g02", 14, 20),
            BlockGroup("g03", 21, 27),
        ),
    )
    return planned_module_assignments(partition, PrecisionSchedule.parse(partition, "B844"))


def test_exact_realized_map_is_eligible():
    requested = _requested()
    realized = {
        assignment.module_path: RealizedModule(
            realized_precision=assignment.requested_precision,
            scheme=assignment.requested_precision.value,
            module_class="Linear",
            kernel="cuda.test.kernel",
            device="cuda:0",
        )
        for assignment in requested
    }

    comparison = compare_precision_maps(requested, realized)

    assert comparison.exact_match
    assert comparison.missing == ()
    assert comparison.extra == ()
    assert comparison.wrong_precision == ()
    assert comparison.fallback_dispatches == ()


def test_map_comparison_reports_mismatch_and_fallback_without_hiding_it():
    requested = _requested()
    realized = {
        assignment.module_path: RealizedModule(
            realized_precision=assignment.requested_precision,
            scheme=assignment.requested_precision.value,
            module_class="Linear",
            kernel="cuda.test.kernel",
            device="cuda:0",
        )
        for assignment in requested[1:]
    }
    realized[requested[1].module_path] = RealizedModule(
        realized_precision=Precision.W4A16,
        scheme="W4A16",
        module_class="Linear",
        kernel="cpu.fallback",
        device="cpu",
    )
    realized["model.extra"] = RealizedModule(
        realized_precision=None,
        scheme=None,
        module_class="Linear",
        kernel=None,
        device="cpu",
    )

    comparison = compare_precision_maps(requested, realized)

    assert not comparison.exact_match
    assert requested[0].module_path in comparison.missing
    assert requested[1].module_path in comparison.wrong_precision
    assert requested[1].module_path in comparison.fallback_dispatches
    assert "model.extra" in comparison.extra
