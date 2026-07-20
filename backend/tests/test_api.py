from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dataset_metadata_exposes_provenance() -> None:
    response = client.get("/api/v1/dataset/meta")

    assert response.status_code == 200
    payload = response.json()
    assert payload["project"] == "FloodRoute HCMC"
    assert payload["raw_sources"][0]["sha256"]
    assert payload["fixtures"][0]["data_status"] == "SIMULATED"

