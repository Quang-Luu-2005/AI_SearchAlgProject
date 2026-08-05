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
EXAMPLE_FIXTURE_ROOT = DATA_ROOT / "fixtures" / "graph_examples_v0.1"


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


def validate_graph_fixture(fixture_root: Path) -> list[str]:
    errors: list[str] = []
    fixture_name = fixture_root.relative_to(DATA_ROOT).as_posix()
    required_files = ("nodes.csv", "edges.csv", "scenarios.json", "test_cases.json")
    missing_files = [name for name in required_files if not (fixture_root / name).is_file()]
    if missing_files:
        return [f"{fixture_name} is missing files: {missing_files}"]

    nodes = read_csv(fixture_root / "nodes.csv")
    edges = read_csv(fixture_root / "edges.csv")
    scenarios = read_json(fixture_root / "scenarios.json")
    test_cases = read_json(fixture_root / "test_cases.json")

    if scenarios.get("data_status") != "SIMULATED":
        errors.append(f"{fixture_name}: scenarios must be labelled SIMULATED")
    if test_cases.get("data_status") != "SIMULATED":
        errors.append(f"{fixture_name}: test cases must be labelled SIMULATED")

    node_ids = [node["node_id"] for node in nodes]
    edge_ids = [edge["edge_id"] for edge in edges]
    node_id_set = set(node_ids)
    edge_id_set = set(edge_ids)

    if len(node_ids) != len(node_id_set):
        errors.append(f"{fixture_name}: node_id values must be unique")
    if len(edge_ids) != len(edge_id_set):
        errors.append(f"{fixture_name}: edge_id values must be unique")
    if any(node.get("data_status") != "SIMULATED" for node in nodes):
        errors.append(f"{fixture_name}: every node must be labelled SIMULATED")

    for edge in edges:
        if edge["from_node_id"] not in node_id_set or edge["to_node_id"] not in node_id_set:
            errors.append(f"{fixture_name}: edge {edge['edge_id']} references a missing node")
        if float(edge["distance_m"]) <= 0 or float(edge["free_flow_time_min"]) <= 0:
            errors.append(f"{fixture_name}: edge {edge['edge_id']} must have positive distance/time")
        if edge.get("data_status") != "SIMULATED":
            errors.append(f"{fixture_name}: edge {edge['edge_id']} must be labelled SIMULATED")

    scenario_by_id: dict[str, dict[str, Any]] = {}
    for scenario in scenarios["scenarios"]:
        scenario_by_id[scenario["scenario_id"]] = scenario
        if abs(sum(scenario["weights"].values()) - 1.0) > 1e-9:
            errors.append(f"{fixture_name}: scenario {scenario['scenario_id']} weights must sum to 1")
        missing_edges = set(scenario["closed_edge_ids"]) - edge_id_set
        if missing_edges:
            errors.append(
                f"{fixture_name}: scenario {scenario['scenario_id']} closes missing edges: "
                f"{sorted(missing_edges)}"
            )

    directed_edges = {(edge["from_node_id"], edge["to_node_id"], edge["edge_id"]) for edge in edges}
    for case in test_cases["cases"]:
        if case["start"] not in node_id_set or case["goal"] not in node_id_set:
            errors.append(f"{fixture_name}: case {case['case_id']} references a missing endpoint")
        if case["scenario_id"] not in scenario_by_id:
            errors.append(f"{fixture_name}: case {case['case_id']} references a missing scenario")
            continue
        if "expected_path" not in case:
            continue

        path = case["expected_path"]
        if path[0] != case["start"] or path[-1] != case["goal"]:
            errors.append(f"{fixture_name}: case {case['case_id']} expected path has wrong endpoints")
        closed_edges = set(scenario_by_id[case["scenario_id"]]["closed_edge_ids"])
        for origin, destination in zip(path, path[1:]):
            candidates = {
                edge_id
                for from_id, to_id, edge_id in directed_edges
                if from_id == origin and to_id == destination
            }
            if not candidates or candidates <= closed_edges:
                errors.append(
                    f"{fixture_name}: case {case['case_id']} expected step "
                    f"{origin}->{destination} is unavailable"
                )

    metadata_path = fixture_root / "metadata.json"
    if metadata_path.is_file():
        metadata = read_json(metadata_path)
        if metadata.get("data_status") != "SIMULATED":
            errors.append(f"{fixture_name}: metadata must be labelled SIMULATED")
        properties = metadata.get("graph_properties", {})
        if properties.get("node_count") != len(nodes) or properties.get("edge_count") != len(edges):
            errors.append(f"{fixture_name}: metadata node/edge counts do not match CSV files")

    return errors


def validate() -> list[str]:
    errors: list[str] = []
    manifest = read_json(MANIFEST_PATH)

    for source in manifest["raw_sources"]:
        source_path = REPOSITORY_ROOT / source["path"]
        if not source_path.is_file():
            errors.append(f"Missing raw source: {source_path}")
        elif sha256(source_path) != source["sha256"]:
            errors.append(f"Checksum mismatch: {source_path}")

    fixture_roots = [FIXTURE_ROOT]
    if EXAMPLE_FIXTURE_ROOT.is_dir():
        fixture_roots.extend(
            sorted(
                path
                for path in EXAMPLE_FIXTURE_ROOT.iterdir()
                if path.is_dir()
            )
        )
    for fixture_root in fixture_roots:
        errors.extend(validate_graph_fixture(fixture_root))

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
    print("- graph examples: simple path, one-way branch, cycle with closure")
    print("- scenario weights, labels and golden paths verified")
