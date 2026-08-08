# Changelog

Mọi thay đổi đáng chú ý được ghi tại đây. Nhật ký chi tiết theo công việc nằm trong
`docs/progress/`.

## [Unreleased]

### Added

- UI map scope cố định về `thu_duc_landmarks_v1.0.0` với đúng 65 selectable landmark;
  processed pilot 90 node và capacity graph không còn xuất hiện trong dropdown map.

- Dataset mặc định `thu_duc_landmarks_v1.0.0`: 65 landmark OSM chọn được, 178 cạnh
  shortest-road-path tổng hợp từ mạng UTraffic nguồn 8.952 node/14.043 cạnh.
- Marker dạng nút nhỏ trắng viền xanh cho node `selectable`, polyline geometry cho cạnh
  aggregate, raw Overpass snapshot, builder, validator, API/frontend regression tests.
- ADR 0011 cho định nghĩa địa điểm lớn, graph compression, snapping và connector rule.
- Ẩn `CAPACITY_BENCHMARK_ONLY` 3.229 node khỏi dropdown định tuyến để không nhầm node
  kỹ thuật với landmark chọn được; API và benchmark script vẫn giữ nguyên.

- OpenFreeMap `Liberty` vector basemap, GeoJSON graph layers, popup tên node derived,
  toolbar click-node chọn START/GOAL và fallback nền trung tính khi basemap lỗi.
- ADR 0008 cho quyết định chuyển React Leaflet sang MapLibre GL JS/OpenFreeMap.
- Tài liệu hóa plan triển khai đầy đủ tại `docs/plans/2026-08-09-maplibre-openfreemap.md`.
- Cấu hình MapLibre worker qua Vite worker pipeline và loại `maplibre-gl` khỏi
  dependency optimizer để sửa lỗi thiếu `maplibre-gl-worker.mjs` trong `.vite/deps`.
- Script dev root chuyển tiếp tham số Vite như `--force` để làm mới dependency cache.
- Tách nút reset viewport khỏi nhóm zoom/compass MapLibre để không chồng nút ở góc phải.
- Thêm frozen GeoJSON OSM relation 19407794, API boundary và lớp đỏ “Ranh TP Thủ Đức
  cũ”; rectangle camera B có lề bao trọn polygon A và giới hạn pan trong vùng nghiên cứu.
- Giữ camera ở min zoom 10.5, focus endpoint ở zoom 16.5 và fallback graph context khi
  boundary chưa tải; không thể kéo viewport ra toàn TP.HCM hoặc bản đồ thế giới.
- ADR 0010 ghi quyết định boundary historic, provenance và quy tắc camera A/B.
- Camera `flyTo` endpoint vừa thay đổi khi chọn START/GOAL; không còn tự fit về trung
  điểm của hai endpoint sau mỗi lần chọn.
- Mở picker processed pilot ra đủ 90 topology node và hỗ trợ click basemap snap tới node
  gần nhất trong 200 m khi chọn START/GOAL.
- Graph benchmark UTraffic lõi Thủ Đức 3.229 node/5.057 cạnh, builder/validator, ADR 0009
  và lệnh `npm run benchmark:capacity`.

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

- Frontend map renderer chuyển từ React Leaflet/nền CSS sang MapLibre WebGL; backend,
  graph schema, cost model và processed dataset giữ nguyên.

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
- Cô lập stacking context của map renderer để zoom/reset controls không tràn lên
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
