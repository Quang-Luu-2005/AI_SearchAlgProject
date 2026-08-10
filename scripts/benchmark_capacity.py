"""Benchmark the large Thu Duc graph through loader, search and API serialization."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from time import perf_counter
from typing import Any

from backend.app.api.router import graph_detail, locations
from backend.app.core.graph import GraphLoader
from backend.app.services.search import SearchService


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GRAPH_ID = "processed/thu_duc_core_capacity_v0.1.0"
DEFAULT_GRAPH_PATH = REPOSITORY_ROOT / "data/processed/thu_duc_core_capacity_v0.1.0"
SCENARIO_ID = "CAPACITY_BASELINE"


def percentile(values: list[float], ratio: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int((len(ordered) - 1) * ratio))]


def benchmark(sample_count: int) -> dict[str, Any]:
    started_at = perf_counter()
    graph = GraphLoader.from_directory(DEFAULT_GRAPH_PATH)
    load_time_ms = (perf_counter() - started_at) * 1000
    node_ids = sorted(node.node_id for node in graph.nodes)
    pair_space = max(1, len(node_ids) // 2)
    indexes = (
        [0]
        if sample_count == 1
        else [round(index * (pair_space - 1) / (sample_count - 1)) for index in range(sample_count)]
    )
    pairs = [
        (node_ids[index], node_ids[-index - 1])
        for index in indexes
    ]
    service = SearchService(graph)

    algorithms: dict[str, dict[str, Any]] = {}
    for algorithm in ("UCS", "A_STAR"):
        durations: list[float] = []
        explored: list[int] = []
        path_lengths: list[int] = []
        for start, goal in pairs:
            execution = service.search(
                start=start,
                goal=goal,
                algorithm=algorithm,
                scenario_id=SCENARIO_ID,
            )
            durations.append(execution.result.metrics.processing_time_ms)
            explored.append(execution.result.metrics.explored_nodes)
            path_lengths.append(len(execution.result.path))
        algorithms[algorithm] = {
            "samples": len(durations),
            "median_search_ms": round(statistics.median(durations), 3),
            "p95_search_ms": round(percentile(durations, 0.95), 3),
            "max_search_ms": round(max(durations), 3),
            "median_explored_nodes": round(statistics.median(explored), 1),
            "max_explored_nodes": max(explored),
            "max_path_nodes": max(path_lengths),
        }

    api_started_at = perf_counter()
    graph_payload = graph_detail(DEFAULT_GRAPH_ID, SCENARIO_ID)
    graph_api_ms = (perf_counter() - api_started_at) * 1000
    graph_payload_bytes = len(
        json.dumps(graph_payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    )
    location_started_at = perf_counter()
    location_payload = locations(DEFAULT_GRAPH_ID)
    locations_api_ms = (perf_counter() - location_started_at) * 1000

    return {
        "graph_id": DEFAULT_GRAPH_ID,
        "environment_note": "Single local process; timing varies by machine and warm cache.",
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
        "geojson_feature_count": len(graph.nodes) + len(graph.edges),
        "graph_load_ms": round(load_time_ms, 3),
        "graph_api_build_ms": round(graph_api_ms, 3),
        "graph_api_payload_mb": round(graph_payload_bytes / 1024 / 1024, 3),
        "locations_count": len(location_payload["locations"]),
        "locations_api_build_ms": round(locations_api_ms, 3),
        "algorithms": algorithms,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=12)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    if arguments.samples <= 0:
        raise SystemExit("--samples must be positive")
    report = benchmark(arguments.samples)
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if arguments.output:
        arguments.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
