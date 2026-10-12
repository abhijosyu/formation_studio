from __future__ import annotations

from math import hypot

import numpy as np
from scipy.optimize import linear_sum_assignment

from app.models.domain import Assignment, AssignmentRequest, AssignmentResponse, AssignmentStrategy


def euclidean_cost(request: AssignmentRequest) -> list[list[float]]:
    """Return the dancer-by-target physical-distance cost matrix in metres."""
    return [
        [
            hypot(
                request.start_positions[dancer.id].x - target.position.x,
                request.start_positions[dancer.id].y - target.position.y,
            )
            for target in request.targets
        ]
        for dancer in request.dancers
    ]


def _crosses(a, b, c, d) -> bool:
    def orient(first, second, third):
        return (second.x - first.x) * (third.y - first.y) - (second.y - first.y) * (third.x - first.x)
    return orient(a, b, c) * orient(a, b, d) < 0 and orient(c, d, a) * orient(c, d, b) < 0


def movement_aware_cost(request: AssignmentRequest, costs: list[list[float]]) -> list[list[float]]:
    """Distance plus a deterministic 0.5m predicted-crossing penalty.

    Each candidate is compared with every other dancer's independently nearest target.
    It is a heuristic cost matrix, not a joint collision optimizer.
    """
    nearest = [min(range(len(request.targets)), key=lambda j: costs[i][j]) for i in range(len(request.dancers))]
    adjusted = [row.copy() for row in costs]
    for i, dancer in enumerate(request.dancers):
        for j, target in enumerate(request.targets):
            for other_index, other in enumerate(request.dancers):
                if dancer.id != other.id and _crosses(request.start_positions[dancer.id], target.position, request.start_positions[other.id], request.targets[nearest[other_index]].position): adjusted[i][j] += 0.5
    return adjusted


def solve_assignment(request: AssignmentRequest) -> AssignmentResponse:
    costs = euclidean_cost(request)
    if request.strategy == AssignmentStrategy.MOVEMENT_AWARE:
        costs = movement_aware_cost(request, costs)
    remaining = set(range(len(request.targets)))
    pairs: list[tuple[int, int]] = []

    if request.strategy == AssignmentStrategy.GREEDY:
        for dancer_index, row in enumerate(costs):
            target_index = min(remaining, key=lambda index: (row[index], request.targets[index].id))
            pairs.append((dancer_index, target_index))
            remaining.remove(target_index)
    else:
        # SciPy's solver finds a global minimum. The tiny index perturbation only resolves
        # otherwise equal numerical costs deterministically; reported costs are unperturbed.
        matrix = np.asarray(costs, dtype=float)
        perturbation = np.arange(matrix.size, dtype=float).reshape(matrix.shape) * 1e-12
        dancer_indices, target_indices = linear_sum_assignment(matrix + perturbation)
        pairs = sorted(zip(dancer_indices.tolist(), target_indices.tolist()))

    assignments = [
        Assignment(
            dancer_id=request.dancers[dancer_index].id,
            target_id=request.targets[target_index].id,
            cost=costs[dancer_index][target_index],
        )
        for dancer_index, target_index in pairs
    ]
    return AssignmentResponse(
        strategy=request.strategy,
        assignments=assignments,
        total_cost=sum(item.cost for item in assignments),
    )
