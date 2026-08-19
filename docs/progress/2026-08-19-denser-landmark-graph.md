# Mở rộng lựa chọn đường đi cho landmark graph

## Thay đổi

- Giữ nguyên 65 node hiện tại.
- Mở rộng aggregate graph từ 178 lên 283 directed edge bằng cách thêm tối đa bốn
  nearest outgoing road-path alternatives cho mỗi landmark, dựa trên UTraffic.
- Tạo release `thu_duc_landmarks_v1.0.2` và submission bundle tương ứng.
- Giữ lại scenario hard closure `ASSUMPTION` đóng `LM_EDGE_0001` để kiểm tra detour.

## Giới hạn

Bốn cạnh đi ra không đảm bảo mọi cặp start/goal luôn có ba đường edge-disjoint;
validator và regression tests vẫn kiểm tra route thực tế khi closure xảy ra.
