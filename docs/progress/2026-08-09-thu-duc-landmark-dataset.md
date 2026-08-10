# Thu Duc landmark dataset

## Kết quả

- Đóng băng 311 OSM major-place candidates từ 8 truy vấn Overpass có registry.
- Lọc theo polygon ranh và định nghĩa/quota deterministic; snap thành 65 landmark thật.
- Dùng mạng UTraffic nguồn 8.952 node/14.043 cạnh để sinh 178 directed shortest-path edge.
- Giữ marker ở tọa độ OSM và geometry cạnh theo đường nguồn; connector 20 km/h được ghi rõ.
- Đặt landmark release làm dataset mặc định và thêm marker selectable trắng viền xanh.

## Xác minh

- `npm run test:data`: PASS.
- `npm run test:backend`: PASS, 49 tests.
- `npm run test:frontend`: PASS, 24 tests.
- `npm run build:frontend`: PASS; còn warning chunk MapLibre lớn hơn 500 kB.
- API smoke: graph payload 415.589 byte, load khoảng 30,84 ms; A* sample khoảng
  28,26 ms trong local TestClient.
- Audit 20 cặp ngẫu nhiên trên capacity graph: 20/20 có route; graph 3.229 node được ẩn
  khỏi dropdown vì là benchmark bbox lõi, không phải landmark endpoint dataset.
