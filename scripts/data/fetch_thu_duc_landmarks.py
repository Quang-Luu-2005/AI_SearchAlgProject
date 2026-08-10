"""Fetch and freeze named major-place candidates around former Thu Duc City."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = REPOSITORY_ROOT / "data/raw/thu_duc_landmarks_v1.0.0"
OUTPUT_PATH = OUTPUT_ROOT / "osm_major_places_snapshot.json"
SNAPSHOT_DATE = "2026-08-09"
BBOX = {
    "south": 10.737393497,
    "west": 106.692316968,
    "north": 10.903548603,
    "east": 106.887276832,
}
ENDPOINTS = (
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
)
SELECTORS = {
    "EDUCATION": 'nwr["name"]["amenity"~"^(university|college)$"]',
    "HOSPITAL": 'nwr["name"]["amenity"="hospital"]',
    "MARKET": 'nwr["name"]["amenity"="marketplace"]',
    "CIVIC_TRANSPORT": 'nwr["name"]["amenity"~"^(bus_station|townhall)$"]',
    "MALL": 'nwr["name"]["shop"="mall"]',
    "RAIL_STATION": 'nwr["name"]["railway"="station"]',
    "STADIUM": 'nwr["name"]["leisure"="stadium"]',
    "CULTURE_THEME": 'nwr["name"]["tourism"~"^(museum|theme_park)$"]',
}


def query(selector: str) -> tuple[list[dict[str, Any]], str, str]:
    bbox = ",".join(str(BBOX[key]) for key in ("south", "west", "north", "east"))
    overpass_query = (
        f"[out:json][timeout:90][bbox:{bbox}];"
        f"{selector};out center tags;"
    )
    body = urllib.parse.urlencode({"data": overpass_query}).encode()
    last_error: Exception | None = None
    for attempt in range(3):
        for endpoint in ENDPOINTS:
            request = urllib.request.Request(
                endpoint,
                data=body,
                headers={"User-Agent": "FloodRoute-Academic-Demo/0.1 (landmark snapshot)"},
            )
            try:
                with urllib.request.urlopen(request, timeout=150) as response:
                    payload = json.load(response)
                return payload.get("elements", []), endpoint, overpass_query
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
                last_error = error
        time.sleep(2 ** attempt)
    raise RuntimeError(f"Overpass query failed: {selector}") from last_error


def fetch() -> Path:
    if OUTPUT_PATH.exists():
        raise FileExistsError(f"Raw snapshot already exists and is immutable: {OUTPUT_PATH}")

    elements_by_id: dict[tuple[str, int], dict[str, Any]] = {}
    query_registry: list[dict[str, Any]] = []
    for category, selector in SELECTORS.items():
        elements, endpoint, overpass_query = query(selector)
        query_registry.append({
            "category": category,
            "selector": selector,
            "endpoint": endpoint,
            "query": overpass_query,
            "result_count": len(elements),
        })
        for element in elements:
            key = (str(element["type"]), int(element["id"]))
            stored = elements_by_id.setdefault(key, element)
            categories = stored.setdefault("floodroute_candidate_categories", [])
            if category not in categories:
                categories.append(category)

    payload = {
        "snapshot_date": SNAPSHOT_DATE,
        "source_id": "OSM-THU-DUC-MAJOR-PLACES-2026-08-09",
        "license": "ODbL-1.0",
        "attribution": "© OpenStreetMap contributors",
        "bbox": BBOX,
        "definition": (
            "Named OSM features tagged as university/college, hospital, marketplace, "
            "bus station/townhall, mall, railway station, stadium, museum or theme park."
        ),
        "query_registry": query_registry,
        "elements": [elements_by_id[key] for key in sorted(elements_by_id)],
    }
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=False)
    OUTPUT_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return OUTPUT_PATH


if __name__ == "__main__":
    print(fetch())
