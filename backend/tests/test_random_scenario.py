from pathlib import Path
import pytest

from backend.app.core.graph import GraphLoader
from backend.app.core.contracts import RouteNotFoundError, AffectedEdgeStatus
from backend.app.services.random_scenario import RandomScenarioService

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "toy_graph_v0.1"
SIMPLE_PATH_DIR = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "graph_examples_v0.1" / "simple_path"

@pytest.fixture()
def generator_service() -> RandomScenarioService:
    graph = GraphLoader.from_directory(FIXTURE_DIR)
    return RandomScenarioService(base_graph=graph)

def test_random_scenario_is_deterministic(generator_service: RandomScenarioService) -> None:
    """Test 1: Cùng một seed phải sinh ra kết quả y hệt nhau (Reproducibility)."""
    seed_value = "DEMO_DEFENSE_2026"
    
    result_1 = generator_service.generate(start="N01", goal="N06", num_edges=4, seed=seed_value)
    result_2 = generator_service.generate(start="N01", goal="N06", num_edges=4, seed=seed_value)
    
    assert result_1.scenario_id == result_2.scenario_id
    assert [e.edge_id for e in result_1.affected_edges] == [e.edge_id for e in result_2.affected_edges]
    assert [e.status for e in result_1.affected_edges] == [e.status for e in result_2.affected_edges]

def test_random_scenario_allocates_correct_status_types(generator_service: RandomScenarioService) -> None:
    """Test 2: Đảm bảo phân bổ đúng số lượng và loại (Tối đa 1 CLOSED, còn lại chia đều)."""
    result = generator_service.generate(start="N01", goal="N06", num_edges=5)
    
    assert len(result.affected_edges) == 5

    status_counts = {
        AffectedEdgeStatus.CLOSED: 0,
        AffectedEdgeStatus.FLOODED: 0,
        AffectedEdgeStatus.CONGESTED: 0,
    }
    for edge in result.affected_edges:
        status_counts[edge.status] += 1

    assert status_counts[AffectedEdgeStatus.CLOSED] == 1
    assert status_counts[AffectedEdgeStatus.FLOODED] == 2
    assert status_counts[AffectedEdgeStatus.CONGESTED] == 2


def test_random_scenario_contains_both_flood_and_congestion(generator_service: RandomScenarioService) -> None:
    result = generator_service.generate(start="N01", goal="N06", num_edges=7)

    statuses = {edge.status for edge in result.affected_edges}
    assert AffectedEdgeStatus.FLOODED in statuses
    assert AffectedEdgeStatus.CONGESTED in statuses
    assert sum(edge.status == AffectedEdgeStatus.FLOODED for edge in result.affected_edges) == 3
    assert sum(edge.status == AffectedEdgeStatus.CONGESTED for edge in result.affected_edges) == 3

def test_random_scenario_raises_error_if_unreachable() -> None:
    """Test 3: Văng lỗi đúng chuẩn nếu điểm Start và Goal bị cô lập hoàn toàn."""
    graph = GraphLoader.from_directory(SIMPLE_PATH_DIR)
    service = RandomScenarioService(base_graph=graph)

    with pytest.raises(RouteNotFoundError, match="Could not generate a connected route"):
        service.generate(start="SP_C", goal="SP_A", num_edges=1, max_retries=3)
