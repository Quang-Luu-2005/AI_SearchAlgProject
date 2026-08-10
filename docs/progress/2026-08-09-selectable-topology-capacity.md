# Selectable topology và capacity benchmark

## Kết quả

- Mở `/locations` của processed pilot từ sáu POI lên đủ 90 topology node, không duplicate
  node; POI thật được ưu tiên và node còn lại dùng tên giao lộ deterministic.
- Cho phép click bất kỳ vị trí basemap trong chế độ START/GOAL và snap tới node gần nhất
  trong 200 m; popup hiển thị khoảng cách snap.
- Tạo processed graph `thu_duc_core_capacity_v0.1.0` từ UTraffic: 3.229 node, 5.057 cạnh
  có hướng, 8.286 GeoJSON feature và liên thông mạnh.
- Thêm builder, validator, API regression test, frontend capacity conversion test và lệnh
  `npm run benchmark:capacity`.

## Benchmark cục bộ

Lần chạy 12 cặp endpoint trên máy phát triển hiện tại:

| Chỉ số | Kết quả |
|---|---:|
| Graph load | 128,070 ms |
| API graph payload | 3,652 MB; build 239,266 ms |
| API locations 3.229 node | 189,400 ms |
| UCS median / p95 / max | 47,499 / 89,178 / 98,750 ms |
| A* median / p95 / max | 44,049 / 87,596 / 100,245 ms |
| Max explored | 2.956 node |

Timing là local single-process và phụ thuộc máy/cache. A* dùng `h=0`, vì vậy explored
node giống UCS. Kết quả chứng minh mức 3,2k node chạy tốt trong phạm vi demo, không phải SLA.

## Bằng chứng kiểm tra

- `npm run test:data`: PASS, gồm graph capacity liên thông mạnh.
- `npm run test:backend`: 46 passed; một warning Starlette/httpx hiện hữu.
- `npm run test:frontend`: 20 passed, gồm capacity-conversion 3.229/5.057.
- `npm run build:frontend`: PASS; warning chunk MapLibre lớn hơn 500 kB vẫn còn.
