# LaTeX Beamer presentation

## Đã thực hiện

- Tạo nguồn chỉnh sửa được tại `docs/reports/presentation_slides.tex`.
- Dùng Beamer 16:9 theo phong cách Madrid của slide mẫu: nền trắng, thanh tiêu đề xanh đậm, block xanh nhạt và một họ font TeX Gyre Heros thống nhất.
- Soạn 33 frame: bối cảnh, mục tiêu, graph, dataset, free-flow time, cost, scenario, closure, sáu thuật toán, A*, heuristic, kiến trúc, frontend, gallery ảnh minh họa, alternatives, TSP, kiểm thử, giới hạn và kết luận.
- Thêm logo KHTN ở bìa và các ảnh minh họa giao diện bản đồ, route A*, so sánh thuật toán và tối ưu tour từ `docs/reports/figures/`.
- Thay bảng thành viên/phân công bằng bảng phân bổ điểm: 35%, 25%, 20%, 20% và tổng 100%.
- Đồng bộ các số liệu hiện tại: 65 node, 283 directed edge, 57/283 edge cho FLOOD/CONGESTION và RANDOM gồm cả closure, flood, congestion.

## Kiểm tra

- XeLaTeX biên dịch thành công hai lượt.
- Render toàn bộ 33 trang và kiểm tra các slide ảnh; không phát hiện slide bị cắt nội dung hoặc lỗi bố cục nghiêm trọng.

## Gói nộp Group 7

- Tạo gói `7.zip` gồm source link GitHub, technical report PDF, slide PDF và dataset release `thu_duc_landmarks_v1.0.4`.
- File video link được tạo riêng và ghi rõ cần bổ sung URL thật trước khi nộp vì repository chưa có link demo video.
- Bổ sung mục failure cases cụ thể trong technical report và một slide cảnh báo về snap sai node, hướng cạnh, closure hình học, scenario stale, cost, graph thưa và dữ liệu lỗi.
- Làm lại slide phạm vi release bằng hai thẻ số liệu 65/283 và ảnh bản đồ lớn hơn; làm lại sơ đồ kiến trúc với khoảng cách/mũi tên rõ ràng để không đè lên nhãn.
- Biên dịch và render lại deck sau khi đổi sang một họ font duy nhất; PDF đầu ra có 33 trang.
- Lược bỏ các ảnh minh họa quá nhỏ ở các slide A*, tuyến thay thế và bài toán nhiều điểm; giữ ảnh ở gallery và slide phạm vi release nơi có đủ diện tích hiển thị.
- Căn giữa bảng chú thích màu/trạng thái/ý nghĩa trên slide trực quan hóa bản đồ và tăng khoảng cách dòng cho dễ đọc.
