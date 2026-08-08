# Plan đã triển khai: bản đồ thực tế cho FloodRoute

**Ngày:** 2026-08-09  
**Trạng thái:** Đã triển khai và kiểm thử  
**Phạm vi:** frontend map renderer; không thay đổi REST API, graph contract, cost model hoặc topology định tuyến.

## 1. Mục tiêu

Thay lớp bản đồ CSS/React Leaflet bằng bản đồ vector thực tế để FloodRoute có ngữ cảnh đường phố, tên đường, POI và công trình trong khu vực chợ Thủ Đức. Người dùng vẫn có thể xem toàn bộ graph 90 node/155 cạnh và chọn trực tiếp node làm START hoặc GOAL.

## 2. Quyết định kỹ thuật

- Dùng [MapLibre GL JS](https://maplibre.org/maplibre-gl-js/docs) để render WebGL.
- Dùng style [OpenFreeMap Liberty](https://openfreemap.org/quick_start/) làm basemap mặc định.
- Cho phép thay style qua biến môi trường `VITE_BASEMAP_STYLE_URL`.
- Không dùng runtime reverse-geocoding, Google Places, satellite hoặc routing của nhà cung cấp bản đồ.
- Basemap chỉ là lớp trực quan; UTraffic vẫn là nguồn topology và cost duy nhất.
- Giữ attribution OpenFreeMap/OpenStreetMap trên bản đồ theo [ODbL/OSM copyright](https://www.openstreetmap.org/copyright).

## 3. Các bước đã thực hiện

### 3.1. Thay renderer và dependency

- Gỡ `leaflet`, `react-leaflet` và `@types/leaflet`.
- Cài `maplibre-gl` và CSS runtime tương ứng.
- Thêm `frontend/.env.example` cho URL style công khai.
- Cấu hình worker MapLibre v6 bằng import `?worker&url` và `setWorkerUrl`.
- Loại `maplibre-gl` khỏi `optimizeDeps` để Vite không tìm worker trong cache `.vite/deps`.

### 3.2. Chuyển graph sang GeoJSON

- Tạo `frontend/src/features/map/mapData.ts` với ba bộ dữ liệu:
  - edge topology;
  - node topology;
  - route đang chạy theo thứ tự edge.
- Bỏ qua node thiếu tọa độ khi render nhưng không mutate graph backend.
- Giữ trạng thái `start`, `goal`, `path`, `explored`, `default` để layer hiển thị nhất quán.
- Edge đóng được vẽ đỏ nét đứt; route tối ưu có lớp halo trắng và lớp tím.

### 3.3. Hiển thị tên node deterministic

Thứ tự ưu tiên nhãn:

1. Tên POI có sẵn — `SOURCE_BACKED`.
2. Hai hoặc nhiều đường kề — `Giao A × B` — `DERIVED`.
3. Một đường kề — `Nút trên A` — `DERIVED`.
4. Không có tên đường — `Node tại <lat>, <lon>` — `DERIVED`.

Nhãn chỉ dùng cho presentation và popup, không ghi ngược vào dataset.

### 3.4. Chọn START/GOAL trên bản đồ

- Thêm toolbar `Chọn START`, `Chọn GOAL`, `Hủy chọn`.
- Khi chế độ chọn đang bật, click vào hitbox của node sẽ gọi callback chọn endpoint.
- Sau khi chọn, chế độ tự tắt và searchable picker được đồng bộ.
- `Escape` hủy chế độ chọn.
- Thay đổi endpoint, scenario hoặc swap endpoint đều xóa route/compare result cũ.
- Khi có endpoint, bản đồ tự focus; nút reset đưa viewport về toàn graph.

### 3.5. Khả năng lỗi

- Nếu style OpenFreeMap không tải được trước khi map sẵn sàng, MapLibre chuyển sang nền trung tính cục bộ.
- Graph source/layer vẫn được cài và thuật toán vẫn chạy khi basemap lỗi.
- Lỗi tile sau khi map đã tải chỉ hiện cảnh báo không chặn.

### 3.6. Tài liệu và kiểm thử

- Tạo [ADR 0008](../decisions/0008-maplibre-openfreemap-basemap.md).
- Cập nhật architecture, runbook, README, changelog và progress log.
- Thêm unit test cho GeoJSON, nhãn node và trạng thái layer.
- Thêm component test mock MapLibre cho lifecycle, source/layer, click node, toolbar và cleanup.

## 4. Interface frontend mới

`RouteMap` giữ các input graph/route hiện có và bổ sung:

```ts
pickTarget: 'START' | 'GOAL' | null
onNodePick: (target: 'START' | 'GOAL', nodeId: string) => void
onPickTargetChange: (target: 'START' | 'GOAL' | null) => void
```

REST API, schema graph và cost/search contract không thay đổi.

## 5. Nghiệm thu

- `npm run test:data`: PASS; dataset 90 node/155 directed edge.
- `npm run test:backend`: 45 tests PASS.
- `npm run test:frontend`: 16 tests PASS.
- `npm run build:frontend`: PASS.
- OpenFreeMap Liberty style endpoint đã kiểm tra HTTP 200 và JSON hợp lệ.
- `npm audit --omit=dev`: không có production vulnerability.

## 6. Giới hạn đã biết

- OpenFreeMap là dịch vụ online best-effort, không phải nguồn real-time.
- Build frontend có cảnh báo chunk lớn do MapLibre (~1.15 MB trước gzip).
- Basemap không làm thay đổi topology hoặc cost; nó chỉ cung cấp ngữ cảnh trực quan.
- Chưa có browser smoke test thủ công trên trình duyệt thật trong môi trường hiện tại; component behavior đã được kiểm tra bằng mock jsdom.

## 7. Việc có thể làm tiếp theo

- Tự host style/vector tile nếu cần SLA hoặc demo offline hoàn toàn.
- Tách MapLibre thành lazy-loaded chunk để giảm bundle khởi động.
- Bổ sung browser E2E test trên Chromium với network online/offline.
- Bổ sung nhãn POI/road được xác minh ở pipeline dữ liệu nếu cần dùng ngoài mục đích demo/nghiên cứu.
