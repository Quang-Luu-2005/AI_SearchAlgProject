"""Run the reproducible 10 OD x 3 scenario search benchmark."""

from __future__ import annotations

import argparse
import json
import platform
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.app.core.graph import GraphLoader
from backend.app.services.search import SearchService


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "experiments/cases/search_benchmark_v1.json"


def percentile(values: list[float], ratio: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int((len(ordered) - 1) * ratio))]


def run(case_path: Path, repetitions: int) -> dict[str, Any]:
    config = json.loads(case_path.read_text(encoding="utf-8"))
    graph_path = ROOT / "data" / config["graph_id"]
    graph = GraphLoader.from_directory(graph_path)
    service = SearchService(graph)
    rows: list[dict[str, Any]] = []
    routes: dict[tuple[str, str], dict[str, tuple[str, ...]]] = {}

    for case in config["pairs"]:
        for scenario in config["scenarios"]:
            for algorithm in config["algorithms"]:
                service.search(
                    start=case["start"], goal=case["goal"],
                    algorithm=algorithm, scenario_id=scenario,
                )
                durations: list[float] = []
                execution = None
                for _ in range(repetitions):
                    execution = service.search(
                        start=case["start"], goal=case["goal"],
                        algorithm=algorithm, scenario_id=scenario,
                    )
                    durations.append(execution.result.metrics.processing_time_ms)
                assert execution is not None
                metrics = execution.result.metrics
                routes.setdefault((case["case_id"], algorithm), {})[scenario] = execution.edge_ids
                rows.append({
                    "case_id": case["case_id"],
                    "start": case["start"],
                    "goal": case["goal"],
                    "scenario": scenario,
                    "algorithm": algorithm,
                    "repetitions": repetitions,
                    "median_search_ms": round(statistics.median(durations), 6),
                    "p95_search_ms": round(percentile(durations, 0.95), 6),
                    "explored_nodes": metrics.explored_nodes,
                    "distance_km": round(metrics.distance_m / 1000, 6),
                    "estimated_time_min": round(metrics.estimated_time_min, 6),
                    "total_cost": round(metrics.total_cost, 6),
                    "path_nodes": len(execution.result.path),
                })

    route_change_summary = []
    for (case_id, algorithm), scenario_routes in sorted(routes.items()):
        signatures = {route for route in scenario_routes.values()}
        route_change_summary.append({
            "case_id": case_id,
            "algorithm": algorithm,
            "distinct_routes_across_scenarios": len(signatures),
            "route_changed": len(signatures) > 1,
        })

    aggregate_summary = []
    for algorithm in config["algorithms"]:
        algorithm_rows = [row for row in rows if row["algorithm"] == algorithm]
        changed_cases = sum(
            item["route_changed"]
            for item in route_change_summary
            if item["algorithm"] == algorithm
        )
        aggregate_summary.append({
            "algorithm": algorithm,
            "combinations": len(algorithm_rows),
            "median_of_median_search_ms": round(statistics.median(
                row["median_search_ms"] for row in algorithm_rows
            ), 6),
            "max_p95_search_ms": max(row["p95_search_ms"] for row in algorithm_rows),
            "median_explored_nodes": statistics.median(
                row["explored_nodes"] for row in algorithm_rows
            ),
            "od_cases_with_route_change": changed_cases,
        })

    return {
        "benchmark_id": config["case_set_id"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "result_status": "DERIVED_BENCHMARK",
        "graph_id": config["graph_id"],
        "graph_data_status": config["data_status"],
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "note": "Single local process with one warm-up per case; timings vary by machine.",
        },
        "design": {
            "od_pairs": len(config["pairs"]),
            "scenarios": len(config["scenarios"]),
            "algorithms": len(config["algorithms"]),
            "repetitions_per_combination": repetitions,
            "measured_runs": len(rows) * repetitions,
        },
        "results": rows,
        "aggregate_summary": aggregate_summary,
        "route_change_summary": route_change_summary,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--repetitions", type=int, default=20)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.repetitions < 1:
        raise SystemExit("--repetitions must be positive")
    report = run(args.cases, args.repetitions)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
