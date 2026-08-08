# Backend API

## Processed dataset catalog

`GET /api/v1/graphs` chỉ khám phá hai root cấu hình (`data/fixtures` và
`data/processed`). Processed graph ID có prefix `processed/`, ví dụ
`processed/thu_duc_market_v1.0.0`. Mỗi catalog row bổ sung `dataset_kind`,
`snapshot_date`, `real_time`, `source_ids`, `limitations` và
`routing_dataset_status`.

Fixture result vẫn là `SIMULATED`. Processed result propagate `SOURCE_BACKED`,
`DERIVED`, `ASSUMPTION` hoặc `MIXED`; limitation của pilot nói rõ traffic là lịch sử,
không real-time.

All endpoints use prefix `/api/v1`. Swagger UI is available at `/docs`, and the
OpenAPI document is available at `/openapi.json`.

## Study-area boundary

`GET /api/v1/boundaries/thu-duc` trả frozen GeoJSON của OSM relation `19407794`.
Payload giữ source, snapshot, license và `boundary_status=HISTORIC_OSM_RELATION`.
Frontend dùng polygon để vẽ “Ranh TP Thủ Đức cũ” và tính overview rectangle; endpoint
không tham gia topology hoặc cost.

## Search catalog

- `GET /api/v1/locations?graph_id=toy_graph_v0.1` lists every selectable topology node.
  Với processed pilot, POI thật đứng trước và node còn lại có tên giao lộ deterministic;
  response có đúng một row cho mỗi `node_id`.
- Với `processed/thu_duc_landmarks_v1.0.0`, response chỉ có 65 named landmark; không trả
  8.952 node đường nguồn dùng trong bước build.
- `GET /api/v1/scenarios?graph_id=toy_graph_v0.1` lists scenario, preset, weights
  and closed edges.

Basemap feature không được gửi thẳng vào search. Frontend snap click basemap tới node gần
nhất trong 200 m rồi mới dùng `node_id` hợp lệ trong request.

## Search

`POST /api/v1/search` accepts:

```json
{
  "start": "N01",
  "goal": "N06",
  "algorithm": "A_STAR",
  "scenario": "HEAVY_RAIN_SAFE"
}
```

`graph_id` is optional and defaults to `toy_graph_v0.1`. Initial algorithm names
are `UCS` and `A_STAR`; A* currently uses admissible `h=0`.

The response includes `path`, `edge_ids`, `metrics`, `trace`, `guarantee`,
`explanation`, `edge_breakdown`, `data_status` and `limitations`. Fixture results
are always marked `SIMULATED`.

## Compare

`POST /api/v1/compare` accepts the same start, goal and scenario with an
`algorithms` array. When omitted, it compares `UCS` and `A_STAR` using exactly the
same graph and cost engine.

## Errors

| Condition | Status |
|---|---:|
| Unknown node or scenario | 404 |
| No directed route in the active scenario | 404 |
| Invalid algorithm or cost configuration | 422 |
| Missing/invalid request field | 422 |

Error responses use `{ "detail": "actionable message" }`.
