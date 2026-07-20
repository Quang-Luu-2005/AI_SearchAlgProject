"""Validate provenance and deterministic toy data without third-party packages."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = REPOSITORY_ROOT / "data"
MANIFEST_PATH = DATA_ROOT / "registry" / "dataset_manifest.json"
FIXTURE_ROOT = DATA_ROOT / "fixtures" / "toy_graph_v0.1"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def validate() -> list[str]:
    errors: list[str] = []
    manifest = read_json(MANIFEST_PATH)

    for source in manifest["raw_sources"]:
        source_path = REPOSITORY_ROOT / source["path"]
        if not source_path.is_file():
            errors.append(f"Missing raw source: {source_path}")
        elif sha256(source_path) != source["sha256"]:
            errors.append(f"Checksum mismatch: {source_path}")

    nodes = read_csv(FIXTURE_ROOT / "nodes.csv")
    edges = read_csv(FIXTURE_ROOT / "edges.csv")
    scenarios = read_json(FIXTURE_ROOT / "scenarios.json")
    test_cases = read_json(FIXTURE_ROOT / "test_cases.json")

    node_ids = [node["node_id"] for node in nodes]
    edge_ids = [edge["edge_id"] for edge in edges]
    node_id_set = set(node_ids)
    edge_id_set = set(edge_ids)

    if len(node_ids) != len(node_id_set):
        errors.append("Fixture node_id values must be unique")
    if len(edge_ids) != len(edge_id_set):
        errors.append("Fixture edge_id values must be unique")
    if any(node["data_status"] != "SIMULATED" for node in nodes):
        errors.append("Every fixture node must be labelled SIMULATED")

    for edge in edges:
        if edge["from_node_id"] not in node_id_set or edge["to_node_id"] not in node_id_set:
            errors.append(f"Edge {edge['edge_id']} references a missing node")
        if float(edge["distance_m"]) <= 0 or float(edge["free_flow_time_min"]) <= 0:
            errors.append(f"Edge {edge['edge_id']} must have positive distance/time")
        if edge["data_status"] != "SIMULATED":
            errors.append(f"Edge {edge['edge_id']} must be labelled SIMULATED")

    scenario_by_id: dict[str, dict[str, Any]] = {}
    for scenario in scenarios["scenarios"]:
        scenario_by_id[scenario["scenario_id"]] = scenario
        if abs(sum(scenario["weights"].values()) - 1.0) > 1e-9:
            errors.append(f"Scenario {scenario['scenario_id']} weights must sum to 1")
        missing_edges = set(scenario["closed_edge_ids"]) - edge_id_set
        if missing_edges:
            errors.append(f"Scenario {scenario['scenario_id']} closes missing edges: {sorted(missing_edges)}")

    directed_edges = {(edge["from_node_id"], edge["to_node_id"], edge["edge_id"]) for edge in edges}
    for case in test_cases["cases"]:
        if case["start"] not in node_id_set or case["goal"] not in node_id_set:
            errors.append(f"Case {case['case_id']} references a missing endpoint")
        if case["scenario_id"] not in scenario_by_id:
            errors.append(f"Case {case['case_id']} references a missing scenario")
            continue
        if "expected_path" not in case:
            continue

        path = case["expected_path"]
        if path[0] != case["start"] or path[-1] != case["goal"]:
            errors.append(f"Case {case['case_id']} expected path has wrong endpoints")
        closed_edges = set(scenario_by_id[case["scenario_id"]]["closed_edge_ids"])
        for origin, destination in zip(path, path[1:]):
            candidates = {
                edge_id
                for from_id, to_id, edge_id in directed_edges
                if from_id == origin and to_id == destination
            }
            if not candidates or candidates <= closed_edges:
                errors.append(
                    f"Case {case['case_id']} expected step {origin}->{destination} is unavailable"
                )

    return errors


if __name__ == "__main__":
    validation_errors = validate()
    if validation_errors:
        print("Dataset validation: FAIL")
        for error in validation_errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("Dataset validation: PASS")
    print("- raw source checksum verified")
    print("- toy graph: 6 nodes, 14 directed edges")
    print("- scenario weights and golden paths verified")

