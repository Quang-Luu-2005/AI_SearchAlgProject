# 2026-07-20 — Bootstrap repository

## Mục tiêu

Tổ chức repository để bắt đầu website, chuẩn hóa dataset cho kiểm thử và tạo cơ
chế theo dõi tiến độ lâu dài dựa trên các file đầu vào hiện có.

## Thay đổi đã thực hiện

- Đọc đề bài, ghi chú vấn đáp, kế hoạch dự án và toàn bộ workbook v0.1.
- Chọn React/TypeScript/Vite/React Leaflet + Python/FastAPI.
- Dựng dashboard responsive với map fixture offline và hai scenario mẫu.
- Dựng FastAPI health/dataset metadata cùng `SearchResult`/trace contracts.
- Chuyển tài liệu nguồn vào `docs/references`, workbook bất biến vào `data/raw`.
- Tạo vòng đời data, manifest checksum, schema, toy graph và golden cases.
- Tạo validator, test nền, ADR, changelog và quy trình cập nhật docs.

## Quyết định/giả định

- Chưa dùng Next.js vì không có yêu cầu SSR/SEO và React Leaflet chạy client-side.
- Không coi workbook v0.1 là routable graph.
- Mọi tọa độ/edge/metric của toy graph mang nhãn `SIMULATED`.

## Bằng chứng kiểm tra

Các lệnh đã chạy khi đóng mốc:

```powershell
python scripts/data/validate_dataset.py
python -m pytest backend/tests
npm --prefix frontend run test
npm --prefix frontend run build
```

- Dataset validator: PASS; checksum, 6 node, 14 edge, weights và golden paths hợp lệ.
- Backend: 2 test PASS (còn một deprecation warning từ TestClient dependency).
- Frontend: 3 test PASS.
- Production build: PASS; 61 modules được build bằng Vite 8.1.5.

## Tồn tại/rủi ro

- OSM road graph và map-match 24 hotspot chưa thực hiện.
- Search endpoints/algorithms chưa triển khai; UI hiện phát route preview của fixture.
- Traffic multiplier vẫn là assumptions cần sensitivity analysis.

## Bước tiếp theo

Chốt bbox/polygon vùng Thủ Đức, tạo snapshot OSM có version và hoàn thiện processed
dataset v1.0 trước khi dùng kết quả để kết luận về tuyến thực tế.
