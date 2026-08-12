"""Exact Dynamic Programming Held-Karp TSP solver and Brute Force verification solver."""

from __future__ import annotations

from itertools import permutations

from ..core.contracts import RouteNotFoundError
from .matrix import PairwiseMatrix


class HeldKarpSolver:
    """Exact DP solver for Travelling Salesperson Problem using bitmask memoization."""

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
        if start_index != 0:
            raise ValueError("HeldKarpSolver currently expects start_index = 0")

        full_mask = (1 << n) - 1
        # dp[(mask, u)] = (min_cost, parent_node)
        dp: dict[tuple[int, int], tuple[float, int | None]] = {}
        dp[(1 << 0, 0)] = (0.0, None)

        for size in range(2, n + 1):
            for mask in range(1 << n):
                if not (mask & (1 << 0)):
                    continue
                # Count bits set in mask
                if bin(mask).count("1") != size:
                    continue

                for u in range(1, n):
                    if not (mask & (1 << u)):
                        continue
                    prev_mask = mask ^ (1 << u)
                    best_cost = float("inf")
                    best_prev: int | None = None

                    for v in range(n):
                        if not (prev_mask & (1 << v)):
                            continue
                        if (prev_mask, v) not in dp:
                            continue

                        prev_cost = dp[(prev_mask, v)][0]
                        step_cost = matrix.cost_matrix[v][u]
                        if prev_cost == float("inf") or step_cost == float("inf"):
                            continue

                        candidate_cost = prev_cost + step_cost
                        # Deterministic tie-breaking: lower cost, then lower node index
                        if candidate_cost < best_cost or (
                            abs(candidate_cost - best_cost) < 1e-9
                            and (best_prev is None or v < best_prev)
                        ):
                            best_cost = candidate_cost
                            best_prev = v

                    if best_cost < float("inf"):
                        dp[(mask, u)] = (best_cost, best_prev)

        # Final step: find minimum overall tour cost
        best_final_cost = float("inf")
        best_last_node: int | None = None

        if return_to_depot:
            for u in range(1, n):
                if (full_mask, u) not in dp:
                    continue
                path_cost = dp[(full_mask, u)][0]
                return_cost = matrix.cost_matrix[u][0]
                if path_cost == float("inf") or return_cost == float("inf"):
                    continue

                total_cost = path_cost + return_cost
                if total_cost < best_final_cost or (
                    abs(total_cost - best_final_cost) < 1e-9
                    and (best_last_node is None or u < best_last_node)
                ):
                    best_final_cost = total_cost
                    best_last_node = u
        else:
            for u in range(1, n):
                if (full_mask, u) not in dp:
                    continue
                path_cost = dp[(full_mask, u)][0]
                if path_cost < best_final_cost or (
                    abs(path_cost - best_final_cost) < 1e-9
                    and (best_last_node is None or u < best_last_node)
                ):
                    best_final_cost = path_cost
                    best_last_node = u

        if best_final_cost == float("inf") or best_last_node is None:
            raise RouteNotFoundError(
                f"Held-Karp failed: no valid tour visiting all {n} nodes in scenario '{matrix.scenario_id}'"
            )

        # Backtrack path reconstruction
        curr_mask = full_mask
        curr_node: int | None = best_last_node
        path_indices: list[int] = []

        while curr_node is not None:
            path_indices.append(curr_node)
            next_node = dp.get((curr_mask, curr_node), (0.0, None))[1]
            curr_mask ^= 1 << curr_node
            curr_node = next_node

        path_indices.reverse()
        if return_to_depot:
            path_indices.append(0)

        # Calculate exact total distance along optimal path_indices
        total_distance = 0.0
        for i in range(len(path_indices) - 1):
            u_idx = path_indices[i]
            v_idx = path_indices[i + 1]
            total_distance += matrix.distance_matrix[u_idx][v_idx]

        return path_indices, best_final_cost, total_distance


class BruteForceSolver:
    """Brute Force TSP solver used to cross-verify Held-Karp exactness on small inputs."""

    def solve(
        self,
        matrix: PairwiseMatrix,
        start_index: int = 0,
        return_to_depot: bool = True,
    ) -> tuple[list[int], float, float]:
        n = matrix.n
        if n > 7:
            raise ValueError("BruteForceSolver is intended for small inputs N <= 7 only")
        if n <= 1:
            return [0], 0.0, 0.0

        other_nodes = [i for i in range(n) if i != start_index]
        best_cost = float("inf")
        best_tour: list[int] = []
        best_distance = 0.0

        for perm in permutations(other_nodes):
            tour = [start_index] + list(perm)
            if return_to_depot:
                tour.append(start_index)

            current_cost = 0.0
            current_distance = 0.0
            valid = True

            for i in range(len(tour) - 1):
                u_idx = tour[i]
                v_idx = tour[i + 1]
                step_c = matrix.cost_matrix[u_idx][v_idx]
                step_d = matrix.distance_matrix[u_idx][v_idx]
                if step_c == float("inf"):
                    valid = False
                    break
                current_cost += step_c
                current_distance += step_d

            if valid and current_cost < best_cost:
                best_cost = current_cost
                best_tour = tour
                best_distance = current_distance

        if best_cost == float("inf"):
            raise RouteNotFoundError("BruteForceSolver failed: no valid tour found")

        return best_tour, best_cost, best_distance


__all__ = ["HeldKarpSolver", "BruteForceSolver"]
