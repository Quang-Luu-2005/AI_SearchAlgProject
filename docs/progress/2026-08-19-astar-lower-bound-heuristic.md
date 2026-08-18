# 2026-08-19 — A* scenario-aware lower-bound heuristic

## Mục tiêu

Thay heuristic Haversine chỉ dùng trọng số distance bằng lower bound theo
scenario, kiểm tra closure/edge gần 0 và đối chiếu A* với UCS.

## Thay đổi đã thực hiện

- Thêm `compute_scenario_rho` và `compute_lower_bound_heuristic` trong
  `backend/app/algorithms/weighted.py`.
- A* tính `rho_s` một lần trên snapshot bất biến; Greedy dùng cùng scale.
- Loại cạnh đóng bởi scenario hoặc override khỏi rho; bỏ cạnh có Haversine
  `<= 1e-6 km`; fallback `rho_s = 0` nếu không có cạnh usable.
- Thêm benchmark tái lập `npm run benchmark:lower-bound`, xuất JSON và bảng
  Markdown với nhãn `DERIVED_BENCHMARK`/`SIMULATED`.
- Thêm unit test cho công thức, closure, near-zero edge và 5 cặp O-D trên ba
  scenario baseline/peak/rain.

## Quyết định/giả định

Scenario được freeze trong một lần search. Tất cả cost là non-negative; các
scenario và cặp O-D benchmark dùng fixture `toy_graph_v0.1`, dữ liệu
`SIMULATED`. Không chỉnh sửa `data/raw/`.

## Bằng chứng kiểm tra

- `.venv\Scripts\python.exe -m pytest backend/tests/test_weighted_algorithms.py -q` — 7 passed.
- `npm run benchmark:lower-bound` — 15 combinations, 0 cost mismatch; A* mở
  không quá số node của UCS ở 15/15 trường hợp.

## Tồn tại/rủi ro

Benchmark là fixture nhỏ nên số node khám phá không đại diện hiệu năng graph
production. Heuristic giảm ít node khi `rho_s` thấp hoặc topology nhỏ.

## Bước tiếp theo

Nếu cần báo cáo trên graph processed lớn, bổ sung cặp O-D có seed và kiểm tra
coordinate completeness trước khi kết luận về hiệu năng.
