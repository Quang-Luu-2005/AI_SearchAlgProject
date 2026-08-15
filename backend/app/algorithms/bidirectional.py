"""Bidirectional Breadth-First Search Implementation."""

from collections import deque

from ..core.contracts import (
    Graph,
    RouteNotFoundError,
    SearchPath,
    TraceEvent,
    TraceEventKind,
)
from ..core.cost import ScenarioCostEngine


def bidirectional_search(
    graph: Graph,
    cost_engine: ScenarioCostEngine,
    start: str,
    goal: str,
    scenario_id: str,
) -> SearchPath:
    graph.get_node(start)
    graph.get_node(goal)
    graph.scenario(scenario_id)

    if start == goal:
        return SearchPath(
            path=(start,),
            edge_ids=(),
            trace=(TraceEvent(step=0, kind=TraceEventKind.GOAL, node_id=start),),
            explored_nodes=0,
            guarantee="Optimal for minimum hop count (Bidirectional BFS). Start matches goal.",
        )

    rev_adj: dict[str, list[tuple[str, str]]] = {n.node_id: [] for n in graph.nodes}
    for edge in graph.list_edges(scenario_id):
        rev_adj[edge.to_node_id].append((edge.from_node_id, edge.edge_id))

    for n_id in rev_adj:
        rev_adj[n_id].sort(key=lambda x: x[0])

    q_fwd: deque[str] = deque([start])
    q_bwd: deque[str] = deque([goal])
    
    visited_fwd: set[str] = {start}
    visited_bwd: set[str] = {goal}
    
    parent_fwd: dict[str, tuple[str, str]] = {}
    parent_bwd: dict[str, tuple[str, str]] = {}
    
    trace: list[TraceEvent] = []
    step = 0
    expanded_count = 0

    def record(kind: TraceEventKind, node_id: str, dir_name: str) -> None:
        nonlocal step
        trace.append(TraceEvent(step=step, kind=kind, node_id=node_id, details={"direction": dir_name}))
        step += 1

    record(TraceEventKind.OPEN, start, "forward")
    record(TraceEventKind.OPEN, goal, "backward")

    intersect_node = None

    while q_fwd and q_bwd:
        curr_fwd = q_fwd.popleft()
        expanded_count += 1
        record(TraceEventKind.EXPAND, curr_fwd, "forward")

        neighbors_fwd = sorted(graph.neighbors(curr_fwd, scenario_id), key=lambda e: e.to_node_id)
        for edge in neighbors_fwd:
            nxt = edge.to_node_id
        
        for edge in graph.neighbors(curr_fwd, scenario_id):
            nxt = edge.to_node_id
            if nxt not in visited_fwd:
                visited_fwd.add(nxt)
                parent_fwd[nxt] = (curr_fwd, edge.edge_id)
                q_fwd.append(nxt)
                if nxt in visited_bwd:
                    intersect_node = nxt
                    break
        if intersect_node:
            break

        curr_bwd = q_bwd.popleft()
        expanded_count += 1
        record(TraceEventKind.EXPAND, curr_bwd, "backward")
        
        for prev, edge_id in rev_adj[curr_bwd]:
            if prev not in visited_bwd:
                visited_bwd.add(prev)
                parent_bwd[prev] = (curr_bwd, edge_id)
                q_bwd.append(prev)
                if prev in visited_fwd:
                    intersect_node = prev
                    break
        if intersect_node:
            break

    if intersect_node:
        path_fwd, edges_fwd = [], []
        curr = intersect_node
        while curr != start:
            p, e_id = parent_fwd[curr]
            path_fwd.append(curr)
            edges_fwd.append(e_id)
            curr = p
        path_fwd.append(start)
        path_fwd.reverse()
        edges_fwd.reverse()

        path_bwd, edges_bwd = [], []
        curr = intersect_node
        while curr != goal:
            c, e_id = parent_bwd[curr]
            path_bwd.append(c)
            edges_bwd.append(e_id)
            curr = c
        path_bwd.append(goal)

        final_path = tuple(path_fwd[:-1] + path_bwd)
        final_edges = tuple(edges_fwd + edges_bwd)

        record(TraceEventKind.GOAL, intersect_node, "intersection_found")
        return SearchPath(
            path=final_path,
            edge_ids=final_edges,
            trace=tuple(trace),
            explored_nodes=expanded_count,
            guarantee="Optimal for minimum hop count (Bidirectional BFS).",
        )

    record(TraceEventKind.FAIL, goal, "NO_ROUTE")
    raise RouteNotFoundError(f"No route from {start} to {goal} in scenario {scenario_id}")