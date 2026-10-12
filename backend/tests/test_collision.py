from app.collision.validator import validate_transition
from app.models.domain import Dancer, Path, Point, Stage, ValidateRequest


def test_head_on_paths_report_temporal_collision() -> None:
    result = validate_transition(ValidateRequest(
        dancers=[Dancer(id="a", label="A"), Dancer(id="b", label="B")],
        paths=[Path(dancer_id="a", points=[Point(x=-2, y=0), Point(x=2, y=0)]), Path(dancer_id="b", points=[Point(x=2, y=0), Point(x=-2, y=0)])],
        stage=Stage(width=10, depth=10), duration_seconds=4,
    ))
    assert result.status == "conflicts_detected"
    assert any(conflict.kind == "dancer_collision" for conflict in result.conflicts)


def test_boundary_violation_is_reported() -> None:
    result = validate_transition(ValidateRequest(dancers=[Dancer(id="a", label="A")], paths=[Path(dancer_id="a", points=[Point(x=0, y=0), Point(x=3, y=0)])], stage=Stage(width=4, depth=4), duration_seconds=2))
    assert any(conflict.kind == "boundary" for conflict in result.conflicts)
