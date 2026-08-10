"""Deterministic non-negative weighted search implementations."""

from __future__ import annotations

import heapq
from collections.abc import Callable

from ..core.contracts import (
    AlgorithmName,
    AlgorithmNotFoundError,
    CostModelError,
    Graph,
    RouteNotFoundError,
    SearchPath,
    TraceEvent,
    TraceEventKind,
)
from ..core.cost import ScenarioCostEngine


import math

SearchImplementation = Callable[
    [Graph, ScenarioCostEngine, str, str, str],
    SearchPath,
]


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two WGS84 points in kilometers."""
    r = 6371.0  # Earth's mean radius in kilometers
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c


def compute_heuristic(
    graph: Graph,
    cost_engine: ScenarioCostEngine,
    node_id: str,
    goal_id: str,
    scenario_id: str,
) -> float:
    """Compute the admissible and consistent geographic weighted Haversine distance heuristic."""
    if node_id == goal_id:
        return 0.0
    node = graph.get_node(node_id)
    goal_node = graph.get_node(goal_id)
    if (
        node.latitude is None
        or node.longitude is None
        or goal_node.latitude is None
        or goal_node.longitude is None
    ):
        return 0.0
    dist_km = haversine_distance_km(
        node.latitude, node.longitude, goal_node.latitude, goal_node.longitude
    )
    try:
        preset = cost_engine.preset_for_scenario(scenario_id)
        w_dist = preset.weights.get("distance", 0.0)
    except CostModelError:
        w_dist = 0.0
    return w_dist * dist_km


def _reconstruct_path(
    start: str,
    goal: str,
    parents: dict[str, tuple[str, str]],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    nodes = [goal]
    edges: list[str] = []
    current = goal
    while current != start:
        parent, edge_id = parents[current]
        nodes.append(parent)
        edges.append(edge_id)
        current = parent
    nodes.reverse()
    edges.reverse()
    return tuple(nodes), tuple(edges)


def _weighted_search(
    graph: Graph,
    cost_engine: ScenarioCostEngine,
    start: str,
    goal: str,
    scenario_id: str,
    *,
    algorithm: AlgorithmName,
) -> SearchPath:
    graph.get_node(start)
    graph.get_node(goal)
    graph.scenario(scenario_id)

    is_astar = algorithm == AlgorithmName.A_STAR
    start_h = compute_heuristic(graph, cost_engine, start, goal, scenario_id) if is_astar else 0.0

    # Priority queue element: (f_cost, g_cost, node_id) for A*, (g_cost, node_id) for UCS
    frontier: list[tuple[float, ...]] = (
        [(start_h, 0.0, start)] if is_astar else [(0.0, start)]
    )
    best_cost: dict[str, float] = {start: 0.0}
    parents: dict[str, tuple[str, str]] = {}
    expanded: set[str] = set()
    trace: list[TraceEvent] = []
    step = 0

    def record(
        kind: TraceEventKind,
        node_id: str,
        *,
        parent_id: str | None = None,
        g_cost: float | None = None,
        h_cost: float | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        nonlocal step
        trace.append(
            TraceEvent(
                step=step,
                kind=kind,
                node_id=node_id,
                parent_id=parent_id,
                g_cost=g_cost,
                h_cost=h_cost,
                details=dict(details or {}),
            )
        )
        step += 1

    record(TraceEventKind.OPEN, start, g_cost=0.0, h_cost=start_h)
    while frontier:
        pop_item = heapq.heappop(frontier)
        if is_astar:
            _, current_cost, node_id = pop_item
        else:
            current_cost, node_id = pop_item

        if current_cost != best_cost.get(node_id) or node_id in expanded:
            continue

        expanded.add(node_id)
        current_h = compute_heuristic(graph, cost_engine, node_id, goal, scenario_id) if is_astar else 0.0
        record(TraceEventKind.EXPAND, node_id, g_cost=current_cost, h_cost=current_h)

        if node_id == goal:
            record(TraceEventKind.GOAL, node_id, g_cost=current_cost, h_cost=0.0)
            path, edge_ids = _reconstruct_path(start, goal, parents)
            guarantee = (
                "Optimal for non-negative edge costs (UCS)."
                if algorithm == AlgorithmName.UCS
                else "Optimal for non-negative edge costs; A* uses admissible and consistent geographic weighted Haversine heuristic."
            )
            return SearchPath(
                path=path,
                edge_ids=edge_ids,
                trace=tuple(trace),
                explored_nodes=len(expanded),
                guarantee=guarantee,
            )

        for edge in graph.neighbors(node_id, scenario_id):
            breakdown = cost_engine.cost_for_edge(edge.edge_id, scenario_id)
            if breakdown.is_closed or breakdown.total_cost is None:
                continue
            candidate_cost = current_cost + breakdown.total_cost
            previous_cost = best_cost.get(edge.to_node_id)
            if previous_cost is not None and candidate_cost >= previous_cost:
                continue
            best_cost[edge.to_node_id] = candidate_cost
            parents[edge.to_node_id] = (node_id, edge.edge_id)

            next_h = compute_heuristic(graph, cost_engine, edge.to_node_id, goal, scenario_id) if is_astar else 0.0
            if is_astar:
                f_cost = candidate_cost + next_h
                heapq.heappush(frontier, (f_cost, candidate_cost, edge.to_node_id))
            else:
                heapq.heappush(frontier, (candidate_cost, edge.to_node_id))

            record(
                TraceEventKind.RELAX,
                edge.to_node_id,
                parent_id=node_id,
                g_cost=candidate_cost,
                h_cost=next_h,
                details={"edge_id": edge.edge_id, "edge_cost": breakdown.total_cost},
            )
        record(TraceEventKind.CLOSE, node_id, g_cost=current_cost, h_cost=current_h)

    record(TraceEventKind.FAIL, goal, details={"reason": "NO_ROUTE"})
    raise RouteNotFoundError(
        f"No route from {start} to {goal} in scenario {scenario_id}"
    )


def uniform_cost_search(
    graph: Graph,
    cost_engine: ScenarioCostEngine,
    start: str,
    goal: str,
    scenario_id: str,
) -> SearchPath:
    return _weighted_search(
        graph,
        cost_engine,
        start,
        goal,
        scenario_id,
        algorithm=AlgorithmName.UCS,
    )


def a_star_search(
    graph: Graph,
    cost_engine: ScenarioCostEngine,
    start: str,
    goal: str,
    scenario_id: str,
) -> SearchPath:
    return _weighted_search(
        graph,
        cost_engine,
        start,
        goal,
        scenario_id,
        algorithm=AlgorithmName.A_STAR,
    )


ALGORITHM_REGISTRY: dict[AlgorithmName, SearchImplementation] = {
    AlgorithmName.UCS: uniform_cost_search,
    AlgorithmName.A_STAR: a_star_search,
}


def resolve_algorithm(name: str) -> tuple[AlgorithmName, SearchImplementation]:
    normalized = name.strip().upper().replace("-", "_")
    aliases = {"A*": "A_STAR", "ASTAR": "A_STAR"}
    normalized = aliases.get(normalized, normalized)
    try:
        algorithm = AlgorithmName(normalized)
        return algorithm, ALGORITHM_REGISTRY[algorithm]
    except (ValueError, KeyError) as error:
        available = ", ".join(item.value for item in AlgorithmName)
        raise AlgorithmNotFoundError(
            f"Unknown algorithm: {name}. Available algorithms: {available}"
        ) from error


__all__ = [
    "ALGORITHM_REGISTRY",
    "a_star_search",
    "compute_heuristic",
    "haversine_distance_km",
    "resolve_algorithm",
    "uniform_cost_search",
]
