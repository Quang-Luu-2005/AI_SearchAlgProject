# Tiến độ: BE-04 Triển khai UCS, A* và Geographic Weighted Haversine Heuristic

**Ngày thực hiện:** 2026-08-10  
**Tác giả:** Antigravity AI  
**Hạng mục:** Backend Search Engine & Algorithms

## Tóm tắt công việc

1. **Thuật toán Weighted Search ([`weighted.py`](file:///c:/Study/foundation_AI/AI_SearchAlgProject/backend/app/algorithms/weighted.py)):**
   - Triển khai Uniform Cost Search (UCS) với priority $f(n) = g(n)$ và tie-break ưu tiên cost thấp hơn, sau đó xếp alphabet theo `node_id`.
   - Triển khai A* Search với priority $f(n) = g(n) + h(n)$ và heuristic khoảng cách đại cầu Haversine kết hợp trọng số khoảng cách của scenario ($w_{\text{dist}}$).
   - Đóng gói TraceEvent ghi nhận chính xác $g\_cost$ và $h\_cost$ tại các bước `OPEN`, `EXPAND`, `RELAX`, `CLOSE`, `GOAL`, `FAIL` phục vụ replay trace trên UI.

2. **Quyết định kiến trúc ([`ADR-0008`](file:///c:/Study/foundation_AI/AI_SearchAlgProject/docs/decisions/0008-geographic-weighted-haversine-heuristic-astar.md)):**
   - Lập tài liệu ADR-0008 xác lập công thức $h(n) = w_{\text{dist}} \cdot D_{\text{Haversine}}(n, \text{goal})$.
   - Cung cấp chứng minh toán học đầy đủ về tính **Admissible** ($h(n) \le h^*(n)$) và tính **Consistent / Monotonic** ($h(u) \le c(u, v) + h(v)$).

3. **Kiểm thử tự động ([`test_weighted_algorithms.py`](file:///c:/Study/foundation_AI/AI_SearchAlgProject/backend/tests/test_weighted_algorithms.py)):**
   - Kiểm tra tính đúng đắn của công thức Haversine giữa các điểm tọa độ WGS84 thực tế.
   - Kiểm tra tính tương thích fallback $h=0$ trên graph không có tọa độ (toy graph).
   - So sánh kết quả route giữa UCS và A* trên dataset chợ Thủ Đức (`thu_duc_market_v1.0.0`), xác nhận A* mở rộng số lượng node ít hơn hoặc bằng UCS trong khi giữ nguyên optimal cost.

## Kết quả kiểm thử

- `pytest backend/tests/` vượt qua 100% các bài test (25/25 tests pass).
- Validator dataset `python scripts/data/validate_dataset.py` kiểm tra thành công tất cả checksum và golden path.
