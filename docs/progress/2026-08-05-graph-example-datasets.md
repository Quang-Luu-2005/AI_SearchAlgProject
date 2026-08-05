# 2026-08-05 — Tạo package dataset graph ví dụ

## Mục tiêu

Tạo sẵn một folder dataset gồm vài graph nhỏ, dễ đọc và load trực tiếp để học,
demo, viết thuật toán và kiểm tra Graph Loader.

## Thay đổi đã thực hiện

- Thêm `data/fixtures/graph_examples_v0.1/` với ba graph: `simple_path`,
  `one_way_branch` và `cycle_with_closure`.
- Mỗi graph có Node/Edge CSV, Scenario/metadata/test case JSON và nhãn
  `SIMULATED` đầy đủ.
- Đăng ký package trong dataset manifest v0.2.0.
- Mở rộng validator để kiểm tra mọi example graph: file bắt buộc, ID/FK, trọng
  số dương, nhãn, scenario closure, golden path và metadata count.
- Bổ sung unit test load cả ba graph và kiểm tra one-way, neighbor order, cycle
  cùng scenario phá cycle.
- Cập nhật tài liệu fixture, data management và graph format.

## Quyết định/giả định

- Mỗi example là một folder độc lập để dùng trực tiếp với
  `GraphLoader.from_directory()`.
- CSV là nguồn chuẩn cho Node/Edge; JSON dùng cho cấu trúc lồng nhau.
- Giá trị tọa độ, khoảng cách và thời gian chỉ phục vụ fixture, đều `SIMULATED`.
- Không sửa `data/raw/`, không thay schema/cost/API nên không cần ADR mới.

## Bằng chứng kiểm tra

```powershell
python scripts/data/validate_dataset.py
python -m pytest backend/tests
```

- Dataset validator: PASS cho toy graph và ba graph examples.
- Backend: 11 test PASS; còn 1 `StarletteDeprecationWarning` đã biết từ TestClient.

## Tồn tại/rủi ro

- Đây không phải graph đường TP.HCM và không dùng để đưa ra kết luận thực tế.
- Golden paths chỉ kiểm tra tính hợp lệ cấu trúc; oracle search sẽ được bổ sung
  khi các thuật toán tương ứng được triển khai.

## Bước tiếp theo

Dùng từng graph làm focused fixture cho BFS/DFS/UCS và scenario-aware search.
