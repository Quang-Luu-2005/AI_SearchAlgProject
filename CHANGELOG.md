# Changelog

Mọi thay đổi đáng chú ý được ghi tại đây. Nhật ký chi tiết theo công việc nằm trong
`docs/progress/`.

## [Unreleased]

### Added

- BE-02 ScenarioCostEngine với các preset `BALANCED`, `PEAK_TRAFFIC`, `RAIN_SAFE`,
  breakdown edge/route, edge override, flood risk, congestion penalty và closed edge.
- Runbook chạy toàn bộ dự án từ cài môi trường, validate dataset, khởi động
  backend/frontend, nạp graph folder đến test và troubleshooting.
- Graph dataset explorer: tự khám phá folder fixture hợp lệ, API list/load graph
  an toàn theo scenario và giao diện chọn dataset để vẽ Node/Edge động.
- Package `graph_examples_v0.1` gồm directed path, one-way branch và cycle có
  scenario đóng cạnh; kèm metadata, golden case, validation và unit test loader.
- Graph Loader bất biến cho graph có hướng, hỗ trợ fixture CSV/JSON, scenario
  đóng cạnh, neighbor deterministic và cycle detection; thêm unit test BE-01 và
  quy ước CSV làm nguồn chuẩn cho Node/Edge, JSON cho dữ liệu lồng nhau.
- Bản DOCX tổng quan FloodRoute HCMC dành cho onboarding/review, tập trung vào ý
  tưởng sản phẩm, trải nghiệm mục tiêu, cost model ở mức khái niệm, kiến trúc hệ
  thống, data governance, vai trò thuật toán và trạng thái MVP.
- Tài liệu tóm tắt đồ án, trạng thái repository và kế hoạch Trello 7 ngày
  backend-first cho nhóm bốn người.

### Changed

- Dọn cây thư mục local: loại bỏ lockfile rỗng nằm sai cấp và chuẩn hóa ignore cho
  các dependency/cache sinh tự động (`node_modules/`).
- Chuẩn hóa dev startup bằng `npm run dev`: dùng Python từ `.venv`, chạy Vite
  đúng frontend root, khởi động/dừng đồng thời backend và frontend; vẫn hỗ trợ
  hai lệnh chạy riêng.

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
