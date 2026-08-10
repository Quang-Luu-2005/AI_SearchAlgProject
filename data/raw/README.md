# Raw data

- `thu_duc_market_v1.0.0/`: ZIP UTraffic bất biến, OSM POI snapshot, source registry
  và checksum dùng để tái lập processed pilot chợ Thủ Đức.

Thư mục chỉ chứa snapshot nguồn gốc. Không sửa workbook hoặc OSM snapshot tại
đây; khi cần thay đổi, thêm phiên bản mới và cập nhật `../registry/`.

- `FloodRoute_HCMC_Dataset_v0.1.xlsx`: workbook nghiên cứu ban đầu, gồm 24 flood
  hotspots, giả định scenario, preset cost, source registry và các template graph.
- `osm/`: vị trí chứa các snapshot OSM road graph.
  - `thu_duc_osm_v1.0.0/`: raw snapshot Overpass API `2026-08-10`, bbox Chợ Thủ Đức, source registry và SHA-256 checksums.
