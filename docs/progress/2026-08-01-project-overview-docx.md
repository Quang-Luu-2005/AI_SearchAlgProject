# 2026-08-01 — Tạo DOCX tổng quan ý tưởng và kiến trúc

## Mục tiêu

Tạo một tài liệu Word có thể gửi trực tiếp cho thành viên nhóm, giảng viên hoặc
người review để họ hiểu FloodRoute HCMC muốn giải bài toán gì, trải nghiệm mục
tiêu ra sao và các khối hệ thống phối hợp như thế nào.

## Thay đổi đã thực hiện

- Tạo `docs/FloodRoute_HCMC_Tong_quan_y_tuong_va_kien_truc.docx` gồm 10 phần,
  bao quát idea, user flow, hai bài toán two-point/multi-stop, cost model ở mức
  khái niệm, kiến trúc logic, module boundary, `SearchResult`, data lifecycle,
  vai trò thuật toán, trạng thái bootstrap và tiêu chí thành công.
- Thêm hai sơ đồ trực quan cho kiến trúc hệ thống và vòng đời dữ liệu; thêm năm
  bảng so sánh có fixed geometry để tránh lệch layout giữa renderer.
- Phân biệt rõ phần đã có với đích MVP; giữ cảnh báo prototype học thuật,
  `SIMULATED`, `ASSUMPTION` và `routing_dataset_status = NOT_READY`.
- Thêm link tới tài liệu trong root `README.md` và bản đồ tài liệu `docs/README.md`.

## Quyết định/giả định

- Dùng design preset `standard_business_brief` và first-page pattern
  `editorial_cover`; khổ Letter, lề 1 inch, Calibri 11 pt, heading xanh và footer
  số trang.
- Cost formula trong tài liệu được ghi là `ASSUMPTION / thiết kế dự kiến`; tài
  liệu không chốt normalization, weight chính thức hoặc heuristic guarantee.
- Nội dung tổng hợp từ README, architecture, data management, ADR, manifest,
  core contract, code frontend/backend và project brief hiện có.
- Không thay stack, schema, API contract, cost model, heuristic hoặc dataset nên
  không tạo ADR và không sửa `data/raw/`.

## Bằng chứng kiểm tra

Kiểm tra DOCX:

```powershell
.\.venv\Scripts\python.exe <documents-skill>\scripts\table_geometry.py `
  docs\FloodRoute_HCMC_Tong_quan_y_tuong_va_kien_truc.docx
.\.venv\Scripts\python.exe <documents-skill>\scripts\a11y_audit.py `
  docs\FloodRoute_HCMC_Tong_quan_y_tuong_va_kien_truc.docx
```

- Table geometry: PASS; cả 5 bảng có `tblW=9360`, `tblInd=120`, `tblGrid` và
  toàn bộ `tcW` khớp nhau.
- Accessibility audit: 0 high, 0 medium, 0 low finding; hai hình có alt text.
- Structural audit: 10 Heading 1, 12 Heading 2, 5 bảng, 2 hình; không có comment,
  tracked change hoặc citation token nội bộ; phần cuối tài liệu còn nguyên.
- Renderer chuẩn `render_docx.py` đã được chạy nhưng máy không có LibreOffice.
  Dùng renderer DOCX dự phòng để xuất 10 trang đầu và một bản tail QA riêng cho
  hai phần cuối; đã mở kiểm tra từng PNG, không thấy clipping, overlap, bảng vỡ,
  glyph lỗi hoặc footer lệch.

Kiểm tra repository:

```powershell
npm run test:data
.\.venv\Scripts\python.exe -m pytest backend\tests
npm run test:frontend
npm run build:frontend
```

- Dataset validator: PASS; 6 node, 14 directed edge, checksum/scenario/golden
  path hợp lệ.
- Backend: 2 test PASS; còn 1 `StarletteDeprecationWarning` đã biết.
- Frontend: 3 test PASS.
- Production build: PASS; 61 modules transformed.

## Tồn tại/rủi ro

- LibreOffice không có trong môi trường và Word PDF export bị treo, nên visual QA
  dùng renderer dự phòng. DOCX vẫn mở và parse được bằng Word-compatible OOXML.
- Nội dung phải được cập nhật khi nhóm chốt cost normalization, graph/scenario
  contract, Bidirectional variant, heuristic A* hoặc API schema.

## Bước tiếp theo

Chia sẻ DOCX trong buổi kickoff/review, thống nhất các quyết định còn mở ở phần
cuối tài liệu, sau đó cập nhật overview cùng ADR/architecture khi contract thật
được chốt.
