# Nâng cấp trực quan hóa kết quả thuật toán Tour (Held-Karp DP & Nearest Neighbor)

## Bối cảnh & Mục đích
Sau khi chạy các thuật toán giao hàng đa điểm (Tour Held-Karp DP, Tour Nearest Neighbor, So sánh Tour), giao diện cũ còn tồn tại một số điểm bất cập:
- Hiển thị chuỗi node ID kỹ thuật thô (`N01 -> N03...`) thay vì tên địa điểm/landmark thực tế.
- Khối so sánh thứ tự nhập ban đầu (Original Order) với thứ tự tối ưu chưa làm nổi bật mức tiết kiệm (số km, số phút, % chi phí).
- Chưa thể hiện rõ ràng độ phức tạp và cam kết học thuật (Exact Optimal $O(N^2 \cdot 2^N)$ vs Greedy Approx $O(N^2)$).
- Render trùng lặp các thẻ metrics và kết quả 2 điểm ở chân trang khi đang ở chế độ Tour.
- Bảng chi tiết từng chặng (Legs Breakdown) tràn dữ liệu chuỗi nút micro.

## Các thay đổi đã thực hiện

1. **Hiển thị Huy hiệu Địa danh Lộ trình (Landmark Badges with Real Names):**
   - Ánh xạ `visit_order` sang tên địa danh thực tế có icon và phân định: `[Depot] Tên trạm xuất phát ➔ [#1] Tên trạm 1 ➔ ... ➔ [Depot] Về lại trạm`.
   
2. **Khối Đối chiếu Trước vs Sau Tối ưu (Optimization Efficiency Card):**
   - Đặt 2 cột song song: *Thứ tự nhập ban đầu (Baseline)* vs *Thứ tự sau tối ưu (Optimized)*.
   - Thêm thanh highlight màu xanh lá làm nổi bật mức tiết kiệm: `🎉 Tiết kiệm: X.XX km · Y.YY phút (Giảm Z.ZZ% chi phí)`.

3. **Thẻ Cam kết Thuật toán & Độ phức tạp (Theoretical Guarantee Badge):**
   - **Held-Karp DP:** Làm rõ nghiệm tối ưu toàn cục `OPTIMAL_HELD_KARP` với độ phức tạp $O(N^2 \cdot 2^N)$.
   - **Nearest Neighbor:** Làm rõ nghiệm tham lam xấp xỉ `APPROXIMATE_NEAREST_NEIGHBOR` với độ phức tạp $O(N^2)$ và chỉ số `% Approximation Gap`.
   - **Optimize Tour (Compare):** Hiển thị bảng so sánh 3 cột giữa Held-Karp, Nearest Neighbor và Thứ tự ban đầu.

4. **Bảng Lộ trình Từng Chặng Tinh gọn (Legs Breakdown Table):**
   - Hiển thị rõ Trạm đi $\rightarrow$ Trạm đến kèm khoảng cách, thời gian và chi phí chặng.
   - Thu gọn chuỗi nút trung gian trong thẻ `<details>` dạng `qua {count} giao lộ`.

5. **Cô lập Khối Hiển thị Tour:**
   - Ẩn khối `metrics-bar` và khối `result-details` chân trang của bài toán 2 điểm khi đang xem kết quả Tour (`!tourResult`).

6. **Đa ngôn ngữ & Kiểm thử:**
   - Bổ sung translation keys tương ứng trong `frontend/src/lib/i18n.ts`.
   - Bổ sung unit tests trong `frontend/src/lib/i18n.test.ts`.

## Bằng chứng Kiểm thử (Verification Evidence)
- `npm run test:frontend`: 13 test files, 53/53 tests passed.
- `npm run build:frontend`: TypeScript compiler & Vite build thành công 100% (0 errors).
- `npm run test:backend`: 86 passed, 3 skipped.
