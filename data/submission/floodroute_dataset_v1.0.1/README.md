# FloodRoute HCMC — dataset nộp bài v1.0.1

Bundle này tách rõ hai lớp dữ liệu:

```text
raw_collected/   snapshot nguồn thu thập được, giữ nguyên dạng gốc
normalized/      dữ liệu đã chuẩn hóa cho bài toán tìm đường
```

## 1. Dữ liệu thô — `raw_collected/`

- `osm_major_places_snapshot.json`: snapshot Overpass các địa điểm lớn có tên.
- `osm_relation_19407794.geojson`: snapshot boundary OSM dùng làm vùng nghiên cứu.
- `utraffic_hcm_v6.zip`: mạng đường UTraffic lịch sử dùng làm nguồn đường.
- `source_registry.json`: thông tin nguồn, license và thời gian thu thập.
- `checksums.sha256`: checksum để kiểm tra file thô.

Các file trong lớp này là `SOURCE_BACKED` và không phải dữ liệu real-time.

## 2. Dữ liệu chuẩn hóa — `normalized/`

- `nodes.csv`: 65 landmark có thể chọn, tọa độ và trạng thái provenance.
- `edges.csv`: 178 cạnh có hướng, khoảng cách, thời gian và polyline đường.
- `landmarks.csv`: bảng landmark phục vụ tra cứu.
- `scenarios.json`: baseline và hard-closure detour scenario `LM_EDGE_0001`, gắn nhãn `ASSUMPTION`.
- `metadata.json`, `validation_report.json`, `checksums.sha256`.

Đây là graph đã chuẩn hóa để chạy routing cho bài toán FloodRoute. Validation
release đạt `PASS`. Dataset là bản snapshot lịch sử, chỉ dùng cho mục đích học
thuật, không dùng làm hướng dẫn điều hướng hoặc an toàn thực tế. Hard closure chỉ áp
dụng cho landmark edge ID cụ thể, không lan sang aggregate edge có source segment
hoặc hình học chồng lên.
