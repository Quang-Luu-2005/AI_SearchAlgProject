# Processed datasets

- `thu_duc_market_v1.0.0/`: 90 node, 155 directed edge, UTraffic historical dataset.
- `osm_thu_duc_v1.0.0/`: 27 node, 40 directed edge, release trích xuất trực tiếp từ OSM Overpass API snapshot (bbox Chợ Thủ Đức), có metadata, provenance, checksums và trạng thái `ACADEMIC_DEMO_READY`.

Đích của dataset v1.0 dùng trong API. Mỗi release đặt trong thư mục version riêng,
ví dụ `v1.0.0/`, gồm `nodes.csv`, `edges.csv`, `scenarios.json`, metadata, checksum
và báo cáo validation. Release chợ Thủ Đức hiện có thể chạy trong app nhưng chưa được
nâng `ACADEMIC_DEMO_READY` do còn chờ hai human review.
