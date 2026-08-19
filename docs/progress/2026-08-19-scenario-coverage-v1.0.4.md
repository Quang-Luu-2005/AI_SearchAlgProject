# Mở rộng phạm vi scenario lên khoảng 20% cạnh

## Thay đổi

- Tạo release `thu_duc_landmarks_v1.0.4`, giữ nguyên 65 node và 283 edge.
- Scenario `LANDMARK_FLOOD` áp dụng flood override cho 57 cạnh.
- Scenario `LANDMARK_CONGESTION` áp dụng congestion override cho 57 cạnh.
- 57/283 = 20.14%; các giá trị vẫn được gắn nhãn `ASSUMPTION`, không phải dữ liệu
  thời gian thực.
- Frontend chuyển mặc định sang release v1.0.4; v1.0.3 được giữ lại để đối chiếu.
- Khi đang ở scenario `RANDOM`, nút sinh lại tạo seed mới mỗi lần nhấp và cập nhật lại
  danh sách edge bị ảnh hưởng.
- Mỗi lần random trên frontend chọn 7 edge: 1 `CLOSED`, 3 `FLOODED` và 3 `CONGESTED`,
  nên luôn có cả ngập và kẹt trong cùng một scenario.
