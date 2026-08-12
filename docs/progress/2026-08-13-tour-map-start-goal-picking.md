# 2026-08-13 — Sửa START/GOAL picker cho tour đa điểm

## Mục tiêu

Cho phép Held-Karp, Nearest Neighbor và chế độ so sánh tour chọn depot cùng nhiều điểm
giao hàng trực tiếp trên bản đồ, thay vì nút gộp START/GOAL chỉ cập nhật START.

## Thay đổi đã thực hiện

- Tách hai nút tour: START chọn depot, GOAL thêm delivery stop.
- Giữ GOAL mode sau mỗi click để chọn liên tiếp; tự dừng khi đủ 10 stop hoặc khi nhấn Esc.
- Dùng chung validation cho dropdown và map: không cho stop trùng depot, stop trùng nhau
  hoặc stop thứ 11.
- Hiển thị marker đánh số cho các stop ngay trước khi chạy; sau khi có kết quả, marker
  theo visit order và biến mất dần theo trace.
- Dùng `textContent` cho tên marker để dữ liệu label không bị diễn giải như HTML.
- Bổ sung thông báo i18n Anh/Việt và regression tests cho picker/selection/marker.

## Quyết định/giả định

- Giữ type `START | GOAL`: trong tour mode, GOAL mang nghĩa một delivery stop mới.
- START mới trùng một stop cũ sẽ loại node đó khỏi danh sách stop để giữ API contract.
- Giới hạn 10 stop dùng cùng hằng số với phạm vi backend/ADR-0013.

## Bằng chứng kiểm tra

- Targeted Vitest: 3 file, 17 test PASS.
- `npm test`: data validator PASS; backend 66/66 test PASS; frontend 11 file,
  50/50 test PASS.
- `npm run build:frontend`: TypeScript + Vite production build PASS.
- `git diff --check`: PASS, không có whitespace error.

## Tồn tại/rủi ro

- Production build vẫn có cảnh báo chunk JavaScript chính lớn hơn 500 kB; không liên quan
  đến map picker và không làm build fail.

## Bước tiếp theo

Smoke test thao tác chọn START rồi click liên tiếp các GOAL trên trình duyệt trước buổi demo.
