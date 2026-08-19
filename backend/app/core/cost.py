"""Scenario-aware edge and route cost engine.

The engine is framework-independent and reads immutable graph/scenario contracts.
It never mutates an edge or graph view while applying scenario overrides.

The three default preset weights are empirical priority coefficients for the
simulated prototype. They are not percentage contributions because distance,
time, traffic penalty and flood risk use different units and scales.
"""

from __future__ import annotations

import math
from types import MappingProxyType
from typing import Any, Mapping

from .contracts import (
    CostModelError,
    CostPreset,
    Edge,
    EdgeCostBreakdown,
    Graph,
    RouteCostBreakdown,
)


DEFAULT_COST_PRESETS: Mapping[str, CostPreset] = MappingProxyType(
    {
        "BALANCED": CostPreset(
            preset_id="BALANCED",
            weights={
                "distance": 0.25,
                "freeflow_time": 0.30,
                "congestion": 0.20,
                "flood_risk": 0.25,
            },
            description="Balanced distance, time, traffic and flood-risk trade-off.",
        ),
        "PEAK_TRAFFIC": CostPreset(
            preset_id="PEAK_TRAFFIC",
            weights={
                "distance": 0.15,
                "freeflow_time": 0.25,
                "congestion": 0.45,
                "flood_risk": 0.15,
            },
            description="Prioritizes avoiding congestion during peak traffic.",
        ),
        "RAIN_SAFE": CostPreset(
            preset_id="RAIN_SAFE",
            weights={
                "distance": 0.10,
                "freeflow_time": 0.25,
                "congestion": 0.15,
                "flood_risk": 0.50,
            },
            description="Prioritizes avoiding flood risk during heavy rain.",
        ),
    }
)


