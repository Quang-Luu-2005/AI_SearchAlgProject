from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = REPOSITORY_ROOT / "data"
FIXTURES_ROOT = DATA_ROOT / "fixtures"
PROCESSED_ROOT = DATA_ROOT / "processed"
DATASET_MANIFEST = DATA_ROOT / "registry" / "dataset_manifest.json"
