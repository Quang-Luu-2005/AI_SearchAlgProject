"""Deterministic non-negative weighted search algorithms (UCS & A*).

This module implements two foundational search algorithms for road routing:
1. Uniform Cost Search (UCS): f(n) = g(n)
2. A* Search: f(n) = g(n) + h(n) using a scenario-aware cost lower-bound heuristic.

Theoretical Guarantees:
- Admissibility: 0 <= h(n) <= h*(n) for all nodes n.
- Consistency (Monotonicity): h(n) <= c(n, n') + h(n') for all edges (n, n').
- Optimality: Guaranteed optimal route when edge costs c(e) >= 0.
- Completeness: Guaranteed to find a solution on finite graphs if a path exists.
"""

from __future__ import annotations

import heapq
import math
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

HeuristicFunction = Callable[[Graph, ScenarioCostEngine, str, str, str], float]
SearchImplementation = Callable[
    [Graph, ScenarioCostEngine, str, str, str],
    SearchPath,
]

# Geographic distances below one millimetre are not useful denominators for a
# cost-per-distance ratio.  Such edges are still valid for routing; they are
# only excluded from rho_s estimation.
MIN_GEO_DISTANCE_KM = 1e-6


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two WGS84 coordinates in kilometers.

    Formula:
        a = sin^2(dLat/2) + cos(lat1) * cos(lat2) * sin^2(dLon/2)
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        d = R * c  (where Earth's mean radius R = 6371.0 km)
    """
    r = 6371.0  # Earth's radius in kilometers
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


def compute_scenario_rho(
    graph: Graph,
    cost_engine: ScenarioCostEngine,
    scenario_id: str,
    *,
    min_geographic_distance_km: float = MIN_GEO_DISTANCE_KM,
) -> float:
    """Return ``rho_s = min(Cost_s(e) / d_geo(e))`` for open edges.

    The graph and scenario are treated as immutable inputs.  Edges closed by
    the scenario view or by an edge override are excluded.  Edges without two
    finite coordinates, with a near-zero Haversine denominator, or with a
    non-finite cost are skipped.  If no usable edge remains, ``0.0`` is the
    safe fallback, making A* equivalent to UCS for that snapshot.
    """
    if min_geographic_distance_km < 0:
        raise ValueError("min_geographic_distance_km must be non-negative")

    graph.scenario(scenario_id)
    ratios: list[float] = []

    for edge in graph.list_edges(scenario_id):
        # list_edges already excludes scenario.closed_edge_ids.  The cost
        # engine additionally handles an override such as {"is_closed": true}.
        try:
            breakdown = cost_engine.cost_for_edge_value(edge, scenario_id)
        except CostModelError:
            # A malformed cost declaration is not a usable rho sample.  The
            # weighted search still validates cost when it actually traverses
            # an edge, preserving the API's normal invalid-cost error path.
            continue
        if breakdown.is_closed or breakdown.total_cost is None:
            continue

        source = graph.get_node(edge.from_node_id)
        target = graph.get_node(edge.to_node_id)
        coordinates = (source.latitude, source.longitude, target.latitude, target.longitude)
        if any(value is None or not math.isfinite(value) for value in coordinates):
            continue

        geographic_distance_km = haversine_distance_km(*coordinates)  # type: ignore[arg-type]
        if (
            not math.isfinite(geographic_distance_km)
            or geographic_distance_km <= min_geographic_distance_km
        ):
            continue

        cost = breakdown.total_cost
        if cost is None or not math.isfinite(cost):
            continue
        ratios.append(cost / geographic_distance_km)

    return min(ratios) if ratios else 0.0


def compute_lower_bound_heuristic(
    graph: Graph,
    cost_engine: ScenarioCostEngine,
    node_id: str,
    goal_id: str,
    scenario_id: str,
    *,
    rho_s: float | None = None,
) -> float:
    """Compute ``h_s(n) = rho_s * Haversine(n, goal)``.

    ``rho_s`` may be supplied by a caller that already computed the frozen
    scenario scale, as A* does once per search.  Omitting it keeps this public
    helper convenient for tests and other informed-search consumers.
    """
    if node_id == goal_id:
        return 0.0

    node = graph.get_node(node_id)
    goal_node = graph.get_node(goal_id)
    coordinates = (node.latitude, node.longitude, goal_node.latitude, goal_node.longitude)
    if any(value is None or not math.isfinite(value) for value in coordinates):
        return 0.0

    scale = compute_scenario_rho(graph, cost_engine, scenario_id) if rho_s is None else rho_s
    if scale < 0 or not math.isfinite(scale):
        raise ValueError("rho_s must be a finite non-negative number")
    return scale * haversine_distance_km(*coordinates)  # type: ignore[arg-type]


def compute_geographic_heuristic(
    graph: Graph,
    cost_engine: ScenarioCostEngine,
    node_id: str,
    goal_id: str,
    scenario_id: str,
) -> float:
    """Backward-compatible name for the scenario-aware lower-bound heuristic."""
    return compute_lower_bound_heuristic(
        graph, cost_engine, node_id, goal_id, scenario_id
    )


def _reconstruct_path(
    start: str,
    goal: str,
    parents: dict[str, tuple[str, str]],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Reconstruct the sequence of nodes and edge IDs from start to goal."""
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
    heuristic_fn: HeuristicFunction | None = None,
) -> SearchPath:
    """Core Priority Queue Search Engine for UCS and A*.

    Pseudocode:
        1. Initialize frontier = MinPriorityQueue([(h(start), 0.0, start)])
        2. Initialize best_cost = {start: 0.0}, expanded = set(), parents = {}
        3. Record TraceEvent(OPEN, start)
        4. While frontier is not empty:
            a. Pop (f_cost, g_cost, u) with minimum f_cost
            b. If u is in expanded or g_cost > best_cost[u]: continue
            c. Mark u as expanded, record TraceEvent(EXPAND, u)
            d. If u == goal: return reconstructed SearchPath
            e. For each neighbor v via edge e:
                i. Calculate edge cost c(e) via cost_engine
                ii. If e is closed or c(e) is invalid: continue
                iii. candidate_g = g_cost + c(e)
                iv. If candidate_g < best_cost[v]:
                    - Update best_cost[v] = candidate_g
                    - Update parents[v] = (u, e.id)
                    - f_val = candidate_g + h(v)
                    - Push (f_val, candidate_g, v) to frontier
                    - Record TraceEvent(RELAX, v)
            f. Record TraceEvent(CLOSE, u)
        5. If frontier becomes empty: Raise RouteNotFoundError
    """
    graph.get_node(start)
    graph.get_node(goal)
    graph.scenario(scenario_id)

    start_h = heuristic_fn(graph, cost_engine, start, goal, scenario_id) if heuristic_fn else 0.0

    # Heap tuple: (f_cost, g_cost, node_id) for deterministic tie-breaking
    frontier: list[tuple[float, float, str]] = [(start_h, 0.0, start)]
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
        _, current_g, node_id = heapq.heappop(frontier)

        if current_g != best_cost.get(node_id) or node_id in expanded:
            continue

        expanded.add(node_id)
        current_h = heuristic_fn(graph, cost_engine, node_id, goal, scenario_id) if heuristic_fn else 0.0
        record(TraceEventKind.EXPAND, node_id, g_cost=current_g, h_cost=current_h)

        if node_id == goal:
            record(TraceEventKind.GOAL, node_id, g_cost=current_g, h_cost=0.0)
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

            candidate_g = current_g + breakdown.total_cost
            previous_g = best_cost.get(edge.to_node_id)

            if previous_g is not None and candidate_g >= previous_g:
                continue

            best_cost[edge.to_node_id] = candidate_g
            parents[edge.to_node_id] = (node_id, edge.edge_id)

            next_h = heuristic_fn(graph, cost_engine, edge.to_node_id, goal, scenario_id) if heuristic_fn else 0.0
            f_cost = candidate_g + next_h

            heapq.heappush(frontier, (f_cost, candidate_g, edge.to_node_id))
            record(
                TraceEventKind.RELAX,
                edge.to_node_id,
                parent_id=node_id,
                g_cost=candidate_g,
                h_cost=next_h,
                details={"edge_id": edge.edge_id, "edge_cost": breakdown.total_cost},
            )

        record(TraceEventKind.CLOSE, node_id, g_cost=current_g, h_cost=current_h)

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
    """Uniform Cost Search (UCS): Special case of A* with heuristic h(n) = 0.

    Evaluation function: f(n) = g(n)
    Optimality: Optimal for non-negative edge costs c(e) >= 0.
    Completeness: Complete on finite graphs if edge costs c(e) >= epsilon > 0.
    """
    return _weighted_search(
        graph,
        cost_engine,
        start,
        goal,
        scenario_id,
        algorithm=AlgorithmName.UCS,
        heuristic_fn=None,
    )


