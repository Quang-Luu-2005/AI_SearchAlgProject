# 2026-08-07 — BE-03 Xây dựng API Backend

## Mục tiêu

Cung cấp API locations/scenarios/search/compare chạy thật trên toy graph, validate
input và trả đầy đủ path, metrics, trace, guarantee, explanation.

## Thay đổi đã thực hiện

- Thêm registry deterministic cho `UCS` và `A_STAR`; A* dùng `h=0`.
- Thêm `SearchService` framework-independent dùng chung cost/scenario engine.
- Thêm Pydantic request/response models và OpenAPI example.
- Thêm `GET /api/v1/locations`, `GET /api/v1/scenarios`,
  `POST /api/v1/search`, `POST /api/v1/compare`.
- Validate start/goal/algorithm/scenario; trả 404 cho input không tồn tại/no route
  và 422 cho algorithm/cost/request không hợp lệ.
- Response gồm path, edge IDs, metrics, trace, guarantee, explanation, edge
  breakdown, data status và limitations.
- Thêm API/service tests, ADR-0006, API docs, architecture/runbook/README/changelog.

## Quyết định/giả định

A* chưa dùng khoảng cách địa lý vì chưa có heuristic cùng đơn vị cost được chứng
minh. `h=0` giữ bảo đảm optimal với cost không âm và tránh claim vượt bằng chứng.

## Bằng chứng kiểm tra

- Request `N01 → N06`, `A_STAR`, `HEAVY_RAIN_SAFE` trả HTTP 200 và path
  `N01 → N02 → N04 → N06`.
- Full backend suite: 37 passed; còn 1 TestClient dependency deprecation warning.
- OpenAPI test xác nhận đủ bốn endpoint và example bàn giao.
- Dataset validator: PASS; frontend: 5 passed; production build: PASS (62 modules).

## Tồn tại/rủi ro

- Registry mới có `UCS` và `A_STAR`; BFS/DFS/Greedy/Bidirectional thuộc card thuật toán.
- A* `h=0` đúng nhưng chưa nhanh hơn UCS.
- TestClient còn dependency deprecation warning đã biết.

## Bước tiếp theo

Tích hợp frontend với API, triển khai các thuật toán còn lại và chỉ thay heuristic
A* sau khi có ADR/test admissibility-consistency.
