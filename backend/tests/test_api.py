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


def test_graph_catalog_discovers_loadable_fixture_folders() -> None:
    response = client.get("/api/v1/graphs")

    assert response.status_code == 200
    payload = response.json()
    assert payload["invalid_graphs"] == []
    graph_by_id = {item["graph_id"]: item for item in payload["graphs"]}
    assert graph_by_id["toy_graph_v0.1"]["node_count"] == 6
    assert graph_by_id["graph_examples_v0.1/simple_path"]["edge_count"] == 2
    assert graph_by_id["graph_examples_v0.1/cycle_with_closure"]["scenario_ids"] == [
        "BREAK_CYCLE",
        "OPEN_CYCLE",
    ]


def test_graph_detail_applies_scenario_without_hiding_closed_edge() -> None:
    response = client.get(
        "/api/v1/graphs/graph_examples_v0.1/cycle_with_closure",
        params={"scenario_id": "BREAK_CYCLE"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["active_edge_count"] == 2
    edge_by_id = {edge["edge_id"]: edge for edge in payload["edges"]}
    assert edge_by_id["CY_E03"]["is_closed"] is True
    assert payload["nodes"][0]["attributes"]["data_status"] == "SIMULATED"


def test_graph_detail_rejects_unknown_or_unsafe_folder() -> None:
    assert client.get("/api/v1/graphs/not-a-graph").status_code == 404
    assert client.get("/api/v1/graphs/../raw").status_code in {404, 422}
