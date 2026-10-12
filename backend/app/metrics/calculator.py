from __future__ import annotations

from math import acos

from app.models.domain import Metrics, Path, ValidationResult
from app.simulation.core import polyline_length


def _crossings(paths: list[Path]) -> int:
    # Geometric route crossings, excluding shared end points; separate from temporal collisions.
    def orient(a, b, c): return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)
    count = 0
    for index, first in enumerate(paths):
        for second in paths[index + 1:]:
            for a, b in zip(first.points, first.points[1:]):
                for c, d in zip(second.points, second.points[1:]):
                    if orient(a, b, c) * orient(a, b, d) < 0 and orient(c, d, a) * orient(c, d, b) < 0: count += 1
    return count


def calculate_metrics(paths: list[Path], duration: float, validation: ValidationResult, planning_time_ms: float) -> Metrics:
    lengths = [polyline_length(path) for path in paths]
    changes = 0
    for path in paths:
        for a, b, c in zip(path.points, path.points[1:], path.points[2:]):
            ab, bc = (b.x - a.x, b.y - a.y), (c.x - b.x, c.y - b.y)
            denominator = (ab[0] ** 2 + ab[1] ** 2) ** .5 * (bc[0] ** 2 + bc[1] ** 2) ** .5
            if denominator and acos(max(-1, min(1, (ab[0] * bc[0] + ab[1] * bc[1]) / denominator))) > .2: changes += 1
    return Metrics(total_distance=sum(lengths), max_individual_distance=max(lengths, default=0), mean_individual_distance=sum(lengths) / len(lengths) if lengths else 0, collision_count=len(validation.conflicts), minimum_separation=validation.minimum_separation, path_crossings=_crossings(paths), direction_changes=changes, duration_seconds=duration, planning_time_ms=planning_time_ms, validation_status=validation.status)
