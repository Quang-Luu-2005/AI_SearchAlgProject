# Hướng dẫn chạy FloodRoute HCMC

Validator kiểm tra cả fixture và processed pilot chợ Thủ Đức. Dòng
`release status: REVIEW_REQUIRED` là trạng thái dự kiến cho đến khi hai reviewer
xác nhận mapping; đây không phải validation failure.

Tài liệu này mô tả toàn bộ luồng chạy repository ở trạng thái hiện tại: cài môi
trường, kiểm tra dataset, khởi động API và giao diện, nạp graph folder, xem
scenario trên bản đồ, gọi API và chạy test.

> FloodRoute HCMC hiện là prototype học thuật. Fixture và graph examples mang
> nhãn `SIMULATED`; chưa có search algorithm và không dùng kết quả làm chỉ dẫn
> định tuyến hoặc an toàn ngoài thực tế.

## 1. Yêu cầu môi trường

- Windows PowerShell.
- Python 3.11 trở lên.
- Node.js 22.12 trở lên và npm.
- Git nếu cần clone hoặc quản lý thay đổi.

Kiểm tra phiên bản:

```powershell
python --version
node --version
npm --version
```

Tất cả lệnh bên dưới chạy từ repository root:

```powershell
cd D:\AI\Lab\Lab_1
```

## 2. Cài đặt lần đầu

### Backend

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".\backend[dev]"
```

Nếu PowerShell chặn script activate, chỉ mở quyền trong terminal hiện tại:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

### Frontend

```powershell
npm --prefix frontend install
```

Các lần chạy sau vẫn cần activate `.venv` trong terminal backend nhưng không cần
cài lại package nếu dependency chưa thay đổi.

## 3. Kiểm tra dataset trước khi chạy

```powershell
.\.venv\Scripts\Activate.ps1
npm run test:data
```

Kết quả đúng phải bắt đầu bằng:

```text
Dataset validation: PASS
```

Validator hiện kiểm tra checksum raw source, nhãn `SIMULATED`, unique ID, khóa
ngoại Node/Edge, trọng số dương, scenario closure, metadata count và golden path.

## 4. Chạy ứng dụng

Cách khuyến nghị là chạy cả backend và frontend trong một terminal:

```powershell
cd D:\AI\Lab\Lab_1
npm run dev
```

Script kiểm tra `.venv` và frontend dependencies trước khi chạy, dùng đúng Python
trong `.venv`, khởi động Vite từ folder `frontend/` và dừng cả hai service khi
nhấn `Ctrl+C`.

Khi lưu file, Uvicorn tự reload backend và Vite tự cập nhật frontend qua HMR.
Vite dùng polling để watcher ổn định trên Windows, OneDrive hoặc thư mục mount
mạng. Dùng `npm run dev` trong lúc phát triển; `build`/`preview` không có hot
reload.

Các địa chỉ:

- Frontend: `http://localhost:5173`
- API root: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/api/v1/health`

Nếu muốn xem log ở hai terminal riêng:

```powershell
# Terminal backend
cd D:\AI\Lab\Lab_1
npm run dev:backend

# Terminal frontend khác
cd D:\AI\Lab\Lab_1
npm run dev:frontend
```

Các script riêng vẫn tự dùng đúng working directory; không cần activate `.venv`
để chạy server. Mở `http://localhost:5173` trong trình duyệt. Vite tự proxy
request `/api` sang backend ở port 8000.

## 5. Nạp và hiển thị graph trên giao diện

Giao diện không còn hard-code Node/Edge. Khi mở trang, backend tự khám phá các graph
folder hợp lệ bên dưới `data/fixtures` và `data/processed`; pilot chợ Thủ Đức được
chọn mặc định.

1. Chọn graph trong ô **Dataset folder**.
2. Chọn **Scenario** nếu graph có `scenarios.json`.
3. OpenFreeMap hiển thị nền đường/POI; MapLibre overlay Node và directed Edge từ CSV.
4. Edge đang mở có màu xanh; edge bị đóng có nét đứt màu đỏ.
5. Bấm **Chọn START** hoặc **Chọn GOAL**, sau đó click bất kỳ node; `Escape` để hủy.
6. Sau khi thêm hoặc sửa folder, bấm **Quét và nạp lại**.

Basemap cần mạng nhưng không bắt buộc cho search. Nếu không tải được, UI báo lỗi nền
và tiếp tục vẽ graph trên background trung tính. Đổi provider/style bằng cách copy
`frontend/.env.example` thành `frontend/.env` rồi sửa `VITE_BASEMAP_STYLE_URL`.

