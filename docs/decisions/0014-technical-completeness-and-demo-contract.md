# ADR-0014 — Hoàn thiện contract demo kỹ thuật

## Status

Accepted.

## Context

Rubric yêu cầu GUI thể hiện frontier/current/closed, đầy đủ metrics, so sánh nhiều
thuật toán, giải thích penalty và đối chiếu thứ tự tour ban đầu. Pilot 90 node có ba
scenario và golden route-change đã tồn tại nhưng bị ẩn khỏi dropdown. Response tour cũ
không mang baseline nên frontend không thể trình bày mức cải thiện có thể kiểm chứng.

## Decision

- Giữ landmark 65 node làm dataset mặc định, đồng thời cho phép chọn pilot
  `thu_duc_market_v1.0.0` trong GUI với nguyên trạng nhãn `REVIEW_REQUIRED`/`MIXED` và
  cảnh báo traffic lịch sử, không real-time. Capacity graph vẫn chỉ dành cho benchmark.
- Mở Greedy và Bidirectional trong GUI và compare cả sáu thuật toán two-point.
- Suy diễn trạng thái hiển thị frontier/current/closed chỉ từ trace API; frontend không
  chạy lại thuật toán.
- Mở rộng `TourComparisonResponse` theo kiểu additive bằng baseline thứ tự nhập, distance,
  ETA, cost và mức tiết kiệm của tour được chọn. Cost và subpath vẫn lấy từ cùng pairwise
  matrix/scenario, không tạo cost model mới.
- Lưu case benchmark cố định 10 OD × 3 scenario × 6 thuật toán × 20 lần đo; kết quả mang
  nhãn `DERIVED_BENCHMARK` và timing chỉ có ý nghĩa trên môi trường ghi trong artifact.

## Consequences

- Client cũ vẫn dùng được vì các field cũ không đổi; client schema nghiêm ngặt cần nhận
  thêm field comparison mới.
- Demo có thể trực tiếp tái hiện golden route-change nhưng không được diễn giải pilot như
  dữ liệu vận hành đã review hoặc thông tin thời gian thực.
- Kết quả benchmark tái lập về case/path/cost; runtime có dao động theo máy.

## Alternatives rejected

- Tính baseline tour ở frontend sẽ nhân đôi cost logic và có thể sai với graph có hướng.
- Giữ pilot khỏi GUI khiến scenario route-change chỉ có thể chứng minh bằng script.
- Đổi cost model/chuẩn hóa trọng số ở mốc này sẽ làm thay đổi kết quả đã đóng băng và cần
  một đợt kiểm định riêng.
