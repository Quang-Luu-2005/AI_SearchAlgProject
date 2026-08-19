# Cost profiles and route-change evidence

Status: `DERIVED_PROFILE_REVIEW`. Profile values are `ASSUMPTION` coefficients for the prototype.

Cost formula: `distance*w_distance + freeflow_time*w_freeflow_time + traffic_penalty*w_congestion + flood_risk*w_flood_risk`.
The weights are priority coefficients, not percentage contributions: the four components have different units/scales.
Road closure is a hard constraint; weights never make a closed edge traversable.

## Frozen profiles

| Preset | Distance | Free-flow time | Congestion | Flood risk | Sum | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| BALANCED | 0.25 | 0.30 | 0.20 | 0.25 | 1.00 | Default trade-off across distance, free-flow time, congestion and flood risk. |
| PEAK_TRAFFIC | 0.15 | 0.25 | 0.45 | 0.15 | 1.00 | Raises congestion priority to avoid delay during peak traffic; distance/flood remain secondary signals. |
| RAIN_SAFE | 0.10 | 0.25 | 0.15 | 0.50 | 1.00 | Raises flood-risk priority so a longer/different route can be preferred when flooding is exposed. |

## Route examples

### EX01_TOY_PROFILE_AND_RAIN — toy_graph_v0.1 (SIMULATED)

OD: `N01 → N06`

| Scenario | Route | Edges | Cost | Distance (km) | ETA (min) |
|---|---|---:|---:|---:|---:|
| OFFPEAK_BALANCED | `N01 → N02 → N06` | 2 | 2.343000 | 2.500 | 5.560 |
| PEAK_TRAFFIC | `N01 → N02 → N06` | 2 | 2.920900 | 2.500 | 8.062 |
| HEAVY_RAIN_SAFE | `N01 → N02 → N04 → N06` | 3 | 2.562625 | 3.000 | 9.838 |

Interpretation: Peak raises cost on the same available route; heavy rain closes E03/E04, so the route must detour through E11/E09.

### EX02_TOY_ALTERNATIVE_RAIN — toy_graph_v0.1 (SIMULATED)

OD: `N05 → N01`

| Scenario | Route | Edges | Cost | Distance (km) | ETA (min) |
|---|---|---:|---:|---:|---:|
| OFFPEAK_BALANCED | `N05 → N06 → N02 → N01` | 3 | 3.733000 | 3.800 | 9.110 |
| HEAVY_RAIN_SAFE | `N05 → N06 → N04 → N02 → N01` | 4 | 3.713250 | 4.300 | 14.275 |

Interpretation: The simulated N05 to N01 route changes under heavy rain because the direct E04 segment is closed and the path detours through E10/E12.

### EX03_LANDMARK_PM_PEAK_DETOUR — thu_duc_landmarks_v1.0.0 (ASSUMPTION)

OD: `LM_065 (Vincom Plaza Thủ Đức) → LM_054 (Trường Đại học FPT)`

| Scenario | Route | Edges | Cost | Distance (km) | ETA (min) |
|---|---|---:|---:|---:|---:|
| LANDMARK_HISTORICAL_BASELINE | `Vincom Thủ Đức → Ga Thủ Đức → SIU → Khu CNC → Sân FTown → ĐH FPT` | 5 | 8.381300 | 11.310 | 18.510 |
| LANDMARK_PM_PEAK | `Vincom Thủ Đức → Ga Thủ Đức → BV Quân Dân y → HV Chính trị II → Chợ Tăng Nhơn Phú → KTX ĐH GTVT → ĐH FPT` | 6 | 11.184000 | 10.280 | 31.390 |

Interpretation: Under PM Peak, the arterial Lê Văn Việt corridor (LM_EDGE_0127) suffers heavy traffic delay (+18 min). A* detours through the internal Tăng Nhơn Phú corridor, saving substantial travel time compared to staying on the congested main road.

### EX04_LANDMARK_HEAVY_RAIN_DETOUR — thu_duc_landmarks_v1.0.0 (SIMULATED)

OD: `LM_065 (Vincom Plaza Thủ Đức) → LM_054 (Trường Đại học FPT TP.HCM)`

| Scenario | Route | Edges | Cost | Distance (km) | ETA (min) |
|---|---|---:|---:|---:|---:|
| LANDMARK_HISTORICAL_BASELINE | `Vincom Plaza → Ga Thủ Đức → SIU → Xa Lộ Hà Nội → KTX ĐHQG Khu B → ĐH FPT` | 5 | 8.381300 | 11.310 | 18.510 |
| LANDMARK_HEAVY_RAIN | `Vincom Plaza → Ga Thủ Đức → BV Quân Dân Y → Trạm Y Tế → Chợ Tăng Nhơn Phú → Bưu Điện → ĐH FPT` | 6 | 7.940700 | 10.280 | 26.920 |

Interpretation: Under Heavy Rain, the direct arterial Lê Văn Việt corridor (LM_EDGE_0127) is closed due to severe tidal flooding. A* strictly avoids the closed corridor (zero closed-edge expansions) and detours safely via the internal Tăng Nhơn Phú bypass corridor to reach FPT University. Neither Start nor Goal coincides with any road closure.

