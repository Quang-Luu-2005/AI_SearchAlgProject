# Toy graph v0.1

Graph mô phỏng 6 nút, 14 cạnh có hướng. Nó cố ý tạo hai tình huống:

1. `OFFPEAK_BALANCED`: đường `N01 → N02 → N06` ngắn nhất.
2. `HEAVY_RAIN_SAFE`: cạnh ngập `E03/E04` bị đóng, nên tuyến phải đổi.

Mọi địa danh chỉ tạo ngữ cảnh cho fixture. Tọa độ, cạnh, thời gian và congestion
không phải số liệu giao thông thật. Golden cases trong `test_cases.json` sẽ được
dùng để đối chiếu UCS/A* và kiểm tra phản ví dụ cho thuật toán không tối ưu.

