# MapLibre real basemap

Kế hoạch triển khai đầy đủ được lưu tại
[docs/plans/2026-08-09-maplibre-openfreemap.md](../plans/2026-08-09-maplibre-openfreemap.md).

## Kết quả

- Thay React Leaflet bằng MapLibre GL JS và OpenFreeMap `Liberty` vector basemap.
- Cấu hình worker MapLibre v6 qua Vite `?worker&url`/`setWorkerUrl` và loại khỏi
  `optimizeDeps` để tránh lỗi `maplibre-gl-worker.mjs` trong `.vite/deps`.
- Điều chỉnh vị trí nút reset viewport xuống dưới NavigationControl, tránh chồng với
  zoom/compass trên desktop và mobile.
- Giữ viewport ở min zoom 10.5, tắt world-copy và bỏ hard `maxBounds`. Initial/reset
  ưu tiên rectangle B bao polygon ranh A; graph context là fallback; endpoint đơn dùng
  zoom 16.5.
- Chuyển Node/Edge/route thành GeoJSON layers; giữ closed edge, explored node, endpoint
  và route animation theo response backend.
- Cho phép click mọi node bằng hitbox GPU; toolbar chọn START/GOAL, Escape để hủy và
  đồng bộ với searchable picker.
- Suy ra tên node từ POI hoặc road names kề; popup công bố `DERIVED LABEL` khi phù hợp.
- Thêm fallback nền trung tính khi basemap lỗi, attribution, navigation/scale/reset.

## Bằng chứng

- `npm run test:data`: PASS; dataset vẫn 90 node/155 edge và `REVIEW_REQUIRED`.
- `npm run test:backend`: 45 passed; một Starlette/httpx deprecation warning.
- `npm run test:frontend`: 16 passed.
- `npm run build:frontend`: PASS; có warning chunk MapLibre lớn hơn 500 kB.
- Dev smoke sau khi cấu hình worker: `src/main.tsx` và URL worker MapLibre trả HTTP 200.
- OpenFreeMap `Liberty` style endpoint: HTTP 200, JSON hợp lệ.
- `npm audit --omit=dev`: không có production vulnerability.
