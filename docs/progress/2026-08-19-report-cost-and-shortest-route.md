# Report update: cost model and shortest-route priority

## Thay đổi

- Cập nhật các chương LaTeX để dùng release `thu_duc_landmarks_v1.0.4` với 65 node và 283 directed edges.
- Ghi rõ mục tiêu của nhóm là ưu tiên tuyến đường ngắn nhất khả thi; trong scenario có cản trở, route được tối ưu theo composite cost.
- Bổ sung cách suy ra `free_flow_time_min` từ tốc độ UTraffic, tốc độ fallback theo loại đường và giả định 20 km/h cho connector.
- Mô tả bốn scenario NORMAL, CONGESTION, FLOOD và RANDOM; CONGESTION/FLOOD áp dụng 57/283 edge và RANDOM sinh cả kẹt lẫn ngập.
- Làm rõ heuristic A* sử dụng lower bound của toàn bộ composite cost, không phải một tập dữ kiện dư thừa và cũng không tối ưu khoảng cách thuần túy.

## Kiểm tra

- Đã rà các tham chiếu cũ `v1.0.0`/178 edge trong nguồn LaTeX của report và cập nhật các phần liên quan.
- Sẽ xác nhận bản PDF sau khi biên dịch XeLaTeX hai lượt.
