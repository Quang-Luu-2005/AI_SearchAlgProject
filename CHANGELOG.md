# Changelog

Mọi thay đổi đáng chú ý được ghi tại đây. Nhật ký chi tiết theo công việc nằm trong
`docs/progress/`.

## [Unreleased]

### Added

- Triển khai toàn bộ quy trình 14 bước OSM Dataset Pipeline: snapshot raw `thu_duc_osm_v1.0.0` từ Overpass API, script tái tạo `scripts/data/build_osm_dataset.py`, release `data/processed/osm_thu_duc_v1.0.0/` (27 nodes, 40 directed edges), SHA-256 checksums, provenance registry và cập nhật validator.
- BE-04 Triển khai Uniform Cost Search (UCS) và A* với Geographic Weighted Haversine Distance Heuristic ($h(n) = w_{\text{dist}} \cdot D_{\text{Haversine}}(n, \text{goal})$), được chứng minh toán học đạt tính Admissible và Consistent (Monotonic), kèm ADR-0008 và unit test toàn bộ thuật toán weighted search.
- Dataset thực tế `thu_duc_market_v1.0.0` cho pilot giao hàng quanh chợ Thủ Đức: 90
  node, 155 directed edge, traffic lịch sử UTraffic, POI OSM, flood hotspot 2025–2026,
  ba scenario và golden case đổi tuyến.
- Pipeline tái lập, raw/processed checksum, provenance registry và QC cho bbox,
  connectivity, snapping, traffic/flood mapping cùng review state.
- ADR 0007 cho nguồn dữ liệu, quy tắc P85/LOS/flood penalty, processed catalog và
  điều kiện nâng `ACADEMIC_DEMO_READY`.

- Giao diện Pathfinder AI responsive theo thiết kế Stitch, tích hợp trực tiếp
  locations, scenarios, graph, search và compare API; hiển thị đường tối ưu,
  node đã duyệt, metrics, guarantee và explanation từ backend.
- BE-03 Backend API: locations, scenarios, search và compare với Pydantic/OpenAPI
  schema, validation/error mapping, metrics, trace, guarantee và explanation.
- Registry/search service deterministic cho `UCS` và `A_STAR`; A* dùng heuristic
  `h=0` có bảo đảm tối ưu với cost không âm.
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

- Route picker trên UI chuyển từ danh sách select dài sang tìm kiếm theo tên hoặc
  `node_id`, giới hạn 40 kết quả hiển thị; endpoint được highlight và bản đồ tự zoom
  vào start/goal khi chọn.

- Graph catalog/API/UI hỗ trợ cả `data/fixtures` và `data/processed`; UI chọn pilot
  Thủ Đức mặc định, truyền trạng thái `MIXED` và hiển thị historical/not real-time,
  limitations cùng attribution OSM.
- Cost/search loại bỏ giả định hard-code mọi traffic/flood là `SIMULATED` và propagate
  đúng `SOURCE_BACKED`, `DERIVED`, `ASSUMPTION`, `MIXED`.

- Thay dashboard graph explorer cũ bằng control panel/canvas mới; loại bỏ dữ liệu
  path hardcode từ bản HTML thiết kế và dùng hoàn toàn response `SIMULATED` của backend.
- Map có nút đưa viewport về graph, marker start/goal màu riêng và animation vẽ
  từng đoạn của tuyến tối ưu với màu tím/viền sáng nổi bật.
- Nút reset viewport dùng icon PNG trong suốt được tạo bằng image model, không
  hiển thị chữ nhưng vẫn có tooltip và nhãn accessibility.
- Cô lập stacking context của Leaflet để zoom/reset controls không tràn lên
  sticky header khi cuộn trang.
- Các script test data/backend ở repository root dùng Python trong `.venv`, đồng
  nhất với `npm run dev` và không phụ thuộc Python hệ thống.
- Dev server: backend now watches the `backend/` tree with Uvicorn reload and
  Vite uses polling-based HMR for reliable updates on Windows.

- Dọn cây thư mục local: loại bỏ lockfile rỗng nằm sai cấp và chuẩn hóa ignore cho
  các dependency/cache sinh tự động (`node_modules/`).
- Chuẩn hóa dev startup bằng `npm run dev`: dùng Python từ `.venv`, chạy Vite
  đúng frontend root, khởi động/dừng đồng thời backend và frontend; vẫn hỗ trợ
  hai lệnh chạy riêng.

### Planned

- Trích xuất và kiểm định OSM road graph v1.0.
- Triển khai BFS/DFS/Greedy/Bidirectional và heuristic địa lý đã kiểm chứng cho A*.

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
