# Graph format và Graph Loader

Catalog khám phá cả `data/fixtures` và `data/processed`. ID fixture giữ dạng cũ; ID
processed có prefix `processed/`. Cả hai loại đều bị giới hạn trong root đã cấu hình
sau khi resolve path. Processed release phải có metadata/checksum/validation/provenance;
fixture phải giữ nhãn simulation.

## Phạm vi

`backend.app.core.graph.GraphLoader` đọc graph có hướng từ hai dạng input:

- CSV: một `nodes.csv`, một `edges.csv`, và tùy chọn `scenarios.json`.
- JSON: một object có `nodes`, `edges`, và tùy chọn `scenarios`, theo
  `data/schemas/graph.schema.json`.

## Quy ước lưu trữ khuyến nghị

Định dạng chuẩn trong repository là **CSV cho Node/Edge** và **JSON cho dữ liệu
có cấu trúc lồng nhau**:

| Nội dung | Định dạng chính | Lý do |
|---|---|---|
| Node | `nodes.csv` | Dễ nhập, lọc và kiểm tra bằng Excel hoặc công cụ dạng bảng |
| Edge | `edges.csv` | Gọn khi graph lớn, dễ review từng dòng và kiểm tra khóa ngoại |
| Scenario | `scenarios.json` | Phù hợp với weights, edge overrides và danh sách edge đóng |
| Metadata | `metadata.json` | Phù hợp với provenance, version và limitations |
| Golden test case | `test_cases.json` | Phù hợp với path, visit list và expected result lồng nhau |

Một graph release/fixture nên có cấu trúc:

```text
graph_vX.Y.Z/
  nodes.csv
  edges.csv
  scenarios.json
  metadata.json          # bắt buộc với processed release
  test_cases.json        # dùng cho fixture/golden test
  checksums.sha256       # bắt buộc với processed release
  validation_report.json # bắt buộc với processed release
```

Không dùng một file full-graph JSON làm nguồn dữ liệu chính khi graph lớn vì khó
chỉnh sửa bằng công cụ dạng bảng, Git diff dễ nhiễu và thường phải parse toàn bộ
file. Full-graph JSON vẫn được loader hỗ trợ cho fixture nhỏ, import/export hoặc
trao đổi qua API. Khi có cả CSV và JSON, CSV là nguồn chuẩn; bản JSON phải được
tạo lại từ cùng version thay vì chỉnh sửa độc lập để tránh dữ liệu lệch nhau.

Fixture hiện tại có thể load trực tiếp:

```python
from backend.app.core.graph import GraphLoader

graph = GraphLoader.from_directory("data/fixtures/toy_graph_v0.1")
```

## Dataset ví dụ có sẵn

Folder `data/fixtures/graph_examples_v0.1/` có ba graph `SIMULATED` hoàn chỉnh:

| Ví dụ | Node/Edge | Minh họa |
|---|---:|---|
| `simple_path` | 3/2 | Đường có hướng `SP_A → SP_B → SP_C` |
| `one_way_branch` | 4/4 | Hai nhánh một chiều và neighbor deterministic |
| `cycle_with_closure` | 3/3 | Directed cycle và scenario `BREAK_CYCLE` |

Toy graph `toy_graph_v0.1` có ba scenario cost `OFFPEAK_BALANCED`, `PEAK_TRAFFIC`
và `HEAVY_RAIN_SAFE`. Mỗi scenario khai báo `cost_preset`, `weights`,
`traffic_multiplier`, `data_status`, `edge_overrides` và `closed_edge_ids`.
`ScenarioCostEngine` trả breakdown edge gồm:

```json
{
  "distance_km": 1.2,
  "free_flow_time_min": 3.6,
  "travel_time_min": 4.5,
  "congestion_level_1_5": 4,
  "traffic_penalty": 0.9,
  "flood_risk": 0.0,
  "total_cost": 1.8,
  "is_closed": false,
  "data_status": "SIMULATED"
}
```

`total_cost` là tổng các component đã nhân weight; `free_flow_time_min` và
`traffic_penalty` được tách riêng để tránh cộng congestion hai lần. Edge bị đóng
vẫn có metric/breakdown nhưng `total_cost` là `null` và `is_closed` là `true`.

