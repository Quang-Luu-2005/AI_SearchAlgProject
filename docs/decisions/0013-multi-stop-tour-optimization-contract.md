# ADR-0013 — Hợp đồng tối ưu hóa tour đa điểm

## Status

Accepted.

## Context

Card OPT bổ sung tối ưu hóa lộ trình giao hàng đa điểm vào graph có hướng và cost thay
đổi theo scenario. Tính năng phải dùng lại graph/cost/search contract hiện có, không
mutate graph, có tie-break deterministic và phân biệt rõ bảo đảm chính xác với heuristic.
API cũng cần giới hạn kích thước để Held-Karp không tăng chi phí ngoài phạm vi demo.

## Decision

- Cung cấp `POST /api/v1/optimize-tour` với một depot và từ 5 đến 10 stop duy nhất;
  depot không được lặp trong `stops`.
- `algorithm` chọn search engine cho từng cặp điểm. `tour_algorithm` chỉ nhận
  `HELD_KARP` hoặc `NEAREST_NEIGHBOR`; giá trị khác trả về HTTP 422, không fallback ngầm.
- Tạo ma trận chi phí có hướng bằng `SearchService` trên cùng immutable `Graph`, scenario
  và `ScenarioCostEngine` như tìm đường hai điểm. Không định nghĩa cost riêng cho tour.
- Held-Karp DP có độ phức tạp $O(N^2 2^N)$ và cho nghiệm tối ưu theo ma trận shortest-path
  đã tạo. Nearest Neighbor chọn cost thấp nhất, tie-break theo index điểm đầu vào, và chỉ
  mang bảo đảm heuristic.
- Chạy cả hai solver để trả comparison và approximation gap; route được chọn theo
  `tour_algorithm`. Subpath liên tiếp được ghép mà không lặp node ở ranh chặng.
- Bảo đảm `OPTIMAL_HELD_KARP` chỉ nói về graph, scenario và cost snapshot đang dùng;
  không phải tuyên bố tối ưu hay an toàn ngoài đời thực.

## Consequences

- Tổng số điểm tối đa là 11 tính cả depot, giữ thời gian/bộ nhớ Held-Karp phù hợp demo.
- Request lặp depot/stop hoặc dùng tên thuật toán tour không hỗ trợ bị từ chối sớm và
  có test regression.
- Graph có hướng có thể làm một số cặp không reachable; khi không tồn tại tour hợp lệ,
  API trả lỗi route thay vì tạo kết quả một phần.
- Kết quả vẫn phụ thuộc chất lượng và trạng thái provenance của dataset; traffic lịch sử
  không được trình bày như dữ liệu real-time.

## Alternatives rejected

- Tự tạo cost Euclidean cho tour sẽ lệch khỏi cost/search contract và bỏ qua đường một chiều.
- Cho phép nhiều hơn 10 stop với Held-Karp đồng bộ trong request sẽ làm thời gian tăng theo
  hàm mũ; quy mô lớn hơn cần heuristic hoặc kiến trúc job riêng.
- Tự động coi mọi tên `tour_algorithm` không hợp lệ là Held-Karp che giấu lỗi client.
