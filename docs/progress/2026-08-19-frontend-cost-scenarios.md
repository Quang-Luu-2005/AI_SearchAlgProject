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
- Rút dropdown còn đúng `CONGESTION`, `FLOOD`, `RANDOM`; ẩn scenario kỹ thuật và bỏ legend trùng phía dưới map.
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
