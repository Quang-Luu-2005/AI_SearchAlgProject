# 2026-07-31 — Rà soát project, project brief và kế hoạch sprint

## Mục tiêu

Rà soát trạng thái thực tế của FloodRoute HCMC và tạo một tài liệu thống nhất để
bốn thành viên hiểu đồ án làm gì, vì sao làm và cần thực hiện gì trong bảy ngày
31/07–07/08/2026, ưu tiên backend và thuật toán.

## Thay đổi đã thực hiện

- Đối chiếu README, kiến trúc, data management, ADR, progress log, đề bài PDF,
  ghi chú vấn đáp, kế hoạch DOCX, code backend/frontend, fixture, manifest,
  validator và test hiện có.
- Tạo `docs/project-brief-and-trello-plan.md` gồm project brief, trạng thái repo,
  sprint goal, Definition of Done, board Trello và card chi tiết cho bốn người.
- Đặt backend/core contract, graph/cost/scenario, sáu thuật toán và search API trên
  đường găng; OSM/data chạy song song nhưng không chặn fixture.
- Ghi nhận onboarding gap: root `npm test` dừng nếu Python hiện tại chưa cài
  dependency dev; backend tests chạy PASS bằng Python trong `.venv`.

## Quyết định/giả định

- Chưa biết tên bốn thành viên nên tài liệu dùng TV1–TV4; nhóm thay bằng tên thật
  khi tạo board.
- Sprint tính theo bảy ngày lịch từ 31/07 đến hết 07/08/2026.
- Tài liệu chuẩn bị card để nhập/copy sang Trello; không thay đổi một board ngoài
  repository.
- Không thay stack, schema, cost model, heuristic hay API contract trong bước tài
  liệu này, nên không tạo ADR mới. Card TEAM-00 yêu cầu ADR khi nhóm thực hiện các
  quyết định đó.
- Không sửa `data/raw/`. Runtime spreadsheet bắt buộc không khả dụng, nên workbook
  raw không được mở bằng thư viện thay thế; checksum vẫn được validator xác minh.

## Bằng chứng kiểm tra

Các lệnh đã chạy:

```powershell
npm run test:data
.\.venv\Scripts\python.exe -m pytest backend/tests
npm run test:frontend
npm run build:frontend
```

Kết quả:

- Dataset validator: PASS; checksum raw source, 6 node, 14 directed edge, scenario
  weights và golden paths hợp lệ.
- Backend: 2 test PASS; còn 1 deprecation warning từ TestClient dependency.
- Frontend: 3 test PASS.
- Production build: PASS; Vite build 61 modules.
- `npm test` bằng Python hệ thống: dừng ở backend vì môi trường đó thiếu `pytest`;
  đây là setup/onboarding gap, không phải backend test failure trong `.venv`.

## Tồn tại/rủi ro

- Chưa triển khai graph loader, scenario/cost engine, sáu thuật toán, search API,
  multi-stop optimizer hoặc trace player thật.
- OSM graph/map-match chưa sẵn sàng; manifest vẫn `NOT_READY`.
- Kế hoạch cần được nhóm gán tên, xác nhận sức chứa cuối tuần và tạo card thực tế
  trên Trello.

## Bước tiếp theo

Tạo board theo tài liệu, hoàn tất TEAM-00 trong ngày 31/07, sau đó triển khai
vertical slice backend-first và chỉ chuyển card sang Done khi test/acceptance PASS.
