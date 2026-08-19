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

## Kiểm tra

- Data validator: PASS.
- Frontend tests: 53 passed.
- Frontend build: PASS.
- Graph v1.0.3: 65 node, 283 edge, bốn scenario cố định.