Nếu Vite báo thiếu `frontend/node_modules/.vite/deps/maplibre-gl-worker.mjs`, dừng
frontend rồi khởi động lại với `npm run dev:frontend -- --force`. Cấu hình Vite đã
đóng gói worker bằng `?worker&url`/`setWorkerUrl` và loại `maplibre-gl` khỏi dependency
optimizer; tùy chọn `--force` chỉ dùng để làm mới cache cũ của lần chạy trước.

Các fixture có sẵn:

| Dataset folder | Nội dung |
|---|---|
| `toy_graph_v0.1` | 6 node, 14 directed edge và hai scenario |
| `graph_examples_v0.1/simple_path` | Đường thẳng có hướng |
| `graph_examples_v0.1/one_way_branch` | Nhánh một chiều |
| `graph_examples_v0.1/cycle_with_closure` | Cycle và scenario phá cycle |
| `processed/thu_duc_market_v1.0.0` | Pilot thực tế 90 node/155 edge, historical/not real-time |
| `processed/thu_duc_landmarks_v1.0.0` | Mặc định: 65 landmark chọn được/178 road-path edge |
| `processed/thu_duc_core_capacity_v0.1.0` | Benchmark UTraffic 3.229 node/5.057 edge; không flood-aware |

Trong landmark dataset, circle trắng viền xanh là nút có thể chọn. Trong chế độ START/GOAL
có thể click trực tiếp marker hoặc vị trí gần marker trên basemap; trường hợp thứ hai snap
tới landmark gần nhất trong 200 m. Nếu không có landmark trong bán kính này, chế độ chọn
được giữ nguyên và UI báo lỗi.

Map vẽ đường đỏ “Ranh TP Thủ Đức cũ” từ frozen OSM boundary snapshot. Camera chỉ pan
trong rectangle B có lề bao trọn polygon ranh A; min zoom 10.5 và
`renderWorldCopies=false` ngăn viewport đi ra toàn TP.HCM hoặc bản đồ thế giới. Nút reset
fit lại B, nhờ vậy các cạnh sát biên và một vành nhỏ bên ngoài đường đỏ vẫn nhìn thấy.
Nếu boundary API lỗi, camera fallback và giới hạn theo graph context bounds.

## 6. Thêm dataset folder mới

Tạo folder mới bên dưới `data/fixtures`:

```text
data/fixtures/my_graph_v0.1/
  nodes.csv
  edges.csv
  scenarios.json
  metadata.json
  test_cases.json
```

Loader chỉ bắt buộc `nodes.csv` và `edges.csv` để khám phá graph. Tuy nhiên,
fixture dùng để nộp hoặc review nên có đủ năm file trên và gắn `SIMULATED` hoặc
`ASSUMPTION` phù hợp.

Ví dụ tối thiểu cho `nodes.csv`:

```csv
node_id,name,node_type,latitude,longitude,source_id,validation_status,data_status
EX_A,Điểm A,start,10.8000,106.7000,SIM-MY-GRAPH,Fixture,SIMULATED
EX_B,Điểm B,goal,10.8010,106.7010,SIM-MY-GRAPH,Fixture,SIMULATED
```

Ví dụ tối thiểu cho `edges.csv`:

```csv
edge_id,from_node_id,to_node_id,road_name,direction,distance_m,free_flow_time_min,source_id,is_restricted,data_status
EX_E01,EX_A,EX_B,Đoạn A-B,one-way,100,1.0,SIM-MY-GRAPH,false,SIMULATED
```

Sau khi lưu file:

```powershell
npm run test:data
```

Quay lại giao diện và bấm **Quét và nạp lại**. Folder sai contract không xuất
hiện trong dropdown và được liệt kê trong cảnh báo màu vàng.

Chi tiết field xem [graph-format.md](graph-format.md).

## 7. Kiểm tra API graph

Liệt kê graph folder hợp lệ:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/graphs
```

Nạp một graph:

```powershell
Invoke-RestMethod `
  http://localhost:8000/api/v1/graphs/graph_examples_v0.1/simple_path
```

Nạp graph với scenario:

```powershell
Invoke-RestMethod `
  "http://localhost:8000/api/v1/graphs/graph_examples_v0.1/cycle_with_closure?scenario_id=BREAK_CYCLE"
```

API chỉ cho phép `graph_id` nằm dưới `data/fixtures` hoặc `data/processed`; không nhận
filesystem path tùy ý từ frontend.

### Kiểm tra API search BE-03

Liệt kê location và scenario:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/locations
Invoke-RestMethod http://localhost:8000/api/v1/scenarios
```

