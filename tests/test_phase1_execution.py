from qcb.backend import planned_module_assignments
from qcb.contract import BlockGroup, BlockPartition, PrecisionSchedule
from qcb.execution import _requested_precisions


def test_requested_precisions_accepts_mixed_schedule() -> None:
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
    assignments = planned_module_assignments(
        partition, PrecisionSchedule.parse(partition, "B844")
    )

    assert _requested_precisions(assignments) == (
        assignments[0].requested_precision,
        assignments[7 * 7].requested_precision,
        assignments[14 * 7].requested_precision,
    )
