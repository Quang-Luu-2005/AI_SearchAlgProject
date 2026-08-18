# 2026-08-19 — Chốt cost profiles và trọng số

## Mục tiêu

Hoàn thiện Task 4 theo kế hoạch: giữ nguyên composite cost hiện tại, chốt ba
preset, giải thích đúng ý nghĩa trọng số và ghi nhận bằng chứng route thay đổi.

## Thay đổi đã thực hiện

- Giữ nguyên ba preset public: `BALANCED`, `PEAK_TRAFFIC`, `RAIN_SAFE`.
- Xác nhận các vector lần lượt là `(0.25, 0.30, 0.20, 0.25)`,
  `(0.15, 0.25, 0.45, 0.15)` và `(0.10, 0.25, 0.15, 0.50)` theo thứ tự
  distance, free-flow time, congestion, flood risk.
- Ghi rõ đây là hệ số ưu tiên mô phỏng/empirical, không phải phần trăm
  contribution vì bốn thành phần khác đơn vị và scale.
- Giữ road closure là hard constraint: cạnh đóng có `total_cost=null` và route
  aggregation/search không được đi qua.
- Không mở custom weights trong public API để giữ contract ổn định trong deadline;
  `ScenarioCostEngine` vẫn nhận preset map nội bộ cho test/extension.
- Thêm `scripts/benchmark_cost_profiles.py` và artifact profile review gồm bảng
  3 preset cùng 2 route-change examples.

## Bằng chứng kiểm tra

- `npm run benchmark:cost-profiles` — profile sums đều bằng `1.0`; ghi nhận toy
  `N01 → N06` đổi tuyến khi rain và market golden case đổi từ 4 lên 27 cạnh.
- `npm run test:backend` — 89 passed.
- `npm run test:data` — PASS; không chỉnh sửa `data/raw/`.

## Tồn tại/rủi ro

Các vector là giả định empirical cho prototype; không diễn giải chúng như xác
suất hay tỷ lệ đóng góp thực tế, và cần hiệu chỉnh lại nếu có dữ liệu traffic
thời gian thực/normalization được phê duyệt.
