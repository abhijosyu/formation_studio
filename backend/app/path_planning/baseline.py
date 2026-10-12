from __future__ import annotations

from time import perf_counter

from app.assignment.solver import solve_assignment
from app.collision.validator import validate_transition
from app.metrics.calculator import calculate_metrics
from app.models.domain import (
    Path,
    Point,
    TransitionPlanRequest,
    TransitionPlanResponse,
    ValidateRequest,
)


def _validate(request: TransitionPlanRequest, paths: list[Path]):
    return validate_transition(ValidateRequest(dancers=request.assignment_request.dancers, paths=paths, stage=request.stage, obstacles=request.obstacles, duration_seconds=request.duration_seconds, config=request.config))


def _detour_candidates(start: Point, end: Point, offset: float) -> list[Point]:
    midpoint = Point(x=(start.x + end.x) / 2, y=(start.y + end.y) / 2)
    dx, dy = end.x - start.x, end.y - start.y
    length = max((dx * dx + dy * dy) ** .5, .001)
    return [Point(x=midpoint.x - dy / length * offset, y=midpoint.y + dx / length * offset), Point(x=midpoint.x + dy / length * offset, y=midpoint.y - dx / length * offset)]


def plan_straight_paths(request: TransitionPlanRequest) -> TransitionPlanResponse:
    """Greedy deterministic waypoint repair; feasible result, never a global optimum claim."""
    started = perf_counter()
    assignment = solve_assignment(request.assignment_request)
    targets = {target.id: target.position for target in request.assignment_request.targets}
    paths = [Path(dancer_id=item.dancer_id, points=[request.assignment_request.start_positions[item.dancer_id], targets[item.target_id]]) for item in assignment.assignments]
    validation = _validate(request, paths)
    attempts = 0
    # For each detected moving conflict, try a perpendicular midpoint detour for one participant.
    # Candidate must improve conflict count; bounded iterations prevent accidental expensive plans.
    while request.config.advanced and validation.conflicts and attempts < request.config.max_waypoint_attempts:
        conflict = next((item for item in validation.conflicts if len(item.dancer_ids) == 2), None)
        if conflict is None: break
        candidate_path = next(path for path in paths if path.dancer_id == conflict.dancer_ids[1])
        best_paths, best_validation = paths, validation
        for offset in (0.8, 1.3, 1.8):
            for waypoint in _detour_candidates(candidate_path.points[0], candidate_path.points[-1], offset):
                trial = [path.model_copy(deep=True) for path in paths]
                next(path for path in trial if path.dancer_id == candidate_path.dancer_id).points = [candidate_path.points[0], waypoint, candidate_path.points[-1]]
                checked = _validate(request, trial)
                if len(checked.conflicts) < len(best_validation.conflicts): best_paths, best_validation = trial, checked
        if best_paths is paths: break
        paths, validation = best_paths, best_validation
        attempts += 1
    elapsed = (perf_counter() - started) * 1000
    metrics = calculate_metrics(paths, request.duration_seconds, validation, elapsed)
    status = "valid" if validation.status == "valid" else "no_valid_transition_found" if request.config.advanced else "conflicts_detected"
    note = "Validated with fixed temporal sampling; see README for tolerance." if status == "valid" else "No safe plan found by bounded waypoint search; conflicts are returned for editing."
    return TransitionPlanResponse(assignment=assignment, paths=paths, duration_seconds=request.duration_seconds, validation=validation, metrics=metrics, status=status, note=note)
