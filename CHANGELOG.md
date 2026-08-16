# Changelog

Mọi thay đổi đáng chú ý được ghi tại đây. Nhật ký chi tiết theo công việc nằm trong
`docs/progress/`.

## [Unreleased]

### Added

- Tích hợp BFS và DFS vào luồng two-point search từ API đến GUI: có lựa chọn thuật toán,
  chế độ compare UCS/A*/BFS/DFS, trace và test reachable/unreachable/cycle/start=goal.
- Tự động điều chỉnh thu phóng bản đồ khi thu gọn Panel ở chế độ Desktop để thước đo tỷ lệ scale hiển thị chính xác mốc **`5 km`**.
- Xóa / Ẩn dòng chữ thông tin bản quyền và nguồn dữ liệu bản đồ (`Map Attribution` / `.dataset-attribution`) khỏi giao diện bản đồ.
- Triển khai Giao diện Responsive Đa Thiết Bị (Mobile < 640px, Tablet < 1024px, Desktop > 1024px) toàn bộ ứng dụng FloodRoute HCMC.
- Triển khai Bảng điều khiển dạng Side Drawer trượt Off-Canvas trên màn hình di động/máy tính bảng kèm Nút Hamburger menu `☰` và Lớp phủ mờ (`.mobile-drawer-backdrop`).
- Tích hợp `ResizeObserver` căn chỉnh tự động canvas MapLibre GL JS khi chuyển đổi viewport hoặc ẩn/hiện drawer.
- Tối ưu hóa giao diện responsive cho Trace Player, Bảng chặng tour đa điểm (`.legs-table`), Lưới so sánh thuật toán (`.tour-guarantee-comparison`) và Modal Phím tắt.
- Triển khai Hệ thống Đa ngôn ngữ (i18n) hai chế độ Tiếng Anh (Mặc định - `en`) và Tiếng Việt (`vi`) toàn bộ giao diện FloodRoute HCMC.
- Bổ sung Nút chuyển đổi ngôn ngữ `🌐 EN / VI` trên Topbar với cơ chế lưu trạng thái tự động vào `localStorage`.
- Bổ sung module từ điển tập trung [`frontend/src/lib/i18n.ts`](frontend/src/lib/i18n.ts)
  và bộ kiểm thử Vitest `i18n.test.ts` cùng `LanguageToggle.test.tsx`.

- Triển khai Service/API tối ưu hóa lộ trình giao hàng qua 5–10 điểm (`POST /api/v1/optimize-tour`): tính toán `PairwiseMatrix` cho $N$ điểm, giải thuật chính xác **Held-Karp DP** ($O(N^2 \cdot 2^N)$), giải thuật xấp xỉ **Nearest Neighbor**, đo % Approximation Gap, ghép nối subpath liên tục không lặp nút và bộ unit test suite `TC04_MULTI_STOP`.
- Refactor toàn bộ [`backend/app/algorithms/weighted.py`](backend/app/algorithms/weighted.py)
  thành kiến trúc modular: tách `haversine_distance_km`, `compute_geographic_heuristic`
  ($h(n) = w_{\text{dist}} \cdot D_{\text{Haversine}}$), hàm lõi `_weighted_search` và
  entry points `uniform_cost_search`, `a_star_search`; kèm ADR-0012 và unit test mới.
- Triển khai quy trình dữ liệu OSM 3 lớp (raw $\rightarrow$ interim $\rightarrow$ processed)
  chuẩn hóa: raw snapshot `thu_duc_osm_v1.0.0`, interim topology
  `data/interim/osm_thu_duc_v1.0.0/` (27 nodes, 40 edges), script tái tạo
  [`scripts/data/build_osm_dataset.py`](scripts/data/build_osm_dataset.py), SHA-256
  checksums, metadata và cập nhật validator.
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
- Giữ camera ở min zoom 10.5, dùng fallback graph context khi boundary chưa tải và không
  thể kéo viewport ra toàn TP.HCM hoặc bản đồ thế giới.
- ADR 0010 ghi quyết định boundary historic, provenance và quy tắc camera A/B.
- Chọn START/GOAL giữ nguyên viewport, không gọi `flyTo`/`fitBounds`; hai endpoint dùng
  ghim lớn màu cam/hồng, neo đúng tọa độ để luôn nổi bật trên graph.
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

- Tích hợp PR #2 vào `main`, hoàn thiện trạng thái tài liệu cho Held-Karp/Nearest
  Neighbor, endpoint optimize-tour và heuristic Haversine của A*.
- Chuẩn hóa hợp đồng optimize-tour: 5–10 stop duy nhất, depot không lặp trong stops và
  chỉ chấp nhận `HELD_KARP`/`NEAREST_NEIGHBOR`; bổ sung ADR-0013 cùng test regression.

- Frontend map renderer chuyển từ React Leaflet/nền CSS sang MapLibre WebGL; backend,
  graph schema, cost model và processed dataset giữ nguyên.

- Route picker trên UI chuyển từ danh sách select dài sang tìm kiếm theo tên hoặc
  `node_id`, giới hạn 40 kết quả hiển thị; endpoint được highlight mà không tự zoom
  hoặc đổi tâm bản đồ khi chọn.

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

### Fixed

- Bảo toàn byte của `data/raw/**` bằng `.gitattributes` để checkout trên Windows không
  đổi LF thành CRLF và làm sai checksum SHA-256 của manifest.
- Sửa map picker cho tour đa điểm: START chọn depot, GOAL thêm liên tiếp tối đa 10 stop,
  chặn điểm trùng và hiển thị marker đánh số ngay trước khi chạy thuật toán.

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
