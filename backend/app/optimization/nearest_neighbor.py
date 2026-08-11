"""Greedy Nearest Neighbor solver for multi-stop tour optimization."""

from __future__ import annotations

from ..core.contracts import RouteNotFoundError
from .matrix import PairwiseMatrix


class NearestNeighborSolver:
    """Greedy Nearest Neighbor algorithm to quickly construct a TSP delivery tour."""

    def solve(
        self,
        matrix: PairwiseMatrix,
        start_index: int = 0,
        return_to_depot: bool = True,
    ) -> tuple[list[int], float, float]:
        n = matrix.n
        if n == 0:
            return [], 0.0, 0.0
        if n == 1:
            return [0], 0.0, 0.0

        visited = [start_index]
        unvisited = set(range(n)) - {start_index}
        current = start_index
        total_cost = 0.0
        total_distance = 0.0

        while unvisited:
            # Deterministic tie-breaking: sort by cost, then by node index
            best_next = min(
                unvisited,
                key=lambda candidate: (
                    matrix.cost_matrix[current][candidate],
                    candidate,
                ),
            )
            step_cost = matrix.cost_matrix[current][best_next]
            if step_cost == float("inf"):
                from_id = matrix.points[current]
                to_id = matrix.points[best_next]
                raise RouteNotFoundError(
                    f"Nearest Neighbor failed: unreachable step from '{from_id}' to '{to_id}'"
                )

            total_cost += step_cost
            total_distance += matrix.distance_matrix[current][best_next]
            visited.append(best_next)
            unvisited.remove(best_next)
            current = best_next

        if return_to_depot:
            return_cost = matrix.cost_matrix[current][start_index]
            if return_cost == float("inf"):
                from_id = matrix.points[current]
                to_id = matrix.points[start_index]
                raise RouteNotFoundError(
                    f"Nearest Neighbor failed: unreachable return leg from '{from_id}' to '{to_id}'"
                )
            total_cost += return_cost
            total_distance += matrix.distance_matrix[current][start_index]
            visited.append(start_index)

        return visited, total_cost, total_distance


__all__ = ["NearestNeighborSolver"]
