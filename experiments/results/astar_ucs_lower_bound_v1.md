# A* lower-bound heuristic vs UCS

Status: `DERIVED_BENCHMARK`; graph/scenarios: `SIMULATED` fixture.

Formula: `h_s(n) = rho_s × Haversine(n, goal)`; closed edges and edges with Haversine ≤ 1e-6 km are excluded from rho_s.

| Scenario | OD | Start → goal | rho_s | UCS cost | A* cost | Δ cost | UCS explored | A* explored | Match |
|---|---:|---|---:|---:|---:|---:|---:|---:|:---:|
| OFFPEAK_BALANCED | OD01 | N01 → N06 | 0.368004796 | 2.343000 | 2.343000 | 0.000000000 | 5 | 5 | YES |
| OFFPEAK_BALANCED | OD02 | N03 → N06 | 0.368004796 | 2.000000 | 2.000000 | 0.000000000 | 6 | 4 | YES |
| OFFPEAK_BALANCED | OD03 | N01 → N05 | 0.368004796 | 2.755000 | 2.755000 | 0.000000000 | 6 | 4 | YES |
| OFFPEAK_BALANCED | OD04 | N02 → N05 | 0.368004796 | 3.281000 | 3.281000 | 0.000000000 | 6 | 6 | YES |
| OFFPEAK_BALANCED | OD05 | N06 → N05 | 0.368004796 | 3.455000 | 3.455000 | 0.000000000 | 6 | 5 | YES |
| PEAK_TRAFFIC | OD01 | N01 → N06 | 0.467035595 | 2.920900 | 2.920900 | 0.000000000 | 5 | 4 | YES |
| PEAK_TRAFFIC | OD02 | N03 → N06 | 0.467035595 | 2.562500 | 2.562500 | 0.000000000 | 6 | 4 | YES |
| PEAK_TRAFFIC | OD03 | N01 → N05 | 0.467035595 | 3.451500 | 3.451500 | 0.000000000 | 6 | 4 | YES |
| PEAK_TRAFFIC | OD04 | N02 → N05 | 0.467035595 | 4.222175 | 4.222175 | 0.000000000 | 6 | 6 | YES |
| PEAK_TRAFFIC | OD05 | N06 → N05 | 0.467035595 | 4.416500 | 4.416500 | 0.000000000 | 6 | 5 | YES |
| HEAVY_RAIN_SAFE | OD01 | N01 → N06 | 0.298932016 | 2.562625 | 2.562625 | 0.000000000 | 6 | 5 | YES |
| HEAVY_RAIN_SAFE | OD02 | N03 → N06 | 0.298932016 | 1.637500 | 1.637500 | 0.000000000 | 6 | 4 | YES |
| HEAVY_RAIN_SAFE | OD03 | N01 → N05 | 0.298932016 | 2.207500 | 2.207500 | 0.000000000 | 5 | 4 | YES |
| HEAVY_RAIN_SAFE | OD04 | N02 → N05 | 0.298932016 | 2.697625 | 2.697625 | 0.000000000 | 6 | 6 | YES |
| HEAVY_RAIN_SAFE | OD05 | N06 → N05 | 0.298932016 | 2.822500 | 2.822500 | 0.000000000 | 6 | 4 | YES |

Summary: 15 cases, 0 cost mismatches, A* explored no more nodes than UCS in 15/15 cases.
