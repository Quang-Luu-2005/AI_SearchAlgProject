# FloodRoute HCMC

## Active map release

The active processed map is `processed/thu_duc_landmarks_v1.0.0` (65 selectable
landmarks and 178 road-path edges). The former 90-node processed map has been
removed from the catalog and is no longer an application or benchmark target.

## Dataset mặc định đang dùng

Ứng dụng mặc định dùng `processed/thu_duc_landmarks_v1.0.0`: 65 địa điểm lớn có tên thật
từ OSM và 178 cạnh có hướng được tổng hợp theo đường đi ngắn nhất trên snapshot UTraffic.
Mạng nguồn 8.952 node/14.043 cạnh chỉ dùng lúc build; UI chỉ nhận landmark nên bản đồ
không bị phủ bởi node kỹ thuật. Traffic là dữ liệu lịch sử, **không phải real-time**.

Map 65 landmark là release duy nhất được chọn trong GUI và benchmark search.
Các scenario traffic/flood mô phỏng vẫn được kiểm thử trong fixture `SIMULATED`.
[`metadata.json`](data/processed/thu_duc_landmarks_v1.0.0/metadata.json) và
[ADR 0011](docs/decisions/0011-thu-duc-selectable-landmark-graph.md).

Website mô phỏng tìm đường giao hàng đa điểm cho shipper xe máy tại TP.HCM trong
điều kiện kẹt xe và ngập nước. Repository hiện ở giai đoạn **bootstrap v0.1**:
khung frontend/backend chạy được, dataset có provenance, và fixture deterministic
đã sẵn sàng để bắt đầu triển khai thuật toán.

> Đây là prototype học thuật. Traffic và fixture hiện tại có phần dữ liệu mô
> phỏng, không phải chỉ dẫn an toàn hoặc định tuyến dùng ngoài đời thực.

## Stack đã chọn

- Frontend: React + TypeScript + Vite + MapLibre GL JS; OpenFreeMap vector basemap.
- Backend: Python + FastAPI; thuật toán nằm trong module Python thuần.
- Data: raw workbook/OSM snapshot → interim → processed CSV/JSON/GraphML.
- Test: pytest cho backend, Vitest cho frontend, validator chuẩn thư viện Python
  cho provenance/schema/golden fixtures.

Stack này bám sát kế hoạch đã có trong `docs/references/`, cho phép GUI phát lại
trace mà không ghép thuật toán vào frame render, đồng thời giữ engine dễ unit test.

## Cấu trúc chính

```text
backend/                 FastAPI và search engine độc lập framework
frontend/                React UI, bản đồ và trace player
data/
  raw/                   Nguồn bất biến, có checksum
  interim/               Dữ liệu trung gian có thể tạo lại
  processed/             Dataset version dùng khi chạy ứng dụng
  fixtures/              Graph nhỏ cho test/golden/regression
  schemas/               Hợp đồng dữ liệu
  registry/              Manifest, provenance, limitations
docs/
  references/            Đề bài, kế hoạch và ghi chú ban đầu
  decisions/             Architecture Decision Records (ADR)
  progress/              Nhật ký theo từng mốc thực hiện
experiments/             Case definitions và kết quả batch test
scripts/data/            Công cụ kiểm tra/chuyển đổi dataset
```

Chi tiết xem [kiến trúc](docs/architecture.md), [quản lý dữ liệu](docs/data-management.md)
và [quy trình cập nhật tài liệu](docs/documentation-workflow.md). Hướng dẫn từ
cài đặt đến nạp graph và chạy toàn bộ kiểm tra nằm trong
[runbook dự án](docs/runbook.md).

Để chia sẻ nhanh với thành viên mới hoặc người review, xem bản Word
[Tổng quan ý tưởng và kiến trúc hệ thống](docs/FloodRoute_HCMC_Tong_quan_y_tuong_va_kien_truc.docx).

## Chạy lần đầu

Yêu cầu: Node.js 22.12+ và Python 3.11+.

```powershell
# Cài backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".\backend[dev]"

# Cài frontend
npm --prefix frontend install

# Chạy đồng thời backend và frontend
npm run dev
```

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

