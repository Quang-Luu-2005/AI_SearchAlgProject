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


def test_locations_returns_selectable_simulated_nodes() -> None:
    response = client.get("/api/v1/locations")

    assert response.status_code == 200
    payload = response.json()
    assert payload["graph_id"] == "toy_graph_v0.1"
    assert len(payload["locations"]) == 6
    assert [item["node_id"] for item in payload["locations"]] == [
        "N01",
        "N02",
        "N03",
        "N04",
        "N05",
        "N06",
    ]
    assert all(item["data_status"] == "SIMULATED" for item in payload["locations"])


def test_scenarios_returns_three_cost_presets() -> None:
    response = client.get("/api/v1/scenarios")

    assert response.status_code == 200
    payload = response.json()
    scenario_by_id = {item["scenario_id"]: item for item in payload["scenarios"]}
    assert set(scenario_by_id) == {
        "OFFPEAK_BALANCED",
        "PEAK_TRAFFIC",
        "HEAVY_RAIN_SAFE",
    }
    assert scenario_by_id["PEAK_TRAFFIC"]["cost_preset"] == "PEAK_TRAFFIC"
    assert sum(scenario_by_id["HEAVY_RAIN_SAFE"]["weights"].values()) == 1
    assert scenario_by_id["HEAVY_RAIN_SAFE"]["closed_edge_ids"] == ["E03", "E04"]


def test_search_accepts_handoff_request_and_returns_complete_result() -> None:
    response = client.post(
        "/api/v1/search",
        json={
            "start": "N01",
            "goal": "N06",
            "algorithm": "A_STAR",
            "scenario": "HEAVY_RAIN_SAFE",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["path"] == ["N01", "N02", "N04", "N06"]
    assert payload["edge_ids"] == ["E01", "E11", "E09"]
    assert payload["metrics"]["distance_m"] == 3000
    assert payload["metrics"]["total_cost"] > 0
    assert payload["trace"][-1]["kind"] == "GOAL"
    assert [event["step"] for event in payload["trace"]] == list(
        range(len(payload["trace"]))
    )
    assert "Optimal" in payload["guarantee"]
    assert "SIMULATED" in payload["explanation"]
    assert payload["data_status"] == "SIMULATED"


def test_search_validates_start_and_goal_nodes() -> None:
    base_request = {
        "start": "N01",
        "goal": "N06",
        "algorithm": "A_STAR",
        "scenario": "OFFPEAK_BALANCED",
    }
    invalid_start = client.post(
        "/api/v1/search",
        json={**base_request, "start": "MISSING"},
    )
    invalid_goal = client.post(
        "/api/v1/search",
        json={**base_request, "goal": "MISSING"},
    )

    assert invalid_start.status_code == 404
    assert "Unknown node" in invalid_start.json()["detail"]
    assert invalid_goal.status_code == 404
    assert "Unknown node" in invalid_goal.json()["detail"]


def test_search_validates_algorithm_and_scenario() -> None:
    request = {
        "start": "N01",
        "goal": "N06",
        "algorithm": "NOT_AN_ALGORITHM",
        "scenario": "OFFPEAK_BALANCED",
    }
    invalid_algorithm = client.post("/api/v1/search", json=request)
    invalid_scenario = client.post(
        "/api/v1/search",
        json={**request, "algorithm": "UCS", "scenario": "MISSING"},
    )

    assert invalid_algorithm.status_code == 422
    assert "Available algorithms" in invalid_algorithm.json()["detail"]
    assert invalid_scenario.status_code == 404
    assert "Unknown scenario" in invalid_scenario.json()["detail"]


def test_search_returns_clear_error_when_no_route_exists() -> None:
    response = client.post(
        "/api/v1/search",
        json={
            "graph_id": "graph_examples_v0.1/simple_path",
            "start": "SP_C",
            "goal": "SP_A",
            "algorithm": "A_STAR",
            "scenario": "DEFAULT",
        },
    )

    assert response.status_code == 404
    assert "No route" in response.json()["detail"]


def test_compare_runs_ucs_and_a_star_on_same_input() -> None:
    response = client.post(
        "/api/v1/compare",
        json={
            "start": "N01",
            "goal": "N06",
            "scenario": "HEAVY_RAIN_SAFE",
            "algorithms": ["UCS", "A_STAR"],
        },
    )

    assert response.status_code == 200
    results = response.json()["results"]
    assert [result["algorithm"] for result in results] == ["UCS", "A_STAR"]
    assert results[0]["path"] == results[1]["path"]
    assert results[0]["metrics"]["total_cost"] == results[1]["metrics"]["total_cost"]


def test_openapi_documents_be03_endpoints_and_handoff_example() -> None:
    swagger = client.get("/docs")
    response = client.get("/openapi.json")

    assert swagger.status_code == 200
    assert "Swagger UI" in swagger.text
    assert response.status_code == 200
    schema = response.json()
    for path in (
        "/api/v1/locations",
        "/api/v1/scenarios",
        "/api/v1/search",
        "/api/v1/compare",
    ):
        assert path in schema["paths"]
    assert schema["components"]["schemas"]["SearchRequest"]["example"] == {
        "start": "N01",
        "goal": "N06",
        "algorithm": "A_STAR",
        "scenario": "HEAVY_RAIN_SAFE",
    }
