# ADR-0003: Immutable directed graph loader

- Trạng thái: Accepted
- Ngày: 2026-08-05

## Bối cảnh

Các search algorithm sắp dùng chung graph fixture/processed. Nếu mỗi algorithm
tự đọc CSV hoặc tự tạo adjacency map, thứ tự neighbor và cách áp dụng scenario
có thể khác nhau; nếu mutate adjacency map, các lần chạy sau không còn tái lập.

## Quyết định

- Đặt `Node`, `Edge`, `Scenario`, `Graph` và `GraphView` trong core contracts,
  không phụ thuộc FastAPI.
- Chỉ biểu diễn directed edge; chiều ngược phải là edge riêng trong dữ liệu.
- Dùng `GraphLoader` cho CSV/JSON và lưu metadata mở rộng trong immutable mapping.
- `Graph.for_scenario()` tạo view lọc `closed_edge_ids`; không xóa hoặc sửa edge
  trong graph gốc.
- Adjacency và neighbor được sắp xếp deterministic theo node đích rồi edge ID.

## Hệ quả

- Algorithm có một contract chung, có thể unit test độc lập HTTP.
- Scenario closure không gây side effect giữa các lần chạy.
- Graph nhỏ có thể dùng `GraphLoader.from_directory()`; processed release sau này
  chỉ cần tuân format hiện tại.
- Các quyết định về cost, heuristic và search result vẫn thuộc các card sau.

## Bằng chứng

`backend/tests/test_graph.py` kiểm tra fixture 6 node, CSV/JSON loading, one-way
direction, deterministic neighbors, missing node, scenario closure, cycle và
mutation protection.
