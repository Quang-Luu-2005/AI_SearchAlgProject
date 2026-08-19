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

## Hiệu chỉnh bố cục

- Hạ đường viền trên của trang bìa từ 2.5 cm xuống 3.2 cm để không chồng lên tiêu đề trường.
- Biên dịch lại XeLaTeX hai lượt và kiểm tra trực quan trang bìa sau khi sửa.
- Gom ba dòng tên trường thành một `tabular` block để giữ khoảng cách liền nhau, đồng thời đưa đường viền lên phía trên toàn bộ block.
- Cập nhật ba giảng viên trên trang bìa và các bản Markdown/HTML: Bùi Duy Đăng, Bùi Tiến Lên, Võ Nhật Tân.
- Đưa dòng địa điểm/thời gian vào bên trong khung bìa bằng cách hạ cạnh dưới của khung xuống 1 cm; đã build và kiểm tra trực quan trang đầu.
