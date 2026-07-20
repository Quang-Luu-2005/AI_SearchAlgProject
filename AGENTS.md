# Repository instructions

- Đọc `README.md`, `docs/architecture.md` và `docs/data-management.md` trước khi
  thay đổi kiến trúc hoặc dataset.
- Không chỉnh sửa dữ liệu trong `data/raw/`; tạo version mới và cập nhật manifest.
- Mọi fixture/simulation phải mang nhãn `SIMULATED` hoặc `ASSUMPTION`.
- Mọi thuật toán dùng contract trong `backend/app/core/contracts.py`, không phụ
  thuộc FastAPI, không mutate graph, và dùng tie-break deterministic.
- Sau mỗi bước triển khai, cập nhật một entry trong `docs/progress/`, mục
  `Unreleased` trong `CHANGELOG.md`, và tài liệu kiến trúc/data/API bị ảnh hưởng.
- Tạo ADR mới trong `docs/decisions/` nếu thay stack, schema, cost model, heuristic,
  API contract hoặc quyết định có chi phí đảo ngược đáng kể.
- Chạy các test liên quan; không ghi “hoàn tất” nếu chưa có bằng chứng kiểm tra.

