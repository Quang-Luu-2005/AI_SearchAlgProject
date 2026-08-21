# 2026-08-22 — Format và dọn project

## Mục tiêu

Giảm các artefact sinh tạm và bản sao không cần thiết trong source tree, giữ
nguyên mã nguồn, dataset versioned, provenance và tài liệu đầu ra chính.

## Thay đổi

- Xóa log build và file trung gian LaTeX đã bị track dưới `docs/reports/`.
- Xóa toàn bộ ảnh render kiểm tra cũ dưới `docs/reports/tmp/`.
- Xóa `docs/reports/main.pdf` vì trùng SHA-256 với
  `FloodRoute_HCMC_Technical_Report.pdf`, là bản PDF canonical.
- Xóa file rác `11.86745885` ở root.
- Ghi rõ trong `docs/reports/README.md` rằng artefact build là file tái tạo và
  không thuộc source tree.

## Phạm vi được giữ lại

- Không sửa `data/raw/` và không thay đổi dataset/manifest.
- Giữ report/slides source và các bản xuất bản chính được tài liệu hóa.
- Giữ môi trường local bị ignore (`.venv`, `node_modules`) để chạy test; đây
  không phải file source và không được commit.

## Kiểm tra

- Đối chiếu tham chiếu trước khi xóa các file sinh tự động.
- Xác nhận `main.pdf` và PDF canonical có cùng SHA-256 trước khi xóa.
- Chạy `git diff --check` và bộ test liên quan sau khi hoàn tất.
