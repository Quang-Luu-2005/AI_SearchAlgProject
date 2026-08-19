# Tiến độ: Chuẩn hóa hành lang ngập lụt trục dốc Võ Văn Ngân trong kịch bản Heavy Rain

- **Ngày thực hiện**: 2026-08-19
- **Tác giả**: Antigravity Pair Programming
- **Trạng thái**: Hoàn tất (Verified)

---

## 1. Bối cảnh & Yêu cầu
- Người dùng mong muốn điều chỉnh hành lang ngập lụt / đóng đường trong kịch bản `LANDMARK_HEAVY_RAIN` sang **Phương án 2: Trục dốc Võ Văn Ngân** (điểm nóng ngập lụt nổi tiếng nhất của TP. Thủ Đức khi mưa to).
- Cần đảm bảo:
  1. Start và Goal không trùng lặp hay bị đóng cạnh trực tiếp.
  2. Thuật toán A* thể hiện rõ ràng cơ chế đổi tuyến đường (detour) từ trục dốc sang đường tránh cao ráo.
  3. Bản đồ hiển thị huy hiệu `⛔ ĐÓNG ĐƯỜNG` phát sáng nổi bật trên trục Võ Văn Ngân.

---

## 2. Các thay đổi thực hiện

### 2.1. Dataset & Scenarios
- File: `scripts/data/build_thu_duc_landmarks.py` & `data/processed/thu_duc_landmarks_v1.0.0/scenarios.json`
- Đóng cả 2 chiều trục dốc Võ Văn Ngân: `LM_EDGE_0093` (lên dốc) & `LM_EDGE_0129` (xuống dốc), cùng trục Lê Văn Việt (`LM_EDGE_0127` & `LM_EDGE_0114`).
- Tái tạo dataset và cập nhật mã băm SHA-256.

### 2.2. Cặp Demo & Trải nghiệm Web UI
- Start: `LM_036` (Nhà Truyền Thống Thủ Đức - Gần Chợ Thủ Đức)
- Goal: `LM_043` (Trường Đại học Quốc tế Sài Gòn - SIU)
- Tuyến Baseline: Leo dốc Võ Văn Ngân thẳng lên Ga Thủ Đức ➔ SIU (3.08 km, 6.40 min).
- Tuyến Heavy Rain (Detour): Rẽ sang ngã Vincom Plaza ➔ Ga Thủ Đức ➔ BV Quân Dân Y ➔ SIU (4.82 km, 12.40 min).
- Cập nhật i18n EN/VI và nút 1-chạm *"⚡ Chọn nhanh cặp Demo"*.

### 2.3. Kiểm thử & Bằng chứng thực nghiệm
- `backend/tests/test_cost_profiles.py`: Bổ sung test tự động kiểm tra `LM_036 ➔ LM_043` né hoàn toàn cạnh đóng `LM_EDGE_0093`.
- `experiments/results/cost_profiles_v1.md` & `cost_profiles_v1.json`: Cập nhật bảng kết quả EX04.

---

## 3. Bằng chứng kiểm tra (Test Evidence)
- **Pytest**: `88 passed, 3 skipped, 0 failed` in 2.10s.
- **Vitest**: `13 passed, 53 tests passed, 0 failed` in 5.70s.
- **Frontend Build**: `tsc && vite build` hoàn thành không có lỗi.
