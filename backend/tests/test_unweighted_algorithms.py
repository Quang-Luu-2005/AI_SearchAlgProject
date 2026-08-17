import json
from pathlib import Path
from typing import Any

import pytest

from backend.app.algorithms.unweighted import breadth_first_search, depth_first_search
from backend.app.core.contracts import RouteNotFoundError
from backend.app.core.cost import ScenarioCostEngine
from backend.app.core.graph import GraphLoader

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TOY_GRAPH_DIR = REPOSITORY_ROOT / "data" / "fixtures" / "toy_graph_v0.1"
EXAMPLE_GRAPH_DIR = REPOSITORY_ROOT / "data" / "fixtures" / "graph_examples_v0.1"
TEST_CASES_PATH = TOY_GRAPH_DIR / "test_cases.json"


def load_two_point_cases() -> list[dict[str, Any]]:
    """Đọc file test_cases.json và chỉ lọc ra các bài toán tìm đường 2 điểm (two-point)."""
    with TEST_CASES_PATH.open(encoding="utf-8") as file:
        data = json.load(file)

    return [case for case in data["cases"] if case["mode"] == "two-point"]


@pytest.fixture(scope="module")
def toy_graph():
    return GraphLoader.from_directory(TOY_GRAPH_DIR)


@pytest.fixture(scope="module")
def cost_engine(toy_graph):
    return ScenarioCostEngine(toy_graph)


@pytest.mark.parametrize(
    "case",
    load_two_point_cases(),
    ids=lambda c: c["case_id"]
)
def test_bfs_dfs_against_golden_cases(toy_graph, cost_engine, case):
    """
    Tự động chạy BFS và DFS qua các kịch bản OFFPEAK, PEAK_TRAFFIC và HEAVY_RAIN_SAFE.
    """
    start_id = case["start"]
    goal_id = case["goal"]
    scenario_id = case["scenario_id"]

    bfs_result = breadth_first_search(toy_graph, cost_engine, start_id, goal_id, scenario_id)
    dfs_result = depth_first_search(toy_graph, cost_engine, start_id, goal_id, scenario_id)

    assert len(bfs_result.path) > 0, f"BFS failed to find path in {scenario_id}"
    assert len(dfs_result.path) > 0, f"DFS failed to find path in {scenario_id}"

    assert bfs_result.path[-1] == goal_id, "BFS did not reach goal"
    assert dfs_result.path[-1] == goal_id, "DFS did not reach goal"

    assert len(bfs_result.path) <= len(dfs_result.path), "BFS path has more hops than DFS"


@pytest.mark.parametrize("search", [breadth_first_search, depth_first_search])
def test_unweighted_search_handles_start_equal_goal(search):
    graph = GraphLoader.from_directory(EXAMPLE_GRAPH_DIR / "simple_path")
    result = search(graph, ScenarioCostEngine(graph), "SP_A", "SP_A", "DEFAULT")

    assert result.path == ("SP_A",)
    assert result.edge_ids == ()
    assert result.path[-1] == "SP_A"


@pytest.mark.parametrize("search", [breadth_first_search, depth_first_search])
def test_unweighted_search_handles_directed_cycle_without_revisiting_nodes(search):
    graph = GraphLoader.from_directory(EXAMPLE_GRAPH_DIR / "cycle_with_closure")
    result = search(graph, ScenarioCostEngine(graph), "CY_A", "CY_C", "OPEN_CYCLE")

    assert result.path == ("CY_A", "CY_B", "CY_C")
    assert result.explored_nodes <= len(graph.nodes)


@pytest.mark.parametrize("search", [breadth_first_search, depth_first_search])
def test_unweighted_search_reports_unreachable_directed_goal(search):
    graph = GraphLoader.from_directory(EXAMPLE_GRAPH_DIR / "simple_path")

    with pytest.raises(RouteNotFoundError, match="No route"):
        search(graph, ScenarioCostEngine(graph), "SP_C", "SP_A", "DEFAULT")
