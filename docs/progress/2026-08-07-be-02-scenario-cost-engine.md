# 2026-08-07 — BE-02 Scenario và Cost Engine

## Mục tiêu

Xây dựng cost engine dùng chung cho scenario và search trên graph contract bất
biến, có thể truy nguyên từng thành phần cost của edge và route.

## Thay đổi đã thực hiện

- Thêm `CostPreset`, `EdgeCostBreakdown`, `RouteCostBreakdown` và `CostModelError`
  vào core contracts.
- Thêm `ScenarioCostEngine` với preset `BALANCED`, `PEAK_TRAFFIC`, `RAIN_SAFE`.
- Tính distance km, free-flow time, travel time, congestion level, traffic
  penalty, flood risk và weighted total cost.
- Hỗ trợ edge override, closed edge, route aggregation và nhãn `SIMULATED`.
- Bắt buộc preset weights không âm và tổng bằng 1; từ chối metric/cost âm.
- Bổ sung scenario `PEAK_TRAFFIC` vào toy fixture; giữ `OFFPEAK_BALANCED` và
  `HEAVY_RAIN_SAFE` với metadata mô phỏng rõ ràng.
- Tạo ADR-0005 và cập nhật architecture, data management, graph format, fixture
  README, changelog.

## Quyết định/giả định

`total_cost = distance × weight + free-flow time × weight + traffic penalty ×
weight + flood risk × weight`. Traffic penalty là phần thời gian trễ vượt
free-flow, không phải toàn bộ travel time.

## Bằng chứng kiểm tra

- `backend/tests/test_cost.py`: 12 passed.
- Existing backend tests: 14 passed, 1 dependency deprecation warning.
- `python scripts/data/validate_dataset.py`: PASS.

## Tồn tại/rủi ro

Preset và traffic/flood values hiện là `SIMULATED`; API scenario/search sẽ được
triển khai ở card BE-03.

## Bước tiếp theo

Tích hợp cost engine vào search service và API, sau đó đối chiếu route cost với
UCS/A* trên golden cases.
