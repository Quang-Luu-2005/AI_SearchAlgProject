# Progress Log: 2026-08-12 — Triển khai Giao diện Responsive Đa Thiết Bị (Mobile / Tablet / Desktop)

## Summary of Tasks Executed

1. **Thiết kế Hệ thống Off-Canvas Mobile Drawer (`App.tsx` & `styles.css`)**:
   - Tự động chuyển Bảng điều khiển (`.control-panel`) sang dạng Side Drawer trượt off-canvas trên màn hình di động/máy tính bảng (< 1024px).
   - Thêm nút Hamburger menu (`☰`) trên Topbar để mở/đóng drawer linh hoạt.
   - Bổ sung lớp phủ mờ (`.mobile-drawer-backdrop`) với hiệu ứng làm mờ nền (backdrop blur) và cho phép nhấp ra ngoài hoặc bấm phím `Escape` để đóng drawer.
   - Nút đóng (`✕`) xuất hiện ở góc phải tiêu đề điều khiển trong chế độ mobile.

2. **Resize MapLibre GL Canvas Tự Động (`RouteMap.tsx`)**:
   - Giữ nguyên cơ chế `ResizeObserver` kết hợp hiệu ứng `requestAnimationFrame` giúp canvas bản đồ tự động căn chỉnh lại kích thước mà không vỡ tiles hay hổng viewport khi mở/đóng mobile drawer.

3. **Tối ưu Bố cục Responsive trên Mobile (< 640px) & Tablet (< 1024px)**:
   - **Topbar & Mobile Drawer**: Tối ưu padding, font chữ `clamp`, loại bỏ nút **"Xóa kết quả"** thừa trên Topbar ngang và tập trung nút **"🗑️ Xóa kết quả"** trực tiếp bên trong Bảng điều khiển Mobile Drawer (`.panel-clear-button`).
   - **Chú Thích Bản Đồ & Nút Nguồn Dữ Liệu (Attribution Control)**:
     - Trên **Desktop (> 1024px)**: Ẩn nút floating chú thích (`.map-legend-toggle-btn` / `.map-legend-popover`) trong lòng canvas bản đồ, hiển thị bảng chú thích tĩnh (`.legend`) bên dưới bản đồ.
     - Trên **Mobile & Tablet (< 1024px)**: Bật nút floating chú thích (`.map-legend-toggle-btn`) trực tiếp trên canvas cho phép xem chú thích 1-tap, đồng thời **ẩn nút "Toggle Attribute"** / `ⓘ` MapLibre attribution (`.maplibregl-ctrl-attrib`, `.maplibregl-ctrl-attrib-button`) để giữ cho canvas bản đồ di động hoàn toàn thông thoáng.
     - Nâng cấp **Cụm nút chọn điểm xuất phát (`📍 Pick Start`) & điểm kết thúc (`🎯 Pick Goal`)** (`.map-pick-toolbar`) dạng Card kính mờ bo tròn `12px` với thuộc tính `display: inline-flex; width: max-content; flex: 0 0 auto;`, triệt tiêu hoàn toàn khoảng trắng thừa tràn ra bên phải, ôm vừa khít 2 nút bấm với khoảng đệm `3px/4px` cực kỳ tinh tế và gọn gàng trên thiết bị di động.
   - **Trace Player (Thanh Tua Thuật Toán)**:
     - Thiết kế lại bố cục dạng Card kẹp kính mờ (`backdrop-filter: blur(14px)`) mượt mà trên Mobile & Tablet.
     - Dàn trang cụm điều khiển nút bấm (`⏮`, `◀`, `▶/⏸`, `▶`) dạng Flex full-width 4 cột cân đối với nút Play nổi bật rộng gấp đôi.
     - Tách dòng thông số `Step counter` & `Speed selector` sang hàng tiêu đề riêng (`.player-timeline-meta`), nhường toàn bộ chiều ngang bên dưới cho thanh slider (`.step-slider`) 100% giúp thao tác tua trên màn hình cảm ứng di động cực kỳ chính xác.
   - **Thước Đo Tỉ Lệ Khoảng Cách Đa Thiết Bị (`.maplibregl-ctrl-scale`)**:
     - Thiết kế lại khung thước đo khoảng cách MapLibre linh hoạt, mượt mà và tỉ lệ chuẩn xác trên cả 3 chế độ màn hình (**Desktop**, **Tablet** và **Mobile**).
     - **Chế độ Desktop (> 1024px)**: Thước đo cao `22px` với đường viền xanh primary `2px solid var(--primary)`, độ mờ kính `backdrop-filter: blur(10px)`, phông chữ đậm `11px` và đổ bóng mềm `0 4px 12px rgba(0, 88, 190, 0.15)`.
     - **Chế độ Tablet (640px - 1024px)**: Căn vị trí `bottom: 12px; left: 12px;`, chiều cao `20px` với phông chữ `10.5px`.
     - **Chế độ Mobile (< 640px)**: Căn vị trí `bottom: 8px; left: 8px;`, chiều cao `18px`, đường viền `1.5px` với phông chữ `10px` nhỏ gọn, chống đè vạch các phần tử xung quanh.
   - **Tour Result & So Sánh Guarantee**: Chuyển lưới so sánh Held-Karp vs Nearest Neighbor sang layout 1 cột linh hoạt (`grid-template-columns: 1fr`).
   - **Bảng Dữ Liệu Chặng (`.legs-table-container`)**: Tự động hỗ trợ cuộn ngang (`overflow-x: auto`) mượt mà trên màn hình cảm ứng di động.
   - **Thứ Tự Điểm Dừng Tour (Tour Stops Reordering)**:
     - Khắc phục lỗi kéo thảHTML5 `handleStopDrop` bị mất dữ liệu index giữa các browser bằng cách trích xuất dữ liệu trực tiếp từ `event.dataTransfer.getData('text/plain')`.
     - Bổ sung cặp nút điều hướng nhanh **▲ (Lên)** và **▼ (Số)** trực tiếp trên mỗi chip điểm dừng (`.reorder-btn`), cho phép thay đổi thứ tự tức thì 1-tap trên tất cả thiết bị (bao gồm màn hình cảm ứng di động/máy tính bảng).
   - **Nút Đặt Lại Trung Tâm Bản Đồ (`.map-reset-button`) & Nút Chú Thích Floating (`.map-legend-toggle-btn`)**:
     - Chuẩn hóa kích thước và độ cao đồng bộ tỉ lệ với cụm nút Zoom (+ / -) của MapLibre trên 3 cấp màn hình:
       - **Desktop (> 1024px)**: Nút `32px x 32px` bo góc `8px` căn lề phải `right: 10px; top: 104px;`. Nút Map Legend ẩn hoàn toàn theo yêu cầu.
       - **Tablet (640px - 1024px)**: Nút `32px x 32px` kết hợp nút Map Legend cao `32px`, font chữ `0.74rem` với cửa sổ popover rộng `min(300px, 85vw)`.
       - **Mobile (< 640px)**: Nút `30px x 30px` icon `16px` kết hợp nút Map Legend cao `30px`, font chữ `0.7rem` kẹp viền lề `right: 8px; top: 96px;` và popover tự động căn rộng 2 bên `left: 8px; right: 8px;` chống tràn màn hình.
   - **Keyboard Shortcuts Modal**: Căn chỉnh chiều rộng `95vw` và `max-height: 88vh` với thanh cuộn dọc riêng.

4. **Automated Testing & Build**:
   - Kiểm tra bộ unit test suite Vitest frontend: **All tests passing**.
   - Kiểm tra build production Vite frontend.
