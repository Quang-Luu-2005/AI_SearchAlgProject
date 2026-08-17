"""TC04_MULTI_STOP: Unit and Integration Test Suite for Multi-Stop Tour Optimization."""

import pytest
from fastapi.testclient import TestClient

from backend.app.core.contracts import Edge, Graph, Node, RouteNotFoundError, Scenario
from backend.app.core.paths import FIXTURES_ROOT
from backend.app.main import app
from backend.app.optimization import (
    BruteForceSolver,
    HeldKarpSolver,
    NearestNeighborSolver,
    PairwiseMatrix,
    TourOptimizerService,
)

client = TestClient(app)


@pytest.fixture
def toy_graph() -> Graph:
    return Graph.from_fixture(str(FIXTURES_ROOT / "toy_graph_v0.1"))


def test_tc04_pairwise_matrix_construction(toy_graph: Graph) -> None:
    points = ["N01", "N02", "N03"]
    matrix = PairwiseMatrix(toy_graph, points, scenario_id="OFFPEAK_BALANCED")

    assert matrix.n == 3
    assert len(matrix.cost_matrix) == 3
    assert len(matrix.distance_matrix) == 3
    # Diagonal costs should be 0.0
    for i in range(3):
        assert matrix.cost_matrix[i][i] == 0.0
        assert matrix.distance_matrix[i][i] == 0.0

    # Pairwise subpath retrieval between N01 (idx 0) and N03 (idx 2)
    subpath = matrix.get_subpath(0, 2)
    assert subpath.from_node_id == "N01"
    assert subpath.to_node_id == "N03"
    assert subpath.is_reachable is True
    assert len(subpath.path) >= 2


def test_tc04_unreachable_node_handling() -> None:
    # Graph with directed one-way edge A -> B (no return B -> A)
    nodes = [Node("A"), Node("B")]
    edges = [Edge("E1", "A", "B", distance_m=100.0, free_flow_time_min=1.0)]
    scenarios = [Scenario("BASE_BALANCED", attributes={"cost_preset": "BALANCED"})]
    one_way_graph = Graph(nodes, edges, scenarios)

    matrix = PairwiseMatrix(one_way_graph, ["A", "B"], scenario_id="BASE_BALANCED")
    # Subpath A -> B should exist
    assert matrix.get_subpath(0, 1).is_reachable is True
    # Subpath B -> A is unreachable, so get_subpath raises RouteNotFoundError
    with pytest.raises(RouteNotFoundError):
        matrix.get_subpath(1, 0)




def test_tc04_nearest_neighbor_solver(toy_graph: Graph) -> None:
    points = ["N01", "N02", "N03", "N04"]
    matrix = PairwiseMatrix(toy_graph, points, scenario_id="OFFPEAK_BALANCED")

    indices, cost, distance = NearestNeighborSolver().solve(
        matrix, start_index=0, return_to_depot=True
    )

    assert len(indices) == 5  # 4 unique stops + return to depot (0)
    assert indices[0] == 0
    assert indices[-1] == 0
    assert set(indices) == {0, 1, 2, 3}
    assert cost > 0
    assert distance > 0


def test_tc04_held_karp_solver(toy_graph: Graph) -> None:
    points = ["N01", "N02", "N03", "N04"]
    matrix = PairwiseMatrix(toy_graph, points, scenario_id="OFFPEAK_BALANCED")

    indices, cost, distance = HeldKarpSolver().solve(
        matrix, start_index=0, return_to_depot=True
    )

    assert len(indices) == 5
    assert indices[0] == 0
    assert indices[-1] == 0
    assert set(indices) == {0, 1, 2, 3}
    assert cost > 0
    assert distance > 0


def test_tc04_held_karp_vs_brute_force_small_case(toy_graph: Graph) -> None:
    """Cross-verify Held-Karp exact DP against Brute Force on small inputs (N=4)."""
    points = ["N01", "N02", "N03", "N04"]
    matrix = PairwiseMatrix(toy_graph, points, scenario_id="OFFPEAK_BALANCED")

    hk_tour, hk_cost, hk_dist = HeldKarpSolver().solve(matrix, start_index=0, return_to_depot=True)
    bf_tour, bf_cost, bf_dist = BruteForceSolver().solve(matrix, start_index=0, return_to_depot=True)

    # Costs and distances should match exactly for small inputs
    assert pytest.approx(hk_cost, rel=1e-5) == bf_cost
    assert pytest.approx(hk_dist, rel=1e-5) == bf_dist


