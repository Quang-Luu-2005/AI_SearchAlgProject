# Nhật ký tiến độ: Triển khai OSM Dataset Pipeline 3 lớp (Raw → Interim → Processed)

**Ngày thực hiện:** 2026-08-10  
**Tác giả:** Antigravity AI  
**Hạng mục:** OSM Data Pipeline & Multi-Layer Dataset Reproduction

## Tóm tắt công việc

1. **Layer 1 - Raw Source (`data/raw/osm/thu_duc_osm_v1.0.0/`):**
   - Snapshot Overpass API `osm_road_snapshot.json` cho bbox Chợ Thủ Đức (`south: 10.845, west: 106.751, north: 10.853, east: 106.759`).
   - Khai báo nguồn gốc trong `source_registry.json` (URL `https://overpass-api.de/api/interpreter`, ODbL 1.0 license).
   - Đóng gói mã băm SHA-256 trong `checksums.sha256`.

2. **Layer 2 - Interim Topology (`data/interim/osm_thu_duc_v1.0.0/`):**
   - Xuất dữ liệu nút/cạnh làm sạch trung gian (`interim_nodes.csv` với 27 nút, `interim_edges.csv` với 40 cạnh có hướng).
   - Tự động sinh bởi script tái lập.

3. **Layer 3 - Processed Release (`data/processed/osm_thu_duc_v1.0.0/`):**
   - Xuất gói release chuẩn hóa gồm `nodes.csv`, `edges.csv`, `scenarios.json` (`HISTORICAL_OFFPEAK`, `PEAK_CONGESTION`, `HEAVY_FLOOD_RAIN`), `delivery_points.csv`, `metadata.json`, `checksums.sha256`, `validation_report.json`.

4. **Script tái tạo & Kiểm định (`scripts/data/`):**
   - Tạo script Python thuần [`scripts/data/build_osm_dataset.py`](../../scripts/data/build_osm_dataset.py).
   - Cập nhật [`scripts/data/validate_dataset.py`](../../scripts/data/validate_dataset.py) và `dataset_manifest.json`.

## Kết quả kiểm thử

- `python scripts/data/build_osm_dataset.py` -> Tái lập thành công cả 2 lớp interim & processed.
- `python scripts/data/validate_dataset.py` -> `Dataset validation: PASS`.
- `npm test` -> PASS 100% (49 backend pytest, 24 frontend vitest).
