# Test fixtures

Fixture là dữ liệu nhỏ, deterministic và có expected result. Không dùng fixture
để đưa ra kết luận thực tế về giao thông TP.HCM. `toy_graph_v0.1` được gắn nhãn
`SIMULATED` và là cơ sở để viết thuật toán trước khi dataset OSM v1.0 sẵn sàng.

`graph_examples_v0.1` cung cấp ba dataset nhỏ có thể load độc lập: directed path,
one-way branch và cycle có scenario đóng cạnh. Đây cũng là dữ liệu `SIMULATED`,
dùng cho học tập, demo và focused unit test.
