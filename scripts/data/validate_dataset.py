"""Validate provenance and deterministic toy data without third-party packages."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = REPOSITORY_ROOT / "data"
MANIFEST_PATH = DATA_ROOT / "registry" / "dataset_manifest.json"
FIXTURE_ROOT = DATA_ROOT / "fixtures" / "toy_graph_v0.1"
EXAMPLE_FIXTURE_ROOT = DATA_ROOT / "fixtures" / "graph_examples_v0.1"
CAPACITY_PROCESSED_ROOT = DATA_ROOT / "processed" / "thu_duc_core_capacity_v0.1.0"
LANDMARK_PROCESSED_ROOT = DATA_ROOT / "processed" / "thu_duc_landmarks_v1.0.0"
LANDMARK_V101_PROCESSED_ROOT = DATA_ROOT / "processed" / "thu_duc_landmarks_v1.0.1"
LANDMARK_V102_PROCESSED_ROOT = DATA_ROOT / "processed" / "thu_duc_landmarks_v1.0.2"
LANDMARK_V103_PROCESSED_ROOT = DATA_ROOT / "processed" / "thu_duc_landmarks_v1.0.3"
LANDMARK_V104_PROCESSED_ROOT = DATA_ROOT / "processed" / "thu_duc_landmarks_v1.0.4"
OSM_THU_DUC_PROCESSED_ROOT = DATA_ROOT / "processed" / "osm_thu_duc_v1.0.0"
THU_DUC_BOUNDARY_PATH = (
    DATA_ROOT / "raw" / "thu_duc_boundary_v1.0.0" / "osm_relation_19407794.geojson"
)


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


def _is_strongly_connected(node_ids: set[str], edges: list[dict[str, str]]) -> bool:
    if not node_ids:
        return False
    forward: dict[str, list[str]] = defaultdict(list)
    reverse: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        forward[edge["from_node_id"]].append(edge["to_node_id"])
        reverse[edge["to_node_id"]].append(edge["from_node_id"])

    def reachable(adjacency: dict[str, list[str]]) -> set[str]:
        seen: set[str] = set()
        stack = [min(node_ids)]
        while stack:
            node_id = stack.pop()
            if node_id in seen:
                continue
            seen.add(node_id)
            stack.extend(adjacency[node_id])
        return seen

    return reachable(forward) == node_ids and reachable(reverse) == node_ids


def validate_thu_duc_boundary(path: Path) -> list[str]:
    errors: list[str] = []
    payload = read_json(path)
    if payload.get("source_id") != "OSM-THU-DUC-BOUNDARY-2026-08-09":
        errors.append("Thu Duc boundary source_id is missing or unexpected")
    features = payload.get("features", [])
    if len(features) != 1:
        return errors + ["Thu Duc boundary must contain exactly one frozen feature"]
    feature = features[0]
    properties = feature.get("properties", {})
    geometry = feature.get("geometry", {})
    if properties.get("osm_id") != 19407794:
        errors.append("Thu Duc boundary must identify OSM relation 19407794")
    if properties.get("boundary_status") != "HISTORIC_OSM_RELATION":
        errors.append("Thu Duc boundary must disclose its historic OSM status")
    if geometry.get("type") not in {"Polygon", "MultiPolygon"}:
        errors.append("Thu Duc boundary geometry must be Polygon or MultiPolygon")

    coordinates: list[tuple[float, float]] = []

    def collect(value: Any) -> None:
        if (
            isinstance(value, list)
            and len(value) >= 2
            and all(isinstance(item, (int, float)) for item in value[:2])
        ):
            coordinates.append((float(value[0]), float(value[1])))
            return
        if isinstance(value, list):
            for child in value:
                collect(child)

    collect(geometry.get("coordinates", []))
    if len(coordinates) < 4:
        errors.append("Thu Duc boundary polygon has too few coordinates")
    else:
        west = min(item[0] for item in coordinates)
        east = max(item[0] for item in coordinates)
        south = min(item[1] for item in coordinates)
        north = max(item[1] for item in coordinates)
        if not (west < 106.70 and east > 106.88 and south < 10.75 and north > 10.89):
            errors.append("Thu Duc boundary extent does not cover the frozen study area")
    return errors


def validate_processed_dataset(dataset_root: Path) -> list[str]:
    errors: list[str] = []
    dataset_name = dataset_root.relative_to(DATA_ROOT).as_posix()
    required_files = {
        "nodes.csv", "edges.csv", "scenarios.json", "delivery_points.csv",
        "flood_hotspots.csv", "traffic_profiles.csv", "mapping_review.csv",
        "metadata.json", "validation_report.json", "test_cases.json",
        "checksums.sha256",
    }
    missing = sorted(name for name in required_files if not (dataset_root / name).is_file())
    if missing:
        return [f"{dataset_name} is missing files: {missing}"]

    declared_checksums: dict[str, str] = {}
    for line in (dataset_root / "checksums.sha256").read_text(encoding="utf-8").splitlines():
        checksum, filename = line.split(maxsplit=1)
        declared_checksums[filename.strip()] = checksum.upper()
    for filename in required_files - {"checksums.sha256"}:
        if declared_checksums.get(filename) != sha256(dataset_root / filename):
            errors.append(f"{dataset_name}: checksum mismatch for {filename}")

    nodes = read_csv(dataset_root / "nodes.csv")
    edges = read_csv(dataset_root / "edges.csv")
    scenarios = read_json(dataset_root / "scenarios.json")
    metadata = read_json(dataset_root / "metadata.json")
    deliveries = read_csv(dataset_root / "delivery_points.csv")
    hotspots = read_csv(dataset_root / "flood_hotspots.csv")
    reviews = read_csv(dataset_root / "mapping_review.csv")
    test_cases = read_json(dataset_root / "test_cases.json")

    node_ids = [row["node_id"] for row in nodes]
    edge_ids = [row["edge_id"] for row in edges]
    node_id_set, edge_id_set = set(node_ids), set(edge_ids)
    if len(node_ids) != len(node_id_set) or len(edge_ids) != len(edge_id_set):
        errors.append(f"{dataset_name}: node and edge IDs must be unique")

    for node in nodes:
        latitude, longitude = float(node["latitude"]), float(node["longitude"])
        if not (10.845 <= latitude <= 10.853 and 106.751 <= longitude <= 106.759):
            errors.append(f"{dataset_name}: node {node['node_id']} falls outside the frozen bbox")
        if node.get("data_status") != "SOURCE_BACKED":
            errors.append(f"{dataset_name}: node {node['node_id']} needs SOURCE_BACKED status")

    allowed_statuses = {"SOURCE_BACKED", "DERIVED", "ASSUMPTION", "MIXED"}
    edge_by_id = {row["edge_id"]: row for row in edges}
    for edge in edges:
        if edge["from_node_id"] not in node_id_set or edge["to_node_id"] not in node_id_set:
            errors.append(f"{dataset_name}: edge {edge['edge_id']} has an invalid FK")
        values = [float(edge["distance_m"]), float(edge["free_flow_time_min"])]
        if not all(math.isfinite(value) and value > 0 for value in values):
            errors.append(f"{dataset_name}: edge {edge['edge_id']} distance/time must be finite and positive")
        if edge.get("data_status") not in allowed_statuses:
            errors.append(f"{dataset_name}: edge {edge['edge_id']} has invalid data_status")
        if edge.get("flood_observation_status") == "NO_RECORD_IN_SELECTED_SOURCES" and edge.get("flood_risk_0_1") != "0":
            errors.append(f"{dataset_name}: no-record edge {edge['edge_id']} must use risk 0")
    if not _is_strongly_connected(node_id_set, edges):
        errors.append(f"{dataset_name}: directed graph must be strongly connected")

    expected_scenarios = {
        "HISTORICAL_OFFPEAK", "HISTORICAL_PM_PEAK", "RAIN_FLOOD_AWARE_2025_2026"
    }
    scenario_rows = scenarios.get("scenarios", [])
    if {row.get("scenario_id") for row in scenario_rows} != expected_scenarios:
        errors.append(f"{dataset_name}: required scenario set does not match")
    for scenario in scenario_rows:
        if abs(sum(float(value) for value in scenario.get("weights", {}).values()) - 1.0) > 1e-9:
            errors.append(f"{dataset_name}: scenario {scenario.get('scenario_id')} weights must sum to 1")
        if scenario.get("closed_edge_ids"):
            errors.append(f"{dataset_name}: source-backed release must not auto-close roads")
        for edge_id, override in scenario.get("edge_overrides", {}).items():
            if edge_id not in edge_id_set:
                errors.append(f"{dataset_name}: override references unknown edge {edge_id}")
            for key in ("traffic_multiplier", "congestion_level_1_5", "flood_risk_0_1"):
                if key in override and not math.isfinite(float(override[key])):
                    errors.append(f"{dataset_name}: {edge_id}.{key} must be finite")
            if "traffic_multiplier" in override and float(override["traffic_multiplier"]) <= 0:
                errors.append(f"{dataset_name}: {edge_id} has non-positive traffic multiplier")

    selected_osm_pois = [
        point for point in deliveries
        if point["selected_for_demo"].casefold() == "true" and point["osm_id"]
    ]
    if len(selected_osm_pois) != 6:
        errors.append(f"{dataset_name}: exactly six source-backed OSM POIs are required")
    for point in deliveries:
        if point["snap_node_id"] not in node_id_set or float(point["snap_distance_m"]) > 100:
            errors.append(f"{dataset_name}: delivery point {point['point_id']} failed 100 m snapping QC")
        if point["location_data_status"] != "SOURCE_BACKED" or point["order_data_status"] != "ASSUMPTION":
            errors.append(f"{dataset_name}: delivery point {point['point_id']} status split is invalid")

    hotspot_ids = {row["record_id"] for row in hotspots}
    for review in reviews:
        if review["record_id"] not in hotspot_ids:
            errors.append(f"{dataset_name}: mapping review has no hotspot source row")
        mapped = [item for item in review["mapped_edge_ids"].split(";") if item]
        if review["mapping_status"] == "OUT_OF_GRAPH" and mapped:
            errors.append(f"{dataset_name}: OUT_OF_GRAPH review must not map an edge")
        if review["mapping_status"] != "OUT_OF_GRAPH" and any(item not in edge_id_set for item in mapped):
            errors.append(f"{dataset_name}: mapping review references an unknown edge")
        if review["review_status"] == "VERIFIED" and (
            review["reviewer_1_status"] != "COMPLETED"
            or review["reviewer_2_status"] != "COMPLETED"
            or not review["reviewer_1"]
            or not review["reviewer_2"]
        ):
            errors.append(f"{dataset_name}: VERIFIED mapping requires two signed reviews")
    if any(not row.get("source_url") for row in hotspots):
        errors.append(f"{dataset_name}: every hotspot needs a source URL")

    properties = metadata.get("graph_properties", {})
    if metadata.get("data_status") != "MIXED" or metadata.get("real_time") is not False:
        errors.append(f"{dataset_name}: metadata must declare MIXED and real_time=false")
    if properties.get("node_count") != 90 or properties.get("edge_count") != 155:
        errors.append(f"{dataset_name}: metadata graph counts do not match the frozen release")
    if metadata.get("routing_dataset_status") == "ACADEMIC_DEMO_READY" and any(
        row["review_status"] != "VERIFIED" for row in reviews
    ):
        errors.append(f"{dataset_name}: cannot be ACADEMIC_DEMO_READY before all mappings are verified")

    cases = test_cases.get("cases", [])
    if not cases:
        errors.append(f"{dataset_name}: golden route-change case is required")
    for case in cases:
        baseline = case.get("expected_baseline_edge_ids", [])
        comparison = case.get("expected_comparison_edge_ids", [])
        if not baseline or not comparison or baseline == comparison:
            errors.append(f"{dataset_name}: golden case must contain two different non-empty routes")
        for path, route_edges in (
            (case.get("expected_baseline_path", []), baseline),
            (case.get("expected_comparison_path", []), comparison),
        ):
            if len(path) != len(route_edges) + 1:
                errors.append(f"{dataset_name}: golden path/edge lengths do not align")
                continue
            for origin, destination, edge_id in zip(path, path[1:], route_edges):
                edge = edge_by_id.get(edge_id)
                if not edge or edge["from_node_id"] != origin or edge["to_node_id"] != destination:
                    errors.append(f"{dataset_name}: golden case edge {edge_id} does not match path")
    return errors


def validate_capacity_dataset(dataset_root: Path) -> list[str]:
    errors: list[str] = []
    dataset_name = dataset_root.relative_to(DATA_ROOT).as_posix()
    required_files = {
        "nodes.csv", "edges.csv", "scenarios.json", "metadata.json",
        "README.md", "checksums.sha256",
    }
    missing = sorted(name for name in required_files if not (dataset_root / name).is_file())
    if missing:
        return [f"{dataset_name} is missing files: {missing}"]

    declared_checksums: dict[str, str] = {}
    for line in (dataset_root / "checksums.sha256").read_text(encoding="utf-8").splitlines():
        checksum, filename = line.split(maxsplit=1)
        declared_checksums[filename.strip()] = checksum.upper()
    for filename in required_files - {"checksums.sha256"}:
        if declared_checksums.get(filename) != sha256(dataset_root / filename):
            errors.append(f"{dataset_name}: checksum mismatch for {filename}")

    nodes = read_csv(dataset_root / "nodes.csv")
    edges = read_csv(dataset_root / "edges.csv")
    scenarios = read_json(dataset_root / "scenarios.json")
    metadata = read_json(dataset_root / "metadata.json")
    if len(nodes) != 3229 or len(edges) != 5057:
        errors.append(f"{dataset_name}: expected 3229 nodes and 5057 directed edges")

    node_ids = [row["node_id"] for row in nodes]
    edge_ids = [row["edge_id"] for row in edges]
    node_id_set = set(node_ids)
    if len(node_ids) != len(node_id_set) or len(edge_ids) != len(set(edge_ids)):
        errors.append(f"{dataset_name}: node and edge IDs must be unique")
    for node in nodes:
        latitude, longitude = float(node["latitude"]), float(node["longitude"])
        if not (10.82 <= latitude <= 10.88 and 106.72 <= longitude <= 106.79):
            errors.append(f"{dataset_name}: node {node['node_id']} falls outside capacity bbox")
        if node.get("data_status") != "SOURCE_BACKED":
            errors.append(f"{dataset_name}: node {node['node_id']} needs SOURCE_BACKED status")
    for edge in edges:
        if edge["from_node_id"] not in node_id_set or edge["to_node_id"] not in node_id_set:
            errors.append(f"{dataset_name}: edge {edge['edge_id']} has an invalid FK")
        values = [float(edge["distance_m"]), float(edge["free_flow_time_min"])]
        if not all(math.isfinite(value) and value > 0 for value in values):
            errors.append(f"{dataset_name}: edge {edge['edge_id']} distance/time must be positive")
        if edge.get("data_status") != "DERIVED":
            errors.append(f"{dataset_name}: edge {edge['edge_id']} must be DERIVED")
    if not _is_strongly_connected(node_id_set, edges):
        errors.append(f"{dataset_name}: directed capacity graph must be strongly connected")

    scenario_rows = scenarios.get("scenarios", [])
    if [row.get("scenario_id") for row in scenario_rows] != ["CAPACITY_BASELINE"]:
        errors.append(f"{dataset_name}: CAPACITY_BASELINE scenario is required")
    for scenario in scenario_rows:
        if abs(sum(float(value) for value in scenario.get("weights", {}).values()) - 1.0) > 1e-9:
            errors.append(f"{dataset_name}: scenario weights must sum to 1")
        if scenario.get("data_status") != "ASSUMPTION":
            errors.append(f"{dataset_name}: scenario must be labelled ASSUMPTION")

    properties = metadata.get("graph_properties", {})
    if metadata.get("routing_dataset_status") != "CAPACITY_BENCHMARK_ONLY":
        errors.append(f"{dataset_name}: metadata status must be CAPACITY_BENCHMARK_ONLY")
    if metadata.get("data_status") != "MIXED" or metadata.get("real_time") is not False:
        errors.append(f"{dataset_name}: metadata must declare MIXED and real_time=false")
    if properties.get("node_count") != len(nodes) or properties.get("edge_count") != len(edges):
        errors.append(f"{dataset_name}: metadata graph counts do not match CSV files")
    return errors


def validate_landmark_dataset(dataset_root: Path) -> list[str]:
    errors: list[str] = []
    dataset_name = dataset_root.relative_to(DATA_ROOT).as_posix()
    required_files = {
        "nodes.csv", "edges.csv", "landmarks.csv", "scenarios.json", "metadata.json",
        "validation_report.json", "README.md", "checksums.sha256",
    }
    missing = sorted(name for name in required_files if not (dataset_root / name).is_file())
    if missing:
        return [f"{dataset_name} is missing files: {missing}"]

    declared: dict[str, str] = {}
    for line in (dataset_root / "checksums.sha256").read_text(encoding="utf-8").splitlines():
        checksum, filename = line.split(maxsplit=1)
        declared[filename.strip()] = checksum.upper()
    for filename in required_files - {"checksums.sha256"}:
        if declared.get(filename) != sha256(dataset_root / filename):
            errors.append(f"{dataset_name}: checksum mismatch for {filename}")

    nodes = read_csv(dataset_root / "nodes.csv")
    edges = read_csv(dataset_root / "edges.csv")
    landmarks = read_csv(dataset_root / "landmarks.csv")
    scenarios = read_json(dataset_root / "scenarios.json")
    metadata = read_json(dataset_root / "metadata.json")
    expected_edge_count = 283 if dataset_root in {
        LANDMARK_V102_PROCESSED_ROOT,
        LANDMARK_V103_PROCESSED_ROOT,
        LANDMARK_V104_PROCESSED_ROOT,
    } else 178
    if len(nodes) != 65 or len(edges) != expected_edge_count or len(landmarks) != 65:
        errors.append(f"{dataset_name}: expected 65 landmarks and {expected_edge_count} directed edges")
    node_ids = {row["node_id"] for row in nodes}
    if len(node_ids) != len(nodes) or len({row["edge_id"] for row in edges}) != len(edges):
        errors.append(f"{dataset_name}: node and edge IDs must be unique")
    allowed_categories = {
        "EDUCATION", "HOSPITAL", "MARKET", "CIVIC_TRANSPORT", "MALL",
        "RAIL_STATION", "STADIUM", "CULTURE_THEME",
    }
    node_coordinates: dict[str, tuple[float, float]] = {}
    for node in nodes:
        longitude, latitude = float(node["longitude"]), float(node["latitude"])
        node_coordinates[node["node_id"]] = (longitude, latitude)
        if node.get("selectable", "").casefold() != "true":
            errors.append(f"{dataset_name}: {node['node_id']} must be selectable")
        if node.get("node_type") != "SELECTABLE_LANDMARK":
            errors.append(f"{dataset_name}: {node['node_id']} must be a landmark node")
        if node.get("place_category") not in allowed_categories:
            errors.append(f"{dataset_name}: {node['node_id']} has invalid category")
        if not node.get("name") or node.get("data_status") != "SOURCE_BACKED":
            errors.append(f"{dataset_name}: {node['node_id']} needs a source-backed name")
        if float(node["snap_distance_m"]) > 1_500:
            errors.append(f"{dataset_name}: {node['node_id']} exceeds snap threshold")

    for edge in edges:
        origin, destination = edge["from_node_id"], edge["to_node_id"]
        if origin not in node_ids or destination not in node_ids:
            errors.append(f"{dataset_name}: {edge['edge_id']} has invalid FK")
            continue
        if float(edge["distance_m"]) <= 0 or float(edge["free_flow_time_min"]) <= 0:
            errors.append(f"{dataset_name}: {edge['edge_id']} has invalid cost")
        if edge.get("data_status") != "DERIVED":
            errors.append(f"{dataset_name}: {edge['edge_id']} must be DERIVED")
        try:
            coordinates = json.loads(edge["path_coordinates_json"])
        except json.JSONDecodeError:
            errors.append(f"{dataset_name}: {edge['edge_id']} has invalid path geometry")
            continue
        if len(coordinates) < 2:
            errors.append(f"{dataset_name}: {edge['edge_id']} path is too short")
            continue
        for actual, expected in (
            (coordinates[0], node_coordinates[origin]),
            (coordinates[-1], node_coordinates[destination]),
        ):
            if abs(float(actual[0]) - expected[0]) > 1e-7 or abs(float(actual[1]) - expected[1]) > 1e-7:
                errors.append(f"{dataset_name}: {edge['edge_id']} geometry misses endpoint")
                break
    if not _is_strongly_connected(node_ids, edges):
        errors.append(f"{dataset_name}: landmark graph must be strongly connected")

    scenario_rows = scenarios.get("scenarios", [])
    scenario_ids = [row.get("scenario_id") for row in scenario_rows]
    expected_scenario_ids = ["LANDMARK_HISTORICAL_BASELINE"]
    if dataset_root in {LANDMARK_V101_PROCESSED_ROOT, LANDMARK_V102_PROCESSED_ROOT}:
        expected_scenario_ids.append("LANDMARK_HARD_CLOSURE_DETOUR")
    if dataset_root in {LANDMARK_V103_PROCESSED_ROOT, LANDMARK_V104_PROCESSED_ROOT}:
        expected_scenario_ids = [
            "LANDMARK_NORMAL",
            "LANDMARK_FLOOD",
            "LANDMARK_CONGESTION",
            "LANDMARK_HARD_CLOSURE_DETOUR",
        ]
    if scenario_ids != expected_scenario_ids:
        errors.append(f"{dataset_name}: expected scenarios are {expected_scenario_ids}")
    if dataset_root in {
        LANDMARK_V101_PROCESSED_ROOT,
        LANDMARK_V102_PROCESSED_ROOT,
        LANDMARK_V103_PROCESSED_ROOT,
        LANDMARK_V104_PROCESSED_ROOT,
    }:
        closure = next(
            (row for row in scenario_rows if row.get("scenario_id") == "LANDMARK_HARD_CLOSURE_DETOUR"),
            None,
        )
        if not closure or closure.get("data_status") != "ASSUMPTION":
            errors.append(f"{dataset_name}: hard closure scenario must be labelled ASSUMPTION")
        elif closure.get("closed_edge_ids") != ["LM_EDGE_0001"]:
            errors.append(f"{dataset_name}: hard closure scenario must close LM_EDGE_0001")
    if dataset_root in {LANDMARK_V103_PROCESSED_ROOT, LANDMARK_V104_PROCESSED_ROOT}:
        expected_override_count = 57 if dataset_root == LANDMARK_V104_PROCESSED_ROOT else 3
        for scenario_id, field_name in (
            ("LANDMARK_FLOOD", "flood_risk"),
            ("LANDMARK_CONGESTION", "traffic_penalty_min"),
        ):
            scenario = next(row for row in scenario_rows if row.get("scenario_id") == scenario_id)
            overrides = scenario.get("edge_overrides", {})
            if len(overrides) != expected_override_count or any(field_name not in override for override in overrides.values()):
                errors.append(f"{dataset_name}: {scenario_id} must define {expected_override_count} {field_name} overrides")
    properties = metadata.get("graph_properties", {})
    if properties.get("selectable_node_count") != len(nodes):
        errors.append(f"{dataset_name}: selectable count does not match nodes")
    if properties.get("hidden_source_road_node_count", 0) <= len(nodes):
        errors.append(f"{dataset_name}: hidden source road graph disclosure is invalid")
    return errors


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


def validate_osm_thu_duc_dataset(dataset_root: Path) -> list[str]:
    errors: list[str] = []
    dataset_name = dataset_root.relative_to(DATA_ROOT).as_posix()
    required_files = {
        "nodes.csv", "edges.csv", "scenarios.json", "delivery_points.csv",
        "metadata.json", "validation_report.json", "checksums.sha256",
    }
    missing = sorted(name for name in required_files if not (dataset_root / name).is_file())
    if missing:
        return [f"{dataset_name} is missing files: {missing}"]

    declared_checksums: dict[str, str] = {}
    for line in (dataset_root / "checksums.sha256").read_text(encoding="utf-8").splitlines():
        checksum, filename = line.split(maxsplit=1)
        declared_checksums[filename.strip()] = checksum.upper()
    for filename in declared_checksums.keys():
        if (dataset_root / filename).is_file():
            if declared_checksums.get(filename) != sha256(dataset_root / filename):
                errors.append(f"{dataset_name}: checksum mismatch for {filename}")

    nodes = read_csv(dataset_root / "nodes.csv")
    edges = read_csv(dataset_root / "edges.csv")
    metadata = read_json(dataset_root / "metadata.json")

    if metadata.get("node_count") != len(nodes) or metadata.get("edge_count") != len(edges):
        errors.append(f"{dataset_name}: metadata graph counts do not match CSV files")
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

    if THU_DUC_BOUNDARY_PATH.is_file():
        errors.extend(validate_thu_duc_boundary(THU_DUC_BOUNDARY_PATH))

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

    for processed in manifest.get("processed_datasets", []):
        processed_root = REPOSITORY_ROOT / processed["path"]
        if processed_root == CAPACITY_PROCESSED_ROOT:
            errors.extend(validate_capacity_dataset(processed_root))
        elif processed_root in {
            LANDMARK_PROCESSED_ROOT,
            LANDMARK_V101_PROCESSED_ROOT,
            LANDMARK_V102_PROCESSED_ROOT,
            LANDMARK_V103_PROCESSED_ROOT,
            LANDMARK_V104_PROCESSED_ROOT,
        }:
            errors.extend(validate_landmark_dataset(processed_root))
        elif processed_root == OSM_THU_DUC_PROCESSED_ROOT:
            errors.extend(validate_osm_thu_duc_dataset(processed_root))
        else:
            errors.append(f"Unexpected processed dataset path: {processed_root}")

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
    print("- historic Thu Duc boundary geometry and disclosure verified")
    print("- toy graph: 6 nodes, 14 directed edges")
    print("- graph examples: simple path, one-way branch, cycle with closure")
    print("- scenario weights, labels and golden paths verified")
    print("- Thu Duc capacity graph: 3229 nodes, 5057 directed edges, strongly connected")
    print("- Thu Duc landmarks: 65 selectable POIs, 178 derived road-path edges")
    print("- landmark graph provenance and deterministic search cases verified")
    print("- active map release: 65 selectable landmarks; no 90-node processed map")
