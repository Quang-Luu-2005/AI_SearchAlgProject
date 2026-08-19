# Tiến độ: Đóng đường 2 chiều (Bidirectional Closures) và Nâng cấp Trực quan Cạnh Đóng trên Bản đồ

**Ngày**: 2026-08-19  
**Người thực hiện**: Agent  
**Trạng thái**: Hoàn tất & Đã kiểm thử

---

## 1. Bối Cảnh & Vấn Đề (Context & Problem)
- Khi thử nghiệm thuật toán trên kịch bản ngập lụt (`LANDMARK_HEAVY_RAIN`), phát hiện các tuyến đường thực tế gồm 2 chiều độc lập (đi và về). Cấu hình cũ chỉ đóng chiều thuận (`Forward`), chưa đóng chiều nghịch (`Reverse`), khiến thuật toán khi chạy ngược chiều hoặc đổi điểm (Swap) vẫn đi qua chiều mở còn lại.
- Nét vẽ cạnh đóng (`floodroute-edge-closed`) trước đó chỉ dùng nét đứt 2px, ở mức thu phóng toàn cảnh (zoom 10.5 - 13) bị chìm vào nền bản đồ và không có tương tác chuột (hover/click) hay biểu tượng rào chắn cảnh báo.

---

## 2. Các Công Việc Đã Thực Hiện (Work Completed)

### 2.1. Dữ Liệu & Backend
- Cập nhật `scripts/data/build_thu_duc_landmarks.py`:
  - Kịch bản `LANDMARK_HEAVY_RAIN`: đóng toàn bộ cả 2 chiều của hành lang Linh Xuân (`LM_EDGE_0002`, `LM_EDGE_0166`, `LM_EDGE_0168`, `LM_EDGE_0055`) và hành lang Lê Văn Việt (`LM_EDGE_0127`, `LM_EDGE_0114`).
  - Kịch bản `LANDMARK_PM_PEAK`: áp dụng phạt tắc đường 2 chiều cho Lê Văn Việt (`LM_EDGE_0127`, `LM_EDGE_0114`) và Võ Văn Ngân (`LM_EDGE_0093`, `LM_EDGE_0129`).
- Tái tạo `data/processed/thu_duc_landmarks_v1.0.0/scenarios.json` và cập nhật mã băm SHA-256.
- Bổ sung acceptance test trong `backend/tests/test_cost_profiles.py` xác minh thuật toán A* không sử dụng bất kỳ cạnh đóng nào ở cả 2 chiều và tìm đường vòng chính xác.

### 2.2. Giao Diện & Bản Đồ (Frontend)
- Cập nhật `frontend/src/features/map/mapData.ts`:
  - Bổ sung `distance_m`, `free_flow_time_min` vào thuộc tính feature cạnh.
  - Viết hàm `buildClosedEdgeMarkers` tính toán trung điểm tọa độ và gộp nhóm các cặp đường 2 chiều để cắm Marker cảnh báo.
- Cập nhật `frontend/src/features/map/RouteMap.tsx`:
  - Thêm lớp viền phát quang đỏ `floodroute-edge-closed-halo` (`#ff4d4f`, width 6px-16px, opacity 0.48).
  - Nâng cấp lớp nét đứt `floodroute-edge-closed` (`#dc2626`, width 3px-8px, opacity 1.0).
  - Thêm lớp hitbox `floodroute-edge-closed-hitbox` (width 24px) và đăng ký sự kiện chuột `mouseenter`, `mouseleave`, `click`.
  - Hiển thị HTML Markers rào chắn `⛔ ĐÓNG ĐƯỜNG` nhấp nháy động tại trung tâm các tuyến đường đóng.
  - Xây dựng Popup chi tiết `closedEdgePopupContent` thể hiện: Tên đường, Cự ly, Lý do ngập sâu, Trạng thái đóng cứng và cảnh báo chi phí $\infty$.
  - Cập nhật Chú giải Bản đồ (Map Legend) với biểu tượng `⛔`.
- Cập nhật `frontend/src/styles.css`: Styling hiện đại cho `.road-closure-marker`, `.road-closure-badge`, `.road-closure-pulse`, `.map-edge-popup`.

---

## 3. Bằng Chứng Kiểm Thử (Verification Evidence)
- **Backend pytest**: 88 passed, 3 skipped, 0 failed.
- **Frontend vitest**: 13 test suites, 53 passed, 0 failed.
- **Frontend bundle build**: `tsc && vite build` hoàn thành với 0 lỗi TypeScript.
