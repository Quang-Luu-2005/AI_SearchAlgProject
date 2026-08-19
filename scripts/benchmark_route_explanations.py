"""Generate reproducible edge-level evidence for route explanations in the report.

The report intentionally uses the small ``toy_graph_v0.1`` fixture here: its
traffic and flood inputs are explicitly labelled SIMULATED, so the two route
choices can be reproduced without implying live traffic advice.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.app.core.cost import ScenarioCostEngine
from backend.app.core.graph import GraphLoader
from backend.app.services.search import SearchService


ROOT = Path(__file__).resolve().parents[1]
TOY_GRAPH = ROOT / "data" / "fixtures" / "toy_graph_v0.1"
_COMPONENTS = ("distance", "freeflow_time", "congestion", "flood_risk")

# These alternatives are deliberate, connected routes in the immutable fixture.
# The script validates their direction and reports them as unavailable whenever a
# scenario closes one of their edges; it never turns a closed edge into a route.
CASE_DEFINITIONS = (
    {
        "case_id": "CASE_A_PEAK_TRAFFIC",
        "title": "Peak traffic: compare the optimal route with the next short detour",
        "scenario_id": "PEAK_TRAFFIC",
        "start": "N01",
        "goal": "N06",
        "expected_selected_edges": ("E01", "E03"),
        "alternative_label": "Detour through N04",
        "alternative_edges": ("E01", "E11", "E09"),
        "fixture_note": (
            "All open edges in this peak fixture use congestion level 4 and "
            "traffic multiplier 1.45. Therefore this case must not be described "
            "as a traffic-avoidance reroute; it is a component-level comparison "
            "under the PEAK_TRAFFIC profile."
        ),
    },
    {
        "case_id": "CASE_B_HEAVY_RAIN",
        "title": "Heavy rain: reroute because the direct segment is closed",
        "scenario_id": "HEAVY_RAIN_SAFE",
        "start": "N05",
        "goal": "N01",
        "expected_selected_edges": ("E14", "E10", "E12", "E02"),
        "alternative_label": "Former direct route through E04",
        "alternative_edges": ("E14", "E04", "E02"),
        "fixture_note": (
            "E04 is closed by the HEAVY_RAIN_SAFE scenario. Closure is a hard "
            "constraint, so the former direct route has no valid total cost in "
            "this scenario regardless of the selected weights."
        ),
    },
)


def _number(value: float | None) -> float | None:
    return None if value is None else round(value, 9)


def _edge_ids_to_path(graph: Any, edge_ids: tuple[str, ...]) -> list[str]:
    if not edge_ids:
        raise ValueError("A route explanation requires at least one edge")
    edges = [graph.get_edge(edge_id) for edge_id in edge_ids]
    for previous, current in zip(edges, edges[1:]):
        if previous.to_node_id != current.from_node_id:
            raise ValueError(
                f"Route edges are not connected: {previous.edge_id} then {current.edge_id}"
            )
    return [edges[0].from_node_id, *(edge.to_node_id for edge in edges)]


def _route_summary(
    graph: Any,
    cost_engine: ScenarioCostEngine,
    edge_ids: tuple[str, ...],
    scenario_id: str,
) -> dict[str, Any]:
    path = _edge_ids_to_path(graph, edge_ids)
    route = cost_engine.route_cost(edge_ids, scenario_id)
    edge_rows = []
    for edge in route.edge_costs:
        edge_rows.append(
            {
                "edge_id": edge.edge_id,
                "distance_km": _number(edge.distance_km),
                "free_flow_time_min": _number(edge.free_flow_time_min),
                "travel_time_min": _number(edge.travel_time_min),
                "congestion_level_1_5": _number(edge.congestion_level_1_5),
                "traffic_penalty_min": _number(edge.traffic_penalty),
                "flood_risk_0_1": _number(edge.flood_risk),
                "weighted_components": {
                    component: _number(edge.weighted_components[component])
                    for component in _COMPONENTS
                },
                "total_cost": _number(edge.total_cost),
                "is_closed": edge.is_closed,
                "data_status": edge.data_status,
            }
        )

    component_totals = {
        component: _number(
            sum(edge.weighted_components[component] for edge in route.edge_costs)
        )
        for component in _COMPONENTS
    }
    is_available = route.is_available and route.total_cost is not None
    return {
        "path": path,
        "edge_ids": list(edge_ids),
        "is_available": is_available,
        "closed_edge_ids": [edge.edge_id for edge in route.edge_costs if edge.is_closed],
        "distance_km": _number(sum(edge.distance_km for edge in route.edge_costs)),
        "estimated_time_min": _number(sum(edge.travel_time_min for edge in route.edge_costs)),
        "component_totals": component_totals if is_available else None,
        "total_cost": _number(route.total_cost),
        "edges": edge_rows,
        "data_status": route.data_status,
    }


def _algorithm_summary(execution: Any) -> dict[str, Any]:
    metrics = execution.result.metrics
    return {
        "algorithm": execution.algorithm.value,
        "path": list(execution.result.path),
        "edge_ids": list(execution.edge_ids),
        "total_cost": _number(metrics.total_cost),
        "explored_nodes": metrics.explored_nodes,
        "guarantee": execution.result.guarantee,
    }


def _build_case(
    graph: Any,
    service: SearchService,
    cost_engine: ScenarioCostEngine,
    definition: dict[str, Any],
) -> dict[str, Any]:
    scenario_id = definition["scenario_id"]
    start = definition["start"]
    goal = definition["goal"]
    ucs = service.search(start=start, goal=goal, algorithm="UCS", scenario_id=scenario_id)
    astar = service.search(start=start, goal=goal, algorithm="A*", scenario_id=scenario_id)
    selected_edges = tuple(ucs.edge_ids)

    if selected_edges != definition["expected_selected_edges"]:
        raise AssertionError(
            f"{definition['case_id']} selected {selected_edges}, expected "
            f"{definition['expected_selected_edges']}"
        )
    if ucs.edge_ids != astar.edge_ids:
        raise AssertionError(
            f"{definition['case_id']} path mismatch: UCS {ucs.edge_ids}, A* {astar.edge_ids}"
        )
    if abs(ucs.result.metrics.total_cost - astar.result.metrics.total_cost) > 1e-9:
        raise AssertionError(f"{definition['case_id']} has an A*/UCS cost mismatch")

    selected = _route_summary(graph, cost_engine, selected_edges, scenario_id)
    alternative = _route_summary(
        graph,
        cost_engine,
        definition["alternative_edges"],
        scenario_id,
    )
    if selected["total_cost"] != _number(ucs.result.metrics.total_cost):
        raise AssertionError(f"{definition['case_id']} cost aggregation does not match UCS")

    return {
        "case_id": definition["case_id"],
        "title": definition["title"],
        "data_status": "SIMULATED",
        "graph_id": "toy_graph_v0.1",
        "scenario_id": scenario_id,
        "start": start,
        "goal": goal,
        "selected": selected,
        "alternative": {
            "label": definition["alternative_label"],
            **alternative,
        },
        "algorithm_validation": {
            "ucs": _algorithm_summary(ucs),
            "a_star": _algorithm_summary(astar),
            "cost_delta_a_star_minus_ucs": _number(
                astar.result.metrics.total_cost - ucs.result.metrics.total_cost
            ),
            "same_optimal_path": list(ucs.edge_ids) == list(astar.edge_ids),
        },
        "fixture_note": definition["fixture_note"],
    }


def run() -> dict[str, Any]:
    graph = GraphLoader.from_directory(TOY_GRAPH)
    service = SearchService(graph)
    cost_engine = ScenarioCostEngine(graph)
    cases = [
        _build_case(graph, service, cost_engine, definition)
        for definition in CASE_DEFINITIONS
    ]
    return {
        "benchmark_id": "ROUTE_EXPLANATIONS_V1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "result_status": "DERIVED_ROUTE_EXPLANATION",
        "data_status": "SIMULATED",
        "graph_id": "toy_graph_v0.1",
        "cost_formula": "cost(e) = distance*w_distance + freeflow_time*w_freeflow_time + traffic_penalty*w_congestion + flood_risk*w_flood_risk",
        "closure_rule": "Closed edges are unavailable and have total_cost=null; they cannot be selected by UCS or A*.",
        "optimality_rule": "UCS is optimal for non-negative edge costs. A* has the same guarantee here because it uses the frozen scenario-aware admissible and consistent lower-bound heuristic.",
        "cases": cases,
    }


def _format(value: float | None, digits: int = 6) -> str:
    return "N/A" if value is None else f"{value:.{digits}f}"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Route explanation and alternative comparison evidence",
        "",
        "Status: `DERIVED_ROUTE_EXPLANATION`; all route inputs below are `SIMULATED`.",
        "",
    ]
    for case in report["cases"]:
        selected = case["selected"]
        alternative = case["alternative"]
        validation = case["algorithm_validation"]
        lines.extend(
            [
                f"## {case['case_id']}: {case['title']}",
                "",
                f"OD: `{case['start']} -> {case['goal']}`; scenario: `{case['scenario_id']}`.",
                "",
                "| Route | Edge IDs | Available | Distance (km) | ETA (min) | Total cost |",
                "|---|---|---:|---:|---:|---:|",
                f"| Selected | `{', '.join(selected['edge_ids'])}` | yes | {_format(selected['distance_km'], 3)} | {_format(selected['estimated_time_min'], 3)} | {_format(selected['total_cost'])} |",
                f"| {alternative['label']} | `{', '.join(alternative['edge_ids'])}` | {'yes' if alternative['is_available'] else 'no'} | {_format(alternative['distance_km'], 3)} | {_format(alternative['estimated_time_min'], 3)} | {_format(alternative['total_cost'])} |",
                "",
                "| Algorithm | Cost | Explored nodes |",
                "|---|---:|---:|",
                f"| UCS | {_format(validation['ucs']['total_cost'])} | {validation['ucs']['explored_nodes']} |",
                f"| A* | {_format(validation['a_star']['total_cost'])} | {validation['a_star']['explored_nodes']} |",
                "",
                f"Fixture note: {case['fixture_note']}",
                "",
            ]
        )
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-markdown", type=Path)
    args = parser.parse_args()
    report = run()
    rendered_json = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered_json, end="")
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(rendered_json, encoding="utf-8")
    if args.output_markdown:
        args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
        args.output_markdown.write_text(render_markdown(report), encoding="utf-8")
