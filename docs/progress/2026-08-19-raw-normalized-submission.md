# Tách dữ liệu thô và dữ liệu chuẩn hóa cho bundle nộp bài

## Thay đổi

- `raw_collected/` chứa snapshot OSM POI, boundary OSM, gói UTraffic lịch sử và
  source registry được sao chép nguyên trạng từ `data/raw/`.
- `normalized/` chứa graph routing 65 node/178 edge, scenario, metadata và
  validation report đã chuẩn hóa cho bài toán FloodRoute.
- Cập nhật `submission_manifest.json` để phân biệt `SOURCE_BACKED`, `DERIVED`
  và `ASSUMPTION`, đồng thời tách checksum cho hai lớp.

## Quy tắc bảo toàn

- Không sửa file nào trong `data/raw/`.
- Raw snapshot không được dùng trực tiếp làm graph runtime; ứng dụng dùng
  processed release trong lớp `normalized/`/`data/processed/`.
