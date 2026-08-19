# Quản lý dataset và cơ sở kiểm thử

## Release chợ Thủ Đức v1.0.0

Processed release đang dùng là landmark graph với 65 node và 178 directed edge.
Dataset có trạng thái `MIXED`, `real_time=false`; scenario active là baseline lịch sử.
Không được hiểu
`NO_RECORD_IN_SELECTED_SOURCES` là an toàn và không được nâng
`ACADEMIC_DEMO_READY` trước khi toàn bộ review đạt.

Pipeline tái lập landmark release:

```powershell
node scripts/python.mjs scripts/data/build_thu_duc_landmarks.py
npm run test:data
```

Landmark release giữ polyline road-path, metadata và scenario baseline; dữ liệu
raw cũ chỉ giữ vai trò provenance bất biến.

## Capacity graph Thủ Đức v0.1.0

`thu_duc_core_capacity_v0.1.0` là graph benchmark riêng, sinh từ cùng raw UTraffic nhưng
dùng bbox lõi Thủ Đức rộng hơn và giữ thành phần liên thông mạnh lớn nhất: 3.229 node,
5.057 directed edge. Dataset mang trạng thái `CAPACITY_BENCHMARK_ONLY`, không thay thế
landmark map và không tuyên bố flood-aware hoặc real-time.

```powershell
node scripts/python.mjs scripts/data/build_thu_duc_capacity.py
npm run benchmark:capacity
```

Benchmark search canonical không sửa processed data. Lệnh `npm run benchmark:search`
đọc case `experiments/cases/search_benchmark_v1.json`, warm-up rồi đo 10 OD × 1 scenario
× 6 thuật toán × 20 lần. Output là `DERIVED_BENCHMARK`, không phải nguồn traffic mới và
không thay đổi provenance của dataset.

Node/tọa độ là `SOURCE_BACKED`; free-flow time là `DERIVED`; baseline scenario là
`ASSUMPTION`. Validator kiểm tra checksum, bbox, ID/FK, weight dương, count và strong
connectivity cho graph này.

## Snapshot ranh vùng nghiên cứu

`data/raw/thu_duc_boundary_v1.0.0/osm_relation_19407794.geojson` là snapshot bất biến
của OSM relation `19407794`, tải ngày 2026-08-09 và kiểm tra bằng SHA-256 trong manifest.
OSM hiện gắn relation này là `historic`, nên UI bắt buộc ghi “Ranh TP Thủ Đức cũ”. Polygon
chỉ cung cấp ngữ cảnh và rectangle camera; không sửa graph, edge cost hay tuyên bố địa giới
hành chính hiện hành.

## Landmark graph Thủ Đức v1.0.0

`thu_duc_landmarks_v1.0.2` là release mặc định: 65 named major places và 283 directed
aggregate road-path edge. “Địa điểm lớn” được định nghĩa bằng nhóm tag OSM có tên:
university/college, hospital, marketplace, bus station/townhall, mall, railway station,
stadium, museum hoặc theme park. Snapshot candidate được lưu bất biến tại
`data/raw/thu_duc_landmarks_v1.0.0/`.

Builder lọc POI trong polygon ranh, snap vào thành phần liên thông mạnh UTraffic
8.952 node/14.043 cạnh, rồi tạo một bidirectional road-distance MST và hai cạnh gần nhất
cho mỗi landmark. Edge giữ polyline UTraffic đầy đủ. Marker ở tọa độ OSM thật; connector
từ POI đến node đường dùng giả định 20 km/h và được công bố trong edge/metadata.

```powershell
node scripts/python.mjs scripts/data/build_thu_duc_landmarks.py
```

## Trạng thái hiện tại

Workbook v0.1 vẫn là nguồn nghiên cứu không routable. Ứng dụng hiện dùng processed
pilot chợ Thủ Đức, còn fixture phục vụ regression. Manifest giữ
`routing_dataset_status = REVIEW_REQUIRED` cho đến khi có hai reviewer.

## Current active release

The application uses `thu_duc_landmarks_v1.0.2` as its default selectable processed
map: 65 nodes and 283 directed road-path edges. The former 90-node processed
market release was removed from the registry and workspace; immutable
`data/raw/` provenance remains unchanged.

## Vòng đời dữ liệu

| Lớp | Nội dung | Git | Quy tắc |
|---|---|---|---|
| `raw` | Workbook và OSM snapshot nguyên bản | Có, theo version | Bất biến, checksum SHA-256 |
| `interim` | Clean/simplify/map-match tạm | Không | Phải tạo lại được bằng script |
| `processed` | Graph release cho app/thí nghiệm | Có khi freeze | Version + metadata + validation |
| `fixtures` | Graph nhỏ với expected result | Có | Deterministic, luôn gắn SIMULATED |

## Bundle nộp bài

Các bundle dùng để nộp bài được đặt dưới `data/submission/`, có version riêng,
manifest, provenance, validation report và checksum. Bundle được tách thành
`raw_collected/` (snapshot nguồn sao chép nguyên trạng) và `normalized/` (graph
đã chuẩn hóa cho bài toán); không sửa hoặc di chuyển dữ liệu trong `data/raw/`.