Chạy request bàn giao:

```powershell
$body = @{
  start = "N01"
  goal = "N06"
  algorithm = "A_STAR"
  scenario = "HEAVY_RAIN_SAFE"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/search `
  -ContentType "application/json" `
  -Body $body
```

Mở `http://localhost:8000/docs`, chọn `POST /api/v1/search`, bấm **Try it out**
và **Execute** để kiểm tra cùng example trong Swagger. Registry hiện hỗ trợ
`UCS` và `A_STAR`; A* dùng `h=0` nên có cùng optimality guarantee với UCS nhưng
chưa có lợi thế heuristic.

## 8. Nạp graph trực tiếp bằng Python

```powershell
@'
from backend.app.core.graph import GraphLoader

graph = GraphLoader.from_directory(
    "data/fixtures/graph_examples_v0.1/cycle_with_closure"
)

print("Nodes:", len(graph.nodes))
print("Edges:", len(graph.edges))
print("Has cycle:", graph.has_cycle())

scenario_graph = graph.for_scenario("BREAK_CYCLE")
print("Has cycle after closure:", scenario_graph.has_cycle())

for edge in scenario_graph.edges:
    print(edge.edge_id, edge.from_node_id, "->", edge.to_node_id)
'@ | python -
```

Graph và Scenario view đều bất biến; áp dụng scenario không thay đổi graph gốc.

## 9. Chạy kiểm tra toàn bộ

Activate virtual environment trước để script backend dùng đúng Python có pytest:

```powershell
.\.venv\Scripts\Activate.ps1
npm run test:data
npm run test:backend
npm run test:frontend
npm run build:frontend
```

Có thể chạy data, backend và frontend test liên tiếp bằng:

```powershell
npm test
```

`npm test` chưa bao gồm production build; vẫn nên chạy riêng
`npm run build:frontend` trước khi bàn giao.

## 10. Chạy production build frontend

```powershell
npm run build:frontend
npm --prefix frontend run preview
```

Vite sẽ in URL preview trong terminal. Backend vẫn phải chạy ở port 8000 để các
request graph API hoạt động; khi dùng preview không có dev proxy, cấu hình deploy
thực tế sẽ cần reverse proxy hoặc API base URL phù hợp.

## 11. Lỗi thường gặp

### `No module named pytest`

Terminal đang dùng Python hệ thống thay vì `.venv`:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest backend\tests
```

### Frontend báo không tải được graph

- Kiểm tra backend còn chạy ở port 8000.
- Mở `http://localhost:8000/api/v1/health`.
- Kiểm tra terminal backend có validation hoặc parsing error.
- Đảm bảo frontend được mở từ `http://localhost:5173`, không mở trực tiếp file HTML.

### Frontend mở nhưng trả 404

Dùng script ở repository root thay vì gọi trực tiếp file Vite:

```powershell
npm run dev
```

Script này đặt working directory của Vite về đúng `frontend/`. Nếu dependency
chưa có, chạy `npm --prefix frontend install` rồi thử lại.

### Folder không xuất hiện trong dropdown

- Folder phải nằm dưới `data/fixtures`.
- Phải có đúng tên `nodes.csv` và `edges.csv`.
- Chạy `npm run test:data` để xem lỗi ID/FK, trọng số hoặc nhãn.
- Bấm **Quét và nạp lại** sau khi sửa.

### Có graph nhưng bản đồ không thấy node

Node cần `latitude` và `longitude` hợp lệ. Node thiếu tọa độ vẫn tồn tại trong
Graph contract nhưng không thể vẽ trên Leaflet.

### Port 8000 hoặc 5173 đang được sử dụng

Tìm process đang giữ port:

```powershell
Get-NetTCPConnection -LocalPort 8000,5173 -State Listen |
  Select-Object LocalPort,OwningProcess
```

Đóng terminal cũ hoặc dừng đúng process trước khi chạy lại.

## 12. Phạm vi hiện tại

Đã có:

- Graph/Node/Edge/Scenario contract bất biến.
- CSV/JSON Graph Loader và fixture discovery.
- Dataset validator và graph examples.
- API catalog/detail cho graph fixture.
- Giao diện chọn dataset/scenario và bản đồ topology động.

Chưa có:

- BFS, DFS, UCS, A*, Greedy và Bidirectional Search.
- API search và route optimization.
- OSM graph v1.0 đã kiểm định.
- Kết quả định tuyến thực tế.
