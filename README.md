# FloodRoute HCMC

Website mô phỏng tìm đường giao hàng đa điểm cho shipper xe máy tại TP.HCM trong
điều kiện kẹt xe và ngập nước. Repository hiện ở giai đoạn **bootstrap v0.1**:
khung frontend/backend chạy được, dataset có provenance, và fixture deterministic
đã sẵn sàng để bắt đầu triển khai thuật toán.

> Đây là prototype học thuật. Traffic và fixture hiện tại có phần dữ liệu mô
> phỏng, không phải chỉ dẫn an toàn hoặc định tuyến dùng ngoài đời thực.

## Stack đã chọn

- Frontend: React + TypeScript + Vite + React Leaflet.
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
UCS, A* hoặc so sánh hai thuật toán. Đường đi, node đã duyệt và metrics đều lấy
trực tiếp từ Backend API; dữ liệu fixture được hiển thị với nhãn `SIMULATED`.

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
| OSM graph 80–150 nút | Chưa thực hiện |
| Map-match 24 flood hotspots | Chưa thực hiện |
| UCS và A* (`h=0`) | Hoàn tất |
| BFS/DFS/Greedy/Bidirectional | Chưa thực hiện |
| Held-Karp/Nearest Neighbor | Chưa thực hiện |

Ưu tiên tiếp theo là chốt vùng nghiên cứu và đóng băng OSM snapshot v1.0; không
tuyên bố kết quả định tuyến thực tế khi `routing_dataset_status` vẫn là `NOT_READY`.
