"""Fetch and freeze the former Thu Duc City OSM boundary relation."""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = REPOSITORY_ROOT / "data/raw/thu_duc_boundary_v1.0.0"
OUTPUT_PATH = OUTPUT_ROOT / "osm_relation_19407794.geojson"
SOURCE_URL = (
    "https://nominatim.openstreetmap.org/lookup?osm_ids=R19407794"
    "&format=geojson&polygon_geojson=1&addressdetails=1"
)


def fetch() -> Path:
    if OUTPUT_PATH.exists():
        raise FileExistsError(f"Raw snapshot already exists and is immutable: {OUTPUT_PATH}")
    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "FloodRoute-Academic-Demo/0.1 (boundary snapshot)"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload: dict[str, Any] = json.load(response)
    features = payload.get("features", [])
    if len(features) != 1:
        raise ValueError("Expected exactly one Thu Duc boundary feature")
    feature = features[0]
    properties = feature.get("properties", {})
    if properties.get("osm_type") != "relation" or properties.get("osm_id") != 19407794:
        raise ValueError("Unexpected OSM relation in boundary response")
    if feature.get("geometry", {}).get("type") not in {"Polygon", "MultiPolygon"}:
        raise ValueError("Thu Duc boundary must be Polygon or MultiPolygon")

    properties.update({
        "data_status": "SOURCE_BACKED",
        "boundary_status": "HISTORIC_OSM_RELATION",
        "display_label": "Ranh TP Thủ Đức cũ",
    })
    frozen_payload = {
        "type": "FeatureCollection",
        "snapshot_date": "2026-08-09",
        "source_url": SOURCE_URL,
        "source_id": "OSM-THU-DUC-BOUNDARY-2026-08-09",
        "license": "ODbL-1.0",
        "attribution": "© OpenStreetMap contributors",
        "scope_note": (
            "OSM relation 19407794 is tagged historic. It represents the former "
            "Thu Duc City boundary used as project study-area context."
        ),
        "features": features,
    }
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=False)
    OUTPUT_PATH.write_text(
        json.dumps(frozen_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return OUTPUT_PATH


if __name__ == "__main__":
    print(fetch())
