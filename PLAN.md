# Kế hoạch lập báo cáo đánh giá kỹ thuật Lab 1

> Cập nhật triển khai 2026-08-16: các mục 1, 3, 5, 6 và đồng bộ tài liệu ở mục 7 đã
> hoàn tất; mục 2 đã mở pilot ba scenario và giữ đúng nhãn review. Mục 4 đã có penalty
> edge và so sánh shortest/fastest/best cost; việc sinh một tuyến thay thế k-shortest
> riêng chưa được thêm vì compare hiện dùng các tuyến khác nhau từ sáu thuật toán.

## Tóm tắt

- Tạo báo cáo tiếng Việt tại `docs/assessment/lab-1-technical-gap-analysis.md`.
- Đánh giá branch `main` tại commit `5d7f1f7` theo **85 điểm kỹ thuật**; không tính 10 điểm báo cáo và 5 điểm video theo lựa chọn của người dùng.
- Điểm ước lượng hiện tại: **58/85, tương đương 68,2%**.
- Mọi kết luận phải dẫn chứng bằng yêu cầu trong PDF và mã nguồn, dữ liệu, giao diện hoặc test tương ứng.

## Nội dung báo cáo

- Lập ma trận yêu cầu–bằng chứng–thiếu sót–điểm dự kiến:

| Hạng mục kỹ thuật | Hiện tại |
|---|---:|
| Bối cảnh giao thông Việt Nam | 9/10 |
| Mô hình graph, dataset và cost | 11/15 |
| BFS, DFS, UCS, A* | 10/20 |
| Thuật toán bổ sung | 9/10 |
| Bài toán nhiều địa điểm | 8/10 |
| GUI và trực quan hóa | 7/10 |
| Giải thích và tuyến thay thế | 4/10 |
| **Tổng** | **58/85** |

- Ghi nhận điểm mạnh: dữ liệu Thủ Đức có nguồn gốc rõ ràng; UCS/A*, Held–Karp và Nearest Neighbor đã hoạt động; thuật toán deterministic; API, GUI bản đồ và test tương đối hoàn chỉnh.
- Phân tích các thiếu sót chính:
  - Chưa có BFS và DFS trong contract, backend, API, giao diện và test.
  - Dataset mặc định 65 địa điểm chỉ có một trạng thái congestion/risk nên chưa chứng minh được giao thông làm thay đổi tuyến; dataset 90 node có ba scenario lại chưa được đưa vào GUI.
  - Cost cộng trực tiếp các đại lượng khác đơn vị, chưa có chuẩn hóa hoặc thí nghiệm chứng minh trọng số; GUI chưa tách “tiêu chí tối ưu” khỏi scenario.
  - Trace chưa biểu diễn đúng frontier/open, current và closed; metrics của bài toán hai điểm đang bị ẩn.
  - Explanation chưa chỉ ra tuyến thay thế, đoạn đường ùn tắc/rủi ro, và so sánh shortest–fastest–best composite cost.
  - Multi-stop chưa so sánh thứ tự người dùng nhập với thứ tự tối ưu và mức tiết kiệm.
  - Thư mục experiments còn placeholder; một số test heuristic phụ thuộc dataset bị Git ignore; một số tài liệu đã lỗi thời.

## Lộ trình đạt tối đa 85 điểm

1. Bổ sung BFS và DFS theo contract hiện hữu, deterministic tie-break, trace đầy đủ và test reachable/unreachable/cycle/start=goal; đưa vào API, GUI và chế độ so sánh.
2. Kiểm định rồi đưa dataset nhiều scenario vào GUI; bổ sung lựa chọn tiêu chí tối ưu và ít nhất ba ca minh họa tuyến thay đổi do ùn tắc hoặc ngập.
3. Hoàn thiện trace player để hiển thị frontier/open, node hiện tại, closed/explored và final path; khôi phục đầy đủ distance, ETA, cost, explored nodes và runtime.
4. Nâng explanation bằng tuyến thay thế có số liệu, đoạn đường gây penalty lớn nhất, lý do chọn tuyến và cam kết optimal/near-optimal.
5. Bổ sung baseline thứ tự multi-stop ban đầu, thứ tự tối ưu, chi phí và phần trăm tiết kiệm.
6. Tạo benchmark tái lập tối thiểu 10 cặp OD × 3 scenario × 20 lần chạy, báo cáo median/p95, explored nodes, cost và mức thay đổi tuyến.
7. Loại bỏ phụ thuộc test vào dataset bị ignore; đồng bộ README thuật toán, optimization, API và kiến trúc. Nếu thay cost model hoặc contract, yêu cầu ADR, changelog và progress entry theo quy định repository.

Mỗi hạng mục sẽ có mức tăng điểm dự kiến, độ ưu tiên P0/P1 và tiêu chí nghiệm thu cụ thể để có thể giao trực tiếp cho người triển khai.

## Kiểm tra báo cáo

- Đối chiếu đủ cả bảy tiêu chí kỹ thuật trong rubric PDF và kiểm tra tổng điểm đúng **58/85**.
- Mỗi nhận định phải có đường dẫn tới file hoặc test làm bằng chứng; phân biệt rõ “đã có”, “có một phần” và “chưa có”.
- Ghi lại bằng chứng kiểm thử hiện tại: backend 66/66, frontend 50/50, build thành công và cảnh báo còn tồn tại.
- Không thay đổi API, dataset hoặc mã nguồn khi tạo báo cáo; báo cáo/video chỉ xuất hiện dưới dạng checklist ngoài phạm vi chấm điểm hiện tại.
