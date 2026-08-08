# Kế hoạch đã triển khai: landmark graph Thủ Đức

1. Định nghĩa named major-place categories từ OSM và đóng băng Overpass snapshot.
2. Lọc POI theo polygon ranh TP Thủ Đức cũ, deduplicate và áp dụng quota deterministic.
3. Tạo strongly-connected UTraffic source graph, snap landmark và tính pairwise shortest paths.
4. Nén thành MST hai chiều cộng nearest-neighbor edges, giữ full road polyline geometry.
5. Chỉ expose landmark node; thêm selectable marker, picker/search integration và attribution.
6. Đăng ký manifest/checksum, validator, ADR, tests và tài liệu vận hành.
