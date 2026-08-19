"""Acceptance tests for the frozen cost profiles and route-change evidence."""

from pathlib import Path

import pytest

from backend.app.core.cost import DEFAULT_COST_PRESETS, ScenarioCostEngine
from backend.app.core.graph import GraphLoader
from backend.app.services.search import SearchService


ROOT = Path(__file__).resolve().parents[2]
TOY_GRAPH_DIR = ROOT / "data" / "fixtures" / "toy_graph_v0.1"

EXPECTED_WEIGHTS = {
    "BALANCED": {
        "distance": 0.25,
        "freeflow_time": 0.30,
        "congestion": 0.20,
        "flood_risk": 0.25,
    },
    "PEAK_TRAFFIC": {
        "distance": 0.15,
        "freeflow_time": 0.25,
        "congestion": 0.45,
        "flood_risk": 0.15,
    },
    "RAIN_SAFE": {
        "distance": 0.10,
        "freeflow_time": 0.25,
        "congestion": 0.15,
        "flood_risk": 0.50,
    },
}


def test_three_cost_profiles_are_frozen_to_expected_priority_coefficients() -> None:
    assert set(DEFAULT_COST_PRESETS) == set(EXPECTED_WEIGHTS)
    for preset_id, expected in EXPECTED_WEIGHTS.items():
        assert dict(DEFAULT_COST_PRESETS[preset_id].weights) == pytest.approx(expected)
        assert sum(expected.values()) == pytest.approx(1.0)


def test_road_closure_is_hard_constraint_not_a_small_weight() -> None:
    graph = GraphLoader.from_directory(TOY_GRAPH_DIR)
    engine = ScenarioCostEngine(graph)

    closed_route = engine.route_cost(["E01", "E03"], "HEAVY_RAIN_SAFE")
    rain_result = SearchService(graph).search(
        start="N01",
        goal="N06",
        algorithm="UCS",
        scenario_id="HEAVY_RAIN_SAFE",
    )

    assert closed_route.is_available is False
    assert closed_route.total_cost is None
    assert rain_result.edge_ids == ("E01", "E11", "E09")
    assert "E03" not in rain_result.edge_ids
    assert "E04" not in rain_result.edge_ids


def test_toy_fixture_records_profile_and_scenario_route_change() -> None:
    service = SearchService(GraphLoader.from_directory(TOY_GRAPH_DIR))
    baseline = service.search(
        start="N01", goal="N06", algorithm="UCS", scenario_id="OFFPEAK_BALANCED"
    )
    peak = service.search(
        start="N01", goal="N06", algorithm="UCS", scenario_id="PEAK_TRAFFIC"
    )
    rain = service.search(
        start="N01", goal="N06", algorithm="UCS", scenario_id="HEAVY_RAIN_SAFE"
    )

    assert baseline.edge_ids == ("E01", "E03")
    assert peak.edge_ids == baseline.edge_ids
    assert peak.result.metrics.total_cost > baseline.result.metrics.total_cost
    assert rain.edge_ids == ("E01", "E11", "E09")
    assert rain.edge_ids != baseline.edge_ids


LANDMARK_GRAPH_DIR = ROOT / "data" / "processed" / "thu_duc_landmarks_v1.0.0"


def test_second_simulated_route_change_stays_within_the_toy_fixture() -> None:
    service = SearchService(GraphLoader.from_directory(TOY_GRAPH_DIR))
    baseline = service.search(
        start="N05", goal="N01", algorithm="UCS", scenario_id="OFFPEAK_BALANCED"
    )
    comparison = service.search(
        start="N05", goal="N01", algorithm="UCS", scenario_id="HEAVY_RAIN_SAFE"
    )

    assert baseline.edge_ids == ("E14", "E04", "E02")
    assert comparison.edge_ids == ("E14", "E10", "E12", "E02")
    assert baseline.edge_ids != comparison.edge_ids


def test_landmark_pm_peak_route_detour_avoids_congested_arterial() -> None:
    service = SearchService(GraphLoader.from_directory(LANDMARK_GRAPH_DIR))
    baseline = service.search(
        start="LM_065", goal="LM_054", algorithm="A_STAR", scenario_id="LANDMARK_HISTORICAL_BASELINE"
    )
    peak = service.search(
        start="LM_065", goal="LM_054", algorithm="A_STAR", scenario_id="LANDMARK_PM_PEAK"
    )

    assert "LM_EDGE_0127" in baseline.edge_ids
    assert "LM_EDGE_0127" not in peak.edge_ids
    assert peak.edge_ids != baseline.edge_ids
    assert peak.result.metrics.total_cost > baseline.result.metrics.total_cost
    assert "LM_EDGE_0020" in peak.edge_ids
    assert "LM_EDGE_0078" in peak.edge_ids


def test_landmark_heavy_rain_road_closure_forces_safe_detour() -> None:
    service = SearchService(GraphLoader.from_directory(LANDMARK_GRAPH_DIR))
    baseline = service.search(
        start="LM_065", goal="LM_054", algorithm="A_STAR", scenario_id="LANDMARK_HISTORICAL_BASELINE"
    )
    rain = service.search(
        start="LM_065", goal="LM_054", algorithm="A_STAR", scenario_id="LANDMARK_HEAVY_RAIN"
    )

    closed_edges = {
        "LM_EDGE_0127", "LM_EDGE_0114", "LM_EDGE_0168", "LM_EDGE_0055",
    }
    assert baseline.edge_ids == (
        "LM_EDGE_0178", "LM_EDGE_0127", "LM_EDGE_0113", "LM_EDGE_0083", "LM_EDGE_0119"
    )
    assert "LM_EDGE_0127" in baseline.edge_ids
    assert not (set(rain.edge_ids) & closed_edges)
    assert rain.edge_ids != baseline.edge_ids
    assert "LM_EDGE_0020" in rain.edge_ids

    # Verify zero closed edges were ever relaxed or traversed in the search trace
    closed_relaxes = [ev for ev in rain.result.trace if ev.details and ev.details.get("edge_id") in closed_edges]
    assert len(closed_relaxes) == 0

    # Also verify Dao Son Tay -> SPKT detours around closed Linh Xuan corridor
    rain_spkt = service.search(
        start="LM_007", goal="LM_052", algorithm="A_STAR", scenario_id="LANDMARK_HEAVY_RAIN"
    )
    assert not (set(rain_spkt.edge_ids) & closed_edges)
    assert "LM_EDGE_0001" in rain_spkt.edge_ids

