# Hide Map Attribution Component

- **Date**: 2026-08-12
- **Task**: Xóa dòng chữ Map Attribution / Map Attribute khỏi giao diện bản đồ theo yêu cầu người dùng.

## Changes Made
1. **`frontend/src/features/map/RouteMap.tsx`**:
   - Loại bỏ `map.addControl(new maplibregl.AttributionControl(...))` khi khởi tạo bản đồ MapLibre GL JS.

2. **`frontend/src/App.tsx`**:
   - Loại bỏ thẻ `<p className="dataset-attribution">` hiển thị thông tin bản quyền dữ liệu dưới khu vực bản đồ.

3. **`frontend/src/styles.css`**:
   - Thêm quy tắc ẩn toàn bộ control attribution MapLibre (`.maplibregl-ctrl-attrib { display: none !important; }`).

## Verification
- Chạy `npm test` thành công (10 test files, 43 unit tests passed).
