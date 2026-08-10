from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = REPOSITORY_ROOT / "data"
FIXTURES_ROOT = DATA_ROOT / "fixtures"
PROCESSED_ROOT = DATA_ROOT / "processed"
DATASET_MANIFEST = DATA_ROOT / "registry" / "dataset_manifest.json"
THU_DUC_BOUNDARY = (
    DATA_ROOT / "raw/thu_duc_boundary_v1.0.0/osm_relation_19407794.geojson"
)
