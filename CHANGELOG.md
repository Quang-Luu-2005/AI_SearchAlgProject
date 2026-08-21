# Changelog

Mọi thay đổi đáng chú ý được ghi tại đây. Nhật ký chi tiết theo công việc nằm trong
`docs/progress/`.

## [Unreleased]

- Cleaned tracked LaTeX build logs, intermediate files, temporary report renders,
  a duplicate report PDF, and an orphan root file; documented the report
  artefact policy in `docs/reports/README.md`.
- Added an editable XeLaTeX Beamer presentation source `docs/reports/presentation_slides.tex` and compiled PDF with 30 frames covering the current dataset, scenarios, cost model, algorithms, frontend flow, experiments, limitations, and conclusion.
- Added four project UI illustrations and the KHTN logo to the LaTeX deck, including two dedicated gallery frames for map, route, comparison, and delivery-tour views; rebuilt the PDF with 32 frames.
- Updated the LaTeX team slide to show the requested score allocation table: 35%, 25%, 20%, 20%, total 100%.
- Restyled the LaTeX presentation to follow the supplied Madrid template: white canvas, navy title bars, light-blue blocks, Latin Modern typography, and a matching cover layout.
- Packaged Group 7 submission archive `7.zip` with GitHub source link, technical report, PDF slides, and the v1.0.4 dataset release; added a video-link placeholder pending the real demo URL.
- Added concrete failure-case analysis to the technical report and presentation, including incorrect snapping, one-way edge assumptions, geometry-overlapping closures, stale random scenarios, cost-objective mismatch, sparse topology, heuristic/profile mismatch, and invalid data.
- Unified the LaTeX slide deck on the TeX Gyre Heros font and redesigned the release metrics/architecture slides with clearer cards, spacing, and arrows.
- Removed undersized duplicate screenshots from explanatory slides and centered the map color/status legend table for readability.
- Added the Slides branch presentation bundle: 28-slide PPTX, HTML preview, Markdown source, slide report README, and progress note. Conflicting report metadata was kept from the current main branch.
- Moved the title-page date inside the cover frame by lowering the frame bottom and preserving a balanced bottom margin.
- Updated the report cover and HTML/Markdown metadata to list the three instructors: Bùi Duy Đăng, Bùi Tiến Lên, and Võ Nhật Tân.
- Reworked the title-page institution heading into one compact block (`TRƯỜNG...`, `ĐHQG-HCM`, `KHOA...`) and moved the frame above the full block.
- Adjusted the title-page border top offset so the university heading no longer overlaps the frame.
- Updated the LaTeX report to describe the active v1.0.4 dataset (65 nodes/283 edges), the four current cost scenarios, the 20% fixed obstruction coverage, random mixed obstructions, same-algorithm detours, and the shortest-route priority. Documented free-flow-time derivation and clarified that A* optimizes the complete scenario cost rather than distance alone.
- Added processed/submission release `thu_duc_landmarks_v1.0.1` with unchanged 65-node/178-edge topology and an `ASSUMPTION` hard-closure detour scenario for `LM_EDGE_0001`.
- Normalized graph closure semantics so both `closed_edge_ids` and `edge_overrides.is_closed` are excluded before every search algorithm; impossible scenarios return `NO_ROUTE`.
- Added `thu_duc_landmarks_v1.0.2`: 65 nodes and 283 directed edges, with up to four nearest outgoing road-path alternatives per landmark for more detour choices.
- Added `thu_duc_landmarks_v1.0.3` cost scenarios: normal, flood, congestion, and hard closure; added frontend random affected-edge generation and map highlighting.
- Added bilingual Vietnamese/English labels for cost scenarios, random edge statuses, and an always-visible map legend for normal, congested, flooded, closed, and selected-route edges.
- Simplified the frontend scenario selector to exactly congestion, flood, and random; hid technical normal/hard-closure entries and removed the duplicate below-map legend.
- For flood, congestion, and random scenarios, the frontend now compares six algorithms, displays up to three distinct routes, and marks the lowest weighted-cost route as optimal with a cost proof.
- Fixed map scenario coloring by returning the active edge status (`CONGESTED`, `FLOODED`, or `CLOSED`) in the graph payload for fixed and random scenarios.
- Replaced cross-algorithm alternative-route comparison with `/api/v1/alternatives`, which uses the selected algorithm and returns up to two distinct detours under the same scenario.
- Added dataset release `thu_duc_landmarks_v1.0.4`; FLOOD and CONGESTION now affect 57/283 edges each (20.14%), while topology remains unchanged.
- Added a `RANDOM` regenerate action so every click creates a new random seed and replaces the affected edge set.
- RANDOM now deliberately includes both obstruction types in one draw: 1 closure, 3 flooded edges, and 3 congested edges.
- Restored the frontend `NORMAL` demo scenario and made it the default baseline alongside congestion, flood, and random conditions.
- Rewrote the v1.0.4 dataset descriptions in Vietnamese, synchronized normalized/processed README files and checksums, and repackaged the Group 7 submission archives.
- Expanded `.gitignore` to exclude large ZIP/raw snapshots, compiled PDF/PPTX artifacts, LaTeX auxiliary files, and local temporary/package directories while keeping source and metadata files trackable.
- Removed the historical-traffic notice card from the frontend panel while retaining provenance and limitations in the submission manifest.
- Added the self-contained `data/submission/floodroute_dataset_v1.0.0` bundle with CSV/JSON data, validation report, checksums, provenance labels, and submission manifest.
- Split the submission bundle into `raw_collected/` source snapshots and `normalized/` routing data, with separate checksums and provenance manifests.

