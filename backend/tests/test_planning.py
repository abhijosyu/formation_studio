from app.models.domain import (
    AssignmentRequest,
    AssignmentStrategy,
    Dancer,
    Point,
    TargetSlot,
    TransitionPlanRequest,
)
from app.path_planning.baseline import plan_straight_paths


def test_baseline_paths_match_assignment_endpoints_and_are_validated() -> None:
    assignment = AssignmentRequest(
        dancers=[Dancer(id="a", label="A")],
        start_positions={"a": Point(x=-1, y=0)},
        targets=[TargetSlot(id="slot-1", position=Point(x=2, y=1))],
        strategy=AssignmentStrategy.MINIMUM_DISTANCE,
    )
    result = plan_straight_paths(TransitionPlanRequest(assignment_request=assignment, duration_seconds=3))
    assert result.paths[0].points == [Point(x=-1, y=0), Point(x=2, y=1)]
    assert result.status == "valid"
