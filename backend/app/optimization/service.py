"""High-level Multi-Stop Tour Optimization Orchestrator Service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..core.contracts import Graph, NodeNotFoundError, RouteNotFoundError
from .held_karp import HeldKarpSolver
from .matrix import PairwiseMatrix, PairwiseSubpath
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "held_karp_cost": self.held_karp_cost,
            "nearest_neighbor_cost": self.nearest_neighbor_cost,
            "approximation_gap_percent": self.approximation_gap_percent,
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
        return_to_depot: bool = True,
    ) -> TourExecutionResult:
        if not self._graph.has_node(depot):
            raise NodeNotFoundError(f"Depot node '{depot}' not found in graph")
        if not stops:
            raise ValueError("Tour optimization requires at least 1 delivery stop")
        if len(stops) > 10:
            raise ValueError("Tour optimization supports up to 10 delivery stops per request")

        # Validate unique stop nodes and existence in graph
        all_points = [depot] + list(stops)
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

        comparison = TourComparison(
            held_karp_cost=hk_cost,
            nearest_neighbor_cost=nn_cost,
            approximation_gap_percent=round(approx_gap, 2),
        )

        # Reconstruct visit order of point IDs
        visit_order = tuple(matrix.points[idx] for idx in hk_indices)

        # Subpath stitching for consecutive legs in optimal tour
        legs: list[TourLeg] = []
        full_path_nodes: list[str] = []
        full_edge_ids: list[str] = []
        total_distance_m = 0.0
        total_time_min = 0.0

        for i in range(len(hk_indices) - 1):
            u_idx = hk_indices[i]
            v_idx = hk_indices[i + 1]
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
            f"Held-Karp DP optimal tour selected visit sequence {' -> '.join(visit_order)} under "
            f"scenario {scenario_id}. Total weighted cost is {hk_cost:.6f}; "
            f"distance is {total_distance_m / 1000.0:.3f} km and ETA is "
            f"{total_time_min:.3f} min. Nearest Neighbor heuristic cost is "
            f"{nn_cost:.6f} (approximation gap: {approx_gap:.2f}%). {data_note}"
        )

        guarantee = "OPTIMAL_HELD_KARP"

        return TourExecutionResult(
            depot=depot,
            visit_order=visit_order,
            full_path=tuple(full_path_nodes),
            edge_ids=tuple(full_edge_ids),
            total_distance_m=total_distance_m,
            total_distance_km=total_distance_m / 1000.0,
            estimated_time_min=total_time_min,
            total_cost=hk_cost,
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
