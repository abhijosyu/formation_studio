from __future__ import annotations

from math import cos, pi, radians, sin

from app.models.domain import Point, TargetSlot, TemplateKind, TemplateRequest


def _rotate_and_mirror(point: Point, request: TemplateRequest) -> Point:
    x = -point.x if request.mirrored else point.x
    angle = radians(request.rotation_degrees)
    return Point(
        x=request.center.x + x * cos(angle) - point.y * sin(angle),
        y=request.center.y + x * sin(angle) + point.y * cos(angle),
    )


def generate_template(request: TemplateRequest) -> list[TargetSlot]:
    """Generate deterministic local coordinates then apply mirror/rotation/translation."""
    n, col, row = request.count, request.column_spacing, request.row_spacing
    coords: list[Point]
    if request.kind == TemplateKind.LINE:
        coords = [Point(x=(index - (n - 1) / 2) * col, y=0) for index in range(n)]
    elif request.kind == TemplateKind.DIAGONAL:
        coords = [Point(x=(index - (n - 1) / 2) * col, y=(index - (n - 1) / 2) * row) for index in range(n)]
    elif request.kind == TemplateKind.V:
        coords = [Point(x=(index - (n - 1) / 2) * col, y=abs(index - (n - 1) / 2) * row) for index in range(n)]
    elif request.kind == TemplateKind.CIRCLE:
        radius = max(col, row) * n / (2 * pi)
        coords = [Point(x=radius * cos(-pi / 2 + 2 * pi * index / n), y=radius * sin(-pi / 2 + 2 * pi * index / n)) for index in range(n)]
    else:
        columns = max(1, int(n**0.5 + 0.999))
        coords = []
        for index in range(n):
            r, c = divmod(index, columns)
            offset = (0.5 * col if request.kind == TemplateKind.STAGGERED_ROWS and r % 2 else 0)
            coords.append(Point(x=(c - (columns - 1) / 2) * col + offset, y=(r - (n - 1) / columns / 2) * row))
    return [TargetSlot(id=f"slot-{index + 1}", position=_rotate_and_mirror(point, request)) for index, point in enumerate(coords)]

