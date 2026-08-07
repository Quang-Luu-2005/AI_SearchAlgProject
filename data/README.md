# Dataset workspace

Release ứng dụng hiện tại là `processed/thu_duc_market_v1.0.0` (90 node, 155 directed
edge). Trạng thái `REVIEW_REQUIRED`; traffic lịch sử không real-time và flood mapping
còn chờ hai reviewer.

Dataset được chia theo vòng đời để tránh trộn nguồn gốc với dữ liệu đã xử lý:

- `raw/`: nguồn gốc bất biến; không sửa trực tiếp.
- `interim/`: kết quả trích xuất/map-match đang làm, có thể tạo lại.
- `processed/`: snapshot graph đã kiểm định và được ứng dụng sử dụng.
- `fixtures/`: graph nhỏ, cố định, chỉ dùng cho unit/golden/regression test.
- `schemas/`: hợp đồng dữ liệu máy đọc được.
- `registry/`: version, checksum, provenance và trạng thái xác minh.

Quy trình chi tiết nằm tại `docs/data-management.md`. Chạy kiểm tra hiện có bằng:

```powershell
python scripts/data/validate_dataset.py
```