## Gói processed tối thiểu

Mỗi academic routing release đầy đủ phải có:

```text
nodes.csv
edges.csv
scenarios.json
delivery_points.csv
metadata.json
checksums.sha256
validation_report.json
```

`nodes.csv` cần ID, tọa độ WGS84, source và trạng thái xác minh. `edges.csv` là
directed edge, có distance, free-flow speed/time, direction, road type, restriction,
hotspot mapping, source và snapshot date. Một đường hai chiều phải thành hai cạnh.
Capacity-only package có thể bỏ delivery/flood review files nếu metadata công bố rõ
`CAPACITY_BENCHMARK_ONLY`, nhưng vẫn phải có nodes, edges, scenarios, metadata và checksum.

## Provenance và nhãn

- `SOURCE_BACKED`: giữ `source_id` và URL/location.
- `DERIVED`: có công thức hoặc script tái lập.
- `SIMULATED`/`ASSUMPTION`: hiện rõ trong file, API, UI và biểu đồ.
- `Verified` map-match cần hai thành viên review.
- Không điền số đo độ sâu/thời gian nếu nguồn chỉ mô tả định tính.

## Cơ sở kiểm thử

`toy_graph_v0.1` tách correctness khỏi dữ liệu thật chưa hoàn chỉnh:

- TC01: tuyến ngắn hợp lý khi không mưa.
- TC02: cạnh ngập đóng và tuyến phải đổi.
- TC03: A* phải khớp optimal cost của UCS.
- TC04: Held-Karp làm oracle cho Nearest Neighbor.

`graph_examples_v0.1` bổ sung ba fixture tập trung để học/demo và unit test:
directed path, one-way branch và directed cycle có scenario đóng cạnh. Mỗi graph
có metadata và golden case riêng, luôn gắn `SIMULATED`.

Toy graph v0.1 có ba scenario cost `OFFPEAK_BALANCED`, `PEAK_TRAFFIC` và
`HEAVY_RAIN_SAFE`. Preset bốn thành phần (`distance`, `freeflow_time`,
`congestion`, `flood_risk`) phải không âm và tổng bằng 1. Cost engine dùng
free-flow time làm component nền, sau đó cộng riêng traffic penalty là thời gian
trễ để không tính congestion hai lần. Edge override có thể thay congestion,
traffic multiplier, flood risk hoặc cost metric; closed edge không có total cost
khả dụng và không được dùng trong route.

Graph explorer chỉ tự khám phá folder dưới hai root cấu hình `data/fixtures` và
`data/processed`. Một folder cần tối thiểu `nodes.csv` và `edges.csv` để được xem là
candidate; chỉ graph load/validate thành công mới xuất hiện trong dropdown. Fixture
giữ nhãn `SIMULATED`; processed release phải có metadata, checksum và validation.

Khi triển khai thuật toán, bổ sung thêm case unreachable, start=goal, one-way,
tie-break, invalid/negative weight, heuristic consistency và counterexample cho
DFS/Greedy/Nearest Neighbor.

## Quy trình tạo graph v1.0

1. Chốt bbox/polygon đủ khoảng 80–150 node sau topology simplification.
2. Lưu query, ngày snapshot, OSMnx/Python version và attribution ODbL.
3. Export GraphML cùng nodes/edges CSV; không bỏ thuộc tính one-way.
4. Map-match 24 hotspot bằng tên đường và điểm đầu/cuối đoạn.
5. Review hai người; chuyển `Pending → Matched → Verified`.
6. Chạy QC: ID/FK, weight không âm, connectivity, direction, units, schema.
7. Freeze version, checksum, changelog và đổi manifest status khi thực sự sẵn sàng.

## Lệnh validation

```powershell
python scripts/data/validate_dataset.py
```

Validator hiện kiểm tra checksum raw workbook, unique ID, foreign key, distance/time
dương, nhãn fixture, tổng trọng số, edge closure và tính hợp lệ của golden path.
Các snapshot dưới `data/raw/` được đánh dấu `-text` trong `.gitattributes` để Git không
đổi LF/CRLF khi checkout; nhờ đó SHA-256 luôn được tính trên đúng byte đã freeze trên
Windows, macOS và Linux. Đây chỉ là bảo vệ byte, không cho phép sửa trực tiếp raw dataset.

## Graph loader và format

Graph fixture/processed được đọc bằng `GraphLoader` từ `nodes.csv` + `edges.csv`
và tùy chọn `scenarios.json`, hoặc từ JSON theo
[`data/schemas/graph.schema.json`](../data/schemas/graph.schema.json). Loader
giữ provenance và các cột mở rộng trong metadata của Node/Edge, kiểm tra ID/FK,
trọng số dương, duplicate ID và scenario không đóng edge không tồn tại. Graph
được xây dựng bất biến; scenario chỉ tạo view đóng cạnh. Chi tiết API và quy tắc
cạnh một chiều xem [graph-format.md](graph-format.md).