def a_star_search(
    graph: Graph,
    cost_engine: ScenarioCostEngine,
    start: str,
    goal: str,
    scenario_id: str,
) -> SearchPath:
    """A* Search using one frozen scenario-aware lower-bound scale.

    Evaluation function: f(n) = g(n) + h(n)
    Heuristic: h_s(n) = rho_s * Haversine_km(n, goal)
    Optimality: guaranteed when the scenario is static and edge costs are non-negative.
    Completeness: Complete on finite graphs if edge costs c(e) >= epsilon > 0.
    Pruning Advantage: Significantly reduces expanded nodes compared to UCS.
    """
    rho_s = compute_scenario_rho(graph, cost_engine, scenario_id)

    def lower_bound(
        active_graph: Graph,
        active_cost_engine: ScenarioCostEngine,
        node_id: str,
        goal_id: str,
        active_scenario_id: str,
    ) -> float:
        return compute_lower_bound_heuristic(
            active_graph,
            active_cost_engine,
            node_id,
            goal_id,
            active_scenario_id,
            rho_s=rho_s,
        )

    return _weighted_search(
        graph,
        cost_engine,
        start,
        goal,
        scenario_id,
        algorithm=AlgorithmName.A_STAR,
        heuristic_fn=lower_bound,
    )


ALGORITHM_REGISTRY: dict[AlgorithmName, SearchImplementation] = {
    AlgorithmName.UCS: uniform_cost_search,
    AlgorithmName.A_STAR: a_star_search,
}


def resolve_algorithm(name: str) -> tuple[AlgorithmName, SearchImplementation]:
    """Resolve an algorithm string name to its enum and execution callable."""
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
    "compute_lower_bound_heuristic",
    "compute_geographic_heuristic",
    "compute_scenario_rho",
    "haversine_distance_km",
    "resolve_algorithm",
    "uniform_cost_search",
]
