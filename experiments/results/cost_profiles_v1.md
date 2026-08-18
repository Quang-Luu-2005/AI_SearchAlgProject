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

### EX02_MARKET_GOLDEN_FLOOD_DETOUR — processed/thu_duc_market_v1.0.0 (MIXED)

OD: `UTR_NODE_2947068442 → UTR_NODE_366385739`

| Scenario | Route | Edges | Cost | Distance (km) | ETA (min) |
|---|---|---:|---:|---:|---:|
| HISTORICAL_OFFPEAK | `UTR_NODE_2947068442 → UTR_NODE_5758041297 → UTR_NODE_2947068443 → UTR_NODE_366410061 → UTR_NODE_366385739` | 4 | 0.348775 | 0.143 | 0.225 |
| RAIN_FLOOD_AWARE_2025_2026 | `UTR_NODE_2947068442 → UTR_NODE_5758041297 → UTR_NODE_2947068443 → … → UTR_NODE_366457374 → UTR_NODE_366442171 → UTR_NODE_366385739` | 27 | 0.435970 | 0.612 | 1.764 |

Interpretation: The frozen market golden case changes from the off-peak route to a longer flood-aware detour when the rain/flood profile is active.
