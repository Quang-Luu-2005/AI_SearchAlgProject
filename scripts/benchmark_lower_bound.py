"""Benchmark the scenario-aware A* lower bound against UCS on the fixture graph."""

from __future__ import annotations

import argparse
import json
import math
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.app.algorithms.weighted import compute_scenario_rho
from backend.app.core.cost import ScenarioCostEngine
from backend.app.core.graph import GraphLoader
from backend.app.services.search import SearchService


ROOT = Path(__file__).resolve().parents[1]
GRAPH_ID = "fixtures/toy_graph_v0.1"
SCENARIOS = ("OFFPEAK_BALANCED", "PEAK_TRAFFIC", "HEAVY_RAIN_SAFE")
PAIRS = (
    ("OD01", "N01", "N06"),
    ("OD02", "N03", "N06"),
    ("OD03", "N01", "N05"),
    ("OD04", "N02", "N05"),
    ("OD05", "N06", "N05"),
)


def run() -> dict[str, Any]:
    graph = GraphLoader.from_directory(ROOT / "data" / GRAPH_ID)
    cost_engine = ScenarioCostEngine(graph)
    service = SearchService(graph)
    rows: list[dict[str, Any]] = []

    for scenario_id in SCENARIOS:
        rho_s = compute_scenario_rho(graph, cost_engine, scenario_id)
        for case_id, start, goal in PAIRS:
            ucs = service.search(
                start=start, goal=goal, algorithm="UCS", scenario_id=scenario_id
            )
            astar = service.search(
                start=start, goal=goal, algorithm="A_STAR", scenario_id=scenario_id
            )
            ucs_cost = ucs.result.metrics.total_cost
            astar_cost = astar.result.metrics.total_cost
            rows.append(
                {
                    "case_id": case_id,
                    "start": start,
                    "goal": goal,
                    "scenario": scenario_id,
                    "rho_s": round(rho_s, 9),
                    "ucs_cost": round(ucs_cost, 9),
                    "astar_cost": round(astar_cost, 9),
                    "cost_delta": round(astar_cost - ucs_cost, 9),
                    "cost_match": math.isclose(astar_cost, ucs_cost, rel_tol=1e-9, abs_tol=1e-9),
                    "ucs_explored_nodes": ucs.result.metrics.explored_nodes,
                    "astar_explored_nodes": astar.result.metrics.explored_nodes,
                    "ucs_processing_time_ms": round(ucs.result.metrics.processing_time_ms, 6),
                    "astar_processing_time_ms": round(astar.result.metrics.processing_time_ms, 6),
                    "ucs_path": list(ucs.result.path),
                    "astar_path": list(astar.result.path),
                }
            )

    return {
        "benchmark_id": "ASTAR_UCS_LOWER_BOUND_V1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "result_status": "DERIVED_BENCHMARK",
        "data_status": "SIMULATED",
        "graph_id": GRAPH_ID,
        "selection_method": "ASSUMPTION: deterministic fixture pairs; no random sampling",
        "heuristic": {
            "formula": "h_s(n) = rho_s * Haversine(n, goal)",
            "rho_formula": "rho_s = min(Cost_s(e) / Haversine(e)) over open usable edges",
            "near_zero_threshold_km": 1e-6,
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "note": "Processing times are local measurements; costs and explored nodes are deterministic.",
        },
        "design": {
            "od_pairs": len(PAIRS),
            "scenarios": list(SCENARIOS),
            "algorithms": ["UCS", "A_STAR"],
        },
        "results": rows,
        "summary": {
            "cases": len(rows),
            "cost_mismatches": sum(not row["cost_match"] for row in rows),
            "astar_explored_leq_ucs": sum(
                row["astar_explored_nodes"] <= row["ucs_explored_nodes"] for row in rows
            ),
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# A* lower-bound heuristic vs UCS",
        "",
        "Status: `DERIVED_BENCHMARK`; graph/scenarios: `SIMULATED` fixture.",
        "",
        "Formula: `h_s(n) = rho_s × Haversine(n, goal)`; closed edges and edges with Haversine ≤ 1e-6 km are excluded from rho_s.",
        "",
        "| Scenario | OD | Start → goal | rho_s | UCS cost | A* cost | Δ cost | UCS explored | A* explored | Match |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for row in report["results"]:
        lines.append(
            f"| {row['scenario']} | {row['case_id']} | {row['start']} → {row['goal']} | "
            f"{row['rho_s']:.9f} | {row['ucs_cost']:.6f} | {row['astar_cost']:.6f} | "
            f"{row['cost_delta']:.9f} | {row['ucs_explored_nodes']} | "
            f"{row['astar_explored_nodes']} | {'YES' if row['cost_match'] else 'NO'} |"
        )
    summary = report["summary"]
    lines.extend(
        [
            "",
            f"Summary: {summary['cases']} cases, {summary['cost_mismatches']} cost mismatches, "
            f"A* explored no more nodes than UCS in {summary['astar_explored_leq_ucs']}/{summary['cases']} cases.",
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
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(rendered, encoding="utf-8")
    if args.output_markdown:
        args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
        args.output_markdown.write_text(render_markdown(report), encoding="utf-8")
