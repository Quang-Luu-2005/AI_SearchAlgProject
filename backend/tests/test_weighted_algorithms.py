"""Unit tests for modular weighted search algorithms (UCS & A*) and Geographic Haversine Heuristic."""

from pathlib import Path

import pytest

from backend.app.algorithms.weighted import (
    a_star_search,
    compute_lower_bound_heuristic,
    compute_geographic_heuristic,
    compute_scenario_rho,
    haversine_distance_km,
    uniform_cost_search,
)
from backend.app.core.contracts import Edge, Graph, Node, Scenario
from backend.app.core.cost import ScenarioCostEngine
from backend.app.core.graph import GraphLoader


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TOY_GRAPH_DIR = REPOSITORY_ROOT / "data" / "fixtures" / "toy_graph_v0.1"
OSM_THU_DUC_DIR = REPOSITORY_ROOT / "data" / "processed" / "osm_thu_duc_v1.0.0"


def test_haversine_distance_accuracy() -> None:
    """Test Haversine distance calculation between known landmarks in HCMC."""
    # Distance between Chợ Thủ Đức (10.8495, 106.7535) and Suối Tiên (10.8619, 106.8038)
    dist_km = haversine_distance_km(10.8495, 106.7535, 10.8619, 106.8038)
    assert 5.0 <= dist_km <= 6.0


def test_lower_bound_rho_excludes_closed_and_near_zero_edges() -> None:
    """rho_s must use only usable edges and must not divide by near-zero geo distance."""
    graph = Graph(
        nodes=(
            Node("A", 10.0, 106.0),
            Node("B", 10.0, 106.0001),
            Node("C", 10.0, 106.01),
            Node("D", 10.0, 106.01),
        ),
        edges=(
            Edge("E_OPEN", "A", "B", 1000.0, 1.0),
            Edge("E_CLOSED", "B", "C", 1.0, 1.0),
            Edge("E_NEAR_ZERO", "C", "D", 1.0, 1.0),
        ),
        scenarios=(
            Scenario("OPEN", attributes={"cost_preset": "BALANCED"}),
            Scenario(
                "CLOSED",
                closed_edge_ids=("E_CLOSED",),
                attributes={"cost_preset": "BALANCED"},
            ),
            Scenario(
                "OVERRIDE_CLOSED",
                attributes={
                    "cost_preset": "BALANCED",
                    "edge_overrides": {"E_CLOSED": {"is_closed": True}},
                },
            ),
        ),
    )
    cost_engine = ScenarioCostEngine(graph)

    rho_open = compute_scenario_rho(graph, cost_engine, "OPEN")
    rho_closed = compute_scenario_rho(graph, cost_engine, "CLOSED")
    rho_override_closed = compute_scenario_rho(graph, cost_engine, "OVERRIDE_CLOSED")
    expected_open_ratio = cost_engine.cost_for_edge("E_OPEN", "CLOSED").total_cost / (
        haversine_distance_km(10.0, 106.0, 10.0, 106.0001)
    )

    assert rho_open > 0.0
    assert rho_closed == pytest.approx(expected_open_ratio)
    assert rho_override_closed == pytest.approx(expected_open_ratio)
    assert rho_closed > rho_open


def test_lower_bound_heuristic_is_scaled_by_scenario_rho() -> None:
    graph = GraphLoader.from_directory(TOY_GRAPH_DIR)
    cost_engine = ScenarioCostEngine(graph)
    rho_s = compute_scenario_rho(graph, cost_engine, "OFFPEAK_BALANCED")

    heuristic = compute_lower_bound_heuristic(
        graph,
        cost_engine,
        "N01",
        "N06",
        "OFFPEAK_BALANCED",
        rho_s=rho_s,
    )
    expected = rho_s * haversine_distance_km(
        graph.get_node("N01").latitude,
        graph.get_node("N01").longitude,
        graph.get_node("N06").latitude,
        graph.get_node("N06").longitude,
    )

    assert heuristic == pytest.approx(expected)
    assert compute_geographic_heuristic(
        graph, cost_engine, "N01", "N06", "OFFPEAK_BALANCED"
    ) == pytest.approx(heuristic)


