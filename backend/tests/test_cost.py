from pathlib import Path

import pytest

from backend.app.core.contracts import CostModelError, CostPreset, Graph, Scenario
from backend.app.core.cost import DEFAULT_COST_PRESETS, ScenarioCostEngine
from backend.app.core.graph import GraphLoader


FIXTURE_DIR = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "toy_graph_v0.1"


@pytest.fixture()
def engine() -> ScenarioCostEngine:
    return ScenarioCostEngine(GraphLoader.from_directory(FIXTURE_DIR))


def test_all_cost_presets_are_non_negative_and_sum_to_one() -> None:
    assert set(DEFAULT_COST_PRESETS) == {"BALANCED", "PEAK_TRAFFIC", "RAIN_SAFE"}
    for preset in DEFAULT_COST_PRESETS.values():
        assert sum(preset.weights.values()) == pytest.approx(1.0)
        assert all(weight >= 0 for weight in preset.weights.values())


@pytest.mark.parametrize(
    ("scenario_id", "preset_id"),
    [
        ("OFFPEAK_BALANCED", "BALANCED"),
        ("PEAK_TRAFFIC", "PEAK_TRAFFIC"),
        ("HEAVY_RAIN_SAFE", "RAIN_SAFE"),
    ],
)
def test_each_scenario_resolves_simulated_cost_preset(
    engine: ScenarioCostEngine,
    scenario_id: str,
    preset_id: str,
) -> None:
    breakdown = engine.cost_for_edge("E01", scenario_id)

    assert breakdown.cost_preset == preset_id
    assert breakdown.data_status == "SIMULATED"
    assert breakdown.distance_km == pytest.approx(1.1)
    assert breakdown.total_cost is not None


def test_offpeak_separates_free_flow_time_from_congestion(engine: ScenarioCostEngine) -> None:
    breakdown = engine.cost_for_edge("E01", "OFFPEAK_BALANCED")

    assert breakdown.free_flow_time_min == pytest.approx(2.2)
    assert breakdown.travel_time_min == pytest.approx(2.2)
    assert breakdown.traffic_penalty == pytest.approx(0.0)
    assert breakdown.flood_risk == pytest.approx(0.0)
    assert breakdown.total_cost == pytest.approx(0.935)
    assert set(breakdown.to_dict()) >= {
        "distance_km",
        "travel_time_min",
        "traffic_penalty",
        "flood_risk",
        "total_cost",
        "weighted_components",
    }


def test_peak_traffic_increases_estimated_time_and_penalty(engine: ScenarioCostEngine) -> None:
    offpeak = engine.cost_for_edge("E01", "OFFPEAK_BALANCED")
    peak = engine.cost_for_edge("E01", "PEAK_TRAFFIC")

    assert peak.congestion_level_1_5 == pytest.approx(4)
    assert peak.travel_time_min > offpeak.travel_time_min
    assert peak.traffic_penalty > offpeak.traffic_penalty
    assert peak.total_cost > offpeak.total_cost


def test_peak_edge_override_changes_congestion_and_flood_risk(engine: ScenarioCostEngine) -> None:
    breakdown = engine.cost_for_edge("E03", "PEAK_TRAFFIC")

    assert breakdown.congestion_level_1_5 == pytest.approx(4)
    assert breakdown.flood_risk == pytest.approx(0.2)
    assert breakdown.is_closed is False


def test_heavy_rain_closes_flooded_edge_and_keeps_breakdown(engine: ScenarioCostEngine) -> None:
    breakdown = engine.cost_for_edge("E03", "HEAVY_RAIN_SAFE")

    assert breakdown.is_closed is True
    assert breakdown.flood_risk == pytest.approx(1.0)
    assert breakdown.total_cost is None


def test_route_total_is_sum_of_edge_costs(engine: ScenarioCostEngine) -> None:
    first = engine.cost_for_edge("E01", "OFFPEAK_BALANCED")
    second = engine.cost_for_edge("E05", "OFFPEAK_BALANCED")
    route = engine.route_cost(["E01", "E05"], "OFFPEAK_BALANCED")

    assert route.is_available is True
    assert route.total_cost == pytest.approx(first.total_cost + second.total_cost)
    assert len(route.edge_costs) == 2
    assert route.data_status == "SIMULATED"


def test_closed_edge_makes_route_unavailable(engine: ScenarioCostEngine) -> None:
    route = engine.route_cost(["E03", "E05"], "HEAVY_RAIN_SAFE")

    assert route.is_available is False
    assert route.total_cost is None


def test_negative_cost_inputs_are_rejected(engine: ScenarioCostEngine) -> None:
    with pytest.raises(CostModelError, match="negative weights"):
        CostPreset(
            preset_id="BROKEN",
            weights={
                "distance": -0.1,
                "freeflow_time": 0.4,
                "congestion": 0.4,
                "flood_risk": 0.3,
            },
        )

    graph = Graph(
        nodes=engine.graph.nodes,
        edges=engine.graph.edges,
        scenarios=(
            Scenario(
                scenario_id="NEGATIVE_OVERRIDE",
                attributes={
                    "data_status": "SIMULATED",
                    "cost_preset": "BALANCED",
                    "weights": dict(DEFAULT_COST_PRESETS["BALANCED"].weights),
                    "edge_overrides": {"E01": {"traffic_penalty_min": -1}},
                },
            ),
        ),
    )
    negative_engine = ScenarioCostEngine(graph)
    with pytest.raises(CostModelError, match="cannot be negative"):
        negative_engine.cost_for_edge("E01", "NEGATIVE_OVERRIDE")


def test_unknown_preset_is_rejected(engine: ScenarioCostEngine) -> None:
    graph = Graph(
        nodes=engine.graph.nodes,
        edges=engine.graph.edges,
        scenarios=(
            Scenario(
                scenario_id="UNKNOWN_PRESET",
                attributes={
                    "data_status": "SIMULATED",
                    "cost_preset": "MISSING",
                },
            ),
        ),
    )
    with pytest.raises(CostModelError, match="Unknown cost preset"):
        ScenarioCostEngine(graph).cost_for_edge("E01", "UNKNOWN_PRESET")
