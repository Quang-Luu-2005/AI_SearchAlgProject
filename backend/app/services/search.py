"""Framework-independent search orchestration for API and experiments."""

from __future__ import annotations

from time import perf_counter

from ..algorithms import resolve_algorithm
from ..core.contracts import (
    Graph,
    RouteMetrics,
    SearchExecution,
    SearchResult,
    RouteNotFoundError,
    Scenario,
)
from ..core.cost import ScenarioCostEngine


class SearchService:
    """Validate graph inputs, dispatch search and build verifiable metrics."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph
        self._cost_engine = ScenarioCostEngine(graph)

    @property
    def graph(self) -> Graph:
        return self._graph

    def search(
        self,
        *,
        start: str,
        goal: str,
        algorithm: str,
        scenario_id: str,
    ) -> SearchExecution:
        self._graph.get_node(start)
        self._graph.get_node(goal)
        self._graph.scenario(scenario_id)
        algorithm_name, implementation = resolve_algorithm(algorithm)

        started_at = perf_counter()
        search_path = implementation(
            self._graph,
            self._cost_engine,
            start,
            goal,
            scenario_id,
        )
        processing_time_ms = (perf_counter() - started_at) * 1000

        route_cost = self._cost_engine.route_cost(list(search_path.edge_ids), scenario_id)
        if not route_cost.is_available or route_cost.total_cost is None:
            raise RuntimeError("Search returned a route containing a closed edge")

        distance_m = sum(edge_cost.distance_km * 1000 for edge_cost in route_cost.edge_costs)
        estimated_time_min = sum(
            edge_cost.travel_time_min for edge_cost in route_cost.edge_costs
        )
        component_totals = {
            component: sum(
                edge_cost.weighted_components.get(component, 0.0)
                for edge_cost in route_cost.edge_costs
            )
            for component in ("distance", "freeflow_time", "congestion", "flood_risk")
        }
        dominant_component = max(
            component_totals,
            key=lambda component: (component_totals[component], component),
        )
        highest_penalty_edge = max(
            route_cost.edge_costs,
            key=lambda edge_cost: (
                edge_cost.weighted_components.get("congestion", 0.0)
                + edge_cost.weighted_components.get("flood_risk", 0.0),
                edge_cost.edge_id,
            ),
            default=None,
        )
        if highest_penalty_edge is None:
            penalty_note = "The route has no traversed edge to evaluate for penalties."
        else:
            penalty_note = (
                f"The highest traffic/flood penalty segment is {highest_penalty_edge.edge_id}: "
                f"traffic penalty {highest_penalty_edge.traffic_penalty:.3f} min and "
                f"flood risk {highest_penalty_edge.flood_risk:.3f}."
            )
        data_note = f"Data status is {route_cost.data_status}."
        if self._graph.metadata.get("real_time") is False:
            data_note += " Traffic profiles are historical, not real-time."
        explanation = (
            f"{algorithm_name.value} selected {' -> '.join(search_path.path)} under "
            f"{scenario_id}. Total weighted cost is {route_cost.total_cost:.6f}; "
            f"distance is {distance_m / 1000:.3f} km and ETA is "
            f"{estimated_time_min:.3f} min. The largest weighted component is "
            f"{dominant_component} ({component_totals[dominant_component]:.6f}). "
            f"{penalty_note} {data_note}"
        )
        result = SearchResult(
            path=search_path.path,
            metrics=RouteMetrics(
                distance_m=distance_m,
                estimated_time_min=estimated_time_min,
                total_cost=route_cost.total_cost,
                explored_nodes=search_path.explored_nodes,
                processing_time_ms=processing_time_ms,
            ),
            trace=search_path.trace,
            guarantee=search_path.guarantee,
            explanation=explanation,
        )
        return SearchExecution(
            algorithm=algorithm_name,
            scenario_id=scenario_id,
            edge_ids=search_path.edge_ids,
            edge_costs=route_cost.edge_costs,
            result=result,
            data_status=route_cost.data_status,
        )

    def compare(
        self,
        *,
        start: str,
        goal: str,
        algorithms: list[str] | tuple[str, ...],
        scenario_id: str,
    ) -> tuple[SearchExecution, ...]:
        if not algorithms:
            raise ValueError("Compare requires at least one algorithm")
        executions: list[SearchExecution] = []
        seen: set[str] = set()
        for algorithm in algorithms:
            normalized = algorithm.strip().upper()
            if normalized in seen:
                continue
            seen.add(normalized)
            executions.append(
                self.search(
                    start=start,
                    goal=goal,
                    algorithm=algorithm,
                    scenario_id=scenario_id,
                )
            )
        return tuple(executions)

    def alternatives(
        self,
        *,
        start: str,
        goal: str,
        algorithm: str,
        scenario_id: str,
        limit: int = 2,
    ) -> tuple[SearchExecution, ...]:
        """Find up to ``limit`` distinct alternatives using one algorithm.

        Each candidate is generated by temporarily closing one edge from the
        previously selected route. This keeps the algorithm, costs and scenario
        identical while guaranteeing that an alternative differs by at least one
        edge from the primary route.
        """
        if limit < 1:
            raise ValueError("Alternative route limit must be positive")
        primary = self.search(
            start=start,
            goal=goal,
            algorithm=algorithm,
            scenario_id=scenario_id,
        )
        results: list[SearchExecution] = [primary]
        seen = {primary.edge_ids}
        base_scenario = self._graph.scenario(scenario_id)
        base_closed = set(base_scenario.closed_edge_ids)

        for edge_id in primary.edge_ids:
            if len(results) >= limit + 1:
                break
            if edge_id in base_closed:
                continue
            alternative_id = f"__ALT__{scenario_id}__{edge_id}"
            alternative_scenario = Scenario(
                scenario_id=alternative_id,
                closed_edge_ids=tuple(sorted(base_closed | {edge_id})),
                attributes=dict(base_scenario.attributes),
            )
            alternative_graph = Graph(
                nodes=self._graph.nodes,
                edges=self._graph.edges,
                scenarios=tuple(self._graph.scenarios) + (alternative_scenario,),
                metadata=self._graph.metadata,
            )
            try:
                candidate = SearchService(alternative_graph).search(
                    start=start,
                    goal=goal,
                    algorithm=algorithm,
                    scenario_id=alternative_id,
                )
            except RouteNotFoundError:
                continue
            if candidate.edge_ids in seen:
                continue
            seen.add(candidate.edge_ids)
            results.append(candidate)

        return tuple(results)


__all__ = ["SearchService"]
