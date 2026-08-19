"""Build a compact landmark graph from OSM POIs and UTraffic road paths."""

from __future__ import annotations

import csv
import hashlib
import heapq
import json
import math
import re
import shutil
import unicodedata
from collections import defaultdict
from io import TextIOWrapper
from pathlib import Path
from typing import Any
from zipfile import ZipFile


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
RAW_ZIP = REPOSITORY_ROOT / "data/raw/thu_duc_market_v1.0.0/utraffic_hcm_v6.zip"
POI_SNAPSHOT = (
    REPOSITORY_ROOT
    / "data/raw/thu_duc_landmarks_v1.0.0/osm_major_places_snapshot.json"
)
BOUNDARY_PATH = (
    REPOSITORY_ROOT
    / "data/raw/thu_duc_boundary_v1.0.0/osm_relation_19407794.geojson"
)
OUTPUT_ROOT = REPOSITORY_ROOT / "data/processed/thu_duc_landmarks_v1.0.0"
DATASET_ID = "thu_duc_landmarks_v1.0.0"
ROAD_TYPES = {
    "motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link",
    "secondary", "secondary_link", "tertiary", "tertiary_link", "residential",
    "unclassified",
}
FALLBACK_SPEED_KPH = {
    "motorway": 60.0,
    "motorway_link": 40.0,
    "trunk": 50.0,
    "trunk_link": 35.0,
    "primary": 40.0,
    "primary_link": 30.0,
    "secondary": 35.0,
    "secondary_link": 28.0,
    "tertiary": 30.0,
    "tertiary_link": 25.0,
    "residential": 25.0,
    "unclassified": 25.0,
}
CATEGORY_PRIORITY = (
    "RAIL_STATION", "CIVIC_TRANSPORT", "HOSPITAL", "EDUCATION",
    "MARKET", "MALL", "CULTURE_THEME", "STADIUM",
)
CATEGORY_QUOTA = {
    "RAIL_STATION": 12,
    "CIVIC_TRANSPORT": 10,
    "HOSPITAL": 10,
    "EDUCATION": 18,
    "MARKET": 12,
    "MALL": 10,
    "CULTURE_THEME": 8,
    "STADIUM": 4,
}
MAX_SNAP_DISTANCE_M = 1_500.0


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def zip_csv(archive: ZipFile, filename: str) -> list[dict[str, str]]:
    with archive.open(filename) as binary_file:
        with TextIOWrapper(binary_file, encoding="utf-8-sig", newline="") as file:
            return list(csv.DictReader(file))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def haversine_m(ax: float, ay: float, bx: float, by: float) -> float:
    radians = math.pi / 180
    dy = (by - ay) * radians
    dx = (bx - ax) * radians
    value = (
        math.sin(dy / 2) ** 2
        + math.cos(ay * radians) * math.cos(by * radians) * math.sin(dx / 2) ** 2
    )
    return 2 * 6_371_000 * math.asin(math.sqrt(value))


def point_in_ring(longitude: float, latitude: float, ring: list[list[float]]) -> bool:
    inside = False
    previous = len(ring) - 1
    for index, (x1, y1) in enumerate(ring):
        x2, y2 = ring[previous]
        if ((y1 > latitude) != (y2 > latitude)) and (
            longitude < (x2 - x1) * (latitude - y1) / (y2 - y1) + x1
        ):
            inside = not inside
        previous = index
    return inside


def polygon_parts(boundary: dict[str, Any]) -> list[list[list[list[float]]]]:
    geometry = boundary["features"][0]["geometry"]
    return geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]


def inside_boundary(
    longitude: float,
    latitude: float,
    polygons: list[list[list[list[float]]]],
) -> bool:
    return any(
        point_in_ring(longitude, latitude, polygon[0])
        and not any(point_in_ring(longitude, latitude, hole) for hole in polygon[1:])
        for polygon in polygons
    )


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


