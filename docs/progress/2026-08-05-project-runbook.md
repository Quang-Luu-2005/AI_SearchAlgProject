# 2026-08-05 — Viết runbook chạy toàn bộ dự án

## Mục tiêu

Tạo một tài liệu duy nhất để thành viên mới có thể cài, chạy, nạp dữ liệu, xem
graph trên giao diện và kiểm tra toàn bộ repository ở trạng thái hiện tại.

## Thay đổi đã thực hiện

- Thêm `docs/runbook.md` bao quát prerequisite, cài backend/frontend, validation,
  dev server, graph explorer, tạo fixture mới, gọi API, Python loader, test,
  production build, troubleshooting và giới hạn hiện tại.
- Liên kết runbook từ root README và documentation map.
- Cập nhật changelog và progress index.

## Quyết định/giả định

- Runbook ưu tiên PowerShell vì đây là môi trường phát triển hiện tại.
- Tách hai terminal backend/frontend để log và vòng đời process rõ ràng.
- Yêu cầu activate `.venv` trước test backend để tránh dùng Python hệ thống.
- Không thay stack, schema hoặc API nên không tạo ADR mới.

## Bằng chứng kiểm tra

- Đối chiếu command với root `package.json`, `backend/pyproject.toml` và
  `frontend/package.json`.
- `git diff --check`: PASS; các file/link nội bộ được nhắc trong runbook tồn tại.

## Tồn tại/rủi ro

- Production preview không dùng Vite dev proxy; deploy thật cần cấu hình API URL
  hoặc reverse proxy.
- Runbook phải được cập nhật khi thêm search API, processed dataset hoặc thay
  dependency/runtime command.

## Bước tiếp theo

Dùng runbook cho một lượt onboarding/smoke test thủ công và ghi lại vấn đề môi
trường nếu có.
