import random
import uuid
from typing import Optional

from backend.app.core.contracts import (
    Graph,
    Scenario,
    RouteNotFoundError
)
from backend.app.core.cost import ScenarioCostEngine
from backend.app.algorithms.unweighted import breadth_first_search

# Import các model chúng ta vừa định nghĩa ở contracts
from backend.app.core.contracts import (
    AffectedEdge,
    AffectedEdgeStatus,
    RandomScenarioResponse
)

class RandomScenarioService:
    """Service sinh kịch bản giao thông ngẫu nhiên có kiểm soát (Reproducible)."""

    def __init__(self, base_graph: Graph):
        self.base_graph = base_graph

    def generate(
        self,
        start: str,
        goal: str,
        num_edges: int = 5,
        seed: Optional[str] = None,
        max_retries: int = 5
    ) -> RandomScenarioResponse:
        
        # Nếu không có seed từ frontend, tự sinh một chuỗi ngẫu nhiên
        current_seed = seed or f"RANDOM_{uuid.uuid4().hex[:8].upper()}"
        
        # Lấy danh sách toàn bộ ID của các cạnh hiện có trong đồ thị
        all_edge_ids = [edge.edge_id for edge in self.base_graph.list_edges()]
        
        if num_edges > len(all_edge_ids):
            num_edges = len(all_edge_ids)

        for attempt in range(max_retries):
            # Khởi tạo bộ sinh ngẫu nhiên với seed (đảm bảo tính reproducible)
            random.seed(current_seed)
            
            # Chọn ngẫu nhiên num_edges cạnh
            selected_edges = random.sample(all_edge_ids, num_edges)
            
            closed_edge_ids = []
            edge_overrides = {}
            affected_edges = []
            
            # Gán trạng thái cho các cạnh
            # Ràng buộc: Tối đa 1 cạnh bị CLOSED
            if selected_edges:
                closure_id = selected_edges[0]
                closed_edge_ids.append(closure_id)
                affected_edges.append(
                    AffectedEdge(edge_id=closure_id, status=AffectedEdgeStatus.CLOSED)
                )
            
            # Chia đều số lượng còn lại cho FLOODED và CONGESTED
            remaining_edges = selected_edges[1:]
            split_idx = len(remaining_edges) // 2
            
            for edge_id in remaining_edges[:split_idx]:
                # Ghi đè trọng số ngập lụt
                edge_overrides[edge_id] = {"flood_risk": 1.0, "data_status": "SIMULATED"}
                affected_edges.append(
                    AffectedEdge(edge_id=edge_id, status=AffectedEdgeStatus.FLOODED)
                )
                
            for edge_id in remaining_edges[split_idx:]:
                # Ghi đè trọng số kẹt xe
                edge_overrides[edge_id] = {"traffic_penalty_min": 5.0, "data_status": "SIMULATED"}
                affected_edges.append(
                    AffectedEdge(edge_id=edge_id, status=AffectedEdgeStatus.CONGESTED)
                )

            # Tạo một Scenario tạm thời để test
            scenario_id = f"SCENARIO_{current_seed}"
            test_scenario = Scenario(
                scenario_id=scenario_id,
                closed_edge_ids=tuple(closed_edge_ids),
                attributes={
                    "cost_preset": "BALANCED", 
                    "edge_overrides": edge_overrides
                }
            )
            
            # Nhúng scenario mới vào một phiên bản Graph tạm thời
            temp_graph = Graph(
                nodes=self.base_graph.nodes,
                edges=self.base_graph.edges,
                scenarios=[test_scenario]
            )
            temp_cost_engine = ScenarioCostEngine(temp_graph)

            try:
                # GỌI BFS ĐỂ KIỂM TRA TÍNH LIÊN THÔNG (REACHABILITY)
                # BFS chạy rất nhẹ, nếu nó trả về path nghĩa là đồ thị chưa bị đứt đôi
                breadth_first_search(
                    graph=temp_graph,
                    cost_engine=temp_cost_engine,
                    start=start,
                    goal=goal,
                    scenario_id=scenario_id
                )
                
                # Nếu không văng lỗi, kịch bản này hợp lệ -> Trả về kết quả
                return RandomScenarioResponse(
                    scenario_id=scenario_id,
                    affected_edges=affected_edges
                )
                
            except RouteNotFoundError:
                # Nếu BFS báo lỗi đứt đường, đổi seed và thử lại ở vòng lặp tiếp theo
                current_seed = f"{current_seed}_RETRY_{attempt}"

        # Nếu xui xẻo thử 5 lần vẫn đứt đường, raise lỗi để API báo 422 về cho người dùng
        raise RouteNotFoundError(
            f"Could not generate a connected route from {start} to {goal} after {max_retries} attempts."
        )