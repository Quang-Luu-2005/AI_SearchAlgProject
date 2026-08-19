# Dữ liệu graph landmark Thủ Đức đã chuẩn hóa — v1.0.4

Đây là graph có hướng phục vụ bài toán tìm tuyến giữa các landmark lớn tại Thủ Đức.
Graph gồm **65 node** và **283 directed edge**. Các edge được tổng hợp từ snapshot
UTraffic đã cố định, giữ chiều di chuyển, chiều dài, thời gian đường thông và
polyline hình học.

Bộ dữ liệu cung cấp các scenario `LANDMARK_NORMAL`, `LANDMARK_FLOOD` và
`LANDMARK_CONGESTION`, cùng scenario kiểm thử `LANDMARK_HARD_CLOSURE_DETOUR`.
Hai scenario FLOOD và CONGESTION mỗi scenario áp dụng lên 57/283 edge, khoảng 20%
graph. Các giá trị này mang nhãn `ASSUMPTION`, chỉ dùng để minh họa thuật toán và
không phải số liệu giao thông/ngập theo thời gian thực.

Trong scenario NORMAL, không có cản trở và cost cơ sở được dùng làm baseline ưu tiên
tuyến ngắn nhất khả thi. Với closure, hệ thống loại đúng edge ID bị đóng khỏi
`neighbors()`; closure không lan sang aggregate edge khác chỉ vì source segment hoặc
hình học của chúng bị chồng lấn.
