"""Build a large, source-backed UTraffic graph for capacity testing.

This builder reads the immutable HCMC UTraffic ZIP already registered by the
project. It selects the largest strongly connected component inside a wider
Thu Duc core bbox and writes a separate processed dataset. It does not modify
the academic pilot release or any raw input.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
from collections import defaultdict
from io import TextIOWrapper
from pathlib import Path
from typing import Any
from zipfile import ZipFile


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RAW_ZIP = (
    REPOSITORY_ROOT
    / "data/raw/thu_duc_market_v1.0.0/utraffic_hcm_v6.zip"
)
OUTPUT_ROOT = (
    REPOSITORY_ROOT
    / "data/processed/thu_duc_core_capacity_v0.1.0"
)
DATASET_ID = "thu_duc_core_capacity_v0.1.0"
BBOX = {"south": 10.82, "west": 106.72, "north": 10.88, "east": 106.79}
ROAD_TYPES = {"trunk", "primary", "secondary", "tertiary"}
FALLBACK_SPEED_KPH = {
    "trunk": 50.0,
    "primary": 40.0,
    "secondary": 35.0,
    "tertiary": 30.0,
}


def zip_csv(archive: ZipFile, filename: str) -> list[dict[str, str]]:
    with archive.open(filename) as binary_file:
        with TextIOWrapper(binary_file, encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file))


def inside(longitude: float, latitude: float) -> bool:
    return (
        BBOX["west"] <= longitude <= BBOX["east"]
        and BBOX["south"] <= latitude <= BBOX["north"]
    )


def haversine_m(
    from_longitude: float,
    from_latitude: float,
    to_longitude: float,
    to_latitude: float,
) -> float:
    radians = math.pi / 180
    delta_latitude = (to_latitude - from_latitude) * radians
    delta_longitude = (to_longitude - from_longitude) * radians
    value = (
        math.sin(delta_latitude / 2) ** 2
        + math.cos(from_latitude * radians)
        * math.cos(to_latitude * radians)
        * math.sin(delta_longitude / 2) ** 2
    )
    return 2 * 6_371_000 * math.asin(math.sqrt(value))


def largest_strong_component(
    node_ids: set[str],
    segments: list[dict[str, str]],
) -> set[str]:
    adjacency: dict[str, list[str]] = defaultdict(list)
    reverse: dict[str, list[str]] = defaultdict(list)
    for segment in segments:
        origin, destination = segment["s_node_id"], segment["e_node_id"]
        adjacency[origin].append(destination)
        reverse[destination].append(origin)
    for values in (*adjacency.values(), *reverse.values()):
        values.sort(key=int)

    seen: set[str] = set()
    order: list[str] = []
    for root in sorted(node_ids, key=int):
        if root in seen:
            continue
        seen.add(root)
        stack: list[tuple[str, int]] = [(root, 0)]
        while stack:
            node_id, index = stack[-1]
            neighbors = adjacency[node_id]
            if index < len(neighbors):
                neighbor = neighbors[index]
                stack[-1] = (node_id, index + 1)
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append((neighbor, 0))
            else:
                order.append(node_id)
                stack.pop()

    seen.clear()
    components: list[set[str]] = []
    for root in reversed(order):
        if root in seen:
            continue
        component: set[str] = set()
        stack = [root]
        seen.add(root)
        while stack:
            node_id = stack.pop()
            component.add(node_id)
            for neighbor in reverse[node_id]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        components.append(component)
    return min(components, key=lambda item: (-len(item), min(map(int, item))))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def build() -> tuple[int, int]:
    with ZipFile(RAW_ZIP) as archive:
        raw_nodes = zip_csv(archive, "nodes.csv")
        raw_segments = zip_csv(archive, "segments.csv")

    nodes_by_id = {
        row["_id"]: (float(row["long"]), float(row["lat"]))
        for row in raw_nodes
    }
    candidate_segments = [
        row
        for row in raw_segments
        if row["street_type"] in ROAD_TYPES
        and row["s_node_id"] in nodes_by_id
        and row["e_node_id"] in nodes_by_id
        and inside(*nodes_by_id[row["s_node_id"]])
        and inside(*nodes_by_id[row["e_node_id"]])
    ]
    candidate_node_ids = {
        node_id
        for segment in candidate_segments
        for node_id in (segment["s_node_id"], segment["e_node_id"])
    }
    selected_node_ids = largest_strong_component(candidate_node_ids, candidate_segments)
    selected_segments = sorted(
        (
            segment
            for segment in candidate_segments
            if segment["s_node_id"] in selected_node_ids
            and segment["e_node_id"] in selected_node_ids
        ),
        key=lambda segment: int(segment["_id"]),
    )

    node_rows = [
        {
            "node_id": f"UTR_NODE_{node_id}",
            "name": f"UTraffic node {node_id}",
            "node_type": "INTERSECTION_OR_GEOMETRY",
            "latitude": f"{nodes_by_id[node_id][1]:.7f}",
            "longitude": f"{nodes_by_id[node_id][0]:.7f}",
            "source_id": "UTRAFFIC-HCM-V6",
            "validation_status": "SOURCE_COORDINATE",
            "data_status": "SOURCE_BACKED",
        }
        for node_id in sorted(selected_node_ids, key=int)
    ]
    edge_rows: list[dict[str, Any]] = []
    for segment in selected_segments:
        distance_m = float(segment["length"])
        distance_derivation = "SOURCE_LENGTH"
        if distance_m <= 0:
            origin = nodes_by_id[segment["s_node_id"]]
            destination = nodes_by_id[segment["e_node_id"]]
            distance_m = haversine_m(*origin, *destination)
            distance_derivation = "DERIVED_HAVERSINE_FALLBACK"
        source_speed = float(segment.get("max_velocity") or 0)
        speed_kph = source_speed if source_speed > 0 else FALLBACK_SPEED_KPH[segment["street_type"]]
        free_flow_time_min = distance_m / (speed_kph * 1000 / 60)
        if not math.isfinite(free_flow_time_min) or free_flow_time_min <= 0:
            raise ValueError(f"Invalid travel time for segment {segment['_id']}")
        edge_rows.append({
            "edge_id": f"UTR_EDGE_{segment['_id']}",
            "from_node_id": f"UTR_NODE_{segment['s_node_id']}",
            "to_node_id": f"UTR_NODE_{segment['e_node_id']}",
            "road_name": segment.get("street_name") or "",
            "road_type": segment["street_type"],
            "direction": "SOURCE_DIRECTED",
            "distance_m": f"{distance_m:.3f}",
            "distance_derivation": distance_derivation,
            "free_flow_speed_kph": f"{speed_kph:.3f}",
            "free_flow_time_min": f"{free_flow_time_min:.6f}",
            "speed_derivation": "SOURCE_MAX_VELOCITY" if source_speed > 0 else "STREET_TYPE_ASSUMPTION",
            "congestion_level_1_5": "1",
            "flood_risk_0_1": "0",
            "flood_observation_status": "NO_RECORD_IN_SELECTED_SOURCES",
            "source_id": "UTRAFFIC-HCM-V6",
            "source_segment_id": segment["_id"],
            "data_status": "DERIVED",
        })

    processed_root = (REPOSITORY_ROOT / "data/processed").resolve()
    if OUTPUT_ROOT.resolve().parent != processed_root:
        raise ValueError(f"Unsafe output path: {OUTPUT_ROOT}")
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    OUTPUT_ROOT.mkdir(parents=True)
    write_csv(OUTPUT_ROOT / "nodes.csv", list(node_rows[0]), node_rows)
    write_csv(OUTPUT_ROOT / "edges.csv", list(edge_rows[0]), edge_rows)
    write_json(OUTPUT_ROOT / "scenarios.json", {
        "dataset_id": DATASET_ID,
        "data_status": "MIXED",
        "real_time": False,
        "scenarios": [{
            "scenario_id": "CAPACITY_BASELINE",
            "data_status": "ASSUMPTION",
            "traffic_scenario": "No live traffic; source max velocity free-flow baseline",
            "cost_preset": "BALANCED",
            "traffic_multiplier": 1.0,
            "default_congestion_level_1_5": 1,
            "weights": {
                "distance": 0.25,
                "freeflow_time": 0.30,
                "congestion": 0.20,
                "flood_risk": 0.25,
            },
            "closed_edge_ids": [],
            "edge_overrides": {},
        }],
    })
    write_json(OUTPUT_ROOT / "metadata.json", {
        "dataset_id": DATASET_ID,
        "dataset_kind": "capacity_benchmark",
        "data_status": "MIXED",
        "routing_dataset_status": "CAPACITY_BENCHMARK_ONLY",
        "snapshot_date": "2021-04-22",
        "real_time": False,
        "bbox": BBOX,
        "source_ids": ["UTRAFFIC-HCM-V6"],
        "attribution": ["UTraffic/HCMUT historical road network"],
        "graph_properties": {
            "directed": True,
            "strongly_connected": True,
            "node_count": len(node_rows),
            "edge_count": len(edge_rows),
        },
        "limitations": [
            "Capacity benchmark only; not the default academic pilot dataset.",
            "Free-flow time is derived from source max_velocity with street-type fallback.",
            "Flood risk 0 means NO_RECORD in selected sources, not flood-safe.",
            "No real-time traffic, POI order model, or verified flood map matching.",
        ],
    })
    (OUTPUT_ROOT / "README.md").write_text(
        "# Thu Duc core capacity benchmark\n\n"
        "Large strongly connected UTraffic extract for API, search, GeoJSON and MapLibre "
        "load testing. This dataset is `MIXED`/`CAPACITY_BENCHMARK_ONLY`, not a safety or "
        "real-time routing release.\n",
        encoding="utf-8",
    )
    checksum_files = ["nodes.csv", "edges.csv", "scenarios.json", "metadata.json", "README.md"]
    (OUTPUT_ROOT / "checksums.sha256").write_text(
        "".join(f"{sha256(OUTPUT_ROOT / filename)}  {filename}\n" for filename in checksum_files),
        encoding="utf-8",
    )
    return len(node_rows), len(edge_rows)


if __name__ == "__main__":
    node_count, edge_count = build()
    print(f"Built {DATASET_ID}: {node_count} nodes, {edge_count} directed edges")
