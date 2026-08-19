# 2026-08-19 — Presentation Slides Deck

## Tóm tắt
Nâng cấp và mở rộng toàn diện bộ slide thuyết trình lên **28 slides chuyên sâu** phục vụ báo cáo và bảo vệ đồ án **FloodRoute HCMC** (Lab 1 - Searching). Bộ slide được cung cấp dưới cả 3 định dạng: PowerPoint (`presentation_slides.pptx`), Web App tương tác (`presentation_slides.html`) và Markdown chuẩn Marp (`presentation_slides.md`). Nội dung bổ sung đầy đủ công thức toán học, chứng minh định lý Admissible & Consistent, bảng trace duyệt nút từng bước, phản ví dụ Greedy, nghiên cứu điển hình OD03, kết quả 3.600 lượt benchmark, Held-Karp DP vs Nearest Neighbor, Explainable AI và bộ Flashcards vấn đáp.

## Các nội dung đã hoàn thành
- [x] Tạo `docs/reports/presentation_slides.md` với 24 slide phân bổ theo 7 khối kiến thức:
  1. Trang bìa, nhóm & ma trận đóng góp (25% mỗi thành viên, rubric 100/100).
  2. Bối cảnh kẹt xe giờ cao điểm và rốn ngập Chợ Thủ Đức.
  3. Mục tiêu hệ thống, kiến trúc phân tầng Clean Architecture và data pipeline 4 tầng.
  4. Không gian trạng thái, mô hình chi phí 4 thành phần, 3 cost presets.
  5. Scenario-aware lower-bound Heuristic (ADR-0015) và chứng minh toán học Admissible/Consistent.
  6. Bộ 6 thuật toán tìm kiếm 2 điểm, cơ chế trace event, bảng duyệt nút mẫu và phản ví dụ Greedy.
  7. Kết quả thực nghiệm 3.600 lượt benchmark (A* = UCS chi phí tối ưu, Bidirectional nhanh nhất).
  8. Bài toán tối ưu giao hàng đa điểm (Asymmetric TSP), giải thuật Held-Karp DP vs Nearest Neighbor, đo % gap và % baseline savings.
  9. Dịch vụ sinh kịch bản ngẫu nhiên có kiểm soát (`RandomScenarioService`) với seed tái lập và Reachability check.
  10. Trí tuệ nhân tạo giải thích (Explainable AI), giao diện web MapLibre GL JS GPU.
  11. Chiến lược kiểm thử QA (11 bộ test) và bộ câu hỏi vấn đáp trọng tâm (Q&A Flashcards).
- [x] Tạo `docs/reports/presentation_slides.html` dạng standalone web presentation hiện đại, hỗ trợ phím tắt (`Left`, `Right`, `Space`, `F` fullscreen, `O` overview grid), thanh tiến trình, công thức LaTeX MathJax và tương thích đa kích thước màn hình.
