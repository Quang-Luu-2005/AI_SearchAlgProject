"""Deterministic non-negative weighted search implementations."""

from __future__ import annotations

import heapq
from collections.abc import Callable

from ..core.contracts import (
    AlgorithmName,
    AlgorithmNotFoundError,
    Graph,
    RouteNotFoundError,
    SearchPath,
    TraceEvent,
    TraceEventKind,
)
from ..core.cost import ScenarioCostEngine


SearchImplementation = Callable[
    [Graph, ScenarioCostEngine, str, str, str],
    SearchPath,
]


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

    frontier: list[tuple[float, float, str]] = [(0.0, 0.0, start)]
    best_cost = {start: 0.0}
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

    record(TraceEventKind.OPEN, start, g_cost=0.0, h_cost=0.0)
    while frontier:
        _, current_cost, node_id = heapq.heappop(frontier)
        if current_cost != best_cost.get(node_id) or node_id in expanded:
            continue

        expanded.add(node_id)
        record(TraceEventKind.EXPAND, node_id, g_cost=current_cost, h_cost=0.0)
        if node_id == goal:
            record(TraceEventKind.GOAL, node_id, g_cost=current_cost, h_cost=0.0)
            path, edge_ids = _reconstruct_path(start, goal, parents)
            guarantee = (
                "Optimal for non-negative edge costs (UCS)."
                if algorithm == AlgorithmName.UCS
                else "Optimal for non-negative edge costs; A* uses admissible h=0."
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
            heapq.heappush(frontier, (candidate_cost, candidate_cost, edge.to_node_id))
            record(
                TraceEventKind.RELAX,
                edge.to_node_id,
                parent_id=node_id,
                g_cost=candidate_cost,
                h_cost=0.0,
                details={"edge_id": edge.edge_id, "edge_cost": breakdown.total_cost},
            )
        record(TraceEventKind.CLOSE, node_id, g_cost=current_cost, h_cost=0.0)

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
    "resolve_algorithm",
    "uniform_cost_search",
]
