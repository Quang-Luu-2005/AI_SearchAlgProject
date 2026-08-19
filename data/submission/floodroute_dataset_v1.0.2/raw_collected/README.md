# Raw collected data

Đây là lớp dữ liệu thô sao chép từ các snapshot bất biến trong `data/raw/` để
đóng gói nộp bài. Không chỉnh sửa trực tiếp các file trong lớp này.

| File | Vai trò | Nhãn |
|---|---|---|
| `osm_major_places_snapshot.json` | POI/landmark từ Overpass OSM | `SOURCE_BACKED` |
| `osm_relation_19407794.geojson` | Boundary vùng nghiên cứu OSM | `SOURCE_BACKED` |
| `utraffic_hcm_v6.zip` | Mạng đường và traffic lịch sử | `SOURCE_BACKED` |
| `source_registry.json` | Registry provenance, license, thời gian | `SOURCE_BACKED` |

Traffic là historical snapshot, không phải real-time.
