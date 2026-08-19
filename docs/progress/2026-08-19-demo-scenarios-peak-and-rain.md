# 2026-08-19 — Hai scenario cố định để demo và nâng cấp khung giải thích kịch bản trên GUI

## Mục tiêu

Hoàn thiện Task 2 ("Hai scenario cứng để demo"): chuẩn bị hai tình huống cố định (`LANDMARK_PM_PEAK` và `LANDMARK_HEAVY_RAIN`) trên dataset demo chính (`thu_duc_landmarks_v1.0.0`), chốt 2 cặp Start-Goal chứng minh rõ ràng sự thay đổi lộ trình (detour), cung cấp giải thích chi tiết về đoạn đường bị ảnh hưởng/phạt trễ, và nâng cấp khung chọn Scenario trên Giao diện Web.

## Thay đổi đã thực hiện

- **Cấu hình 2 Scenario trên `thu_duc_landmarks_v1.0.0`**:
  - `LANDMARK_PM_PEAK` (`ASSUMPTION`): preset `PEAK_TRAFFIC`, tăng mức độ tắc nghẽn lên mức 5 và phạt trễ 18-20 phút trên trục huyết mạch Lê Văn Việt (`LM_EDGE_0127`) và Võ Văn Ngân (`LM_EDGE_0093`).
  - `LANDMARK_HEAVY_RAIN` (`SIMULATED`): preset `RAIN_SAFE`, đóng cứng (`is_closed=true`) đoạn ngập sâu Linh Xuân – Quốc lộ 1K (`LM_EDGE_0002`) và Lê Văn Việt (`LM_EDGE_0127`).
- **Chốt 2 cặp Start-Goal chứng minh đổi tuyến**:
  - `PM_PEAK`: Vincom Plaza Thủ Đức (`LM_065`) ➔ Trường Đại học FPT (`LM_054`). Tuyến A* tự động né trục Lê Văn Việt đang kẹt xe để đi đường vòng nội khu Tăng Nhơn Phú (10.28 km, 31.39 phút).
  - `HEAVY_RAIN`: Đại học Cảnh sát Nhân dân (`LM_001`) ➔ Chợ Linh Trung (`LM_023`). Tuyến trực diện Linh Xuân bị ngập đóng, A* tự động rẽ sang đường vòng an toàn qua Nhà Truyền Thống – Ga Thủ Đức – ĐH Sư phạm Kỹ thuật – BV Đa khoa khu vực (8.25 km, 21.21 phút).
- **Nâng cấp Khung Chọn Scenario trên Giao diện Web**:
  - Dropdown Scenario hiển thị tên thân thiện kèm icon trực quan (🟢 Mặc định, 🚗 Giờ cao điểm, 🌧️ Mưa ngập).
  - Thêm thẻ thông tin ngữ cảnh (`.scenario-info-card`) giải thích chi tiết nguyên nhân, cơ cấu trọng số chi phí, và danh sách các đoạn đường bị phạt/ngập đóng.
  - Bổ sung nút 1-chạm *"⚡ Chọn nhanh cặp Demo"* tự động điền cặp Start-Goal khuyến nghị để kiểm chứng ngay lập tức đường vòng.
  - Hỗ trợ đa ngôn ngữ đầy đủ (EN/VI) qua `i18n.ts`.
- **Kiểm thử & Báo cáo Thực nghiệm**:
  - Thêm 2 acceptance tests trong `backend/tests/test_cost_profiles.py` (`test_landmark_pm_peak_route_detour` và `test_landmark_heavy_rain_road_closure_detour`).
  - Cập nhật số liệu và diễn giải chi tiết trong `experiments/results/cost_profiles_v1.md` và `cost_profiles_v1.json`.

## Bằng chứng kiểm tra

- `.\.venv\Scripts\python.exe -m pytest backend/tests` — 88 passed, 3 skipped, 0 failed.
- `npm --prefix frontend test -- --run` — 13 test suites passed, 53 tests passed, 0 failed.
- `npm --prefix frontend run build` — TypeScript build thành công 100%, 0 lỗi type error.
- `python scripts/data/build_thu_duc_landmarks.py` — sinh đủ 3 scenarios và cập nhật SHA-256 checksums.