Giao diện Pathfinder AI cho phép chọn dataset, scenario, điểm đầu/đích và chạy
UCS, A*, BFS, DFS, Greedy, Bidirectional hoặc so sánh cả sáu. Đường đi, trạng thái
frontier/current/closed và metrics đều lấy
trực tiếp từ Backend API; dữ liệu fixture được hiển thị với nhãn `SIMULATED`.

Điểm đầu/đích có thể tìm theo tên/`node_id` hoặc chọn marker tròn trắng viền xanh bằng
toolbar START/GOAL. Hai điểm đã chọn dùng ghim lớn neo đúng tọa độ: START màu cam và
GOAL màu hồng, không làm thay đổi camera hiện tại. Edge hiển thị polyline đường UTraffic
đã đóng băng, không phải đường thẳng nối POI. Nếu mất mạng, nền trung tính vẫn cho phép
chạy thuật toán.

Với Held-Karp/Nearest Neighbor/tour comparison, START chọn depot còn GOAL thêm nhiều
điểm giao hàng. Chế độ GOAL giữ hoạt động để click liên tiếp tối đa 10 stop; các stop
được đánh số và hiển thị ngay trên bản đồ trước khi chạy.

Bản đồ vẽ đường đỏ theo snapshot ranh TP Thủ Đức cũ. View tổng quan là một hình chữ
nhật có lề bao trọn polygon ranh thật, nên vẫn thấy được khu vực ngoài biên và các cạnh
sát ranh. Nút reset đưa camera về rectangle này và camera bị giới hạn trong B, nên không
thể kéo bản đồ ra toàn TP.HCM hoặc world view.

Catalog có thêm `processed/thu_duc_core_capacity_v0.1.0` gồm 3.229 node/5.057 directed
edge để stress-test. Capacity graph không xuất hiện trong dropdown; landmark 65 node là
map 65 node là lựa chọn demo duy nhất. Chạy benchmark bằng:

```powershell
npm run benchmark:capacity
npm run benchmark:search
npm run benchmark:lower-bound
npm run benchmark:cost-profiles
npm run benchmark:route-explanations
```

Benchmark lower-bound A* vs UCS: `experiments/results/astar_ucs_lower_bound_v1.md`.
The heuristic uses `h_s(n) = rho_s × Haversine(n, goal)` from ADR-0015; results
are derived from the `SIMULATED` fixture and must not be read as live traffic.
Cost profile table and route-change evidence: `experiments/results/cost_profiles_v1.md`.
Detailed selected-vs-alternative route breakdowns: `experiments/results/route_explanations_v1.md`.

Basemap mặc định có thể đổi trong `frontend/.env`:

```env
VITE_BASEMAP_STYLE_URL=https://tiles.openfreemap.org/styles/liberty
```

`npm run dev` luôn dùng Python trong `.venv`, chạy Vite từ đúng folder
`frontend/` và dừng cả hai service khi nhấn `Ctrl+C`. Nếu cần chạy riêng:

Trong chế độ này, backend tự reload khi lưu file Python và frontend tự cập nhật
qua Vite HMR. Không dùng `build` hoặc `preview` khi đang phát triển vì đó là các
chế độ không có hot reload.

```powershell
npm run dev:backend
npm run dev:frontend
```

## Kiểm tra

```powershell
npm run test:data
npm run test:backend
npm run test:frontend
npm run build:frontend
```

Hoặc chạy toàn bộ test sau khi cài cả hai môi trường:

```powershell
npm test
```

## Trạng thái và bước kế tiếp

| Hạng mục | Trạng thái |
|---|---|
| Khung React/FastAPI | Hoàn tất |
| Phân lớp dataset + checksum | Hoàn tất |
| Fixture/golden cases | Hoàn tất |
| Graph landmark thực tế | Có: 65 node/178 edge |
| Map-match flood hotspot trong bbox | Candidate; chờ hai reviewer |
| UCS và A* (scenario-aware cost lower bound) | Hoàn tất |
| BFS/DFS/Greedy/Bidirectional | Hoàn tất API/GUI/compare |
| Held-Karp/Nearest Neighbor (tour 5–10 điểm) | Hoàn tất |

Ưu tiên tiếp theo là hai reviewer xác nhận flood map-match; không tuyên bố kết quả
định tuyến thực tế khi `routing_dataset_status` vẫn là `REVIEW_REQUIRED`.
