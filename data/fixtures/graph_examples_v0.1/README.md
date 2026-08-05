# Graph examples v0.1

Package gồm ba graph nhỏ, deterministic để học, demo và viết unit test cho
`GraphLoader`. Toàn bộ node, edge và giá trị trọng số đều là `SIMULATED`, không
đại diện cho mạng đường hoặc giao thông thực tế.

| Folder | Nội dung chính |
|---|---|
| `simple_path/` | Đường có hướng A → B → C |
| `one_way_branch/` | Nhánh một chiều và thứ tự neighbor deterministic |
| `cycle_with_closure/` | Cycle A → B → C → A và scenario đóng cạnh để phá cycle |

Load một ví dụ:

```python
from backend.app.core.graph import GraphLoader

graph = GraphLoader.from_directory(
    "data/fixtures/graph_examples_v0.1/simple_path"
)
```

Mỗi folder graph có `nodes.csv`, `edges.csv`, `scenarios.json`, `metadata.json`
và `test_cases.json`. CSV là nguồn chuẩn cho Node/Edge.
