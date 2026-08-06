# Search algorithms

Mỗi thuật toán trả về `SearchPath` trong `app/core/contracts.py`; `SearchService`
ghép route metrics/explanation thành `SearchResult`. Thuật toán không gọi FastAPI
và không chỉnh sửa graph đầu vào. Tie-break mặc định: `g` thấp hơn trước, sau đó
`node_id` tăng dần để test có thể tái lập.

`weighted.py` hiện cài `UCS` và `A_STAR` qua cùng registry/cost engine. A* dùng
`h=0`, admissible và consistent nhưng chưa có lợi thế tốc độ so với UCS. Các module
BFS, DFS, Greedy và Bidirectional vẫn thuộc card thuật toán tiếp theo.
