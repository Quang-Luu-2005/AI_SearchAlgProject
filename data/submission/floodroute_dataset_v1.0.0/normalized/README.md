# FloodRoute HCMC — normalized dataset v1.0.0

Đây là lớp dữ liệu đã chuẩn hóa cho bài nộp, được trích từ release đang dùng trong
ứng dụng: 65 landmark có thể chọn và 178 cạnh đường có hướng tại khu vực Thủ Đức.

## Thành phần

- `nodes.csv`: landmark/POI, tọa độ OSM và node đường được snap.
- `edges.csv`: đường đi có hướng được tổng hợp từ các đoạn UTraffic.
- `landmarks.csv`: bảng landmark phục vụ hiển thị và tra cứu.
- `scenarios.json`: preset chi phí; các trọng số và giả định được gắn nhãn `ASSUMPTION`.
- `metadata.json`: provenance, nguồn, snapshot date và giới hạn sử dụng.
- `validation_report.json`: kết quả kiểm tra release (`PASS`).
- `checksums.sha256`: SHA-256 của các file dataset.
- `submission_manifest.json`: manifest của bundle nộp bài.

## Provenance và giới hạn

Dataset là bản snapshot lịch sử, không phải dữ liệu giao thông real-time và không
dùng làm hướng dẫn an toàn/điều hướng thực tế. Landmark lấy từ OpenStreetMap;
đường được tổng hợp từ snapshot UTraffic lịch sử. Dữ liệu có trạng thái `MIXED`:
source-backed, derived và một số tham số học thuật `ASSUMPTION`.

Bundle này không chứa dữ liệu `data/raw/` và không chỉnh sửa raw snapshot gốc.
