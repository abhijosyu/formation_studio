from __future__ import annotations

from math import hypot

from app.models.domain import Path, Point


def smoothstep(progress: float) -> float:
    value = max(0.0, min(1.0, progress))
    return value * value * (3 - 2 * value)


def position_at(path: Path, progress: float) -> Point:
    """Evaluate the same uniform-segment smoothstep path used by UI and validation."""
    eased = smoothstep(progress)
    segments = len(path.points) - 1
    scaled = min(eased * segments, segments - 1e-12)
    index = int(scaled)
    local = scaled - index
    start, end = path.points[index], path.points[index + 1]
    return Point(x=start.x + (end.x - start.x) * local, y=start.y + (end.y - start.y) * local)


def distance(a: Point, b: Point) -> float:
    return hypot(a.x - b.x, a.y - b.y)


def polyline_length(path: Path) -> float:
    return sum(distance(a, b) for a, b in zip(path.points, path.points[1:]))
