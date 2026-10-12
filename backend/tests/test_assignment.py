from app.assignment.solver import solve_assignment
from app.models.domain import AssignmentRequest, AssignmentStrategy, Dancer, Point, TargetSlot


def request(strategy: AssignmentStrategy) -> AssignmentRequest:
    return AssignmentRequest(
        dancers=[Dancer(id="a", label="A"), Dancer(id="b", label="B")],
        start_positions={"a": Point(x=0, y=0), "b": Point(x=1, y=0)},
        targets=[TargetSlot(id="one", position=Point(x=0.9, y=0)), TargetSlot(id="two", position=Point(x=3, y=0))],
        strategy=strategy,
    )


def test_global_assignment_is_no_worse_than_greedy() -> None:
    greedy = solve_assignment(request(AssignmentStrategy.GREEDY))
    optimal = solve_assignment(request(AssignmentStrategy.MINIMUM_DISTANCE))
    assert optimal.total_cost <= greedy.total_cost
    assert len({assignment.target_id for assignment in optimal.assignments}) == 2


def test_rejects_unequal_counts() -> None:
    try:
        AssignmentRequest(
            dancers=[Dancer(id="a", label="A")],
            start_positions={"a": Point(x=0, y=0)},
            targets=[
                TargetSlot(id="one", position=Point(x=0, y=0)),
                TargetSlot(id="two", position=Point(x=1, y=0)),
            ],
        )
    except ValueError as error:
        assert "equal number" in str(error)
    else:
        raise AssertionError("Expected validation error")
