# Desktop Collapsed Panel Scale Bar Optimization (5km Scale Alignment)

- **Date**: 2026-08-12
- **Task**: Cấu hình tự động căn chỉnh khoảng thu phóng (Zoom level ~11.8 - 12.0) khi thu gọn Panel ở chế độ Desktop để thước đo tỷ lệ (`ScaleControl`) hiển thị chính xác mốc **`5 km`**.

## Changes Made
1. **`frontend/src/features/map/RouteMap.tsx`**:
   - Cập nhật thông số `maxWidth: 180` cho `ScaleControl` để MapLibre chọn mốc khoảng cách tròn `5 km` khi mở rộng vùng quan sát thành phố.
   - Thêm `useEffect` tự động lắng nghe biến `isSidebarCollapsed`: Khi Panel bị thu gọn ở chế độ Desktop, bản đồ tự động gọi `map.resize()` và căn chỉnh `fitBounds` theo vùng bao TP. Thủ Đức với `maxZoom: 12.0`.
   - Kết quả: Thước đo tỷ lệ scale hiển thị chính xác **`5 km`** mượt mà.

2. **Verification**:
   - Chạy thành công 10/10 test files (43 unit tests passed).
