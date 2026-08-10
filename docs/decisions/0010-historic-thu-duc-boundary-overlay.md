# ADR 0010: Ranh TP Thủ Đức cũ và rectangle camera

- Trạng thái: Accepted
- Ngày: 2026-08-09

## Bối cảnh

Viewport chỉ suy ra từ bbox của routing graph làm người dùng khó phân biệt phạm vi Thủ
Đức với vùng bên ngoài. Nếu giới hạn đúng bbox của graph, các cạnh sát biên có thể bị che;
nếu không giới hạn, người dùng có thể kéo ra toàn bộ bản đồ.

## Quyết định

Đóng băng GeoJSON OSM relation `19407794` trong raw version mới, giữ checksum, ngày
snapshot, attribution và ODbL. Relation hiện được OSM/Nominatim phân loại `historic`, do
đó mọi presentation phải ghi “Ranh TP Thủ Đức cũ”; lớp này không được dùng như tuyên bố
địa giới hành chính hiện hành.

Frontend tải polygon A từ `GET /api/v1/boundaries/thu-duc`, vẽ fill đỏ rất nhẹ và line
đỏ rõ trên basemap. Rectangle B được tính từ min/max longitude/latitude của A, cộng 3%
padding mỗi chiều và tối thiểu 0,004 độ. Initial/reset camera fit B và `maxBounds` cũng
được đặt thành B. Phần ngoài A nhưng nằm trong vành đệm B vẫn xem được;
`renderWorldCopies=false` và min zoom 10.5 ngăn camera rơi ra vùng lớn hơn. Khi boundary
lỗi, graph context bounds là fallback và cũng trở thành giới hạn camera.

Nominatim chỉ được dùng trong script tạo snapshot, không được gọi lúc runtime.

## Hệ quả

- Người dùng thấy hình dạng ranh thực bên trong một viewport chữ nhật rộng hơn.
- Cạnh sát biên không bị cắt nhờ padding, nhưng không thể pan ra ngoài rectangle B.
- Boundary có provenance tái lập được nhưng mang caveat historic bắt buộc.
- Boundary không ảnh hưởng topology, snapping, thuật toán hoặc cost model.
