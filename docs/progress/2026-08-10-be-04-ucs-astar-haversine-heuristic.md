# Nhật ký tiến độ: Refactor Thuật toán Tìm kiếm Trọng số (UCS & A*) và Geographic Haversine Heuristic

**Ngày thực hiện:** 2026-08-10  
**Tác giả:** Antigravity AI  
**Hạng mục:** BE-04 Refactoring Search Algorithms & Mathematical Heuristic Proofs

## Tóm tắt công việc

1. **Refactor Modular Code trong [`backend/app/algorithms/weighted.py`](file:///c:/Study/foundation_AI/AI_SearchAlgProject/backend/app/algorithms/weighted.py):**
   - Tách biệt trợ lý tính khoảng cách WGS84 `haversine_distance_km(lat1, lon1, lat2, lon2)`.
   - Xây dựng hàm heuristic địa lý độc lập `compute_geographic_heuristic(graph, cost_engine, node_id, goal_id, scenario_id)` với công thức $h(n) = w_{\text{dist}} \cdot D_{\text{Haversine}}(n, \text{goal})$.
   - Đóng gói hàm lõi `_weighted_search()` nhận `heuristic_fn` động và quản lý Priority Queue (`heapq`).
   - Cung cấp hai entry point rõ ràng `uniform_cost_search()` ($h=0$) và `a_star_search()` ($h \ge 0$).
   - Nhúng pseudocode chi tiết trong docstring từng hàm.

2. **Chứng minh Toán học & Đánh giá Thuật toán:**
   - **Tính Admissible (Chấp nhận được):** Cho $h(n) \le h^*(n)$ với mọi nút $n$ do khoảng cách chim bay $D_{\text{Haversine}} \le d^*(n, \text{goal})$ và $c(e) \ge w_{\text{dist}} \cdot d(e)$.
   - **Tính Consistent (Nhất quán/Monotonic):** Cho $h(n) \le c(n, n') + h(n')$ thỏa mãn nhờ bất đẳng thức tam giác địa lý.
   - **Tính Optimal (Tối ưu):** **100% Globally Optimal** cho mọi mạng đồ thị có trọng số cạnh không âm $c(e) \ge 0$.
   - **Tính Complete (Đầy đủ):** Tìm thấy lời giải nếu tồn tại đường đi trên đồ thị hữu hạn có chi phí cạnh bị chặn dưới $c(e) \ge \epsilon > 0$.

3. **ADR & Unit Tests:**
   - Đã tạo [ADR-0012](file:///c:/Study/foundation_AI/AI_SearchAlgProject/docs/decisions/0012-geographic-weighted-haversine-heuristic.md).
   - Đã viết unit test suite [`backend/tests/test_weighted_algorithms.py`](file:///c:/Study/foundation_AI/AI_SearchAlgProject/backend/tests/test_weighted_algorithms.py).

## Kết quả kiểm thử

- `python -m pytest backend/tests` -> PASS 100% (53/53 tests pass).
- `npm test` -> PASS 100% (Data validation, Backend Pytest, Frontend Vitest).
