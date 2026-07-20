# Quy trình cập nhật tài liệu

Docs là một phần của Definition of Done, không phải việc gom lại ở cuối dự án.

## Sau mỗi bước triển khai

1. Tạo hoặc cập nhật entry `docs/progress/YYYY-MM-DD-<slug>.md`.
2. Ghi `CHANGELOG.md` ở mục `Unreleased` nếu người dùng/nhóm thấy được thay đổi.
3. Cập nhật tài liệu bị ảnh hưởng: architecture, data, API, setup hoặc limitations.
4. Tạo ADR nếu thay quyết định khó đảo ngược hoặc ảnh hưởng nhiều module.
5. Gắn bằng chứng kiểm tra: lệnh đã chạy, kết quả, dataset version/seed.
6. Chỉ chuyển trạng thái sang hoàn tất khi test/acceptance tương ứng đã PASS.

## Khi nào cần ADR

Cần ADR khi đổi framework, schema, cost function, heuristic claim, API contract,
data source, cách map-match hoặc guarantee của thuật toán. Sửa code nội bộ nhỏ
không đổi hợp đồng chỉ cần progress entry và changelog nếu phù hợp.

## Template progress entry

```markdown
# YYYY-MM-DD — Tên bước

## Mục tiêu
## Thay đổi đã thực hiện
## Quyết định/giả định
## Bằng chứng kiểm tra
## Tồn tại/rủi ro
## Bước tiếp theo
```

Mỗi entry phải đủ để một thành viên khác trình bày lại công việc trong vấn đáp.

