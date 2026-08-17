# Reproducible experiments

- `cases/`: định nghĩa origin/destination, scenario, preset, algorithm và seed.
- `results/`: CSV/JSON sinh tự động; không sửa tay và không commit mặc định.

Runner `npm run benchmark:search` dùng case cố định 10 OD × 3 scenario × 6 thuật toán,
warm-up trước khi đo, tách runtime thuật toán khỏi animation, chạy lặp 20 lần và báo
median/p95, explored nodes, cost cùng thay đổi tuyến. Artifact canonical mang nhãn
`DERIVED_BENCHMARK`; timing phụ thuộc môi trường được ghi trong file.
