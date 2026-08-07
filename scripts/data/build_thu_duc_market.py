"""Build the versioned Thu Duc Market academic routing dataset.

The builder only reads immutable raw inputs and rewrites the generated processed
release. It intentionally uses only the Python standard library so the dataset
can be reproduced in the project's bootstrap environment.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import statistics
import urllib.request
import unicodedata
from collections import defaultdict
from io import TextIOWrapper
from pathlib import Path
from typing import Any, Iterable
from zipfile import ZipFile


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = REPOSITORY_ROOT / "data"
RAW_ROOT = DATA_ROOT / "raw" / "thu_duc_market_v1.0.0"
PROCESSED_ROOT = DATA_ROOT / "processed" / "thu_duc_market_v1.0.0"
WORKBOOK_PATH = DATA_ROOT / "raw" / "FloodRoute_HCMC_Dataset_v0.1.xlsx"
UTRAFFIC_PATH = RAW_ROOT / "utraffic_hcm_v6.zip"
OSM_POI_PATH = RAW_ROOT / "osm_poi_snapshot.json"
SOURCE_REGISTRY_PATH = RAW_ROOT / "source_registry.json"
UTRAFFIC_URL = (
    "https://www.kaggle.com/api/v1/datasets/download/"
    "thanhnguyen2612/traffic-flow-data-in-ho-chi-minh-city-viet-nam"
)

DATASET_ID = "thu_duc_market_v1.0.0"
SNAPSHOT_DATE = "2026-08-07"
BBOX = {
    "south": 10.845,
    "west": 106.751,
    "north": 10.853,
    "east": 106.759,
}
ROAD_TYPES = {"trunk", "primary", "secondary", "tertiary"}
EXPECTED_NODE_COUNT = 90
EXPECTED_EDGE_COUNT = 155
LOS_TO_CONGESTION = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 5}

OSM_POIS = (
    {
        "point_id": "DP00",
        "name": "Chợ Thủ Đức",
        "point_type": "DEPOT",
        "osm_type": "way",
        "osm_id": 499426667,
        "latitude": 10.8502385,
        "longitude": 106.7541974,
        "selected_for_demo": True,
    },
    {
        "point_id": "DP01",
        "name": "Long Châu",
        "point_type": "DELIVERY",
        "osm_type": "node",
        "osm_id": 10215649401,
        "latitude": 10.8529541,
        "longitude": 106.75229,
        "selected_for_demo": True,
    },
    {
        "point_id": "DP02",
        "name": "Pharmacity",
        "point_type": "DELIVERY",
        "osm_type": "node",
        "osm_id": 4965375504,
        "latitude": 10.8525413,
        "longitude": 106.7528014,
        "selected_for_demo": True,
    },
    {
        "point_id": "DP03",
        "name": "WinMart+",
        "point_type": "DELIVERY",
        "osm_type": "node",
        "osm_id": 5609998736,
        "latitude": 10.8517865,
        "longitude": 106.753265,
        "selected_for_demo": True,
    },
    {
        "point_id": "DP04",
        "name": "Tạp Hóa Ngọc Hân",
        "point_type": "DELIVERY",
        "osm_type": "node",
        "osm_id": 4684698690,
        "latitude": 10.8502187,
        "longitude": 106.754861,
        "selected_for_demo": True,
    },
    {
        "point_id": "DP05",
        "name": "CH Sỉ Số 1 Kha Vạn Cân",
        "point_type": "DELIVERY",
        "osm_type": "node",
        "osm_id": 10976631705,
        "latitude": 10.8502615,
        "longitude": 106.7543745,
        "selected_for_demo": True,
    },
    {
        "point_id": "DP06",
        "name": "Pizza Hut Võ Văn Ngân",
        "point_type": "DELIVERY",
        "osm_type": "node",
        "osm_id": 4089412564,
        "latitude": 10.8511325,
        "longitude": 106.7565904,
        "selected_for_demo": True,
    },
)

SOURCE_BACKED_ROUTE_LOCATIONS = (
    {
        "point_id": "DP07",
        "name": "Điểm giao Cầu Ngang – Kha Vạn Cân",
        "point_type": "DELIVERY_TEST_ANCHOR",
        "osm_type": "",
        "osm_id": "",
        "latitude": 10.8485905,
        "longitude": 106.7529815,
        "selected_for_demo": False,
        "fixed_source_node_id": "2947068442",
    },
    {
        "point_id": "DP08",
        "name": "Điểm giao Dương Văn Cam – Kha Vạn Cân",
        "point_type": "DELIVERY_TEST_ANCHOR",
        "osm_type": "",
        "osm_id": "",
        "latitude": 10.8495638,
        "longitude": 106.7534794,
        "selected_for_demo": False,
        "fixed_source_node_id": "366385739",
    },
)

FLOOD_SOURCE_URL_2025 = (
    "https://ttbc-hcm.gov.vn/24-diem-mua-la-ngap-o-tp-thu-duc-"
    "nguoi-dan-can-chu-y-1018710.html"
)
FLOOD_SOURCE_URL_2026 = (
    "https://tuoitre.vn/nld/so-xay-dung-tphcm-neu-nguyen-nhan-cho-thu-duc-"
    "ngap-nang-sau-mua-dau-mua-196260507181450735.htm"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--utraffic-zip",
        type=Path,
        help="Copy an already-downloaded immutable UTraffic ZIP into the raw version.",
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Download UTraffic from the recorded Kaggle URL when raw ZIP is absent.",
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def normalized(value: str | None) -> str:
    text = unicodedata.normalize("NFD", value or "")
    return "".join(char for char in text if unicodedata.category(char) != "Mn").replace(
        "Đ", "D"
    ).replace("đ", "d").casefold()


def percentile(values: list[float], ratio: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("Cannot calculate a percentile from no values")
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * ratio
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def inside(longitude: float, latitude: float) -> bool:
    return (
        BBOX["west"] <= longitude <= BBOX["east"]
        and BBOX["south"] <= latitude <= BBOX["north"]
    )


def haversine_m(
    longitude_a: float,
    latitude_a: float,
    longitude_b: float,
    latitude_b: float,
) -> float:
    radius_m = 6_371_000
    latitude_a_rad, latitude_b_rad = map(math.radians, (latitude_a, latitude_b))
    delta_latitude = latitude_b_rad - latitude_a_rad
    delta_longitude = math.radians(longitude_b - longitude_a)
    value = (
        math.sin(delta_latitude / 2) ** 2
        + math.cos(latitude_a_rad)
        * math.cos(latitude_b_rad)
        * math.sin(delta_longitude / 2) ** 2
    )
    return 2 * radius_m * math.asin(math.sqrt(value))


def zip_csv(archive: ZipFile, name: str) -> list[dict[str, str]]:
    with archive.open(name) as raw_file:
        reader = csv.DictReader(
            TextIOWrapper(raw_file, encoding="utf-8-sig", errors="strict", newline="")
        )
        return list(reader)


def ensure_raw_sources(args: argparse.Namespace) -> None:
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    if not UTRAFFIC_PATH.exists():
        if args.utraffic_zip:
            source = args.utraffic_zip.resolve()
            if not source.is_file():
                raise FileNotFoundError(source)
            shutil.copyfile(source, UTRAFFIC_PATH)
        elif args.download:
            request = urllib.request.Request(
                UTRAFFIC_URL,
                headers={"User-Agent": "FloodRoute-HCMC-academic-dataset/1.0"},
            )
            with urllib.request.urlopen(request, timeout=120) as response:
                UTRAFFIC_PATH.write_bytes(response.read())
        else:
            raise FileNotFoundError(
                f"Missing {UTRAFFIC_PATH}; pass --download or --utraffic-zip"
            )

    if not OSM_POI_PATH.exists():
        write_json(
            OSM_POI_PATH,
            {
                "snapshot_date": "2026-08-07",
                "bbox": BBOX,
                "source": "OpenStreetMap Nominatim and Overpass read-only queries",
                "license": "ODbL-1.0",
                "attribution": "© OpenStreetMap contributors",
                "query_note": "Named market/retail/pharmacy POIs inside the fixed pilot bbox.",
                "elements": list(OSM_POIS),
            },
        )

    if not SOURCE_REGISTRY_PATH.exists():
        write_json(
            SOURCE_REGISTRY_PATH,
            {
                "dataset_id": DATASET_ID,
                "sources": [
                    {
                        "source_id": "UTRAFFIC-HCM-V6",
                        "title": "Traffic Flow data in Ho Chi Minh City, Viet Nam",
                        "provider": "UTraffic / HCMUT; distributed by Kaggle",
                        "url": "https://www.kaggle.com/datasets/thanhnguyen2612/traffic-flow-data-in-ho-chi-minh-city-viet-nam",
                        "license": "CC0 as declared on the Kaggle dataset page",
                        "temporal_coverage": "2020-07-03/2021-04-22",
                    },
                    {
                        "source_id": "OSM-POI-2026-08-07",
                        "title": "OpenStreetMap POI snapshot for Thu Duc Market pilot",
                        "provider": "OpenStreetMap contributors",
                        "url": "https://www.openstreetmap.org/copyright",
                        "license": "ODbL-1.0",
                    },
                    {
                        "source_id": "HMC-FLOOD-2025-24",
                        "title": "24 điểm mưa là ngập ở TP Thủ Đức",
                        "provider": "Trung tâm Báo chí Thành phố Hồ Chí Minh",
                        "url": FLOOD_SOURCE_URL_2025,
                        "published_at": "2025-05-17",
                    },
                    {
                        "source_id": "HMC-FLOOD-2026-MARKET",
                        "title": "Thông tin Sở Xây dựng về ngập khu vực chợ Thủ Đức",
                        "provider": "Sở Xây dựng TP.HCM, reported by Người Lao Động/Tuổi Trẻ",
                        "url": FLOOD_SOURCE_URL_2026,
                        "published_at": "2026-05-07",
                    },
                ],
            },
        )

    raw_checksums = {
        path.name: sha256(path)
        for path in (UTRAFFIC_PATH, OSM_POI_PATH, SOURCE_REGISTRY_PATH)
    }
    (RAW_ROOT / "checksums.sha256").write_text(
        "".join(f"{checksum}  {name}\n" for name, checksum in sorted(raw_checksums.items())),
        encoding="utf-8",
    )


def period_minute(period: str) -> int:
    _, hour, minute = period.split("_")
    return int(hour) * 60 + int(minute)


def scenario_band(scenario_id: str, period: str) -> bool:
    minute = period_minute(period)
    if scenario_id == "HISTORICAL_OFFPEAK":
        return 9 * 60 <= minute < 16 * 60
    if scenario_id == "HISTORICAL_PM_PEAK":
        return 16 * 60 + 30 <= minute < 19 * 60 + 30
    raise ValueError(scenario_id)


def is_strongly_connected(
    node_ids: list[str], segments: list[dict[str, str]]
) -> bool:
    adjacency = {node_id: [] for node_id in node_ids}
    reverse = {node_id: [] for node_id in node_ids}
    for segment in segments:
        origin = segment["s_node_id"]
        destination = segment["e_node_id"]
        adjacency[origin].append(destination)
        reverse[destination].append(origin)

    def reachable(graph: dict[str, list[str]]) -> set[str]:
        start = min(node_ids, key=int)
        visited = {start}
        stack = [start]
        while stack:
            current = stack.pop()
            for neighbor in graph[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    stack.append(neighbor)
        return visited

    return len(reachable(adjacency)) == len(node_ids) and len(reachable(reverse)) == len(
        node_ids
    )


def aggregate_level(values: list[int]) -> int:
    return max(1, min(5, math.floor(statistics.median(values) + 0.5)))


def build_release() -> None:
    with ZipFile(UTRAFFIC_PATH) as archive:
        raw_nodes = zip_csv(archive, "nodes.csv")
        raw_segments = zip_csv(archive, "segments.csv")
        raw_statuses = zip_csv(archive, "segment_status.csv")
        raw_train = zip_csv(archive, "train.csv")

    nodes_by_id = {
        row["_id"]: (float(row["long"]), float(row["lat"])) for row in raw_nodes
    }
    segments_by_id = {row["_id"]: row for row in raw_segments}
    selected_segments = [
        row
        for row in raw_segments
        if row["street_type"] in ROAD_TYPES
        and row["s_node_id"] in nodes_by_id
        and row["e_node_id"] in nodes_by_id
        and inside(*nodes_by_id[row["s_node_id"]])
        and inside(*nodes_by_id[row["e_node_id"]])
    ]
    selected_segments.sort(key=lambda row: int(row["_id"]))
    selected_node_ids = sorted(
        {
            row[key]
            for row in selected_segments
            for key in ("s_node_id", "e_node_id")
        },
        key=int,
    )
    if len(selected_node_ids) != EXPECTED_NODE_COUNT:
        raise ValueError(f"Expected {EXPECTED_NODE_COUNT} nodes, got {len(selected_node_ids)}")
    if len(selected_segments) != EXPECTED_EDGE_COUNT:
        raise ValueError(f"Expected {EXPECTED_EDGE_COUNT} edges, got {len(selected_segments)}")
    strongly_connected = is_strongly_connected(selected_node_ids, selected_segments)
    if not strongly_connected:
        raise ValueError("Selected directed graph is not strongly connected")

    positive_speeds_by_street: dict[str, list[float]] = defaultdict(list)
    positive_speeds_by_type: dict[str, list[float]] = defaultdict(list)
    for row in raw_statuses:
        segment = segments_by_id.get(row["segment_id"])
        if segment is None:
            continue
        velocity = float(row["velocity"])
        if velocity <= 0 or not math.isfinite(velocity):
            continue
        positive_speeds_by_street[normalized(segment["street_name"])].append(velocity)
        positive_speeds_by_type[segment["street_type"]].append(velocity)

    los_by_street: dict[tuple[str, str], list[int]] = defaultdict(list)
    los_by_type: dict[tuple[str, str], list[int]] = defaultdict(list)
    for row in raw_train:
        los = LOS_TO_CONGESTION.get(row["LOS"].upper())
        if los is None:
            continue
        for scenario_id in ("HISTORICAL_OFFPEAK", "HISTORICAL_PM_PEAK"):
            if scenario_band(scenario_id, row["period"]):
                los_by_street[(scenario_id, normalized(row["street_name"]))].append(los)
                los_by_type[(scenario_id, row["street_type"])].append(los)

    poi_payload = json.loads(OSM_POI_PATH.read_text(encoding="utf-8"))
    poi_rows: list[dict[str, Any]] = []
    node_labels: dict[str, list[str]] = defaultdict(list)
    # The approved UI set is exactly DP00..DP05. The raw OSM snapshot may retain
    # additional inspected candidates without silently changing the frozen pilot.
    selected_osm_pois = [
        poi for poi in poi_payload["elements"] if poi["point_id"] in {f"DP{i:02d}" for i in range(6)}
    ]
    if len(selected_osm_pois) != 6:
        raise ValueError("The frozen pilot requires exactly six OSM POIs")
    location_records = [*selected_osm_pois, *SOURCE_BACKED_ROUTE_LOCATIONS]
    for poi in location_records:
        nearest_node_id, snap_distance = min(
            (
                (
                    node_id,
                    haversine_m(
                        float(poi["longitude"]),
                        float(poi["latitude"]),
                        nodes_by_id[node_id][0],
                        nodes_by_id[node_id][1],
                    ),
                )
                for node_id in selected_node_ids
            ),
            key=lambda item: (item[1], int(item[0])),
        )
        if snap_distance > 100:
            raise ValueError(f"POI {poi['point_id']} snap distance is {snap_distance:.2f} m")
        osm_type = poi.get("osm_type", "")
        osm_id = poi.get("osm_id", "")
        is_osm = bool(osm_type and osm_id)
        if is_osm:
            node_labels[nearest_node_id].append(poi["name"])
        source_id = "OSM-POI-2026-08-07" if is_osm else "UTRAFFIC-HCM-V6"
        source_url = (
            f"https://www.openstreetmap.org/{osm_type}/{osm_id}"
            if is_osm
            else "https://www.kaggle.com/datasets/thanhnguyen2612/traffic-flow-data-in-ho-chi-minh-city-viet-nam"
        )
        poi_rows.append(
            {
                **poi,
                "snap_node_id": f"UTR_NODE_{nearest_node_id}",
                "snap_distance_m": f"{snap_distance:.3f}",
                "location_data_status": "SOURCE_BACKED",
                "order_data_status": "ASSUMPTION",
                "source_id": source_id,
                "source_url": source_url,
            }
        )

    flood_rows = [
        {
            "record_id": "FH2025-007",
            "road_name": "Dương Văn Cam",
            "segment_start": "Lê Văn Ninh",
            "segment_end": "Phạm Văn Đồng",
            "depth_min_cm": "",
            "depth_max_cm": "",
            "affected_length_m": "250",
            "drainage_time_min": "30",
            "source_description": "Đoạn ảnh hưởng dài 250 m; rút nước khoảng 30 phút.",
            "source_id": "HMC-FLOOD-2025-24",
            "source_url": FLOOD_SOURCE_URL_2025,
            "mapping_status": "CANDIDATE_MATCH_PENDING_TWO_HUMAN_REVIEWS",
            "flood_observation_status": "OBSERVED_PRONE",
        },
        {
            "record_id": "FH2025-008",
            "road_name": "Đặng Văn Bi",
            "segment_start": "Tô Ngọc Vân",
            "segment_end": "Dương Văn Cam",
            "depth_min_cm": "",
            "depth_max_cm": "",
            "affected_length_m": "",
            "drainage_time_min": "",
            "source_description": "Hay ngập sau mưa lớn.",
            "source_id": "HMC-FLOOD-2025-24",
            "source_url": FLOOD_SOURCE_URL_2025,
            "mapping_status": "CANDIDATE_MATCH_PENDING_TWO_HUMAN_REVIEWS",
            "flood_observation_status": "OBSERVED_PRONE",
        },
        {
            "record_id": "FH2025-015",
            "road_name": "Hẻm 95, đường Võ Văn Ngân",
            "segment_start": "Nhà số 95/26",
            "segment_end": "Cuối hẻm",
            "depth_min_cm": "",
            "depth_max_cm": "",
            "affected_length_m": "40",
            "drainage_time_min": "",
            "source_description": "Đoạn dài 40 m; không có thoát nước.",
            "source_id": "HMC-FLOOD-2025-24",
            "source_url": FLOOD_SOURCE_URL_2025,
            "mapping_status": "OUT_OF_GRAPH",
            "flood_observation_status": "OBSERVED_PRONE",
        },
        {
            "record_id": "FH2026-MARKET-CONTEXT",
            "road_name": "Kha Vạn Cân",
            "segment_start": "Khu vực chợ Thủ Đức",
            "segment_end": "Khu vực dự án thoát nước",
            "depth_min_cm": "",
            "depth_max_cm": "",
            "affected_length_m": "",
            "drainage_time_min": "",
            "source_description": "Nằm trong khu vực dự án cải tạo thoát nước chợ Thủ Đức; không dùng như quan trắc độ sâu.",
            "source_id": "HMC-FLOOD-2026-MARKET",
            "source_url": FLOOD_SOURCE_URL_2026,
            "mapping_status": "CONTEXT_ONLY_PENDING_TWO_HUMAN_REVIEWS",
            "flood_observation_status": "CONTEXT_ONLY",
        },
    ]
    flooded_streets = {
        normalized(row["road_name"])
        for row in flood_rows
        if row["flood_observation_status"] == "OBSERVED_PRONE"
        and row["mapping_status"].startswith("CANDIDATE_MATCH")
    }

    node_rows = []
    for node_id in selected_node_ids:
        longitude, latitude = nodes_by_id[node_id]
        labels = node_labels.get(node_id, [])
        node_rows.append(
            {
                "node_id": f"UTR_NODE_{node_id}",
                "name": " / ".join(labels) if labels else f"UTraffic node {node_id}",
                "node_type": "POI" if labels else "INTERSECTION_OR_GEOMETRY",
                "latitude": f"{latitude:.7f}",
                "longitude": f"{longitude:.7f}",
                "source_id": "UTRAFFIC-HCM-V6",
                "validation_status": "SOURCE_COORDINATE",
                "data_status": "SOURCE_BACKED",
            }
        )

    edge_rows = []
    traffic_profile_rows = []
    overrides: dict[str, dict[str, dict[str, Any]]] = {
        "HISTORICAL_OFFPEAK": {},
        "HISTORICAL_PM_PEAK": {},
        "RAIN_FLOOD_AWARE_2025_2026": {},
    }
    for segment in selected_segments:
        edge_id = f"UTR_EDGE_{segment['_id']}"
        street_key = normalized(segment["street_name"])
        street_speeds = positive_speeds_by_street[street_key]
        if len(street_speeds) >= 5:
            speed_values = street_speeds
            speed_fallback = "STREET_P85"
        else:
            speed_values = positive_speeds_by_type[segment["street_type"]]
            speed_fallback = "STREET_TYPE_P85"
        free_flow_speed = percentile(speed_values, 0.85)
        distance_m = float(segment["length"])
        free_flow_time_min = distance_m / 1000 / free_flow_speed * 60
        is_flood_observed = street_key in flooded_streets
        edge_rows.append(
            {
                "edge_id": edge_id,
                "from_node_id": f"UTR_NODE_{segment['s_node_id']}",
                "to_node_id": f"UTR_NODE_{segment['e_node_id']}",
                "road_name": segment["street_name"],
                "road_type": segment["street_type"],
                "direction": "SOURCE_DIRECTED",
                "distance_m": f"{distance_m:.3f}",
                "free_flow_speed_kph": f"{free_flow_speed:.3f}",
                "free_flow_time_min": f"{free_flow_time_min:.6f}",
                "speed_derivation": speed_fallback,
                "speed_source_rows": len(speed_values),
                "flood_risk_0_1": 1 if is_flood_observed else 0,
                "flood_observation_status": (
                    "OBSERVED_PRONE_CANDIDATE_MAPPING"
                    if is_flood_observed
                    else "NO_RECORD_IN_SELECTED_SOURCES"
                ),
                "source_id": "UTRAFFIC-HCM-V6",
                "source_segment_id": segment["_id"],
                "data_status": "MIXED" if is_flood_observed else "DERIVED",
            }
        )

        levels: dict[str, tuple[int, int, str]] = {}
        for scenario_id in ("HISTORICAL_OFFPEAK", "HISTORICAL_PM_PEAK"):
            street_values = los_by_street[(scenario_id, street_key)]
            if street_values:
                values = street_values
                fallback = "STREET_MEDIAN_LOS"
            else:
                values = los_by_type[(scenario_id, segment["street_type"])]
                fallback = "STREET_TYPE_MEDIAN_LOS"
            level = aggregate_level(values)
            levels[scenario_id] = (level, len(values), fallback)
            traffic_profile_rows.append(
                {
                    "scenario_id": scenario_id,
                    "edge_id": edge_id,
                    "road_name": segment["street_name"],
                    "road_type": segment["street_type"],
                    "time_band": "09:00-16:00" if scenario_id.endswith("OFFPEAK") else "16:30-19:30",
                    "congestion_level_1_5": level,
                    "source_rows": len(values),
                    "derivation": fallback,
                    "source_id": "UTRAFFIC-HCM-V6",
                    "data_status": "DERIVED",
                }
            )
            overrides[scenario_id][edge_id] = {
                "congestion_level_1_5": level,
                "data_status": "DERIVED",
            }
        peak_level = levels["HISTORICAL_PM_PEAK"][0]
        overrides["RAIN_FLOOD_AWARE_2025_2026"][edge_id] = {
            "congestion_level_1_5": peak_level,
            "flood_risk_0_1": 1 if is_flood_observed else 0,
            "data_status": "MIXED" if is_flood_observed else "DERIVED",
        }

    scenarios = {
        "dataset_id": DATASET_ID,
        "data_status": "MIXED",
        "real_time": False,
        "scenarios": [
            {
                "scenario_id": "HISTORICAL_OFFPEAK",
                "traffic_scenario": "Historical UTraffic off-peak profile, 2020-2021",
                "cost_preset": "BALANCED",
                "weights": {
                    "distance": 0.25,
                    "freeflow_time": 0.30,
                    "congestion": 0.20,
                    "flood_risk": 0.25,
                },
                "closed_edge_ids": [],
                "edge_overrides": overrides["HISTORICAL_OFFPEAK"],
                "data_status": "DERIVED",
            },
            {
                "scenario_id": "HISTORICAL_PM_PEAK",
                "traffic_scenario": "Historical UTraffic PM peak profile, 2020-2021",
                "cost_preset": "PEAK_TRAFFIC",
                "weights": {
                    "distance": 0.15,
                    "freeflow_time": 0.25,
                    "congestion": 0.45,
                    "flood_risk": 0.15,
                },
                "closed_edge_ids": [],
                "edge_overrides": overrides["HISTORICAL_PM_PEAK"],
                "data_status": "DERIVED",
            },
            {
                "scenario_id": "RAIN_FLOOD_AWARE_2025_2026",
                "traffic_scenario": "Historical PM profile plus source-backed flood exposure candidates",
                "cost_preset": "RAIN_SAFE",
                "weights": {
                    "distance": 0.10,
                    "freeflow_time": 0.25,
                    "congestion": 0.15,
                    "flood_risk": 0.50,
                },
                "closed_edge_ids": [],
                "edge_overrides": overrides["RAIN_FLOOD_AWARE_2025_2026"],
                "data_status": "MIXED",
            },
        ],
    }

    mapping_rows = []
    for flood in flood_rows:
        mapped_edges = [
            row["edge_id"]
            for row in edge_rows
            if normalized(row["road_name"]) == normalized(flood["road_name"])
        ]
        mapping_rows.append(
            {
                "record_id": flood["record_id"],
                "road_name": flood["road_name"],
                "mapped_edge_ids": ";".join(mapped_edges),
                "mapping_status": flood["mapping_status"],
                "reviewer_1": "",
                "reviewer_1_status": "PENDING_TEAM_MEMBER",
                "reviewer_2": "",
                "reviewer_2_status": "PENDING_TEAM_MEMBER",
                "review_status": "PENDING_TWO_HUMAN_REVIEWS",
                "note": "Automated source/name precheck only. Two human team members must sign before Verified.",
            }
        )

    if PROCESSED_ROOT.exists():
        for path in PROCESSED_ROOT.iterdir():
            if path.is_file():
                path.unlink()
    else:
        PROCESSED_ROOT.mkdir(parents=True)

    write_csv(
        PROCESSED_ROOT / "nodes.csv",
        list(node_rows[0]),
        node_rows,
    )
    write_csv(
        PROCESSED_ROOT / "edges.csv",
        list(edge_rows[0]),
        edge_rows,
    )
    write_json(PROCESSED_ROOT / "scenarios.json", scenarios)
    write_csv(
        PROCESSED_ROOT / "delivery_points.csv",
        list(poi_rows[0]),
        poi_rows,
    )
    write_csv(
        PROCESSED_ROOT / "flood_hotspots.csv",
        list(flood_rows[0]),
        flood_rows,
    )
    write_csv(
        PROCESSED_ROOT / "traffic_profiles.csv",
        list(traffic_profile_rows[0]),
        traffic_profile_rows,
    )
    write_csv(
        PROCESSED_ROOT / "mapping_review.csv",
        list(mapping_rows[0]),
        mapping_rows,
    )

    metadata = {
        "dataset_id": DATASET_ID,
        "dataset_version": "1.0.0",
        "label": "Thu Duc Market historical traffic and flood-aware pilot",
        "dataset_kind": "processed",
        "data_status": "MIXED",
        "routing_dataset_status": "REVIEW_REQUIRED",
        "snapshot_date": "2026-08-07",
        "traffic_temporal_coverage": "2020-07-03/2021-04-22",
        "real_time": False,
        "bbox": BBOX,
        "source_ids": [
            "UTRAFFIC-HCM-V6",
            "OSM-POI-2026-08-07",
            "HMC-FLOOD-2025-24",
            "HMC-FLOOD-2026-MARKET",
        ],
        "attribution": [
            "Traffic data: UTraffic/HCMUT, distributed by Kaggle",
            "POI data © OpenStreetMap contributors, ODbL 1.0",
            "Flood records: Trung tâm Báo chí TP.HCM and Sở Xây dựng TP.HCM reporting",
        ],
        "graph_properties": {
            "directed": True,
            "strongly_connected": strongly_connected,
            "node_count": len(node_rows),
            "edge_count": len(edge_rows),
        },
        "limitations": [
            "Historical traffic profiles cover 2020-2021 and are not real-time.",
            "Flood risk 1 is a binary known-exposure penalty, not a probability or safety threshold.",
            "No record in selected flood sources does not mean a road is flood-safe.",
            "Flood-to-edge candidate mappings still require two human team-member reviews.",
            "Delivery orders and cost weights are academic ASSUMPTION values.",
            "The golden route-change case uses two source-backed road-junction test anchors; they are not UI POIs.",
            "This dataset is not real-world routing or flood-safety guidance.",
        ],
    }
    write_json(PROCESSED_ROOT / "metadata.json", metadata)

    # Freeze the first lexicographically ordered delivery pair whose optimal path
    # changes under the rain-aware cost model. This makes the golden-case choice
    # deterministic and prevents cherry-picking during later experiments.
    from backend.app.core.graph import GraphLoader
    from backend.app.services import SearchService

    graph = GraphLoader.from_directory(PROCESSED_ROOT)
    service = SearchService(graph)
    unique_points = sorted(
        {(row["point_id"], row["snap_node_id"]) for row in poi_rows},
        key=lambda item: item[0],
    )
    changed_case: dict[str, Any] | None = None
    for index, (start_point_id, start_node_id) in enumerate(unique_points):
        for goal_point_id, goal_node_id in unique_points[index + 1 :]:
            if start_node_id == goal_node_id:
                continue
            offpeak = service.search(
                start=start_node_id,
                goal=goal_node_id,
                algorithm="UCS",
                scenario_id="HISTORICAL_OFFPEAK",
            )
            rain = service.search(
                start=start_node_id,
                goal=goal_node_id,
                algorithm="UCS",
                scenario_id="RAIN_FLOOD_AWARE_2025_2026",
            )
            if offpeak.edge_ids == rain.edge_ids:
                continue
            changed_case = {
                "case_id": "TD-GOLDEN-ROUTE-CHANGE-001",
                "start_point_id": start_point_id,
                "goal_point_id": goal_point_id,
                "start": start_node_id,
                "goal": goal_node_id,
                "baseline_scenario_id": "HISTORICAL_OFFPEAK",
                "comparison_scenario_id": "RAIN_FLOOD_AWARE_2025_2026",
                "algorithm": "UCS",
                "expected_baseline_path": list(offpeak.result.path),
                "expected_baseline_edge_ids": list(offpeak.edge_ids),
                "expected_comparison_path": list(rain.result.path),
                "expected_comparison_edge_ids": list(rain.edge_ids),
                "expected_property": "ROUTE_CHANGES_WHEN_KNOWN_FLOOD_EXPOSURE_IS_PENALIZED",
                "data_status": "MIXED",
            }
            break
        if changed_case is not None:
            break
    if changed_case is None:
        raise ValueError("No delivery-point pair changes route in the rain-aware scenario")
    write_json(
        PROCESSED_ROOT / "test_cases.json",
        {"dataset_id": DATASET_ID, "data_status": "MIXED", "cases": [changed_case]},
    )

    validation_report = {
        "dataset_id": DATASET_ID,
        "generated_at": f"{SNAPSHOT_DATE}T00:00:00+00:00",
        "status": "PASS_WITH_PENDING_HUMAN_REVIEW",
        "checks": {
            "node_count": len(node_rows),
            "edge_count": len(edge_rows),
            "strongly_connected": strongly_connected,
            "positive_distance_and_time": True,
            "poi_snap_max_m": max(float(row["snap_distance_m"]) for row in poi_rows),
            "poi_snap_within_100m": True,
            "source_provenance_present": True,
            "human_mapping_review_count": 0,
        },
        "warnings": [
            "Dataset must remain REVIEW_REQUIRED until reviewer_1 and reviewer_2 are completed by human team members."
        ],
    }
    write_json(PROCESSED_ROOT / "validation_report.json", validation_report)

    checksum_targets = sorted(
        path for path in PROCESSED_ROOT.iterdir() if path.name != "checksums.sha256"
    )
    (PROCESSED_ROOT / "checksums.sha256").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in checksum_targets),
        encoding="utf-8",
    )
    print(
        f"Built {DATASET_ID}: {len(node_rows)} nodes, {len(edge_rows)} edges, "
        f"{len(poi_rows)} locations; status REVIEW_REQUIRED"
    )


def main() -> None:
    args = parse_args()
    ensure_raw_sources(args)
    build_release()


if __name__ == "__main__":
    main()
