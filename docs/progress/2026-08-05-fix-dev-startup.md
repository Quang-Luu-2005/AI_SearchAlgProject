# 2026-08-05 — Sửa cách chạy backend/frontend

## Mục tiêu

Khắc phục frontend trả 404 và tránh backend dùng nhầm Python hệ thống; cung cấp
một lệnh chạy đồng thời cả hai service trên Windows.

## Thay đổi đã thực hiện

- Thêm `scripts/dev.mjs` kiểm tra `.venv` và Vite dependency trước khi chạy.
- Thêm `npm run dev` để khởi động backend ở port 8000 và frontend ở port 5173.
- Chuyển `dev:backend` sang Python trong `.venv` và đặt working directory Vite
  đúng `frontend/` cho `dev:frontend`.
- Xử lý `Ctrl+C` để dừng cây process của cả hai service trên Windows.
- Cập nhật README, runbook và changelog theo lệnh mới.

## Quyết định/giả định

- Dùng Node script không thêm dependency `concurrently`.
- `.venv` ở repository root là Python environment chuẩn cho backend.
- Không đổi stack, API hoặc data schema nên không cần ADR.

## Bằng chứng kiểm tra

- Smoke test `npm run dev`: backend health trả `ok`, frontend trả HTTP 200 và
  graph catalog trả 4 graph.
- Dataset validator PASS; backend 14 test PASS; frontend 5 test PASS; production
  build PASS với 62 modules transformed; `node --check scripts/dev.mjs` PASS.

## Tồn tại/rủi ro

- Script ưu tiên layout `.venv/Scripts/python.exe` trên Windows và hỗ trợ
  `.venv/bin/python` trên hệ Unix.
- Uvicorn reload tạo process con; script dùng `taskkill /T` khi dừng trên Windows.

## Bước tiếp theo

Dùng `npm run dev` làm lệnh onboarding mặc định và cập nhật script nếu cấu trúc
venv hoặc port thay đổi.
