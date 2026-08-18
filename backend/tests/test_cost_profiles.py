"""Acceptance tests for the frozen cost profiles and route-change evidence."""

import json
from pathlib import Path

import pytest

from backend.app.core.cost import DEFAULT_COST_PRESETS, ScenarioCostEngine
from backend.app.core.graph import GraphLoader
from backend.app.services.search import SearchService


ROOT = Path(__file__).resolve().parents[2]
TOY_GRAPH_DIR = ROOT / "data" / "fixtures" / "toy_graph_v0.1"
MARKET_GRAPH_DIR = ROOT / "data" / "processed" / "thu_duc_market_v1.0.0"

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


def test_processed_market_golden_case_records_second_route_change() -> None:
    graph = GraphLoader.from_directory(MARKET_GRAPH_DIR)
    case = json.loads((MARKET_GRAPH_DIR / "test_cases.json").read_text(encoding="utf-8"))["cases"][0]
    service = SearchService(graph)

    baseline = service.search(
        start=case["start"],
        goal=case["goal"],
        algorithm="UCS",
        scenario_id=case["baseline_scenario_id"],
    )
    comparison = service.search(
        start=case["start"],
        goal=case["goal"],
        algorithm="UCS",
        scenario_id=case["comparison_scenario_id"],
    )

    assert baseline.edge_ids == tuple(case["expected_baseline_edge_ids"])
    assert comparison.edge_ids == tuple(case["expected_comparison_edge_ids"])
    assert baseline.edge_ids != comparison.edge_ids
    assert case["data_status"] == "MIXED"
