from pathlib import Path

import pytest

from backend.app.algorithms.weighted import (
    a_star_search,
    compute_heuristic,
    haversine_distance_km,
    resolve_algorithm,
    uniform_cost_search,
)
from backend.app.core.contracts import AlgorithmName, AlgorithmNotFoundError, RouteNotFoundError
from backend.app.core.cost import ScenarioCostEngine
from backend.app.core.graph import GraphLoader


FIXTURE_DIR = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "toy_graph_v0.1"
PROCESSED_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "thu_duc_market_v1.0.0"


def test_haversine_distance_calculation() -> None:
    # Distance between Ben Thanh Market and Thu Duc Market (~12 km)
    ben_thanh_lat, ben_thanh_lon = 10.7721, 106.6983
    thu_duc_lat, thu_duc_lon = 10.8495, 106.7537
    dist = haversine_distance_km(ben_thanh_lat, ben_thanh_lon, thu_duc_lat, thu_duc_lon)
    assert 10.0 <= dist <= 15.0


def test_heuristic_computation() -> None:
    graph = GraphLoader.from_directory(PROCESSED_DIR)
    cost_engine = ScenarioCostEngine(graph)
    start_node_id = "UTR_NODE_2947068442"
    goal_node_id = "UTR_NODE_366385739"
    scenario_id = "RAIN_FLOOD_AWARE_2025_2026"

    h_value = compute_heuristic(graph, cost_engine, start_node_id, goal_node_id, scenario_id)
    assert h_value > 0.0

    # Self-heuristic should be 0
    h_self = compute_heuristic(graph, cost_engine, start_node_id, start_node_id, scenario_id)
    assert h_self == 0.0


def test_heuristic_fallback_when_coordinates_missing() -> None:
    from backend.app.core.contracts import Edge, Graph, Node, Scenario
    node_a = Node("A", latitude=None, longitude=None)
    node_b = Node("B", latitude=None, longitude=None)
    edge = Edge("E1", "A", "B", distance_m=1000.0, free_flow_time_min=2.0)
    scenario = Scenario("S1", attributes={"cost_preset": "BALANCED"})
    graph = Graph([node_a, node_b], [edge], [scenario])
    cost_engine = ScenarioCostEngine(graph)

    h_value = compute_heuristic(graph, cost_engine, "A", "B", "S1")
    assert h_value == 0.0


def test_astar_expands_fewer_or_equal_nodes_than_ucs_on_thu_duc() -> None:
    graph = GraphLoader.from_directory(PROCESSED_DIR)
    cost_engine = ScenarioCostEngine(graph)
    start = "UTR_NODE_2947068442"
    goal = "UTR_NODE_366385739"
    scenario = "HISTORICAL_OFFPEAK"

    ucs_result = uniform_cost_search(graph, cost_engine, start, goal, scenario)
    astar_result = a_star_search(graph, cost_engine, start, goal, scenario)

    assert ucs_result.path == astar_result.path
    assert astar_result.explored_nodes <= ucs_result.explored_nodes
    # Check that A* trace contains non-zero h_cost entries
    h_costs = [event.h_cost for event in astar_result.trace if event.h_cost is not None]
    assert any(h > 0.0 for h in h_costs)


def test_resolve_algorithm() -> None:
    algo_name, fn = resolve_algorithm("ucs")
    assert algo_name == AlgorithmName.UCS
    assert fn == uniform_cost_search

    algo_name, fn = resolve_algorithm("a*")
    assert algo_name == AlgorithmName.A_STAR
    assert fn == a_star_search

    with pytest.raises(AlgorithmNotFoundError):
        resolve_algorithm("INVALID_ALGO")
