# Thu Duc boundary overlay

## Đã triển khai

- Tạo raw snapshot bất biến cho OSM relation `19407794`, đăng ký checksum/provenance và
  công bố trạng thái `HISTORIC_OSM_RELATION`.
- Thêm `GET /api/v1/boundaries/thu-duc` và frontend loader độc lập với graph API.
- Thêm GeoJSON fill/line layer đỏ “Ranh TP Thủ Đức cũ”.
- Tính rectangle B có padding bao trọn polygon A cho initial/reset camera; giữ pan ngoài
  boundary, tắt world copies và dùng graph bounds làm fallback.
- Thêm validator geometry/disclosure, backend API test và MapLibre source/layer test.

## Xác minh

- `npm run test:data`: PASS; gồm checksum và geometry/disclosure của boundary.
- `npm run test:backend`: PASS, 47 tests.
- `npm run test:frontend`: PASS, 20 tests.
- `npm run build:frontend`: PASS; còn warning chunk MapLibre lớn hơn 500 kB.
