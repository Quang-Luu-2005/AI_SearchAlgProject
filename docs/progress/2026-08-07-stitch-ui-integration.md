# 2026-08-07 — Thay UI Stitch và tích hợp Backend API

## Mục tiêu

Chuyển bản thiết kế tĩnh `stitch_optimal_path_finder.zip` thành frontend
React/TypeScript responsive và nối toàn bộ dữ liệu hiển thị với backend BE-03.

## Thay đổi đã thực hiện

- Chuyển visual Pathfinder AI sang React/CSS, giữ bố cục fixed sidebar, fluid
  graph canvas, legend và thanh metrics của thiết kế.
- Nạp graph catalog, locations và scenarios từ `/api/v1`.
- Gọi `/search` cho UCS/A* và `/compare` cho chế độ so sánh.
- Tô đường tối ưu, node start/goal, node đã duyệt và cạnh bị đóng trên React Leaflet.
- Bổ sung nút reset viewport, marker start/goal cam-hồng có label cố định và
  animation vẽ lần lượt từng cạnh của đường tối ưu màu tím có viền sáng.
- Hiển thị metrics, path, guarantee, explanation, lỗi backend và nhãn `SIMULATED`.
- Bổ sung test client cho locations, search và compare.
- Chuẩn hóa `npm test` để test data/backend dùng Python từ `.venv`.

## Bằng chứng kiểm tra

- Frontend unit tests: 8 passed.
- TypeScript + Vite production build: PASS (61 modules).
- Full `npm test`: PASS (dataset, 37 backend tests, 8 frontend tests).

## Giới hạn

- Font web có fallback system font nếu máy chạy không truy cập được Google Fonts.
- A* hiện dùng `h=0` theo ADR-0006 và vì vậy có hành vi tương đương UCS.
