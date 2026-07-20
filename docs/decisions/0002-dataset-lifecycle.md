# ADR-0002: Phân lớp dataset và dùng fixture làm test oracle

- Trạng thái: Accepted
- Ngày: 2026-07-20

## Bối cảnh

Workbook v0.1 có nguồn và assumptions tốt nhưng Road Nodes/Edges vẫn là placeholder.
Nhóm cần bắt đầu code thuật toán mà không biến dữ liệu chưa xác minh thành “sự thật”.

## Quyết định

Tách `raw`, `interim`, `processed`, `fixtures`, `schemas`, `registry`. Raw bất biến
và có checksum. Toy fixture có golden cases, luôn gắn `SIMULATED`; UCS/Held-Karp
sẽ là oracle tương ứng cho two-point và multi-stop test nhỏ.

## Hệ quả

- Có thể phát triển/test song song với OSM extraction.
- Claim thực nghiệm phải ghi rõ dùng fixture hay processed version nào.
- Cần duy trì pipeline, manifest và checksum khi dataset thay đổi.

