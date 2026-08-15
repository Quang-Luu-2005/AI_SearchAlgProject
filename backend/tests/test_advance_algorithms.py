from pathlib import Path
import pytest

from backend.app.core.contracts import Graph, RouteNotFoundError, Scenario
from backend.app.core.graph import GraphLoader
from backend.app.services import SearchService
from backend.app.core.contracts import RouteNotFoundError, Scenario
from backend.app.core.graph import GraphLoader
from backend.app.services import SearchService

PROCESSED_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "thu_duc_landmarks_v1.0.0"

@pytest.fixture(scope="module")
def real_service() -> SearchService:
    """Load đồ thị thật của dự án làm nền tảng test, thay thế kịch bản an toàn."""
    original_graph = GraphLoader.from_directory(PROCESSED_DIR)

    start_node_id = original_graph.nodes[0].node_id
    closed_edges = [edge.edge_id for edge in original_graph.edges if edge.from_node_id == start_node_id]

    isolated_scenario = Scenario(
        scenario_id="TEST_UNREACHABLE_LOCKDOWN",
        closed_edge_ids=closed_edges,
        attributes={
            "cost_preset": "BALANCED",
            "weights": {"distance": 0.25, "freeflow_time": 0.3, "congestion": 0.2, "flood_risk": 0.25}
        }
    )

    new_scenarios = tuple(list(original_graph.scenarios) + [isolated_scenario])

    hacked_graph = Graph(
        nodes=original_graph.nodes,
        edges=original_graph.edges,
        scenarios=new_scenarios
    )
    
    return SearchService(hacked_graph)


def test_greedy_is_suboptimal_on_real_landmarks(real_service: SearchService) -> None:
    """[Checklist: Tạo phản ví dụ cho Greedy]
    Dùng vòng lặp động quét qua các cặp đỉnh trên bản đồ thật để chứng minh
    có những tuyến đường Greedy bị lừa bởi Heuristic và ra cost đắt hơn UCS.
    """
    scenario_id = "LANDMARK_HISTORICAL_BASELINE"
    nodes = real_service.graph.nodes

    for i in range(min(30, len(nodes))):
        for j in range(len(nodes) - 1, max(-1, len(nodes) - 30), -1):
            start_id = nodes[i].node_id
            goal_id = nodes[j].node_id
            
            if start_id == goal_id:
                continue
            
            greedy_exec = real_service.search(start=start_id, goal=goal_id, algorithm="GREEDY", scenario_id=scenario_id)
            ucs_exec = real_service.search(start=start_id, goal=goal_id, algorithm="UCS", scenario_id=scenario_id)

            if greedy_exec.result.metrics.total_cost > ucs_exec.result.metrics.total_cost:
                assert True
                return 

    pytest.fail("Greedy was unexpectedly optimal for all tested pairs. Map lacks complex traps.")


def test_bidirectional_on_real_directed_graph(real_service: SearchService) -> None:
    """[Checklist: Test directed graph]
    Test khả năng tìm đường của Bidirectional trên mạng lưới 178 đường giao thông có hướng.
    """
    start_id = real_service.graph.nodes[0].node_id
    goal_id = real_service.graph.nodes[-1].node_id
    scenario_id = "LANDMARK_HISTORICAL_BASELINE"

    bi_exec = real_service.search(start=start_id, goal=goal_id, algorithm="BIDIRECTIONAL", scenario_id=scenario_id)
    
    assert len(bi_exec.result.path) > 0
    assert bi_exec.result.path[-1] == goal_id


def test_unreachable_nodes_raise_error_on_real_graph(real_service: SearchService) -> None:
    """[Checklist: Test unreachable]
    Ép thuật toán chạy trong kịch bản đã bị phong tỏa để xem nó có báo lỗi chuẩn xác không.
    """
    start_id = real_service.graph.nodes[0].node_id
    goal_id = real_service.graph.nodes[-1].node_id
    scenario_id = "TEST_UNREACHABLE_LOCKDOWN"

    with pytest.raises(RouteNotFoundError):
        real_service.search(start=start_id, goal=goal_id, algorithm="BIDIRECTIONAL", scenario_id=scenario_id)
        
    with pytest.raises(RouteNotFoundError):
        real_service.search(start=start_id, goal=goal_id, algorithm="GREEDY", scenario_id=scenario_id)