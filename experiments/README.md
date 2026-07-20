# Reproducible experiments

- `cases/`: định nghĩa origin/destination, scenario, preset, algorithm và seed.
- `results/`: CSV/JSON sinh tự động; không sửa tay và không commit mặc định.

Khi có search engine, runner phải warm-up trước khi đo, tách runtime thuật toán khỏi
animation, chạy lặp ít nhất 20 lần cho graph nhỏ và báo median/p95.

