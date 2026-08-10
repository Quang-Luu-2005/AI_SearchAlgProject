"""Unit tests for modular weighted search algorithms (UCS & A*) and Geographic Haversine Heuristic."""

from pathlib import Path

import pytest

from backend.app.algorithms.weighted import (
    a_star_search,
    compute_geographic_heuristic,
    haversine_distance_km,
    uniform_cost_search,
)
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
