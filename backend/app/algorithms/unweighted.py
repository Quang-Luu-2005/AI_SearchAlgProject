"""Deterministic unweighted search implementations (BFS, DFS)."""

from __future__ import annotations

from collections import deque

from ..core.contracts import (
    AlgorithmName,
    Graph,
    RouteNotFoundError,
    SearchPath,
    TraceEvent,
    TraceEventKind,
)
from ..core.cost import ScenarioCostEngine
from .weighted import _reconstruct_path

def _unweighted_search(
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

    frontier: deque[str] = deque([start])
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

    record(TraceEventKind.OPEN, start)
    
    while frontier:
        node_id = (
            frontier.popleft() 
            if algorithm == AlgorithmName.BFS 
            else frontier.pop()
        )

        if node_id in expanded:
            continue

        expanded.add(node_id)
        record(TraceEventKind.EXPAND, node_id)
        
        if node_id == goal:
            record(TraceEventKind.GOAL, node_id)
            path, edge_ids = _reconstruct_path(start, goal, parents)
            guarantee = (
                "Optimal for minimum hop count (BFS)."
                if algorithm == AlgorithmName.BFS
                else "No optimality guarantee; explores deeply before backtracking (DFS)."
            )
            return SearchPath(
                path=path,
                edge_ids=edge_ids,
                trace=tuple(trace),
                explored_nodes=len(expanded),
                guarantee=guarantee,
            )

        neighbors = sorted(graph.neighbors(node_id, scenario_id), key=lambda e: e.to_node_id)
        if algorithm == AlgorithmName.DFS:
            neighbors.reverse()

        for edge in neighbors:
            if edge.to_node_id in expanded:
                continue

            if algorithm == AlgorithmName.BFS:
                if edge.to_node_id not in parents:
                    parents[edge.to_node_id] = (node_id, edge.edge_id)
                    frontier.append(edge.to_node_id)
                    record(
                        TraceEventKind.OPEN,
                        edge.to_node_id,
                        parent_id=node_id,
                        details={"edge_id": edge.edge_id},
                    )
            else:
                parents[edge.to_node_id] = (node_id, edge.edge_id)
                frontier.append(edge.to_node_id)
                record(
                    TraceEventKind.OPEN,
                    edge.to_node_id,
                    parent_id=node_id,
                    details={"edge_id": edge.edge_id},
                )
                
        record(TraceEventKind.CLOSE, node_id)

    record(TraceEventKind.FAIL, goal, details={"reason": "NO_ROUTE"})
    raise RouteNotFoundError(
        f"No route from {start} to {goal} in scenario {scenario_id}"
    )

def breadth_first_search(
    graph: Graph,
    cost_engine: ScenarioCostEngine,
    start: str,
    goal: str,
    scenario_id: str,
) -> SearchPath:
    return _unweighted_search(
        graph,
        cost_engine,
        start,
        goal,
        scenario_id,
        algorithm=AlgorithmName.BFS,
    )

def depth_first_search(
    graph: Graph,
    cost_engine: ScenarioCostEngine,
    start: str,
    goal: str,
    scenario_id: str,
) -> SearchPath:
    return _unweighted_search(
        graph,
        cost_engine,
        start,
        goal,
        scenario_id,
        algorithm=AlgorithmName.DFS,
    )

__all__ = [
    "breadth_first_search",
    "depth_first_search",
]