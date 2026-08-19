# Dataset workspace

Release ứng dụng hiện tại là `processed/thu_duc_landmarks_v1.0.2` (65 node, 283 directed
edge). Đây là academic landmark graph; traffic lịch sử không real-time và flood mapping
còn chờ hai reviewer.

Dataset được chia theo vòng đời để tránh trộn nguồn gốc với dữ liệu đã xử lý:

- `raw/`: nguồn gốc bất biến; không sửa trực tiếp.
- `interim/`: kết quả trích xuất/map-match đang làm, có thể tạo lại.
- `processed/`: snapshot graph đã kiểm định và được ứng dụng sử dụng.
- `submission/`: bundle dataset version hóa, tự chứa manifest/checksum để nộp bài.
- `fixtures/`: graph nhỏ, cố định, chỉ dùng cho unit/golden/regression test.
- `schemas/`: hợp đồng dữ liệu máy đọc được.
- `registry/`: version, checksum, provenance và trạng thái xác minh.

Quy trình chi tiết nằm tại `docs/data-management.md`. Chạy kiểm tra hiện có bằng:

```powershell
python scripts/data/validate_dataset.py
```
