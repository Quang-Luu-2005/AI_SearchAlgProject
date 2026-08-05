# 2026-08-05 — Graph explorer nạp folder thông minh

## Mục tiêu

Cho giao diện tự tìm và hiển thị graph từ các folder dataset hợp lệ mà không cần
hard-code Node/Edge hoặc nhập filesystem path thủ công.

## Thay đổi đã thực hiện

- Thêm discovery đệ quy cho Graph Loader và tự nhập `metadata.json` khi có.
- Thêm API catalog/detail cho graph fixture, scenario closure và path validation.
- Thay graph hard-code trong React bằng API client, dropdown dataset/scenario và
  bản đồ Node/Edge động; cạnh đóng hiển thị nét đứt màu đỏ.
- Thêm backend API test, frontend URL test và production build verification.
- Cập nhật architecture, graph format, data management, ADR và changelog.

## Quyết định/giả định

- Chỉ khám phá graph dưới `data/fixtures`; không nhận arbitrary filesystem path.
- Folder tối thiểu có Node/Edge CSV; fixture bàn giao nên có thêm Scenario,
  metadata và test case JSON.
- Frontend không parse CSV để tránh nhân đôi Graph contract.
- Quyết định API/security boundary được ghi trong
  [ADR-0004](../decisions/0004-safe-fixture-graph-explorer-api.md).

## Bằng chứng kiểm tra

```powershell
npm run test:data
npm run test:backend
npm run test:frontend
npm run build:frontend
```

- Dataset validator PASS; backend 14 test PASS với 1 warning TestClient đã biết.
- Frontend: 5 PASS; production build PASS, 62 modules transformed.
- Browser visual QA chưa chạy được vì phiên không có browser instance khả dụng.

## Tồn tại/rủi ro

- API chỉ là local fixture explorer, chưa phải upload endpoint hoặc processed
  dataset registry công khai.
- Chưa có search algorithm/API, nên UI hiển thị topology và scenario closure,
  không tính tuyến tối ưu.

## Bước tiếp theo

Mở local app để visual smoke test thủ công, sau đó dùng API graph này cho các
search endpoint ở card tiếp theo.
