# Processed datasets

`thu_duc_market_v1.0.0/` là release hiện hành: 90 node, 155 directed edge, ba
scenario, POI thật, traffic profile lịch sử và flood records có provenance. Release
được app nạp mặc định nhưng giữ `REVIEW_REQUIRED`, không phải chỉ dẫn an toàn.

Đích của dataset v1.0 dùng trong API. Mỗi release đặt trong thư mục version riêng,
ví dụ `v1.0.0/`, gồm `nodes.csv`, `edges.csv`, `scenarios.json`, metadata, checksum
và báo cáo validation. Release chợ Thủ Đức hiện có thể chạy trong app nhưng chưa được
nâng `ACADEMIC_DEMO_READY` do còn chờ hai human review.
