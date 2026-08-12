"""Pairwise shortest path and cost matrix computation for multi-stop tour optimization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..core.contracts import Graph, RouteNotFoundError
from ..core.cost import ScenarioCostEngine
from ..services.search import SearchService


@dataclass(frozen=True, slots=True)
class PairwiseSubpath:
    """Stores the shortest path search result between a pair of nodes."""

    from_node_id: str
    to_node_id: str
    path: tuple[str, ...]
    edge_ids: tuple[str, ...]
    distance_m: float
    distance_km: float
    travel_time_min: float
    total_cost: float
    is_reachable: bool


class PairwiseMatrix:
    """Computes and stores pairwise distances, costs, and subpaths for N points."""

    def __init__(
        self,
        graph: Graph,
        points: list[str] | tuple[str, ...],
        scenario_id: str,
        algorithm: str = "A_STAR",
    ) -> None:
        if not points:
            raise ValueError("PairwiseMatrix requires at least one point")

        self._graph = graph
        self._points = tuple(points)
        self._scenario_id = scenario_id
        self._algorithm = algorithm
        self._n = len(self._points)
        self._search_service = SearchService(graph)

        self._cost_matrix: list[list[float]] = [
            [0.0 if i == j else float("inf") for j in range(self._n)]
            for i in range(self._n)
        ]
        self._distance_matrix: list[list[float]] = [
            [0.0 if i == j else float("inf") for j in range(self._n)]
            for i in range(self._n)
        ]
        self._subpaths: list[list[PairwiseSubpath | None]] = [
            [None for _ in range(self._n)] for _ in range(self._n)
        ]

        self._compute_matrix()

    @property
    def points(self) -> tuple[str, ...]:
        return self._points

    @property
    def n(self) -> int:
        return self._n

    @property
    def scenario_id(self) -> str:
        return self._scenario_id

    @property
    def cost_matrix(self) -> list[list[float]]:
        return self._cost_matrix

    @property
    def distance_matrix(self) -> list[list[float]]:
        return self._distance_matrix

    def get_subpath(self, i: int, j: int) -> PairwiseSubpath:
        subpath = self._subpaths[i][j]
        if subpath is None or not subpath.is_reachable:
            from_id = self._points[i]
            to_id = self._points[j]
            raise RouteNotFoundError(
                f"No reachable route between '{from_id}' and '{to_id}' in scenario '{self._scenario_id}'"
            )
        return subpath

    def _compute_matrix(self) -> None:
        for i in range(self._n):
            from_node = self._points[i]
            for j in range(self._n):
                if i == j:
                    self._subpaths[i][j] = PairwiseSubpath(
                        from_node_id=from_node,
                        to_node_id=from_node,
                        path=(from_node,),
                        edge_ids=(),
                        distance_m=0.0,
                        distance_km=0.0,
                        travel_time_min=0.0,
                        total_cost=0.0,
                        is_reachable=True,
                    )
                    continue

                to_node = self._points[j]
                try:
                    execution = self._search_service.search(
                        start=from_node,
                        goal=to_node,
                        algorithm=self._algorithm,
                        scenario_id=self._scenario_id,
                    )
                    res = execution.result
                    subpath = PairwiseSubpath(
                        from_node_id=from_node,
                        to_node_id=to_node,
                        path=res.path,
                        edge_ids=execution.edge_ids,
                        distance_m=res.metrics.distance_m,
                        distance_km=res.metrics.distance_m / 1000.0,
                        travel_time_min=res.metrics.estimated_time_min,
                        total_cost=res.metrics.total_cost,
                        is_reachable=True,
                    )
                    self._cost_matrix[i][j] = res.metrics.total_cost
                    self._distance_matrix[i][j] = res.metrics.distance_m
                    self._subpaths[i][j] = subpath
                except (RouteNotFoundError, LookupError, RuntimeError):
                    self._cost_matrix[i][j] = float("inf")
                    self._distance_matrix[i][j] = float("inf")
                    self._subpaths[i][j] = PairwiseSubpath(
                        from_node_id=from_node,
                        to_node_id=to_node,
                        path=(),
                        edge_ids=(),
                        distance_m=float("inf"),
                        distance_km=float("inf"),
                        travel_time_min=float("inf"),
                        total_cost=float("inf"),
                        is_reachable=False,
                    )


__all__ = ["PairwiseMatrix", "PairwiseSubpath"]