Ví dụ load graph cycle:

```python
graph = GraphLoader.from_directory(
    "data/fixtures/graph_examples_v0.1/cycle_with_closure"
)
open_cycle = graph.has_cycle()  # True
closed_cycle = graph.for_scenario("BREAK_CYCLE").has_cycle()  # False
```

Mỗi ví dụ có `nodes.csv`, `edges.csv`, `scenarios.json`, `metadata.json` và
`test_cases.json`. Xem README của package để chọn graph phù hợp với test cần viết.

## Nạp tự động trên giao diện

`GET /api/v1/graphs` tự khám phá đệ quy các folder bên dưới `data/fixtures` và
`data/processed`.
Folder tối thiểu phải có:

```text
nodes.csv
edges.csv
```

Các file `scenarios.json`, `metadata.json` và `test_cases.json` là phần mở rộng;
fixture dùng để nộp/review nên có đủ cả năm file theo quy ước ở trên. Folder có
file bắt buộc nhưng dữ liệu sai contract được trả trong `invalid_graphs` và không
xuất hiện trong dropdown chọn graph.

Sau khi chọn folder, frontend gọi:

```text
GET /api/v1/graphs/{graph_id}?scenario_id={scenario_id}
```

`graph_id` là đường dẫn tương đối bên trong root cho phép; processed ID có prefix
`processed/`. API không chấp nhận đường dẫn thoát ra ngoài root tương ứng. Payload trả
Node, Edge, Scenario, metadata và
`is_closed` cho từng edge để giao diện hiển thị trạng thái scenario.

Mọi fixture phải ghi rõ `SIMULATED` hoặc `ASSUMPTION`. Loader không sửa file
nguồn và không tự tạo cạnh ngược.

## Node

Node cần `node_id`; `latitude`, `longitude` và các cột còn lại là metadata mở rộng.
Các field chuẩn trong fixture là `node_id`, tọa độ WGS84, `source_id` và
`data_status`.

## Edge

Edge cần các field:

| Field | Ý nghĩa |
|---|---|
| `edge_id` | ID duy nhất của cạnh |
| `from_node_id` | Node nguồn |
| `to_node_id` | Node đích |
| `distance_m` | Khoảng cách dương, tính bằng mét |
| `free_flow_time_min` | Thời gian dương ở điều kiện tự do |

Các field như `direction`, `road_type`, `is_restricted` và provenance được giữ
trong `edge.attributes` và có thể truy cập qua `edge.data`. Cạnh luôn là một
hướng từ `from_node_id` tới `to_node_id`; đường hai chiều phải có hai record
edge riêng biệt.

Neighbor được sắp xếp ổn định theo `(to_node_id, edge_id)`. Vì vậy
`graph.neighbors("N01")` trả tuple các `Edge` đi ra; dùng
`graph.neighbor_nodes("N01")` hoặc `graph.neighbor_ids("N01")` nếu chỉ cần node.

## Scenario và tính bất biến

Scenario có `scenario_id` và `closed_edge_ids`. Dùng:

```python
rainy = graph.for_scenario("HEAVY_RAIN_SAFE")
rainy.neighbors("N02")
```

View scenario loại các edge đóng khỏi truy vấn nhưng giữ nguyên `graph` gốc.
`graph.has_edge("E03")` vẫn đúng nếu `E03` chỉ bị đóng trong view mưa. Scenario
tham chiếu edge không tồn tại sẽ làm loader từ chối input.

## Quy tắc truy vấn

- `has_node(id)` trả `False` cho ID không tồn tại.
- `get_node(id)` và `neighbors(id)` ném `NodeNotFoundError` cho node không tồn tại.
- `has_edge(id)` kiểm tra edge tồn tại và đang mở trong scenario hiện hành.
- `edge_exists(from_id, to_id)` kiểm tra đúng chiều; không có suy luận cạnh ngược.
- `has_cycle()` kiểm tra cycle trên graph có hướng đang được truy vấn.
- Node, Edge, Scenario, Graph và GraphView đều không cho mutation; metadata lồng
  nhau được freeze đệ quy.
