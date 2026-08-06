# Hot reload cho dev server

## Mục tiêu

Khi chỉnh sửa mã nguồn, backend tự khởi động lại và frontend cập nhật qua HMR
mà không cần dừng rồi chạy lại thủ công.

## Thay đổi

- `scripts/dev.mjs` chạy Uvicorn với `--reload --reload-dir backend`.
- Vite HMR bật polling mỗi 300 ms để ổn định trên Windows, OneDrive và thư mục
  mount mạng.
- Cập nhật changelog và runbook để dùng `npm run dev`.

## Kiểm tra

- `node --check scripts/dev.mjs`
- `npm run test:frontend`
- `npm run build:frontend`

Mọi thay đổi ở bước này chỉ tác động môi trường phát triển; build production
không thay đổi.
