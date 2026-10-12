"""Reproducible synthetic planner benchmark; run from backend with PYTHONPATH=."""
from __future__ import annotations

import json
import platform
from time import perf_counter

from app.models.domain import AssignmentRequest, AssignmentStrategy, Dancer, Point, TargetSlot, TransitionPlanRequest
from app.path_planning.baseline import plan_straight_paths


def scenario(count: int, strategy: AssignmentStrategy) -> TransitionPlanRequest:
    dancers = [Dancer(id=f"d{i}", label=str(i)) for i in range(count)]
    starts = {d.id: Point(x=-6 + (i % 6) * 2, y=-3 + (i // 6) * 1.5) for i, d in enumerate(dancers)}
    targets = [TargetSlot(id=f"s{i}", position=Point(x=6 - (i % 6) * 2, y=3 - (i // 6) * 1.5)) for i in range(count)]
    return TransitionPlanRequest(assignment_request=AssignmentRequest(dancers=dancers, start_positions=starts, targets=targets, strategy=strategy))


def main() -> None:
    rows = []
    for count in (4, 8, 12, 16, 24):
        for strategy in (AssignmentStrategy.GREEDY, AssignmentStrategy.MINIMUM_DISTANCE, AssignmentStrategy.MOVEMENT_AWARE):
            started = perf_counter(); result = plan_straight_paths(scenario(count, strategy)); elapsed = (perf_counter() - started) * 1000
            rows.append({"dancers": count, "strategy": strategy, "distance": round(result.metrics.total_distance, 3), "conflicts": result.metrics.collision_count, "status": result.status, "runtime_ms": round(elapsed, 3)})
    print(json.dumps({"seed": "deterministic-grid-v1", "python": platform.python_version(), "rows": rows}, indent=2))


if __name__ == "__main__": main()
