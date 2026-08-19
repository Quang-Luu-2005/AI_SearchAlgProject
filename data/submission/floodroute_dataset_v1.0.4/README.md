# Mô tả dữ liệu nộp bài FloodRoute HCMC — v1.0.4

## 1. Mục đích

Bộ dữ liệu phục vụ bài toán tìm tuyến đường giữa các landmark tại khu vực Thủ Đức.
Mục tiêu chính là ưu tiên tuyến đường ngắn nhất khả thi trong điều kiện bình thường,
sau đó đánh giá ảnh hưởng của kẹt xe và ngập nước lên tuyến được chọn.

Đây là dữ liệu phục vụ học tập, minh họa và kiểm thử thuật toán; không phải dữ liệu
dẫn đường hoặc thông tin giao thông theo thời gian thực.

## 2. Quy mô và cấu trúc

Phần dữ liệu đã chuẩn hóa gồm:

- **65 node**: các landmark/địa điểm lớn trong khu vực nghiên cứu.
- **283 cạnh có hướng**: các đoạn đường tổng hợp từ mạng road-path, giữ hướng di
  chuyển và hình học polyline.
- `nodes.csv`: thông tin node, tọa độ và metadata.
- `edges.csv`: node đầu/cuối, chiều dài, thời gian đường thông và hình học tuyến.
- `landmarks.csv`: danh sách landmark dùng trên giao diện.
- `scenarios.json`: các kịch bản chi phí và trạng thái đường.
- `metadata.json`, `validation_report.json`: metadata và kết quả kiểm tra.

## 3. Các kịch bản

- **NORMAL**: không áp dụng cản trở; dùng làm mốc tìm tuyến ngắn nhất khả thi.
- **CONGESTION**: 57/283 cạnh có mức phạt do kẹt xe, khoảng 20% mạng đường.
- **FLOOD**: 57/283 cạnh có rủi ro ngập, khoảng 20% mạng đường.
- **RANDOM**: frontend sinh seed mới mỗi lần kích hoạt, đồng thời chọn cạnh kẹt,
  ngập và đóng đường để minh họa trạng thái động.
- **HARD CLOSURE**: đóng chính xác edge ID được chỉ định; cạnh đóng bị loại khỏi
  quá trình tìm kiếm và không thể xuất hiện trong route.

Các giá trị kẹt/ngập, trọng số chi phí và closure phục vụ demo đều mang nhãn
`ASSUMPTION`, không đại diện cho số liệu thực tế theo thời gian thực.

## 4. Nguồn gốc và giới hạn

- `raw_collected/` là bản sao bất biến của snapshot OSM/UTraffic và registry nguồn.
- `normalized/` là dữ liệu đã chuẩn hóa cho graph và cost engine.
- Node và ranh giới dựa trên OSM; mạng đường và một số thuộc tính tốc độ/thời gian
  lấy từ snapshot UTraffic lịch sử.
- Flood risk bằng 0 nghĩa là nguồn không ghi nhận rủi ro, không khẳng định an toàn.
- Closure áp dụng theo đúng landmark edge ID, không tự lan sang aggregate edge khác
  chỉ vì source segment hoặc hình học bị chồng lấn.
- Kết quả tối ưu theo composite cost; riêng NORMAL dùng cost cơ sở để ưu tiên tuyến
  ngắn nhất khả thi.
