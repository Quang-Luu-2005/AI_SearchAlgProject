# Tách biệt mục So sánh thuật toán trong Bảng điều khiển (Control Panel)

## Bối cảnh & Mục đích
Người dùng yêu cầu phân tách rõ ràng việc so sánh thuật toán thành một phân mục riêng biệt trong bộ chọn thuật toán (`<select>`) tại Bảng điều khiển của giao diện Pathfinder AI (FloodRoute HCMC), giúp phân định rành mạch giữa chế độ chạy thuật toán đơn lẻ và chế độ so sánh đối chuẩn, đồng thời bảo đảm không làm thay đổi hay gây ảnh hưởng ngoài ý muốn đến các thành phần mã nguồn khác.

## Các thay đổi đã thực hiện

1. **Từ điển đa ngôn ngữ (`frontend/src/lib/i18n.ts`):**
   - Bổ sung 3 khóa dịch nhóm thuật toán:
     - `group_two_point`: `"🔍 Two-Point Search (Single Algorithm)"` / `"🔍 Tìm đường 2 điểm (Thuật toán đơn lẻ)"`
     - `group_multi_stop`: `"📦 Multi-Stop Tour (TSP)"` / `"📦 Giao hàng đa điểm (TSP)"`
     - `group_comparison`: `"📊 Algorithm Comparison"` / `"📊 So sánh thuật toán"`
   - Bổ sung unit tests tương ứng trong `frontend/src/lib/i18n.test.ts`.

2. **Giao diện Bảng điều khiển (`frontend/src/App.tsx`):**
   - Tái cấu trúc danh sách `<option>` trong `<select>` bộ chọn thuật toán thành 3 nhóm `<optgroup>`:
     - Nhóm 1: `t('group_two_point', lang)` chứa A*, UCS, BFS, DFS, GREEDY, BIDIRECTIONAL.
     - Nhóm 2: `t('group_multi_stop', lang)` chứa HELD_KARP, NEAREST_NEIGHBOR.
     - Nhóm 3: `t('group_comparison', lang)` chứa COMPARE (So sánh 6 thuật toán tìm kiếm 2 điểm) và OPTIMIZE_TOUR (So sánh Tour Held-Karp vs Nearest Neighbor).
   - Bảo toàn 100% các giá trị `value`, state machine (`algorithm`, `isTourMode`), và luồng gọi API `executeSearch`.

3. **Giao diện CSS (`frontend/src/styles.css`):**
   - Bổ sung style cho `select optgroup` (màu `--primary`, font-weight đậm, cỡ chữ chuẩn) tương thích giao diện dark/light.

## Kiểm thử & Bằng chứng
- `npm run test:frontend`: 13 test files, 53/53 tests passed.
- `npm run build:frontend`: TypeScript compiler & Vite build bundle thành công (0 errors).
- `npm run test:backend`: 86 tests passed, 3 skipped.
