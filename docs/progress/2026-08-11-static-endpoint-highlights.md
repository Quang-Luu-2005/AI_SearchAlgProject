# Nhật ký tiến độ: Giữ viewport khi chọn endpoint

**Ngày:** 2026-08-11  
**Phạm vi:** Frontend MapLibre

## Thay đổi

- Bỏ camera effect gọi `flyTo`/`fitBounds` khi `startId` hoặc `goalId` thay đổi.
- Giữ `fitBounds` cho lúc nạp graph/boundary và thao tác reset viewport.
- Thêm hai HTML marker MapLibre dạng ghim lớn, neo tại tọa độ endpoint: START màu cam,
  GOAL màu hồng; không tạo ghim cho node chưa được chọn.
- Cập nhật regression test để xác nhận thay đổi endpoint không làm camera di chuyển và
  tạo đúng hai ghim START/GOAL bên cạnh visual state `start`/`goal` trong node source.

## Bằng chứng kiểm tra

- `npm run test:frontend`: PASS, 5 test file / 24 test.
- `npm run build:frontend`: PASS (`tsc` và Vite production build).

## Giới hạn

- Vite vẫn cảnh báo bundle JavaScript lớn hơn 500 kB; thay đổi này không làm phát sinh
  cảnh báo đó và chưa thực hiện code splitting.
