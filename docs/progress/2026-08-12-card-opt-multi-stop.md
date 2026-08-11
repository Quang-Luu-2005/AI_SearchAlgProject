# 2026-08-12 — Card OPT: Pairwise Matrix, Held-Karp, Nearest Neighbor & Tour Optimizer Service

## Mục tiêu
Triển khai hoàn chỉnh tính năng tối ưu hóa lộ trình giao hàng qua 5–10 điểm (Card OPT) nhằm phục vụ bài toán định tuyến đa điểm cho shipper xe máy:
- Tạo ma trận chi phí và khoảng cách từng cặp điểm (`PairwiseMatrix`).
- Triển khai thuật toán chính xác **Held-Karp Dynamic Programming** ($O(N^2 \cdot 2^N)$) và thuật toán xấp xỉ tham lam **Nearest Neighbor**.
- Xây dựng **TourOptimizerService** thực hiện ghép nối danh sách đường đi (Subpath Stitching), tính khoảng cách chênh lệch (% Approximation Gap) và sinh thông điệp giải thích/bảo đảm có cấu trúc.
- Cung cấp REST API endpoint `POST /api/v1/optimize-tour` và bộ unit/integration test suite `TC04_MULTI_STOP`.

## Thay đổi đã thực hiện
1. **Module Optimization (`backend/app/optimization/`)**:
   - `matrix.py`: Class `PairwiseMatrix` tính toán ma trận vuông $N \times N$ bằng `SearchService`, lưu trữ chi tiết các chặng `PairwiseSubpath` và xử lý ngõ cụt.
   - `nearest_neighbor.py`: Class `NearestNeighborSolver` thực hiện giải thuật Greedy TSP có tie-breaking deterministic.
   - `held_karp.py`: Class `HeldKarpSolver` thực hiện DP memoization bằng bitmask, kèm class `BruteForceSolver` kiểm tra hoán vị trên đồ thị nhỏ.
   - `service.py`: Class `TourOptimizerService` điều phối bài toán, ghép nối `full_path` và `edge_ids` không bị lặp nút giáp ranh, sinh `guarantee` (`OPTIMAL_HELD_KARP`) và `explanation`.
2. **API Endpoint & Schema (`backend/app/api/`)**:
   - `models.py`: Thêm `OptimizeTourRequest`, `OptimizeTourResponse`, `TourComparisonResponse` và `TourLegResponse`.
   - `router.py`: Đăng ký endpoint `POST /api/v1/optimize-tour` hỗ trợ từ 1 đến 10 điểm giao hàng.
3. **Test Suite & Verification (`backend/tests/`)**:
   - `test_tc04_multi_stop.py`: Bộ 8 unit/integration tests bao phủ 100% các mục checklist.

## Quyết định/Giả định
- **Giới hạn số điểm**: Giới hạn `stops` tối đa 10 điểm (tổng $N \le 11$ tính cả depot) để Held-Karp DP chạy trong vòng dưới 100 ms.
- **Bảo tồn core search**: Không thay đổi bất kỳ logic tìm kiếm hay hợp đồng đồ thị bất biến sẵn có nào.
- **Subpath Stitching**: Loại bỏ nút lặp trùng ở giao điểm các chặng kế tiếp để danh sách `full_path` biểu diễn liên tục trên bản đồ render GPU.

## Bằng chứng kiểm tra
- Chạy toàn bộ backend test suite với pytest:
  `node scripts/python.mjs -m pytest backend/tests -v`
  **Kết quả: 58 PASS, 3 SKIPPED, 0 FAIL (100% PASS)**.
