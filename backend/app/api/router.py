import json

from fastapi import APIRouter

from ..core.paths import DATASET_MANIFEST


router = APIRouter()


@router.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/dataset/meta", tags=["dataset"])
def dataset_meta() -> dict[str, object]:
    """Expose dataset provenance without loading the routing graph."""
    with DATASET_MANIFEST.open(encoding="utf-8") as manifest_file:
        return json.load(manifest_file)

