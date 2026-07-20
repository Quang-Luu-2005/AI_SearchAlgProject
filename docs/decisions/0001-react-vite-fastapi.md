# ADR-0001: React/Vite frontend và FastAPI backend

- Trạng thái: Accepted
- Ngày: 2026-07-20

## Bối cảnh

Lab yêu cầu GUI web phát lại search trace, nhiều thuật toán AI bằng Python và bộ
test chứng minh optimality/counterexample. Kế hoạch gốc cũng đề xuất React,
TypeScript, Leaflet và FastAPI.

## Quyết định

Dùng React + TypeScript + Vite cho client-side visualization; React Leaflet cho
map; FastAPI làm HTTP boundary; thuật toán viết bằng module Python thuần.

## Hệ quả

- Ưu: frontend/backend phát triển song song qua contract; engine dễ test; demo có
  thể chạy offline trên snapshot; không mang thêm SSR/server framework.
- Chi phí: phải giữ schema TypeScript/Python đồng bộ và chạy hai dev server.
- Ràng buộc: React Leaflet chỉ chạy phía client; map nền online không được là phụ
  thuộc bắt buộc của demo.