def normalized_name(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", ascii_value.casefold()).strip()


def element_position(element: dict[str, Any]) -> tuple[float, float] | None:
    position = element.get("center", element)
    longitude, latitude = position.get("lon"), position.get("lat")
    if not isinstance(longitude, (int, float)) or not isinstance(latitude, (int, float)):
        return None
    return float(longitude), float(latitude)


def landmark_score(name: str, category: str, element_type: str) -> tuple[int, str]:
    normalized = normalized_name(name)
    score = 2 if element_type in {"way", "relation"} else 0
    keywords = {
        "EDUCATION": ("dai hoc", "university", "hoc vien"),
        "HOSPITAL": ("benh vien", "hospital"),
        "MARKET": ("cho dau moi", "cho thu duc", "market"),
        "CIVIC_TRANSPORT": ("ben xe", "uy ban", "ubnd"),
        "MALL": ("mall", "vincom", "thuong mai"),
        "CULTURE_THEME": ("bao tang", "museum", "suoi tien", "vinwonders"),
        "RAIL_STATION": (),
        "STADIUM": ("san van dong", "stadium"),
    }
    score += sum(3 for keyword in keywords[category] if keyword in normalized)
    return score, normalized


def select_landmark_candidates(
    snapshot: dict[str, Any],
    polygons: list[list[list[list[float]]]],
) -> list[dict[str, Any]]:
    candidates_by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for element in snapshot["elements"]:
        position = element_position(element)
        name = str(element.get("tags", {}).get("name") or "").strip()
        if not position or not name or not inside_boundary(*position, polygons):
            continue
        categories = element.get("floodroute_candidate_categories", [])
        category = next((item for item in CATEGORY_PRIORITY if item in categories), None)
        if not category:
            continue
        if element["type"] == "node" and category != "RAIL_STATION":
            continue
        normalized = normalized_name(name)
        if category == "HOSPITAL" and any(
            phrase in normalized for phrase in ("tram y te", "phong kham", "clinic", "nha khoa")
        ):
            continue
        candidate = {
            "element": element,
            "category": category,
            "name": name,
            "longitude": position[0],
            "latitude": position[1],
        }
        candidates_by_category[category].append(candidate)

    selected: list[dict[str, Any]] = []
    used_names: set[str] = set()
    for category in CATEGORY_PRIORITY:
        ranked = sorted(
            candidates_by_category[category],
            key=lambda item: (
                -landmark_score(item["name"], category, item["element"]["type"])[0],
                landmark_score(item["name"], category, item["element"]["type"])[1],
                item["element"]["type"],
                int(item["element"]["id"]),
            ),
        )
        category_count = 0
        for candidate in ranked:
            name_key = normalized_name(candidate["name"])
            if name_key in used_names:
                continue
            selected.append(candidate)
            used_names.add(name_key)
            category_count += 1
            if category_count >= CATEGORY_QUOTA[category]:
                break
    return selected


def segment_metrics(
    segment: dict[str, str],
    nodes_by_id: dict[str, tuple[float, float]],
) -> tuple[float, float]:
    distance = float(segment.get("length") or 0)
    if distance <= 0:
        distance = haversine_m(
            *nodes_by_id[segment["s_node_id"]],
            *nodes_by_id[segment["e_node_id"]],
        )
    source_speed = float(segment.get("max_velocity") or 0)
    speed = source_speed if source_speed > 0 else FALLBACK_SPEED_KPH[segment["street_type"]]
    return distance, distance / (speed * 1000 / 60)


def shortest_paths(
    source: str,
    targets: set[str],
    adjacency: dict[str, list[dict[str, str]]],
    metrics_by_edge: dict[str, tuple[float, float]],
) -> dict[str, tuple[float, float, list[dict[str, str]]]]:
    distance = {source: 0.0}
    travel_time = {source: 0.0}
    previous: dict[str, tuple[str, dict[str, str]]] = {}
    queue: list[tuple[float, str]] = [(0.0, source)]
    remaining = set(targets) - {source}
    while queue and remaining:
        current_distance, node_id = heapq.heappop(queue)
        if current_distance != distance.get(node_id):
            continue
        remaining.discard(node_id)
        for segment in adjacency[node_id]:
            destination = segment["e_node_id"]
            edge_distance, edge_time = metrics_by_edge[segment["_id"]]
            candidate_distance = current_distance + edge_distance
            existing = distance.get(destination)
            if existing is not None:
                if candidate_distance > existing:
                    continue
                if candidate_distance == existing:
                    existing_previous = previous.get(destination)
                    if existing_previous is None or (
                        node_id,
                        int(segment["_id"]),
                    ) >= (existing_previous[0], int(existing_previous[1]["_id"])):
                        continue
            distance[destination] = candidate_distance
            travel_time[destination] = travel_time[node_id] + edge_time
            previous[destination] = (node_id, segment)
            heapq.heappush(queue, (candidate_distance, destination))

    routes: dict[str, tuple[float, float, list[dict[str, str]]]] = {}
    for target in targets:
        if target == source or target not in distance:
            continue
        path: list[dict[str, str]] = []
        cursor = target
        while cursor != source:
            parent, segment = previous[cursor]
            path.append(segment)
            cursor = parent
        path.reverse()
        routes[target] = (distance[target], travel_time[target], path)
    return routes


def build() -> tuple[int, int]:
    boundary = read_json(BOUNDARY_PATH)
    polygons = polygon_parts(boundary)
    snapshot = read_json(POI_SNAPSHOT)
    candidates = select_landmark_candidates(snapshot, polygons)

    with ZipFile(RAW_ZIP) as archive:
        raw_nodes = zip_csv(archive, "nodes.csv")
        raw_segments = zip_csv(archive, "segments.csv")
    nodes_by_id = {
        row["_id"]: (float(row["long"]), float(row["lat"]))
        for row in raw_nodes
    }
    road_segments = [
        row for row in raw_segments
        if row["street_type"] in ROAD_TYPES
        and row["s_node_id"] in nodes_by_id
        and row["e_node_id"] in nodes_by_id
    ]
    road_candidate_ids = {
        node_id
        for segment in road_segments
        for node_id in (segment["s_node_id"], segment["e_node_id"])
    }
    inside_node_ids = {
        node_id for node_id in road_candidate_ids
        if inside_boundary(*nodes_by_id[node_id], polygons)
    }
    inside_segments = [
        row for row in road_segments
        if row["s_node_id"] in inside_node_ids and row["e_node_id"] in inside_node_ids
    ]
    component_ids = largest_strong_component(inside_node_ids, inside_segments)
    component_segments = [
        row for row in inside_segments
        if row["s_node_id"] in component_ids and row["e_node_id"] in component_ids
    ]

    snapped: list[dict[str, Any]] = []
    used_snap_nodes: set[str] = set()
    ordered_road_nodes = sorted(component_ids, key=int)
    for candidate in candidates:
        nearest_id = min(
            ordered_road_nodes,
            key=lambda node_id: (
                haversine_m(
                    candidate["longitude"], candidate["latitude"], *nodes_by_id[node_id]
                ),
                int(node_id),
            ),
        )
        snap_distance = haversine_m(
            candidate["longitude"], candidate["latitude"], *nodes_by_id[nearest_id]
        )
        if snap_distance > MAX_SNAP_DISTANCE_M or nearest_id in used_snap_nodes:
            continue
        used_snap_nodes.add(nearest_id)
        candidate.update({"snap_node_id": nearest_id, "snap_distance_m": snap_distance})
        snapped.append(candidate)
    if len(snapped) < 20:
        raise ValueError(f"Too few landmark nodes after snapping: {len(snapped)}")

    metrics_by_edge = {
        segment["_id"]: segment_metrics(segment, nodes_by_id)
        for segment in component_segments
    }
    adjacency: dict[str, list[dict[str, str]]] = defaultdict(list)
    for segment in component_segments:
        adjacency[segment["s_node_id"]].append(segment)
    for values in adjacency.values():
        values.sort(key=lambda row: (int(row["e_node_id"]), int(row["_id"])))

    snap_ids = {item["snap_node_id"] for item in snapped}
    routes_by_source = {
        source: shortest_paths(source, snap_ids, adjacency, metrics_by_edge)
        for source in sorted(snap_ids, key=int)
    }
    landmark_by_snap = {item["snap_node_id"]: item for item in snapped}

    # Directed edges = bidirectional road-distance MST + two nearest outgoing alternatives.
    root = min(snap_ids, key=lambda item: normalized_name(landmark_by_snap[item]["name"]))
    tree_nodes = {root}
    undirected_pairs: set[tuple[str, str]] = set()
    while tree_nodes != snap_ids:
        candidates_for_tree: list[tuple[float, str, str]] = []
        for origin in tree_nodes:
            for destination in snap_ids - tree_nodes:
                forward = routes_by_source[origin][destination][0]
                reverse = routes_by_source[destination][origin][0]
                candidates_for_tree.append((forward + reverse, origin, destination))
        _, origin, destination = min(candidates_for_tree)
        undirected_pairs.add(tuple(sorted((origin, destination), key=int)))
        tree_nodes.add(destination)

    directed_pairs: set[tuple[str, str]] = set()
    for left, right in undirected_pairs:
        directed_pairs.update({(left, right), (right, left)})
    for origin in snap_ids:
        nearest = sorted(
            (routes_by_source[origin][destination][0], destination)
            for destination in snap_ids if destination != origin
        )[:2]
        directed_pairs.update((origin, destination) for _, destination in nearest)

    node_id_by_snap: dict[str, str] = {}
    node_rows: list[dict[str, Any]] = []
    landmark_rows: list[dict[str, Any]] = []
    for index, item in enumerate(sorted(snapped, key=lambda row: normalized_name(row["name"])), 1):
        node_id = f"LM_{index:03d}"
        node_id_by_snap[item["snap_node_id"]] = node_id
        snap_longitude, snap_latitude = nodes_by_id[item["snap_node_id"]]
        element = item["element"]
        node_rows.append({
            "node_id": node_id,
            "name": item["name"],
            "node_type": "SELECTABLE_LANDMARK",
            "place_category": item["category"],
            "selectable": "true",
            "latitude": f"{item['latitude']:.7f}",
            "longitude": f"{item['longitude']:.7f}",
            "poi_latitude": f"{item['latitude']:.7f}",
            "poi_longitude": f"{item['longitude']:.7f}",
            "snap_latitude": f"{snap_latitude:.7f}",
            "snap_longitude": f"{snap_longitude:.7f}",
            "snap_distance_m": f"{item['snap_distance_m']:.3f}",
            "source_id": "OSM-THU-DUC-MAJOR-PLACES-2026-08-09",
            "source_osm_type": element["type"],
            "source_osm_id": element["id"],
            "source_road_node_id": item["snap_node_id"],
            "data_status": "SOURCE_BACKED",
        })
        landmark_rows.append({
            "landmark_id": node_id,
            "name": item["name"],
            "category": item["category"],
            "osm_type": element["type"],
            "osm_id": element["id"],
            "poi_latitude": f"{item['latitude']:.7f}",
            "poi_longitude": f"{item['longitude']:.7f}",
            "snap_node_id": f"UTR_NODE_{item['snap_node_id']}",
            "snap_distance_m": f"{item['snap_distance_m']:.3f}",
            "selection_status": "SELECTABLE",
            "data_status": "SOURCE_BACKED",
        })

    edge_rows: list[dict[str, Any]] = []
    for index, (origin, destination) in enumerate(
        sorted(directed_pairs, key=lambda pair: (node_id_by_snap[pair[0]], node_id_by_snap[pair[1]])),
        1,
    ):
        distance, travel_time, path = routes_by_source[origin][destination]
        origin_landmark = landmark_by_snap[origin]
        destination_landmark = landmark_by_snap[destination]
        connector_distance = (
            origin_landmark["snap_distance_m"] + destination_landmark["snap_distance_m"]
        )
        distance += connector_distance
        travel_time += connector_distance / (20 * 1000 / 60)
        coordinates = [[origin_landmark["longitude"], origin_landmark["latitude"]]]
        coordinates.append(list(nodes_by_id[path[0]["s_node_id"]]))
        coordinates.extend(nodes_by_id[segment["e_node_id"]] for segment in path)
        coordinates.append([
            destination_landmark["longitude"], destination_landmark["latitude"],
        ])
        road_names = list(dict.fromkeys(
            str(segment.get("street_name") or "").strip()
            for segment in path if str(segment.get("street_name") or "").strip()
        ))
        edge_rows.append({
            "edge_id": f"LM_EDGE_{index:04d}",
            "from_node_id": node_id_by_snap[origin],
            "to_node_id": node_id_by_snap[destination],
            "road_name": " → ".join(road_names[:6]) or "UTraffic road path",
            "road_type": "AGGREGATED_PATH",
            "direction": "SOURCE_DIRECTED_PATH",
            "distance_m": f"{distance:.3f}",
            "free_flow_time_min": f"{travel_time:.6f}",
            "congestion_level_1_5": "1",
            "flood_risk_0_1": "0",
            "flood_observation_status": "NO_RECORD_IN_SELECTED_SOURCES",
            "path_coordinates_json": json.dumps(coordinates, separators=(",", ":")),
            "source_path_edge_count": len(path),
            "connector_distance_m": f"{connector_distance:.3f}",
            "connector_speed_assumption_kph": "20",
            "source_segment_ids": ";".join(segment["_id"] for segment in path),
            "source_id": "UTRAFFIC-HCM-V6",
            "data_status": "DERIVED",
        })

    if OUTPUT_ROOT.exists():
        if OUTPUT_ROOT.resolve().parent != (REPOSITORY_ROOT / "data/processed").resolve():
            raise ValueError(f"Unsafe output path: {OUTPUT_ROOT}")
        shutil.rmtree(OUTPUT_ROOT)
    OUTPUT_ROOT.mkdir(parents=True)
    write_csv(OUTPUT_ROOT / "nodes.csv", list(node_rows[0]), node_rows)
    write_csv(OUTPUT_ROOT / "edges.csv", list(edge_rows[0]), edge_rows)
    write_csv(OUTPUT_ROOT / "landmarks.csv", list(landmark_rows[0]), landmark_rows)
    write_json(OUTPUT_ROOT / "scenarios.json", {
        "dataset_id": DATASET_ID,
        "data_status": "MIXED",
        "real_time": False,
        "scenarios": [
            {
                "scenario_id": "LANDMARK_HISTORICAL_BASELINE",
                "data_status": "ASSUMPTION",
                "traffic_scenario": "UTraffic source max-velocity historical baseline",
                "cost_preset": "BALANCED",
                "weights": {
                    "distance": 0.25,
                    "freeflow_time": 0.30,
                    "congestion": 0.20,
                    "flood_risk": 0.25,
                },
                "closed_edge_ids": [],
                "edge_overrides": {},
            },
            {
                "scenario_id": "LANDMARK_PM_PEAK",
                "data_status": "ASSUMPTION",
                "traffic_scenario": "Giờ cao điểm chiều (17:00 - 19:00, ùn tắc trục Võ Văn Ngân & Lê Văn Việt)",
                "cost_preset": "PEAK_TRAFFIC",
                "default_congestion_level_1_5": 2.5,
                "traffic_multiplier": 1.4,
                "weights": {
                    "distance": 0.15,
                    "freeflow_time": 0.25,
                    "congestion": 0.45,
                    "flood_risk": 0.15,
                },
                "closed_edge_ids": [],
                "edge_overrides": {
                    "LM_EDGE_0127": {
                        "congestion_level_1_5": 5.0,
                        "traffic_multiplier": 4.0,
                        "traffic_penalty_min": 18.0,
                        "data_status": "ASSUMPTION",
                    },
                    "LM_EDGE_0114": {
                        "congestion_level_1_5": 5.0,
                        "traffic_multiplier": 4.0,
                        "traffic_penalty_min": 18.0,
                        "data_status": "ASSUMPTION",
                    },
                    "LM_EDGE_0093": {
                        "congestion_level_1_5": 5.0,
                        "traffic_multiplier": 4.5,
                        "traffic_penalty_min": 20.0,
                        "data_status": "ASSUMPTION",
                    },
                    "LM_EDGE_0129": {
                        "congestion_level_1_5": 5.0,
                        "traffic_multiplier": 4.5,
                        "traffic_penalty_min": 20.0,
                        "data_status": "ASSUMPTION",
                    },
                },
            },
            {
                "scenario_id": "LANDMARK_HEAVY_RAIN",
                "data_status": "SIMULATED",
                "traffic_scenario": "Mưa to & Triều cường (Ngập sâu trục đường Lê Văn Việt & Linh Xuân)",
                "cost_preset": "RAIN_SAFE",
                "default_congestion_level_1_5": 2.0,
                "default_flood_risk_0_1": 0.1,
                "traffic_multiplier": 1.2,
                "weights": {
                    "distance": 0.10,
                    "freeflow_time": 0.25,
                    "congestion": 0.15,
                    "flood_risk": 0.50,
                },
                "closed_edge_ids": [
                    "LM_EDGE_0127",
                    "LM_EDGE_0114",
                    "LM_EDGE_0168",
                    "LM_EDGE_0055",
                ],
                "edge_overrides": {
                    "LM_EDGE_0127": {
                        "flood_risk_0_1": 1.0,
                        "is_closed": True,
                        "data_status": "SIMULATED",
                    },
                    "LM_EDGE_0114": {
                        "flood_risk_0_1": 1.0,
                        "is_closed": True,
                        "data_status": "SIMULATED",
                    },
                    "LM_EDGE_0168": {
                        "flood_risk_0_1": 1.0,
                        "is_closed": True,
                        "data_status": "SIMULATED",
                    },
                    "LM_EDGE_0055": {
                        "flood_risk_0_1": 1.0,
                        "is_closed": True,
                        "data_status": "SIMULATED",
                    },
                },
            },
        ],
    })
    write_json(OUTPUT_ROOT / "metadata.json", {
        "dataset_id": DATASET_ID,
        "dataset_kind": "processed_landmark_graph",
        "label": "Thu Duc major landmarks road graph",
        "data_status": "MIXED",
        "routing_dataset_status": "ACADEMIC_LANDMARK_DEMO",
        "snapshot_date": "2026-08-09",
        "real_time": False,
        "source_ids": [
            "UTRAFFIC-HCM-V6", "OSM-THU-DUC-MAJOR-PLACES-2026-08-09",
            "OSM-THU-DUC-BOUNDARY-2026-08-09",
        ],
        "attribution": ["UTraffic/HCMUT historical network", "© OpenStreetMap contributors"],
        "landmark_definition": snapshot["definition"],
        "graph_properties": {
            "directed": True,
            "strongly_connected": True,
            "node_count": len(node_rows),
            "edge_count": len(edge_rows),
            "selectable_node_count": len(node_rows),
            "hidden_source_road_node_count": len(component_ids),
            "hidden_source_road_edge_count": len(component_segments),
        },
        "limitations": [
            "Only selected named major-place categories are exposed as selectable nodes.",
            "Edges are derived aggregate shortest paths over the historic UTraffic road snapshot.",
            "Traffic is historical, not real-time; flood risk 0 means NO_RECORD, not flood-safe.",
            "Markers stay at OSM coordinates; straight POI-to-road connectors use a disclosed 20 km/h assumption.",
            "Former Thu Duc City boundary is an OSM relation currently tagged historic.",
            "Academic visualization only; not navigation or safety guidance.",
        ],
    })
    write_json(OUTPUT_ROOT / "validation_report.json", {
        "status": "PASS",
        "landmark_count": len(node_rows),
        "derived_edge_count": len(edge_rows),
        "max_snap_distance_m": max(float(row["snap_distance_m"]) for row in node_rows),
        "source_road_graph": {
            "node_count": len(component_ids),
            "edge_count": len(component_segments),
            "strongly_connected": True,
        },
    })
    (OUTPUT_ROOT / "README.md").write_text(
        "# Thu Duc major landmarks road graph\n\n"
        "Selectable nodes are named major OSM places. Directed edges are aggregated "
        "UTraffic shortest road paths with frozen polyline geometry. This is a MIXED, "
        "historical academic demo and not real-time navigation.\n",
        encoding="utf-8",
    )
    checksum_files = [
        "nodes.csv", "edges.csv", "landmarks.csv", "scenarios.json", "metadata.json",
        "validation_report.json", "README.md",
    ]
    (OUTPUT_ROOT / "checksums.sha256").write_text(
        "".join(f"{sha256(OUTPUT_ROOT / filename)}  {filename}\n" for filename in checksum_files),
        encoding="utf-8",
    )
    return len(node_rows), len(edge_rows)


if __name__ == "__main__":
    node_count, edge_count = build()
    print(f"Built {DATASET_ID}: {node_count} landmarks, {edge_count} directed road-path edges")
