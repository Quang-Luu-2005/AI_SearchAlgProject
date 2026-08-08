# ADR 0011: Selectable landmark graph Thủ Đức

- Trạng thái: Accepted
- Ngày: 2026-08-09

## Bối cảnh

Mạng đường phủ vùng Thủ Đức có hàng nghìn node kỹ thuật. Hiển thị và cho chọn mọi node
làm che basemap, tên giao lộ ít giá trị và khiến người dùng khó nhận ra endpoint hợp lệ.

## Quyết định

Tạo processed release `thu_duc_landmarks_v1.0.0`. Một “địa điểm lớn” phải có tên trong
OSM và thuộc university/college, hospital, marketplace, bus station/townhall, mall,
railway station, stadium, museum hoặc theme park. Candidate snapshot được đóng băng từ
Overpass, lọc trong polygon ranh TP Thủ Đức cũ, deduplicate và giới hạn quota theo nhóm.

Builder tạo mạng nguồn UTraffic liên thông mạnh 8.952 node/14.043 cạnh nhưng không đưa
mạng này lên UI. POI được snap vào mạng nguồn; graph nén gồm 65 landmark. Cạnh 178 được
tạo từ bidirectional road-distance MST cộng hai neighbor gần nhất, và giữ polyline của
shortest road path. Marker giữ tọa độ OSM thật; connector POI–road dùng giả định 20 km/h.

Frontend chỉ đánh dấu node `selectable` bằng circle trắng viền xanh có hitbox lớn. Search
picker và click map chỉ chọn landmark; core search contract, deterministic tie-break và
REST search request không thay đổi.

## Hệ quả

- Basemap dễ đọc, endpoint có tên thật và dấu hiệu chọn rõ ràng.
- Graph tải nhanh hơn nhiều so với việc gửi toàn bộ topology nguồn.
- Edge là đường tổng hợp giữa landmark, không phải từng road intersection.
- Traffic, connector và flood absence vẫn mang các limitation học thuật đã công bố.
