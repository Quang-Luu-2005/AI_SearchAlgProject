from pathlib import Path

import pytest

from backend.app.core.graph import GraphLoader
from backend.app.services import SearchService


FIXTURE_DIR = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "toy_graph_v0.1"
LANDMARKS_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "thu_duc_landmarks_v1.0.0"


@pytest.fixture()
def service() -> SearchService:
    return SearchService(GraphLoader.from_directory(FIXTURE_DIR))


def test_ucs_and_zero_heuristic_a_star_return_same_optimal_route(
    service: SearchService,
) -> None:
    ucs = service.search(
        start="N01",
        goal="N06",
        algorithm="UCS",
        scenario_id="HEAVY_RAIN_SAFE",
    )
    a_star = service.search(
        start="N01",
        goal="N06",
        algorithm="A_STAR",
        scenario_id="HEAVY_RAIN_SAFE",
    )

    assert ucs.result.path == a_star.result.path == ("N01", "N02", "N04", "N06")
    assert ucs.result.metrics.total_cost == pytest.approx(a_star.result.metrics.total_cost)
    assert ucs.edge_ids == a_star.edge_ids == ("E01", "E11", "E09")


def test_search_trace_is_deterministic_and_graph_remains_immutable(
    service: SearchService,
) -> None:
    original_edges = service.graph.edges
    first = service.search(
        start="N01",
        goal="N06",
        algorithm="A_STAR",
        scenario_id="OFFPEAK_BALANCED",
    )
    second = service.search(
        start="N01",
        goal="N06",
        algorithm="A_STAR",
        scenario_id="OFFPEAK_BALANCED",
    )

    assert first.result.path == second.result.path
    assert first.result.trace == second.result.trace
    assert first.result.metrics.total_cost == second.result.metrics.total_cost
    assert service.graph.edges is original_edges


def test_start_equal_goal_returns_zero_metric_route(service: SearchService) -> None:
    execution = service.search(
        start="N01",
        goal="N01",
        algorithm="UCS",
        scenario_id="OFFPEAK_BALANCED",
    )

    assert execution.result.path == ("N01",)
    assert execution.edge_ids == ()
    assert execution.result.metrics.distance_m == 0
    assert execution.result.metrics.estimated_time_min == 0
    assert execution.result.metrics.total_cost == 0
    assert execution.result.trace[-1].kind.value == "GOAL"


def test_landmark_graph_ucs_and_astar_remain_optimal() -> None:
    service = SearchService(GraphLoader.from_directory(LANDMARKS_DIR))
    ucs = service.search(
        start="LM_001",
        goal="LM_065",
        algorithm="UCS",
        scenario_id="LANDMARK_HISTORICAL_BASELINE",
    )
    astar = service.search(
        start="LM_001",
        goal="LM_065",
        algorithm="A_STAR",
        scenario_id="LANDMARK_HISTORICAL_BASELINE",
    )

    assert astar.edge_ids == ucs.edge_ids
    assert astar.result.metrics.total_cost == pytest.approx(ucs.result.metrics.total_cost)
