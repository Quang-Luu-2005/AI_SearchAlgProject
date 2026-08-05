# ADR-0004: API khám phá graph fixture an toàn cho giao diện

- Trạng thái: Accepted
- Ngày: 2026-08-05

## Bối cảnh

Frontend cần hiển thị graph từ folder dataset thay vì hard-code Node/Edge. Cho
frontend gửi filesystem path tùy ý sẽ làm lộ cấu trúc máy và cho phép đọc file
ngoài phạm vi fixture; parse CSV trực tiếp ở React cũng tạo contract thứ hai.

## Quyết định

- Backend tự khám phá graph folder bên dưới `data/fixtures` bằng
  `GraphLoader.discover_directories()`.
- API dùng `graph_id` tương đối, resolve và xác nhận path vẫn nằm trong fixture
  root trước khi load.
- `GET /api/v1/graphs` trả catalog graph hợp lệ và báo riêng candidate không hợp lệ.
- `GET /api/v1/graphs/{graph_id}` trả Node/Edge/Scenario; scenario đánh dấu
  `is_closed` nhưng không xóa edge khỏi payload để phục vụ visualization.
- Frontend chọn graph/scenario từ catalog và không tự parse dataset file.

## Hệ quả

- Thêm folder hợp lệ vào fixture root là đủ để graph xuất hiện trên UI, không cần
  sửa source frontend.
- Core Graph Loader vẫn là nguồn contract duy nhất và graph gốc không bị mutate.
- API này phục vụ local fixture explorer; processed/public dataset cần policy
  catalog và authorization riêng nếu triển khai sau này.
