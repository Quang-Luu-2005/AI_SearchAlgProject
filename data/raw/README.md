# Raw data

- `thu_duc_market_v1.0.0/`: ZIP UTraffic bất biến, OSM POI snapshot, source registry
  và checksum dùng để tái lập processed pilot chợ Thủ Đức.
- `thu_duc_boundary_v1.0.0/`: snapshot GeoJSON bất biến của OSM relation
  `19407794`, dùng vẽ **ranh TP Thủ Đức cũ**. Relation được OSM gắn `historic`;
  lớp này chỉ mô tả vùng nghiên cứu, không khẳng định địa giới hành chính hiện tại.
- `thu_duc_landmarks_v1.0.0/`: snapshot Overpass của named major-place candidates,
  kèm bbox, định nghĩa, endpoint và registry từng query; ODbL 1.0.

Thư mục chỉ chứa snapshot nguồn gốc. Không sửa workbook hoặc OSM snapshot tại
đây; khi cần thay đổi, thêm phiên bản mới và cập nhật `../registry/`.

- `FloodRoute_HCMC_Dataset_v0.1.xlsx`: workbook nghiên cứu ban đầu, gồm 24 flood
  hotspots, giả định scenario, preset cost, source registry và các template graph.
- `osm/`: vị trí dành cho snapshot OSM/GraphML sau khi chốt vùng nghiên cứu.