- Streamlined the report around the Lab 1 rubric: removed the internal requirement-mapping table, shortened dataset/provenance and A* exposition, moved fixture context to experiments, removed the duplicate UCS screenshot, and simplified usage instructions.
- Added compact algorithm and A*/UCS result tables so the space is used for direct experimental evidence instead of engineering documentation.
- Added a deterministic route-explanation benchmark with selected/alternative route costs, edge breakdowns, closure handling, and UCS/A* validation for the report.
- Added a student-style Chapter 8 comparison for peak traffic and heavy rain, plus a compact algorithm guarantee table and toy graph figure.
- Fixed the Chapter 5 algorithm-comparison table by using wrapped fixed-width columns, preventing text from collapsing into a narrow vertical strip.
- Revised report wording to use a natural student-report voice while retaining technical terms, formulas, benchmark values, and conclusions.
- Added a captured local GUI map image and an in-report system-flow diagram to the FloodRoute LaTeX report.
- Added captured GUI states for A*, UCS, six-algorithm comparison, and a five-stop Held-Karp/Nearest Neighbor tour.

- Nâng cấp toàn diện giao diện hiển thị kết quả thuật toán giao hàng đa điểm (Tour
  Held-Karp DP, Nearest Neighbor và So sánh Tour): hiển thị lộ trình dạng huy hiệu tên
  địa danh thực tế thay vì node ID thô, đối chiếu 2 cột Trước vs Sau tối ưu kèm mức tiết
  kiệm (km, phút, % chi phí), làm rõ cam kết học thuật và độ phức tạp ($O(N^2 \cdot 2^N)$
  vs $O(N^2)$), tinh gọn bảng từng chặng và ẩn các thẻ 2 điểm trùng lặp.

- Tách biệt mục So sánh thuật toán (Algorithm Comparison) thành phân nhóm riêng trong
  bộ chọn thuật toán ở Bảng điều khiển (Control Panel) bằng `<optgroup>` đa ngôn ngữ
  (EN/VI), phân định rành mạch giữa tìm kiếm 2 điểm đơn lẻ, tour giao hàng đa điểm (TSP),
  và các chế độ so sánh đối chuẩn (`COMPARE`, `OPTIMIZE_TOUR`) mà không làm thay đổi các
  luồng xử lý khác.

- Xóa processed map 90 node `thu_duc_market_v1.0.0` khỏi workspace, manifest,
  catalog và benchmark active; giữ `thu_duc_landmarks_v1.0.0` làm map duy nhất
  cho lựa chọn endpoint/search. `data/raw/` không bị chỉnh sửa.

- Chốt ba cost profile `BALANCED`, `PEAK_TRAFFIC`, `RAIN_SAFE` với vector trọng số
  hiện có; ghi rõ đây là hệ số ưu tiên empirical/simulated, giữ road closure là hard
  constraint và bổ sung artifact `cost_profiles_v1` với hai ví dụ đổi tuyến.
- Thêm acceptance tests cho exact weights, profile sums, hard closure và route-change
  golden cases; custom weights không mở trong public API deadline.

- Thay heuristic A* bằng scenario-aware lower bound `h_s(n) = rho_s × Haversine(n, goal)`;
  loại closed/near-zero edges khỏi rho, thêm unit test và benchmark 15 case baseline/peak/rain
  với 0 cost mismatch so với UCS (`experiments/results/astar_ucs_lower_bound_v1.md`).
- Thêm ADR-0015 và lệnh `npm run benchmark:lower-bound` cho bằng chứng tái lập.

- Hoàn thành toàn diện Báo cáo Kỹ thuật Mục 4.9 (`docs/reports/FloodRoute_HCMC_Technical_Report.md`)
  gồm 10 chương mục chuẩn (a–j), đồng bộ phân công trách nhiệm thành viên từ Trello Board `AI_Project_1`,
  tích hợp bảng so sánh lý thuyết, số liệu thực nghiệm từ 3.600 lượt chạy benchmark và kết quả tối ưu hóa TSP.
- Hoàn thiện demo technical: GUI đủ sáu thuật toán two-point, trace frontier/current/closed,
  metrics đầy đủ, so sánh shortest/fastest/best weighted cost và giải thích edge penalty.
- Bổ sung baseline thứ tự nhập cho multi-stop cùng cost/distance/ETA và mức tiết kiệm;
  mở pilot 90 node/ba scenario trong dropdown với nguyên trạng nhãn dữ liệu.
- Thêm benchmark tái lập 10 OD × 3 scenario × 6 thuật toán × 20 lần chạy và artifact
  `DERIVED_BENCHMARK`; ADR-0014 ghi nhận thay đổi contract/demo scope.

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
