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
- `osm/`: vị trí chứa các snapshot OSM road graph infrastructure.
  - `thu_duc_osm_v1.0.0/`: raw snapshot Overpass API `2026-08-10` cho bbox Chợ Thủ Đức, chứa `osm_road_snapshot.json`, `source_registry.json` và `checksums.sha256`.