def test_tc04_tour_optimizer_service_and_stitching(toy_graph: Graph) -> None:
    service = TourOptimizerService(toy_graph)
    result = service.optimize_tour(
        depot="N01",
        stops=["N02", "N03", "N04", "N05", "N06"],
        scenario_id="OFFPEAK_BALANCED",
        return_to_depot=True,
    )

    assert result.depot == "N01"
    assert result.visit_order[0] == "N01"
    assert result.visit_order[-1] == "N01"
    assert len(result.legs) == 6
    assert result.total_cost > 0
    assert result.total_distance_m > 0
    assert result.guarantee == "OPTIMAL_HELD_KARP"
    assert "Held-Karp DP optimal tour" in result.explanation
    assert result.comparison.held_karp_cost <= result.comparison.nearest_neighbor_cost + 1e-6
    assert result.comparison.approximation_gap_percent >= 0.0
    assert result.comparison.original_visit_order == (
        "N01", "N02", "N03", "N04", "N05", "N06", "N01"
    )
    assert result.comparison.original_order_cost > 0
    assert result.comparison.selected_savings_cost == pytest.approx(
        result.comparison.original_order_cost - result.total_cost
    )

    # Verify seamless path stitching (no consecutive duplicate nodes)
    full_path = result.full_path
    for i in range(len(full_path) - 1):
        assert full_path[i] != full_path[i + 1], "Subpath stitching left consecutive duplicate nodes"


def test_tc04_api_optimize_tour_endpoint() -> None:
    response = client.post(
        "/api/v1/optimize-tour",
        json={
            "depot": "N01",
            "stops": ["N02", "N03", "N04", "N05", "N06"],
            "scenario": "OFFPEAK_BALANCED",
            "graph_id": "toy_graph_v0.1",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["depot"] == "N01"
    assert "visit_order" in data
    assert "full_path" in data
    assert "edge_ids" in data
    assert "total_distance_m" in data
    assert "total_cost" in data
    assert "comparison" in data
    assert "held_karp_cost" in data["comparison"]
    assert "nearest_neighbor_cost" in data["comparison"]
    assert "approximation_gap_percent" in data["comparison"]
    assert data["comparison"]["original_visit_order"] == [
        "N01", "N02", "N03", "N04", "N05", "N06", "N01"
    ]
    assert data["comparison"]["original_order_distance_km"] > 0
    assert data["comparison"]["original_order_time_min"] > 0
    assert "selected_savings_percent" in data["comparison"]
    assert data["guarantee"] == "OPTIMAL_HELD_KARP"


def test_tc04_api_invalid_stop_node() -> None:
    response = client.post(
        "/api/v1/optimize-tour",
        json={
            "depot": "N01",
            "stops": ["INVALID_NODE_ID", "N02", "N03", "N04", "N05"],
            "scenario": "OFFPEAK_BALANCED",
            "graph_id": "toy_graph_v0.1",
        },
    )

    assert response.status_code == 404
    assert "not found in graph" in response.json()["detail"]


def test_tc04_api_fewer_than_5_stops_validation() -> None:
    response = client.post(
        "/api/v1/optimize-tour",
        json={
            "depot": "N01",
            "stops": ["N02", "N03", "N04"],
            "scenario": "OFFPEAK_BALANCED",
            "graph_id": "toy_graph_v0.1",
        },
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("stops", "expected_detail"),
    [
        (
            ["N02", "N03", "N04", "N05", "N05"],
            "Delivery stops must contain unique node IDs",
        ),
        (
            ["N01", "N02", "N03", "N04", "N05"],
            "Depot must not also appear in delivery stops",
        ),
    ],
)
def test_tc04_api_rejects_repeated_tour_points(
    stops: list[str], expected_detail: str
) -> None:
    response = client.post(
        "/api/v1/optimize-tour",
        json={
            "depot": "N01",
            "stops": stops,
            "scenario": "OFFPEAK_BALANCED",
            "graph_id": "toy_graph_v0.1",
        },
    )

    assert response.status_code == 422
    assert response.json()["detail"] == expected_detail


def test_tc04_api_rejects_unknown_tour_algorithm() -> None:
    response = client.post(
        "/api/v1/optimize-tour",
        json={
            "depot": "N01",
            "stops": ["N02", "N03", "N04", "N05", "N06"],
            "scenario": "OFFPEAK_BALANCED",
            "graph_id": "toy_graph_v0.1",
            "tour_algorithm": "UNKNOWN",
        },
    )

    assert response.status_code == 422
    assert "Available tour algorithms: HELD_KARP, NEAREST_NEIGHBOR" in response.json()[
        "detail"
    ]


def test_tc04_api_optimize_tour_nearest_neighbor() -> None:
    response = client.post(
        "/api/v1/optimize-tour",
        json={
            "depot": "N01",
            "stops": ["N02", "N03", "N04", "N05", "N06"],
            "scenario": "OFFPEAK_BALANCED",
            "graph_id": "toy_graph_v0.1",
            "tour_algorithm": "NEAREST_NEIGHBOR",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["guarantee"] == "APPROXIMATE_NEAREST_NEIGHBOR"
    assert "Nearest Neighbor" in data["explanation"]


