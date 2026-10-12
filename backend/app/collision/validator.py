from __future__ import annotations

from app.models.domain import Conflict, Point, ValidateRequest, ValidationResult
from app.simulation.core import distance, position_at


def validate_transition(request: ValidateRequest) -> ValidationResult:
    """Sample exact path evaluator at a documented fixed resolution.

    This detects conflicts no briefer than duration/sample_count; it is conservative only
    at that tolerance and deliberately makes no continuous-time guarantee.
    """
    dancer_by_id = {dancer.id: dancer for dancer in request.dancers}
    path_by_id = {path.dancer_id: path for path in request.paths}
    if set(dancer_by_id) != set(path_by_id):
        raise ValueError("paths must contain exactly one path for every dancer")
    conflicts: list[Conflict] = []
    minimum = float("inf")
    seen: set[tuple[str, str, int]] = set()
    for sample in range(request.config.sample_count + 1):
        progress = sample / request.config.sample_count
        time = progress * request.duration_seconds
        positions = {identifier: position_at(path, progress) for identifier, path in path_by_id.items()}
        for identifier, point in positions.items():
            dancer = dancer_by_id[identifier]
            half_w, half_d = request.stage.width / 2, request.stage.depth / 2
            if abs(point.x) + dancer.radius > half_w or abs(point.y) + dancer.radius > half_d:
                key = ("boundary", identifier, sample)
                if key not in seen:
                    seen.add(key)
                    conflicts.append(Conflict(kind="boundary", time_seconds=time, location=point, dancer_ids=[identifier], detail="Dancer radius crosses stage boundary."))
            for obstacle in request.obstacles:
                if distance(point, obstacle.center) < dancer.radius + obstacle.radius + request.config.safety_margin:
                    key = ("obstacle", identifier + obstacle.id, sample)
                    if key not in seen:
                        seen.add(key)
                        conflicts.append(Conflict(kind="obstacle", time_seconds=time, location=point, dancer_ids=[identifier], detail=f"Intersects obstacle {obstacle.id}."))
        identifiers = list(positions)
        for index, first in enumerate(identifiers):
            for second in identifiers[index + 1:]:
                separation = distance(positions[first], positions[second])
                minimum = min(minimum, separation)
                required = dancer_by_id[first].radius + dancer_by_id[second].radius + request.config.safety_margin
                if separation < required:
                    key = (first, second, sample)
                    if key not in seen:
                        seen.add(key)
                        kind = "initial_overlap" if sample == 0 else "final_overlap" if sample == request.config.sample_count else "dancer_collision"
                        conflicts.append(Conflict(kind=kind, time_seconds=time, location=Point(x=(positions[first].x + positions[second].x) / 2, y=(positions[first].y + positions[second].y) / 2), dancer_ids=[first, second], detail=f"Separation {separation:.3f}m is below required {required:.3f}m."))
    return ValidationResult(status="valid" if not conflicts else "conflicts_detected", conflicts=conflicts, minimum_separation=0 if minimum == float("inf") else minimum, samples_checked=request.config.sample_count + 1)

