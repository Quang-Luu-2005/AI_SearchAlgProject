# 2026-08-07 — Dọn cây thư mục local

## Mục tiêu

Loại bỏ artefact cài đặt/cache không thuộc source tree và lockfile rỗng nằm sai cấp.

## Thay đổi đã thực hiện

- Xóa `frontend/frontend/package-lock.json` và thư mục rỗng tương ứng.
- Xóa `.venv/`, `frontend/node_modules/`, `node_modules/` và
  `floodroute_backend.egg-info/`; đây đều là artefact có thể tạo lại từ README/runbook.
- Xóa `frontend/dist/` cùng các thư mục `__pycache__/` và `.pytest_cache/` sinh trong
  quá trình build/kiểm tra.
- Chuẩn hóa `.gitignore` để bỏ qua `node_modules/` ở mọi cấp.
- Giữ nguyên `data/raw/`, dataset fixtures, tài liệu tham khảo và các thư mục
  placeholder có README.

## Quyết định/giả định

Các dependency/cache local không phải source hoặc dataset; khi cần có thể tạo lại
bằng các lệnh cài đặt trong README và `docs/runbook.md`.

## Bằng chứng kiểm tra

- Kiểm tra tham chiếu cho thấy script dùng `frontend/` làm frontend root và không
  tham chiếu `frontend/frontend/`.
- `git status --short` và `git check-ignore` được chạy sau khi dọn.
- Chạy lại test data/backend/frontend sau khi cài dependency sẽ là bước xác nhận
  môi trường đầy đủ; các dependency local đã được loại khỏi working tree.

## Tồn tại/rủi ro

Việc dọn dependency làm mất môi trường chạy cục bộ hiện tại, nhưng không mất mã
nguồn hay dữ liệu và có thể phục hồi bằng quy trình cài đặt đã ghi trong tài liệu.

## Bước tiếp theo

Khi cần phát triển, chạy lại các lệnh cài backend/frontend trong README rồi chạy
`npm test`.
