# 2026-08-16 — Tích hợp BFS/DFS vào API và GUI

## Mục tiêu

Thực hiện mục tiêu P0 trong `PLAN.md`: đưa BFS và DFS từ contract/registry lên
luồng two-point search, giao diện và chế độ so sánh; bổ sung bằng chứng cho các
case reachable, unreachable, cycle và start=goal.

## Thay đổi đã thực hiện

- Giữ BFS/DFS trong registry framework-independent và làm rõ frontier discovery:
  node được đánh dấu ngay khi enqueue/push, tránh parent bị ghi đè khi graph có cycle.
- Frontend hỗ trợ chọn `BFS` và `DFS`, gọi `/api/v1/search`, và compare đồng thời
  `UCS`, `A_STAR`, `BFS`, `DFS`.
- Loại bỏ limitation API cũ nói A* luôn dùng `h=0`; response hiện nhất quán với
  heuristic Haversine và fallback `h=0` khi thiếu tọa độ.
- Cập nhật API/kiến trúc/README/algorithm docs và changelog để phản ánh trạng thái mới.
- Bổ sung API tests cho BFS/DFS và unweighted tests cho start=goal, directed cycle,
  unreachable directed goal.

## Quyết định/giả định

- BFS tối ưu theo số hop, không theo weighted cost; DFS không có guarantee tối ưu.
- Neighbor ordering vẫn deterministic theo contract hiện có; không thay đổi graph,
  cost model hoặc dataset.
- Compare API giữ default tương thích `UCS` + `A_STAR`; frontend truyền rõ bốn
  thuật toán để tránh thay đổi ngầm API contract.

## Bằng chứng kiểm tra

- `..\\.venv\\Scripts\\python.exe -m pytest` từ `backend/` — **82 passed**, 1 warning
  deprecation từ Starlette/httpx.
- `npm --prefix frontend run test` — **50 passed**.
- `npm run build:frontend` — build production thành công; Vite còn cảnh báo chunk JS lớn.
- `npm run test:data` — **FAIL** do checksum mismatch có sẵn ở hai raw OSM file;
  không có thay đổi nào trong `data/raw/` và không sửa manifest.

## Tồn tại/rủi ro

- Trace hiện vẫn là event log dùng chung; hiển thị frontier/closed đầy đủ theo từng
  frame là mục tiêu tiếp theo trong `PLAN.md`.
- Greedy/Bidirectional chưa được mở thành lựa chọn GUI trong bước này.

## Bước tiếp theo

Hoàn thiện trace player và metrics two-point, sau đó dùng scenario nhiều trạng thái để
chứng minh tuyến thay đổi do congestion/flood penalty.
