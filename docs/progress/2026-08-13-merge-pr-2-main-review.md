# 2026-08-13 — Merge và hậu kiểm PR #2 trên main

## Mục tiêu

Tích hợp Card FE-01, FE-02 và OPT từ PR #2 vào `main` mà không sửa nhánh `VLTVan`,
sau đó khắc phục các lỗi hợp đồng, checksum đa nền tảng và tài liệu được phát hiện khi review.

## Thay đổi đã thực hiện

- Merge `origin/VLTVan` vào `main` bằng merge commit, giữ nguyên head của nhánh nguồn.
- Bảo vệ byte của `data/raw/**` bằng `.gitattributes` để Git không đổi LF/CRLF và làm
  sai checksum SHA-256 trên Windows.
- Từ chối stop trùng, depot xuất hiện trong stops và `tour_algorithm` không được hỗ trợ.
- Sửa example OpenAPI/API từ 3 stop thành đúng 5 stop tối thiểu; đồng bộ README,
  architecture, runbook và trạng thái endpoint/heuristic hiện hành.
- Bổ sung ADR-0013 cho cost reuse, giới hạn 5–10 stop và guarantee của Held-Karp/
  Nearest Neighbor.

## Quyết định/giả định

- Không sửa hoặc force-push nhánh `VLTVan`; mọi hậu kiểm nằm trên `main`.
- Không thay dữ liệu raw hoặc checksum manifest. `.gitattributes` chỉ bảo toàn byte đã freeze.
- Held-Karp chính xác theo ma trận shortest-path của graph/scenario snapshot; Nearest
  Neighbor là heuristic và không có bảo đảm tối ưu.

## Bằng chứng kiểm tra

- `npm run test:data`: PASS; raw checksum, graph/schema/provenance và golden cases đều đạt.
- `npm run test:backend`: 66 passed, 0 failed; còn 1 cảnh báo deprecation từ Starlette
  TestClient/httpx.
- `npm run test:frontend`: 10 test files, 43 tests passed, 0 failed.
- `npm run build:frontend`: TypeScript và Vite production build PASS.
- `git diff --check`: PASS, không có whitespace error.

## Tồn tại/rủi ro

- PR lớn (35 file, hơn 5.000 dòng thêm) vẫn cần smoke test tương tác bản đồ trên trình duyệt
  nếu dùng cho buổi demo chính thức.
- Vite cảnh báo bundle JavaScript chính khoảng 1,2 MB trước gzip; nên code-split nếu thời
  gian tải production trở thành vấn đề.
- Starlette TestClient hiện có cảnh báo chuyển từ `httpx` sang `httpx2`; chưa làm test fail.

## Bước tiếp theo

Smoke test các luồng chọn điểm, phát trace và tour đa điểm trên trình duyệt trước buổi demo.
