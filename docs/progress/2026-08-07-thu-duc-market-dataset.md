# Thu Duc Market dataset v1.0.0

## Kết quả

- Thêm pipeline `scripts/data/build_thu_duc_market.py` và raw version bất biến có
  UTraffic ZIP, OSM POI snapshot, source registry, SHA-256.
- Đóng băng `data/processed/thu_duc_market_v1.0.0`: 90 node, 155 directed edge,
  liên thông mạnh; ba scenario lịch sử/rain-aware; POI, traffic profile, hotspot và
  mapping review.
- Thêm golden case DP07 → DP08 có route đổi giữa off-peak và rain-aware; UCS/A* dùng
  chung contract và được kiểm tra deterministic.
- Mở catalog API cho fixture + processed, truyền provenance/status/limitations; UI
  chọn pilot mặc định và công bố historical/not real-time cùng attribution OSM.
- Mở rộng validator cho checksum, bbox, ID/FK, connectivity, weight, snapping,
  provenance, mapping review và golden case.

## Quyết định kiểm định

Không giả chữ ký reviewer. Hai candidate map-match flood edge, một record ngoài graph
và một context record đang ở `PENDING_TWO_HUMAN_REVIEWS`; manifest và metadata giữ
`REVIEW_REQUIRED`. Chỉ hai team member thật mới được điền `reviewer_1`/`reviewer_2`,
chuyển record sang `VERIFIED`, chạy lại pipeline/QC và nâng `ACADEMIC_DEMO_READY`.

Sáu POI OSM đã chốt được dùng trong UI. Golden case riêng dùng hai giao lộ có tọa độ
UTraffic source-backed làm `DELIVERY_TEST_ANCHOR`, không hiển thị như POI; việc gán đơn
hàng cho hai anchor này mang nhãn `ASSUMPTION`.

## Bằng chứng

- `npm run test:data`: PASS; checksum, 90/155, connectivity, provenance và golden case.
- `npm run test:backend`: 45 passed (một deprecation warning từ Starlette/httpx).
- `npm run test:frontend`: 9 passed.
- `npm run build:frontend`: TypeScript và Vite production build thành công.
