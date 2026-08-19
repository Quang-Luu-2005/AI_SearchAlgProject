# Triển khai hard closure v1.0.1

## Thay đổi

- Hợp nhất `closed_edge_ids` và `edge_overrides.is_closed` trong Graph contract.
- Tạo release `thu_duc_landmarks_v1.0.1` và submission bundle tương ứng, giữ nguyên
  65 node/178 edge.
- Thêm scenario `ASSUMPTION` đóng `LM_EDGE_0001`; frontend chọn v1.0.1 mặc định.
- Ghi rõ closure chỉ áp dụng exact landmark edge ID, không lan sang aggregate edge
  có source segment/hình học chồng lấn.

## Kiểm tra

Đã bổ sung regression tests cho sáu thuật toán, closure bằng override và trường hợp
không còn đường. Các lệnh validator, backend/frontend tests và build sẽ được chạy
trước khi bàn giao.
