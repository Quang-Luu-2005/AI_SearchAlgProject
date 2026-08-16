# Search algorithms

Mỗi thuật toán trả về `SearchPath` trong `app/core/contracts.py`; `SearchService`
ghép route metrics/explanation thành `SearchResult`. Thuật toán không gọi FastAPI
và không chỉnh sửa graph đầu vào. Tie-break mặc định: `g` thấp hơn trước, sau đó
`node_id` tăng dần để test có thể tái lập.

`weighted.py` hiện cài `UCS` và `A_STAR` qua cùng registry/cost engine. A* dùng
heuristic Haversine có trọng số theo scenario, admissible/consistent khi graph có
tọa độ và fallback `h=0` khi thiếu tọa độ.

`unweighted.py` cài `BFS` và `DFS` cho graph directed. Cả hai dùng neighbor ordering
theo `(to_node_id, edge_id)`, đánh dấu node ngay khi đưa vào frontier để xử lý cycle
deterministic, và trả `SearchPath`/trace giống các thuật toán weighted. `BFS` có
optimality theo số hop; `DFS` không có guarantee tối ưu chi phí.

`greedy.py` và `bidirectional.py` cũng đã được đăng ký cho service/experiment; UI
hiện ưu tiên công bố BFS/DFS trong hạng mục two-point và chế độ compare.
