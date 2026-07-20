# Changelog

Mọi thay đổi đáng chú ý được ghi tại đây. Nhật ký chi tiết theo công việc nằm trong
`docs/progress/`.

## [Unreleased]

### Planned

- Trích xuất và kiểm định OSM road graph v1.0.
- Triển khai search engine và API `/search`.

## [0.1.0] - 2026-07-20

### Added

- Khung React/TypeScript/Vite với bản đồ fixture offline và dashboard responsive.
- Khung FastAPI, health endpoint, dataset metadata endpoint và data contracts.
- Phân lớp raw/interim/processed/fixtures/schemas/registry cho dataset.
- Toy graph 6 nút, 14 cạnh, hai scenario và bốn test case nền.
- Validator checksum, foreign key, edge weight, scenario và golden path.
- Bộ tài liệu kiến trúc, data governance, ADR và quy trình ghi tiến độ.

### Changed

- Chuyển tài liệu nguồn vào `docs/references/` và workbook vào `data/raw/`.

