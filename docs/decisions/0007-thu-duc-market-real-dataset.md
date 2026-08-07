# ADR 0007: Dataset pilot chợ Thủ Đức và catalog processed

- Trạng thái: Accepted, release `REVIEW_REQUIRED`
- Ngày: 2026-08-07

## Bối cảnh

Ứng dụng cần một graph thực tế 80–150 node, có traffic lịch sử, điểm ngập có nguồn và
POI giao hàng thật. Fixture hiện có chỉ phù hợp kiểm thử. API trước đây chỉ đọc
`data/fixtures` và mặc định mọi dữ liệu traffic/flood là `SIMULATED`.

## Quyết định

Chọn pilot giao hàng xe máy quanh chợ Thủ Đức trong bbox
`10.845–10.853, 106.751–106.759`. Graph có hướng được clip từ UTraffic/HCMUT và đóng
băng ở 90 node, 155 edge, liên thông mạnh. POI dùng snapshot OpenStreetMap; flood
hotspot dùng danh sách TP Thủ Đức năm 2025 và thông tin dự án thoát nước năm 2026.

Tốc độ free-flow là P85 tốc độ dương theo đường, fallback P85 theo `street_type`.
LOS được tổng hợp theo street/time band với ánh xạ `A=1, B=2, C=3, D=4, E/F=5`.
Các edge thuộc ghi nhận ngập dùng penalty nhị phân `flood_risk_0_1=1`; edge không có
ghi nhận dùng `0` kèm `NO_RECORD_IN_SELECTED_SOURCES`, không mang nghĩa an toàn.
Không tự đóng đường. Đơn hàng và cost weights là `ASSUMPTION`.

Catalog được phép đọc hai root cố định: `data/fixtures` và `data/processed`. Processed
graph dùng ID có prefix `processed/`; mọi path được resolve và kiểm tra vẫn nằm trong
root tương ứng. API truyền `SOURCE_BACKED`, `DERIVED`, `ASSUMPTION`, `MIXED` thay vì
hard-code `SIMULATED`.

Release chỉ được nâng lên `ACADEMIC_DEMO_READY` khi mọi map-match có hai reviewer thật.
Hiện cả hai chữ ký human review còn trống nên trạng thái là `REVIEW_REQUIRED`; kiểm tra
tự động của Codex không được tính là reviewer.

## Hệ quả

- Demo mặc định dùng dữ liệu khu vực thật nhưng phải hiển thị historical/not real-time.
- Pipeline có thể tái lập từ raw ZIP và lưu checksum/provenance.
- `0` flood risk không được diễn giải là đường an toàn.
- Thay nguồn, bbox, quy tắc P85/LOS/flood hoặc catalog root cần ADR mới.
