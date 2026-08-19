"""Produce report-ready evidence for the frozen cost profiles."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.app.core.cost import DEFAULT_COST_PRESETS
from backend.app.core.graph import GraphLoader
from backend.app.services.search import SearchService


ROOT = Path(__file__).resolve().parents[1]
TOY_GRAPH = ROOT / "data" / "fixtures" / "toy_graph_v0.1"

PROFILE_STORIES = {
    "BALANCED": "Default trade-off across distance, free-flow time, congestion and flood risk.",
    "PEAK_TRAFFIC": "Raises congestion priority to avoid delay during peak traffic; distance/flood remain secondary signals.",
    "RAIN_SAFE": "Raises flood-risk priority so a longer/different route can be preferred when flooding is exposed.",
}


def _search_summary(service: SearchService, start: str, goal: str, scenario: str) -> dict[str, Any]:
    result = service.search(start=start, goal=goal, algorithm="UCS", scenario_id=scenario)
    return {
        "scenario": scenario,
        "path": list(result.result.path),
        "edge_ids": list(result.edge_ids),
        "path_edge_count": len(result.edge_ids),
        "total_cost": round(result.result.metrics.total_cost, 9),
        "distance_km": round(result.result.metrics.distance_m / 1000, 6),
        "estimated_time_min": round(result.result.metrics.estimated_time_min, 6),
    }


def run() -> dict[str, Any]:
    toy_service = SearchService(GraphLoader.from_directory(TOY_GRAPH))
    toy_routes = [
        _search_summary(toy_service, "N01", "N06", scenario)
        for scenario in ("OFFPEAK_BALANCED", "PEAK_TRAFFIC", "HEAVY_RAIN_SAFE")
    ]

    toy_route_change = [
        _search_summary(toy_service, "N05", "N01", scenario)
        for scenario in ("OFFPEAK_BALANCED", "HEAVY_RAIN_SAFE")
    ]

    profiles = []
    for preset_id, preset in DEFAULT_COST_PRESETS.items():
        profiles.append(
            {
                "preset_id": preset_id,
                "weights": dict(preset.weights),
                "sum": round(sum(preset.weights.values()), 9),
                "story": PROFILE_STORIES[preset_id],
            }
        )

    return {
        "benchmark_id": "COST_PROFILES_V1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "result_status": "DERIVED_PROFILE_REVIEW",
        "profiles_data_status": "ASSUMPTION",
        "formula": "cost(e) = distance*w_distance + freeflow_time*w_freeflow_time + traffic_penalty*w_congestion + flood_risk*w_flood_risk",
        "weight_interpretation": "Priority coefficients for a simulated/empirical prototype, not percentage contributions; components have different units and scales.",
        "closure_rule": "Road closure is a hard constraint: closed edges have total_cost=null and cannot belong to a route, regardless of weights.",
        "custom_weights_api": "Not exposed in the public API for this deadline; the three named scenario profiles are the stable contract.",
        "profiles": profiles,
        "route_examples": [
            {
                "example_id": "EX01_TOY_PROFILE_AND_RAIN",
                "data_status": "SIMULATED",
                "graph_id": "toy_graph_v0.1",
                "start": "N01",
                "goal": "N06",
                "routes": toy_routes,
                "interpretation": "Peak raises cost on the same available route; heavy rain closes E03/E04, so the route must detour through E11/E09.",
            },
            {
                "example_id": "EX02_TOY_ALTERNATIVE_RAIN",
                "data_status": "SIMULATED",
                "graph_id": "toy_graph_v0.1",
                "start": "N05",
                "goal": "N01",
                "routes": toy_route_change,
                "interpretation": "The simulated N05 to N01 route changes under heavy rain because the direct E04 segment is closed and the path detours through E10/E12.",
            },
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    def compact_path(path: list[str]) -> str:
        if len(path) <= 8:
            return " → ".join(path)
        return " → ".join(path[:3] + ["…"] + path[-3:])

    lines = [
        "# Cost profiles and route-change evidence",
        "",
        "Status: `DERIVED_PROFILE_REVIEW`. Profile values are `ASSUMPTION` coefficients for the prototype.",
        "",
        "Cost formula: `distance*w_distance + freeflow_time*w_freeflow_time + traffic_penalty*w_congestion + flood_risk*w_flood_risk`.",
        "The weights are priority coefficients, not percentage contributions: the four components have different units/scales.",
        "Road closure is a hard constraint; weights never make a closed edge traversable.",
        "",
        "## Frozen profiles",
        "",
        "| Preset | Distance | Free-flow time | Congestion | Flood risk | Sum | Interpretation |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for profile in report["profiles"]:
        weights = profile["weights"]
        lines.append(
            f"| {profile['preset_id']} | {weights['distance']:.2f} | {weights['freeflow_time']:.2f} | "
            f"{weights['congestion']:.2f} | {weights['flood_risk']:.2f} | {profile['sum']:.2f} | {profile['story']} |"
        )

    lines.extend(["", "## Route examples", ""])
    for example in report["route_examples"]:
        lines.append(f"### {example['example_id']} — {example['graph_id']} ({example['data_status']})")
        lines.append("")
        lines.append(f"OD: `{example['start']} → {example['goal']}`")
        lines.append("")
        lines.append("| Scenario | Route | Edges | Cost | Distance (km) | ETA (min) |")
        lines.append("|---|---|---:|---:|---:|---:|")
        for route in example["routes"]:
            lines.append(
                f"| {route['scenario']} | `{compact_path(route['path'])}` | {route['path_edge_count']} | "
                f"{route['total_cost']:.6f} | {route['distance_km']:.3f} | {route['estimated_time_min']:.3f} |"
            )
        lines.extend(["", f"Interpretation: {example['interpretation']}", ""])
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-markdown", type=Path)
    args = parser.parse_args()
    report = run()
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(rendered, encoding="utf-8")
    if args.output_markdown:
        args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
        args.output_markdown.write_text(render_markdown(report), encoding="utf-8")
