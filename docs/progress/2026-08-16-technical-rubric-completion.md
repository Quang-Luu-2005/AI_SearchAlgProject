# Hoàn thiện các khoảng trống technical của Lab 1

## Mục tiêu

Hoàn thiện các bằng chứng còn thiếu trong rubric: metrics two-point, trace state, hai
thuật toán bổ sung trên GUI, giải thích penalty/alternative comparison, baseline tour và
benchmark tái lập.

## Thay đổi

- GUI chạy/compare UCS, A*, BFS, DFS, Greedy và Bidirectional; card comparison chỉ ra
  best weighted cost, shortest, fastest và số tuyến khác nhau.
- Trace replay phân biệt frontier, current, closed và final path; metrics distance, ETA,
  cost, explored nodes và runtime được mở lại.
- Search explanation nêu edge có traffic/flood penalty lớn nhất.
- Optimize-tour trả thứ tự nhập ban đầu, baseline distance/time/cost và mức tiết kiệm.
- Pilot 90/155 ba scenario được mở trong dropdown nhưng giữ nhãn review/data limitations.
- Thêm runner và artifact 10 OD × 3 scenario × 6 thuật toán × 20 lần đo.

## Kiểm tra

- Dataset validator: PASS, gồm checksum, schema, connectivity và golden route-change.
- Backend: 82 test passed.
- Frontend: 53 test passed.
- Production build: thành công; còn cảnh báo Vite chunk JavaScript lớn hơn 500 kB.
- Benchmark: 3.600 measured runs; UCS và A* đổi tuyến ở golden OD10 giữa ba scenario.
