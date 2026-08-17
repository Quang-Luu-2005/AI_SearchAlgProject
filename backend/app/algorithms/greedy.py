"""Greedy Best-First Search Implementation."""

import heapq
from typing import Tuple

from ..core.contracts import (
    AlgorithmName,
    Graph,
    RouteNotFoundError,
    SearchPath,
    TraceEvent,
    TraceEventKind,
)
from ..core.cost import ScenarioCostEngine
from .weighted import _reconstruct_path, compute_geographic_heuristic


def greedy_best_first_search(
    graph: Graph,
    cost_engine: ScenarioCostEngine,
    start: str,
    goal: str,
    scenario_id: str,
) -> SearchPath:
    graph.get_node(start)
    graph.get_node(goal)
    graph.scenario(scenario_id)

    start_h = compute_geographic_heuristic(graph, cost_engine, start, goal, scenario_id)
    frontier: list[tuple[float, str]] = [(start_h, start)]
    
    parents: dict[str, tuple[str, str]] = {}
    expanded: set[str] = set()
    visited_h: dict[str, float] = {start: start_h}
    
    trace: list[TraceEvent] = []
    step = 0

    def record(
        kind: TraceEventKind,
        node_id: str,
        parent_id: str | None = None,
        h_cost: float | None = None,
        details: dict[str, object] | None = None
    ) -> None:
        nonlocal step
        trace.append(
            TraceEvent(
                step=step, kind=kind, node_id=node_id, parent_id=parent_id, h_cost=h_cost, details=dict(details or {})
            )
        )
        step += 1

    record(TraceEventKind.OPEN, start, h_cost=start_h)

    while frontier:
        current_h, node_id = heapq.heappop(frontier)

        if node_id in expanded:
            continue

        expanded.add(node_id)
        record(TraceEventKind.EXPAND, node_id, h_cost=current_h)

        if node_id == goal:
            record(TraceEventKind.GOAL, node_id, h_cost=0.0)
            path, edge_ids = _reconstruct_path(start, goal, parents)
            return SearchPath(
                path=path,
                edge_ids=edge_ids,
                trace=tuple(trace),
                explored_nodes=len(expanded),
                guarantee="No optimality guarantee; relies purely on heuristic (Greedy Best-First Search).",
            )

        for edge in graph.neighbors(node_id, scenario_id):
            neighbor = edge.to_node_id
            if neighbor in expanded:
                continue

            breakdown = cost_engine.cost_for_edge(edge.edge_id, scenario_id)
            if breakdown.is_closed or breakdown.total_cost is None:
                continue

            h_val = compute_geographic_heuristic(graph, cost_engine, neighbor, goal, scenario_id)

            if neighbor not in visited_h:
                visited_h[neighbor] = h_val
                parents[neighbor] = (node_id, edge.edge_id)
                heapq.heappush(frontier, (h_val, neighbor))
                record(TraceEventKind.OPEN, neighbor, parent_id=node_id, h_cost=h_val)

        record(TraceEventKind.CLOSE, node_id, h_cost=current_h)

    record(TraceEventKind.FAIL, goal, details={"reason": "NO_ROUTE"})
    raise RouteNotFoundError(f"No route from {start} to {goal} in scenario {scenario_id}")