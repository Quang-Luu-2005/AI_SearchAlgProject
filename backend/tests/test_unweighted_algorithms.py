import json
from pathlib import Path
from typing import Any

import pytest

from backend.app.algorithms.unweighted import breadth_first_search, depth_first_search
from backend.app.core.cost import ScenarioCostEngine
from backend.app.core.graph import GraphLoader

# 1. Khai báo các đường dẫn chuẩn
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
TOY_GRAPH_DIR = REPOSITORY_ROOT / "data" / "fixtures" / "toy_graph_v0.1"
TEST_CASES_PATH = TOY_GRAPH_DIR / "test_cases.json"


def load_two_point_cases() -> list[dict[str, Any]]:
    """Đọc file test_cases.json và chỉ lọc ra các bài toán tìm đường 2 điểm (two-point)."""
    with TEST_CASES_PATH.open(encoding="utf-8") as file:
        data = json.load(file)
    
    # Chỉ lấy các case có mode là 'two-point' (bỏ qua 'multi-stop')
    return [case for case in data["cases"] if case["mode"] == "two-point"]


# 2. Tạo Fixture nạp đồ thị 1 lần duy nhất để tối ưu tốc độ chạy test (scope="module")
@pytest.fixture(scope="module")
def toy_graph():
    return GraphLoader.from_directory(TOY_GRAPH_DIR)


@pytest.fixture(scope="module")
def cost_engine(toy_graph):
    return ScenarioCostEngine(toy_graph)


# 3. Sử dụng parametrize để tự động lặp qua từng test case đã load
@pytest.mark.parametrize(
    "case", 
    load_two_point_cases(), 
    ids=lambda c: c["case_id"]  # Hiển thị tên case_id trên terminal cho đẹp
)
def test_bfs_dfs_against_golden_cases(toy_graph, cost_engine, case):
    """
    Tự động chạy BFS và DFS qua các kịch bản OFFPEAK, PEAK_TRAFFIC và HEAVY_RAIN_SAFE.
    """
    start_id = case["start"]
    goal_id = case["goal"]
    scenario_id = case["scenario_id"]

    # Chạy thuật toán
    bfs_result = breadth_first_search(toy_graph, cost_engine, start_id, goal_id, scenario_id)
    dfs_result = depth_first_search(toy_graph, cost_engine, start_id, goal_id, scenario_id)

    # ĐẢM BẢO 1: Cả hai thuật toán không bị crash do lỗi đóng cạnh ngập lụt
    assert len(bfs_result.path) > 0, f"BFS failed to find path in {scenario_id}"
    assert len(dfs_result.path) > 0, f"DFS failed to find path in {scenario_id}"

    # ĐẢM BẢO 2: Cả hai thuật toán đều thực sự chạm đến đích
    assert bfs_result.path[-1] == goal_id, "BFS did not reach goal"
    assert dfs_result.path[-1] == goal_id, "DFS did not reach goal"

    # ĐẢM BẢO 3: Định lý BFS luôn tìm đường ít số chặng (hop) nhất
    # Dù kịch bản là mưa ngập hay kẹt xe, số node BFS đi qua luôn nhỏ hơn hoặc bằng DFS
    assert len(bfs_result.path) <= len(dfs_result.path), "BFS path has more hops than DFS"