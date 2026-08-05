# Quản lý dataset và cơ sở kiểm thử

## Trạng thái hiện tại

Workbook v0.1 có 24 flood hotspot cùng nguồn, assumptions, scenario và schema
template, nhưng **chưa phải graph định tuyến**. Vì vậy manifest giữ
`routing_dataset_status = NOT_READY`; giao diện hiện dùng toy fixture có badge
`SIMULATED`.

## Vòng đời dữ liệu

| Lớp | Nội dung | Git | Quy tắc |
|---|---|---|---|
| `raw` | Workbook và OSM snapshot nguyên bản | Có, theo version | Bất biến, checksum SHA-256 |
| `interim` | Clean/simplify/map-match tạm | Không | Phải tạo lại được bằng script |
| `processed` | Graph release cho app/thí nghiệm | Có khi freeze | Version + metadata + validation |
| `fixtures` | Graph nhỏ với expected result | Có | Deterministic, luôn gắn SIMULATED |

## Gói processed tối thiểu

Mỗi `data/processed/vX.Y.Z/` phải có:

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

Graph explorer chỉ tự khám phá folder dưới `data/fixtures`. Một folder cần tối
thiểu `nodes.csv` và `edges.csv` để được xem là candidate; chỉ graph load/validate
thành công mới xuất hiện trong dropdown. Fixture dùng để bàn giao nên bổ sung
`scenarios.json`, `metadata.json`, `test_cases.json` và giữ nhãn `SIMULATED`.

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

## Graph loader và format

Graph fixture/processed được đọc bằng `GraphLoader` từ `nodes.csv` + `edges.csv`
và tùy chọn `scenarios.json`, hoặc từ JSON theo
[`data/schemas/graph.schema.json`](../data/schemas/graph.schema.json). Loader
giữ provenance và các cột mở rộng trong metadata của Node/Edge, kiểm tra ID/FK,
trọng số dương, duplicate ID và scenario không đóng edge không tồn tại. Graph
được xây dựng bất biến; scenario chỉ tạo view đóng cạnh. Chi tiết API và quy tắc
cạnh một chiều xem [graph-format.md](graph-format.md).
