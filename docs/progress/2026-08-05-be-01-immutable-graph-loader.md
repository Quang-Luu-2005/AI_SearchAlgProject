# 2026-08-05 — BE-01 Graph Loader bất biến

## Mục tiêu

Xây dựng contract Graph/Node/Edge có hướng, load được fixture 6 node từ CSV/JSON,
giữ graph gốc bất biến và hỗ trợ truy vấn nền cho các thuật toán search.

## Thay đổi đã thực hiện

- Thêm model bất biến `Node`, `Edge`, `Scenario`, `Graph` và `GraphView` trong
  `backend/app/core/contracts.py`.
- Thêm `GraphLoader`/`load_graph` trong `backend/app/core/graph.py` với
  `from_directory`, `from_csv`, `from_json`; hỗ trợ fixture CSV graph và JSON
  scenario hiện tại.
- Thêm truy vấn danh sách node, tồn tại node, neighbor có hướng, edge mở/đóng,
  scenario view và cycle detection deterministic.
- Thêm unit test cho fixture 6 node, node không tồn tại, cạnh một chiều, scenario
  đóng cạnh, cycle/acyclic graph, JSON loader, validation và deep immutability.
- Bổ sung [graph-format.md](../graph-format.md), cập nhật architecture,
  data-management và documentation map.

## Quyết định/giả định

- Graph chỉ hỗ trợ directed edge; đường hai chiều phải biểu diễn bằng hai edge.
- `neighbors()` trả outgoing `Edge`; `neighbor_nodes()`/`neighbor_ids()` dành cho
  caller chỉ cần node đích.
- Scenario không mutate edge hoặc adjacency index; `GraphView` lọc bằng
  `closed_edge_ids`.
- CSV là nguồn chuẩn cho Node/Edge; JSON dùng cho Scenario, metadata, golden case
  và full-graph import/export nhỏ, không duy trì hai bản graph chỉnh sửa độc lập.
- Fixture vẫn là `SIMULATED`; không sửa `data/raw/` và không tạo processed release
  mới. Quyết định graph core và immutability được ghi trong
  [ADR-0003](../decisions/0003-immutable-directed-graph-loader.md).

## Bằng chứng kiểm tra

```powershell
.\.venv\Scripts\python.exe -m pytest backend\tests -q
```

- 8 test PASS; còn 1 `StarletteDeprecationWarning` đã biết từ TestClient.
- Smoke test loader fixture: 6 node, 14 edge, directed, scenario mưa lọc `E03/E04`,
  cycle detection trả `True`.

## Tồn tại/rủi ro

- Chưa có graph processed/OSM v1.0; manifest vẫn giữ
  `routing_dataset_status = NOT_READY`.
- Cost override trong scenario mới được giữ dưới metadata; việc tính cost thuộc
  search/cost model của card sau.

## Bước tiếp theo

Dùng contract này để triển khai search algorithm, bắt đầu từ BFS/DFS/UCS và giữ
tie-break deterministic theo `node_id` trong contract thuật toán.
