"""High-level Multi-Stop Tour Optimization Orchestrator Service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..core.contracts import Graph, NodeNotFoundError
from .held_karp import HeldKarpSolver
from .matrix import PairwiseMatrix
from .nearest_neighbor import NearestNeighborSolver


@dataclass(frozen=True, slots=True)
class TourLeg:
    """Detailed breakdown for a single leg between two consecutive stops."""

    from_node_id: str
    to_node_id: str
    path: tuple[str, ...]
    edge_ids: tuple[str, ...]
    distance_m: float
    distance_km: float
    travel_time_min: float
    total_cost: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "from_node_id": self.from_node_id,
            "to_node_id": self.to_node_id,
            "path": list(self.path),
            "edge_ids": list(self.edge_ids),
            "distance_m": self.distance_m,
            "distance_km": self.distance_km,
            "travel_time_min": self.travel_time_min,
            "total_cost": self.total_cost,
        }


@dataclass(frozen=True, slots=True)
class TourComparison:
    """Comparison metrics between exact Held-Karp and heuristic Nearest Neighbor."""

    held_karp_cost: float
    nearest_neighbor_cost: float
    approximation_gap_percent: float
    original_visit_order: tuple[str, ...]
    original_order_cost: float
    original_order_distance_km: float
    original_order_time_min: float
    selected_savings_cost: float
    selected_savings_percent: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "held_karp_cost": self.held_karp_cost,
            "nearest_neighbor_cost": self.nearest_neighbor_cost,
            "approximation_gap_percent": self.approximation_gap_percent,
            "original_visit_order": list(self.original_visit_order),
            "original_order_cost": self.original_order_cost,
            "original_order_distance_km": self.original_order_distance_km,
            "original_order_time_min": self.original_order_time_min,
            "selected_savings_cost": self.selected_savings_cost,
            "selected_savings_percent": self.selected_savings_percent,
        }


@dataclass(frozen=True, slots=True)
class TourExecutionResult:
    """Structured response for a multi-stop tour optimization request."""

    depot: str
    visit_order: tuple[str, ...]
    full_path: tuple[str, ...]
    edge_ids: tuple[str, ...]
    total_distance_m: float
    total_distance_km: float
    estimated_time_min: float
    total_cost: float
    comparison: TourComparison
    legs: tuple[TourLeg, ...]
    guarantee: str
    explanation: str
    data_status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "depot": self.depot,
            "visit_order": list(self.visit_order),
            "full_path": list(self.full_path),
            "edge_ids": list(self.edge_ids),
            "total_distance_m": self.total_distance_m,
            "total_distance_km": self.total_distance_km,
            "estimated_time_min": self.estimated_time_min,
            "total_cost": self.total_cost,
            "comparison": self.comparison.to_dict(),
            "legs": [leg.to_dict() for leg in self.legs],
            "guarantee": self.guarantee,
            "explanation": self.explanation,
            "data_status": self.data_status,
        }


class TourOptimizerService:
    """Orchestrates pairwise matrix construction, exact DP, heuristic solvers, and subpath stitching."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph

    @property
    def graph(self) -> Graph:
        return self._graph

    def optimize_tour(
        self,
        *,
        depot: str,
        stops: list[str] | tuple[str, ...],
        scenario_id: str,
        algorithm: str = "A_STAR",
        tour_algorithm: str = "HELD_KARP",
        return_to_depot: bool = True,
    ) -> TourExecutionResult:
        if not self._graph.has_node(depot):
            raise NodeNotFoundError(f"Depot node '{depot}' not found in graph")
        if len(stops) < 5:
            raise ValueError("Tour optimization requires at least 5 delivery stops")
        if len(stops) > 10:
            raise ValueError("Tour optimization supports up to 10 delivery stops per request")

        normalized_tour_algorithm = tour_algorithm.strip().upper()
        supported_tour_algorithms = {"HELD_KARP", "NEAREST_NEIGHBOR"}
        if normalized_tour_algorithm not in supported_tour_algorithms:
            available = ", ".join(sorted(supported_tour_algorithms))
            raise ValueError(
                f"Unknown tour algorithm: {tour_algorithm}. "
                f"Available tour algorithms: {available}"
            )

        stop_ids = tuple(stops)
        if depot in stop_ids:
            raise ValueError("Depot must not also appear in delivery stops")
        if len(set(stop_ids)) != len(stop_ids):
            raise ValueError("Delivery stops must contain unique node IDs")

        # Validate stop existence in graph after enforcing the request contract.
        all_points = [depot, *stop_ids]
        for node_id in all_points:
            if not self._graph.has_node(node_id):
                raise NodeNotFoundError(f"Stop node '{node_id}' not found in graph")

        # Build Pairwise Matrix for all (u, v) pairs
        matrix = PairwiseMatrix(
            graph=self._graph,
            points=all_points,
            scenario_id=scenario_id,
            algorithm=algorithm,
        )

        # Solve exact Held-Karp TSP
        hk_indices, hk_cost, hk_distance = HeldKarpSolver().solve(
            matrix=matrix,
            start_index=0,
            return_to_depot=return_to_depot,
        )

        # Solve heuristic Nearest Neighbor TSP
        nn_indices, nn_cost, _ = NearestNeighborSolver().solve(
            matrix=matrix,
            start_index=0,
            return_to_depot=return_to_depot,
        )

        # Compute approximation gap
        if hk_cost > 0:
            approx_gap = ((nn_cost - hk_cost) / hk_cost) * 100.0
        else:
            approx_gap = 0.0

        # Select indices based on tour_algorithm choice
        if normalized_tour_algorithm == "NEAREST_NEIGHBOR":
            selected_indices = nn_indices
            selected_cost = nn_cost
            guarantee = "APPROXIMATE_NEAREST_NEIGHBOR"
            alg_label = "Nearest Neighbor heuristic tour"
        else:
            selected_indices = hk_indices
            selected_cost = hk_cost
            guarantee = "OPTIMAL_HELD_KARP"
            alg_label = "Held-Karp DP optimal tour"

        original_indices = list(range(len(all_points)))
        if return_to_depot:
            original_indices.append(0)
        original_cost = sum(
            matrix.cost_matrix[u_idx][v_idx]
            for u_idx, v_idx in zip(original_indices, original_indices[1:])
        )
        original_distance_m = sum(
            matrix.get_subpath(u_idx, v_idx).distance_m
            for u_idx, v_idx in zip(original_indices, original_indices[1:])
        )
        original_time_min = sum(
            matrix.get_subpath(u_idx, v_idx).travel_time_min
            for u_idx, v_idx in zip(original_indices, original_indices[1:])
        )
        selected_savings = original_cost - selected_cost
        selected_savings_percent = (
            selected_savings / original_cost * 100.0 if original_cost > 0 else 0.0
        )
        comparison = TourComparison(
            held_karp_cost=hk_cost,
            nearest_neighbor_cost=nn_cost,
            approximation_gap_percent=round(approx_gap, 2),
            original_visit_order=tuple(matrix.points[idx] for idx in original_indices),
            original_order_cost=original_cost,
            original_order_distance_km=original_distance_m / 1000.0,
            original_order_time_min=original_time_min,
            selected_savings_cost=selected_savings,
            selected_savings_percent=round(selected_savings_percent, 2),
        )

        # Reconstruct visit order of point IDs
        visit_order = tuple(matrix.points[idx] for idx in selected_indices)

        # Subpath stitching for consecutive legs in chosen tour
        legs: list[TourLeg] = []
        full_path_nodes: list[str] = []
        full_edge_ids: list[str] = []
        total_distance_m = 0.0
        total_time_min = 0.0

        for i in range(len(selected_indices) - 1):
            u_idx = selected_indices[i]
            v_idx = selected_indices[i + 1]
            subpath = matrix.get_subpath(u_idx, v_idx)

            leg = TourLeg(
                from_node_id=subpath.from_node_id,
                to_node_id=subpath.to_node_id,
                path=subpath.path,
                edge_ids=subpath.edge_ids,
                distance_m=subpath.distance_m,
                distance_km=subpath.distance_km,
                travel_time_min=subpath.travel_time_min,
                total_cost=subpath.total_cost,
            )
            legs.append(leg)

            total_distance_m += subpath.distance_m
            total_time_min += subpath.travel_time_min

            # Seamless path stitching without duplicate boundary nodes
            if not full_path_nodes:
                full_path_nodes.extend(subpath.path)
            else:
                full_path_nodes.extend(subpath.path[1:])

            full_edge_ids.extend(subpath.edge_ids)

        data_status = str(self._graph.metadata.get("data_status", "DERIVED"))
        data_note = f"Data status is {data_status}."
        if self._graph.metadata.get("real_time") is False:
            data_note += " Traffic profiles are historical, not real-time."

        explanation = (
            f"{alg_label} selected visit sequence {' -> '.join(visit_order)} under "
            f"scenario {scenario_id}. Total weighted cost is {selected_cost:.6f}; "
            f"distance is {total_distance_m / 1000.0:.3f} km and ETA is "
            f"{total_time_min:.3f} min. Held-Karp exact cost is {hk_cost:.6f}, "
            f"Nearest Neighbor cost is {nn_cost:.6f} (approximation gap: {approx_gap:.2f}%). {data_note}"
            f" Compared with the original input order ({original_cost:.6f}), the selected "
            f"tour changes weighted cost by {-selected_savings:+.6f} and saves "
            f"{selected_savings_percent:.2f}%."
        )

        return TourExecutionResult(
            depot=depot,
            visit_order=visit_order,
            full_path=tuple(full_path_nodes),
            edge_ids=tuple(full_edge_ids),
            total_distance_m=total_distance_m,
            total_distance_km=total_distance_m / 1000.0,
            estimated_time_min=total_time_min,
            total_cost=selected_cost,
            comparison=comparison,
            legs=tuple(legs),
            guarantee=guarantee,
            explanation=explanation,
            data_status=data_status,
        )


__all__ = [
    "TourComparison",
    "TourExecutionResult",
    "TourLeg",
    "TourOptimizerService",
]
