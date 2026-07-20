# Search algorithms

Mỗi thuật toán phải trả về `SearchResult` trong `app/core/contracts.py`, không gọi
FastAPI và không chỉnh sửa graph đầu vào. Tie-break mặc định: `g` thấp hơn trước,
sau đó `node_id` tăng dần để test có thể tái lập.

Các module dự kiến: `bfs.py`, `dfs.py`, `ucs.py`, `astar.py`, `greedy.py` và
`bidirectional.py`.

