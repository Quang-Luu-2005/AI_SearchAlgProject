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

`graph_id` is optional and defaults to `toy_graph_v0.1`. Supported two-point
algorithm names are `UCS`, `A_STAR`, `BFS`, `DFS`, `GREEDY` and `BIDIRECTIONAL`; A* and Greedy use the
scenario-aware lower-bound Haversine heuristic from ADR-0015, with `h=0` fallback
when coordinates are unavailable. A* computes `rho_s` once per frozen scenario;
closed edges and near-zero geographic edges are excluded from its minimum ratio.

The response includes `path`, `edge_ids`, `metrics`, `trace`, `guarantee`,
`explanation`, `edge_breakdown`, `data_status` and `limitations`. Fixture results
are always marked `SIMULATED`.

`GET /api/v1/scenarios` is the public cost-profile catalog. It exposes the
three stable preset names `BALANCED`, `PEAK_TRAFFIC` and `RAIN_SAFE` together
with their weights and closed edges. Custom weights are intentionally not
accepted by the public search contract in this deadline; the prototype keeps
the profile set deterministic. Closed edges remain hard constraints and are
not made traversable by any weight combination.

## Compare

`POST /api/v1/compare` accepts the same start, goal and scenario with an
`algorithms` array. When omitted, it compares `UCS` and `A_STAR`; callers may also
include `BFS`, `DFS`, `GREEDY` and `BIDIRECTIONAL`. The GUI compares all six. Every algorithm uses exactly the same graph and scenario
cost input, and results preserve the request order after duplicate removal.

## Optimize Tour

`POST /api/v1/optimize-tour` accepts:

```json
{
  "depot": "N01",
  "stops": ["N02", "N03", "N04", "N05", "N06"],
  "scenario": "HEAVY_RAIN_SAFE",
  "graph_id": "toy_graph_v0.1",
  "algorithm": "A_STAR",
  "tour_algorithm": "HELD_KARP",
  "return_to_depot": true
}
```

The request requires 5 to 10 unique delivery stops; the depot must not be repeated
in `stops`. `tour_algorithm` accepts `HELD_KARP` or `NEAREST_NEIGHBOR`. The service
computes a directed pairwise cost/distance matrix using the search engine, solves
exact DP Held-Karp and the Nearest Neighbor heuristic, measures the approximation
gap, and returns stitched subpaths, totals, comparison metrics, guarantee, and a
structured explanation. `comparison` also contains the original input visit order and
its cost/distance/ETA plus absolute and percentage savings of the selected tour.


## Errors

| Condition | Status |
|---|---:|
| Unknown node or scenario | 404 |
| No directed route in the active scenario | 404 |
| Invalid algorithm or cost configuration | 422 |
| Duplicate tour point or unsupported tour algorithm | 422 |
| Missing/invalid request field | 422 |

Error responses use `{ "detail": "actionable message" }`.
