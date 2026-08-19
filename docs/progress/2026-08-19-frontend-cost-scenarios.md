# Frontend cost scenarios and random edge conditions

## Thay đổi

- Chuyển frontend mặc định sang `thu_duc_landmarks_v1.0.3`.
- Bổ sung dropdown cho `LANDMARK_NORMAL`, `LANDMARK_FLOOD`,
  `LANDMARK_CONGESTION` và giữ hard-closure scenario.
- Thêm nút sinh random scenario, gọi `POST /api/v1/scenarios/random` với start/goal
  hiện tại, đăng ký scenario tạm trong backend session và hiển thị danh sách edge bị
  `CONGESTED`, `FLOODED` hoặc `CLOSED`.
- Tô màu edge random trên bản đồ: cam/kẹt xe, xanh/ngập, đỏ/đóng đường.
- Thêm nhãn song ngữ Việt/Anh theo nút chọn ngôn ngữ và legend nổi cố định ngay trên map.
- Dropdown demo hiện có đủ bốn lựa chọn `NORMAL`, `CONGESTION`, `FLOOD`, `RANDOM`; `NORMAL` là baseline mặc định khi nạp graph.
- Ẩn scenario kỹ thuật và bỏ legend trùng phía dưới map.
- Với scenario có cản trở, tự động so sánh sáu thuật toán, gom tối đa ba route khác nhau,
  hiển thị chi phí và đánh dấu route có weighted cost thấp nhất là `OPTIMAL`.
- API graph detail trả `scenario_status` trên từng edge để map tô đúng màu theo scenario
  FLOOD/CONGESTION/CLOSED, không chỉ theo random overlay.
- Thay so sánh thuật toán chéo bằng endpoint `/api/v1/alternatives`: cùng algorithm được
  chọn sẽ tìm tối đa hai route khác bằng cách đóng từng edge của route trước.

## Kiểm tra

- Data validator: PASS.
- Frontend tests: 53 passed.
- Frontend build: PASS.
- Graph v1.0.3: 65 node, 283 edge, bốn scenario cố định.

## Cập nhật mô tả dữ liệu — 2026-08-20

- Viết lại README của release `thu_duc_landmarks_v1.0.4` bằng tiếng Việt, gồm mục
  đích, quy mô 65 node/283 edge, cấu trúc file, bốn scenario demo, provenance và
  giới hạn sử dụng.
- Đồng bộ README ở lớp `normalized/` và thư mục `data/processed/`, sau đó cập nhật
  checksum tương ứng.
- Tạo lại `7 - Data.zip`, `Group7.zip` và `7.zip` với README mới.
- Chạy data validator: PASS.
- Bổ sung `.gitignore` cho các artifact nặng và sinh tự động: ZIP/raw snapshot, PDF/PPTX,
  file phụ trợ LaTeX và thư mục tạm; đã kiểm tra bằng `git check-ignore`.