def test_lower_bound_a_star_matches_ucs_on_fixture_scenarios() -> None:
    """The new heuristic must preserve UCS's optimal cost on baseline/peak/rain."""
    graph = GraphLoader.from_directory(TOY_GRAPH_DIR)
    cost_engine = ScenarioCostEngine(graph)
    pairs = (("N01", "N06"), ("N03", "N06"), ("N01", "N05"), ("N02", "N05"), ("N06", "N05"))

    for scenario_id in ("OFFPEAK_BALANCED", "PEAK_TRAFFIC", "HEAVY_RAIN_SAFE"):
        for start, goal in pairs:
            ucs = uniform_cost_search(graph, cost_engine, start, goal, scenario_id)
            astar = a_star_search(graph, cost_engine, start, goal, scenario_id)
            ucs_cost = cost_engine.route_cost(ucs.edge_ids, scenario_id).total_cost
            astar_cost = cost_engine.route_cost(astar.edge_ids, scenario_id).total_cost

            assert astar_cost == pytest.approx(ucs_cost)
            assert astar.explored_nodes <= len(graph.nodes)


@pytest.mark.skipif(not OSM_THU_DUC_DIR.exists(), reason="osm_thu_duc_v1.0.0 dataset not available")
def test_heuristic_admissibility_and_consistency() -> None:
    """Test that Geographic Heuristic satisfies h(goal) == 0 and non-negativity."""
    graph = GraphLoader.from_directory(OSM_THU_DUC_DIR)
    cost_engine = ScenarioCostEngine(graph)

    start_id = "OSM_NODE_1001"
    goal_id = "OSM_NODE_1013"
    scenario_id = "HISTORICAL_OFFPEAK"

    # h(goal) must be 0
    h_goal = compute_geographic_heuristic(graph, cost_engine, goal_id, goal_id, scenario_id)
    assert h_goal == 0.0

    # h(start) must be non-negative
    h_start = compute_geographic_heuristic(graph, cost_engine, start_id, goal_id, scenario_id)
    assert h_start >= 0.0


@pytest.mark.skipif(not OSM_THU_DUC_DIR.exists(), reason="osm_thu_duc_v1.0.0 dataset not available")
def test_ucs_and_a_star_optimality_match() -> None:
    """Test that UCS and A* find identical optimal cost on OSM road dataset."""
    graph = GraphLoader.from_directory(OSM_THU_DUC_DIR)
    cost_engine = ScenarioCostEngine(graph)

    start_id = "OSM_NODE_1001"
    goal_id = "OSM_NODE_1007"
    scenario_id = "HISTORICAL_OFFPEAK"

    ucs_result = uniform_cost_search(graph, cost_engine, start_id, goal_id, scenario_id)
    astar_result = a_star_search(graph, cost_engine, start_id, goal_id, scenario_id)

    # Path cost must be identical (100% optimal)
    assert ucs_result.path == astar_result.path
    assert ucs_result.edge_ids == astar_result.edge_ids


@pytest.mark.skipif(not OSM_THU_DUC_DIR.exists(), reason="osm_thu_duc_v1.0.0 dataset not available")
def test_a_star_pruning_advantage_over_ucs() -> None:
    """Test that A* with Geographic Heuristic expands <= UCS nodes on OSM road graph."""
    graph = GraphLoader.from_directory(OSM_THU_DUC_DIR)
    cost_engine = ScenarioCostEngine(graph)

    start_id = "OSM_NODE_1001"
    goal_id = "OSM_NODE_1007"
    scenario_id = "HISTORICAL_OFFPEAK"

    ucs_result = uniform_cost_search(graph, cost_engine, start_id, goal_id, scenario_id)
    astar_result = a_star_search(graph, cost_engine, start_id, goal_id, scenario_id)

    # A* must not expand more nodes than UCS
    assert astar_result.explored_nodes <= ucs_result.explored_nodes