def _number(value: Any, field_name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as error:
        raise CostModelError(f"Cost field {field_name} must be numeric") from error
    if not math.isfinite(number):
        raise CostModelError(f"Cost field {field_name} must be finite")
    return number


class ScenarioCostEngine:
    """Calculate deterministic cost breakdowns from a graph and scenario."""

    DEFAULT_CONGESTION_LEVEL = 1.0
    DEFAULT_TRAFFIC_MULTIPLIER = 1.0
    CONGESTION_MULTIPLIER_STEP = 0.15

    def __init__(
        self,
        graph: Graph,
        presets: Mapping[str, CostPreset] = DEFAULT_COST_PRESETS,
    ) -> None:
        self._graph = graph
        self._presets = MappingProxyType(dict(presets))
        if any(not isinstance(preset, CostPreset) for preset in self._presets.values()):
            raise TypeError("Cost presets must contain CostPreset values")

    @property
    def graph(self) -> Graph:
        return self._graph

    @property
    def presets(self) -> Mapping[str, CostPreset]:
        return self._presets

    def cost_preset(self, preset_id: str) -> CostPreset:
        try:
            return self._presets[preset_id]
        except KeyError as error:
            raise CostModelError(f"Unknown cost preset: {preset_id}") from error

    def preset_for_scenario(self, scenario_id: str) -> CostPreset:
        scenario = self._graph.scenario(scenario_id)
        preset_id = scenario.data.get("cost_preset")
        if not isinstance(preset_id, str) or not preset_id.strip():
            raise CostModelError(f"Scenario {scenario_id} does not declare cost_preset")
        preset = self.cost_preset(preset_id.strip())

        declared_weights = scenario.data.get("weights")
        if declared_weights is not None:
            try:
                normalized_weights = {
                    key: _number(value, f"{scenario_id}.weights.{key}")
                    for key, value in dict(declared_weights).items()
                }
            except (TypeError, ValueError) as error:
                raise CostModelError(f"Scenario {scenario_id} weights must be an object") from error
            if normalized_weights != dict(preset.weights):
                raise CostModelError(
                    f"Scenario {scenario_id} weights do not match preset {preset.preset_id}"
                )
        return preset

    def cost_for_edge(self, edge_id: str, scenario_id: str) -> EdgeCostBreakdown:
        return self.cost_for_edge_value(self._graph.get_edge(edge_id), scenario_id)

    def cost_for_edge_value(self, edge: Edge, scenario_id: str) -> EdgeCostBreakdown:
        scenario = self._graph.scenario(scenario_id)
        preset = self.preset_for_scenario(scenario_id)
        override = self._edge_override(scenario.data.get("edge_overrides"), edge.edge_id)

        distance_m = self._value(override, edge.data, "distance_m", edge.distance_m)
        free_flow_time = self._value(
            override,
            edge.data,
            "free_flow_time_min",
            edge.free_flow_time_min,
        )
        distance_m = _number(distance_m, f"{edge.edge_id}.distance_m")
        free_flow_time = _number(
            free_flow_time,
            f"{edge.edge_id}.free_flow_time_min",
        )
        if distance_m <= 0 or free_flow_time <= 0:
            raise CostModelError(f"Edge {edge.edge_id} distance/time must be positive")

        congestion_level = _number(
            self._value(
                override,
                edge.data,
                "congestion_level_1_5",
                scenario.data.get(
                    "default_congestion_level_1_5",
                    self.DEFAULT_CONGESTION_LEVEL,
                ),
            ),
            f"{edge.edge_id}.congestion_level_1_5",
        )
        if not 0 <= congestion_level <= 5:
            raise CostModelError(
                f"Edge {edge.edge_id} congestion level must be between 0 and 5"
            )

        flood_risk = _number(
            self._value(
                override,
                edge.data,
                "flood_risk_0_1",
                scenario.data.get("default_flood_risk_0_1", 0.0),
            ),
            f"{edge.edge_id}.flood_risk_0_1",
        )
        if not 0 <= flood_risk <= 1:
            raise CostModelError(f"Edge {edge.edge_id} flood risk must be between 0 and 1")

        traffic_multiplier_value = self._value(
            override,
            edge.data,
            "traffic_multiplier",
            scenario.data.get("traffic_multiplier"),
        )
        if traffic_multiplier_value is None:
            traffic_multiplier = 1 + max(congestion_level - 1, 0) * self.CONGESTION_MULTIPLIER_STEP
        else:
            traffic_multiplier = _number(
                traffic_multiplier_value,
                f"{edge.edge_id}.traffic_multiplier",
            )
        if traffic_multiplier <= 0:
            raise CostModelError(f"Edge {edge.edge_id} traffic multiplier must be positive")

        explicit_penalty = self._value(
            override,
            edge.data,
            "traffic_penalty_min",
            None,
        )
        if explicit_penalty is None:
            travel_time = free_flow_time * traffic_multiplier
            traffic_penalty = max(0.0, travel_time - free_flow_time)
        else:
            traffic_penalty = _number(
                explicit_penalty,
                f"{edge.edge_id}.traffic_penalty_min",
            )
            if traffic_penalty < 0:
                raise CostModelError(f"Edge {edge.edge_id} traffic penalty cannot be negative")
            travel_time = free_flow_time + traffic_penalty

        distance_km = distance_m / 1000
        weighted_components = {
            "distance": distance_km * preset.weights["distance"],
            "freeflow_time": free_flow_time * preset.weights["freeflow_time"],
            "congestion": traffic_penalty * preset.weights["congestion"],
            "flood_risk": flood_risk * preset.weights["flood_risk"],
        }
        is_closed = self._graph.is_edge_closed(edge.edge_id, scenario_id)
        return EdgeCostBreakdown(
            edge_id=edge.edge_id,
            scenario_id=scenario_id,
            cost_preset=preset.preset_id,
            distance_km=distance_km,
            free_flow_time_min=free_flow_time,
            travel_time_min=travel_time,
            congestion_level_1_5=congestion_level,
            traffic_penalty=traffic_penalty,
            flood_risk=flood_risk,
            weighted_components=weighted_components,
            total_cost=None if is_closed else sum(weighted_components.values()),
            is_closed=is_closed,
            data_status=str(
                override.get(
                    "data_status",
                    edge.data.get("data_status", scenario.data.get("data_status", "SIMULATED")),
                )
            ),
        )

    def route_cost(self, edge_ids: tuple[str, ...] | list[str], scenario_id: str) -> RouteCostBreakdown:
        edge_costs = tuple(self.cost_for_edge(edge_id, scenario_id) for edge_id in edge_ids)
        is_available = all(not edge_cost.is_closed for edge_cost in edge_costs)
        total_cost = sum(edge_cost.total_cost or 0.0 for edge_cost in edge_costs) if is_available else None
        statuses = {edge_cost.data_status for edge_cost in edge_costs}
        if not statuses:
            scenario = self._graph.scenario(scenario_id)
            data_status = str(
                scenario.data.get(
                    "data_status",
                    self._graph.metadata.get("data_status", "SIMULATED"),
                )
            )
        elif len(statuses) == 1:
            data_status = next(iter(statuses))
        else:
            data_status = "MIXED"
        return RouteCostBreakdown(
            scenario_id=scenario_id,
            edge_costs=edge_costs,
            total_cost=total_cost,
            is_available=is_available,
            data_status=data_status,
        )

    @staticmethod
    def _edge_override(overrides: Any, edge_id: str) -> Mapping[str, Any]:
        if overrides is None:
            return {}
        if not isinstance(overrides, Mapping):
            raise CostModelError("Scenario edge_overrides must be an object")
        value = overrides.get(edge_id, {})
        if not isinstance(value, Mapping):
            raise CostModelError(f"Edge override for {edge_id} must be an object")
        return value

    @staticmethod
    def _value(
        override: Mapping[str, Any],
        edge_data: Mapping[str, Any],
        key: str,
        default: Any,
    ) -> Any:
        if key in override:
            return override[key]
        if key in edge_data:
            return edge_data[key]
        return default


CostEngine = ScenarioCostEngine


__all__ = ["CostEngine", "DEFAULT_COST_PRESETS", "ScenarioCostEngine"]
