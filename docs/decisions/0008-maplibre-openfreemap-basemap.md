# ADR 0008: MapLibre GL JS và OpenFreeMap basemap

- Trạng thái: Accepted
- Ngày: 2026-08-09
- Thay thế: phần React Leaflet trong ADR 0001

## Bối cảnh

Renderer Leaflet cũ chỉ vẽ Node/Edge trên nền CSS nên thiếu đường phố, địa danh và ngữ
cảnh thật. Yêu cầu mới cần hiển thị toàn bộ node có thể click trên graph lớn, vẫn giữ
route animation và không làm basemap thành phụ thuộc bắt buộc của thuật toán.

## Quyết định

Dùng MapLibre GL JS để render graph thành GeoJSON source/layer bằng WebGL. Basemap mặc
định dùng OpenFreeMap style `Liberty`, cấu hình qua `VITE_BASEMAP_STYLE_URL`. Graph
UTraffic vẫn là nguồn topology/cost duy nhất; basemap chỉ cung cấp ngữ cảnh.

MapLibre v6 được cấu hình worker tường minh qua Vite `?worker&url` và `setWorkerUrl`;
`maplibre-gl` được loại khỏi `optimizeDeps` để tránh Vite tìm worker trong thư mục
`.vite/deps` sau khi cache dependency bị stale.

Node không có POI name được gán display label deterministic từ `road_name` của edge kề.
Tên này mang nghĩa `DERIVED LABEL`, không ghi ngược vào raw/processed dataset. Mọi node
có một hitbox layer trong suốt để click; START và GOAL được đặt qua chế độ chọn rõ ràng.

Nếu remote style không tải được, renderer chuyển sang style nền trung tính cục bộ và
vẫn cài graph sources/layers. Không dùng geocoder, satellite hoặc provider routing.

Camera dùng `minZoom=10.5`, `renderWorldCopies=false` và `maxBounds` theo ADR 0010.
Initial/reset ưu tiên rectangle có padding bao trọn polygon ranh TP Thủ Đức cũ; context
ring động của graph chỉ là fallback khi boundary chưa sẵn sàng.

## Hệ quả

- Bản đồ có tên đường/POI thật và layer graph hiệu năng tốt hơn khi số node tăng.
- Frontend bundle lớn hơn vì MapLibre/WebGL; production build có thể cảnh báo chunk lớn.
- Basemap cần mạng và là best-effort, nhưng search/compare và graph fallback vẫn chạy.
- Attribution OpenFreeMap/OpenStreetMap phải luôn hiển thị trên map.
