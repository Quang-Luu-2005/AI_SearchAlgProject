# ADR-0008 — Geographic Weighted Haversine Distance Heuristic for A* Search

## Status

Accepted for BE-04.

## Context

ADR-0005 defined a multi-component edge cost model balancing distance, free-flow time, traffic congestion, and flood risk:
$$c(e) = w_{\text{dist}} \cdot d(e) + w_{\text{time}} \cdot t_{\text{ff}}(e) + w_{\text{cong}} \cdot \text{traffic\_penalty}(e) + w_{\text{flood}} \cdot \text{flood\_risk}(e)$$
where weights $w_i \ge 0$ sum to 1.0. Previously, ADR-0006 adopted $h=0$ for initial A* bootstrap. However, $h=0$ offers no search space pruning over Uniform Cost Search (UCS). A non-trivial geographic heuristic is required for A* to accelerate route planning on real-world road networks while guaranteeing optimal path costs.

## Decision

- Adopt the **Geographic Weighted Haversine Distance Heuristic** for A* search:
  $$h(n) = w_{\text{dist}} \cdot D_{\text{Haversine}}(n, \text{goal})$$
  where $D_{\text{Haversine}}(n, \text{goal})$ is the great-circle distance (in kilometers) between node $n$ and the goal node calculated using WGS84 coordinates ($\text{lat}, \text{lon}$), and $w_{\text{dist}}$ is the distance weight from the active scenario cost preset.
- If WGS84 coordinates are missing or `None` (e.g. abstract toy graphs), $h(n)$ defaults to $0.0$.
- Record precise $h(n)$ values in `TraceEvent` objects (`OPEN`, `EXPAND`, `RELAX`, `CLOSE`, `GOAL`) to support trace replay and visualization.

## Mathematical Proofs

### 1. Admissibility ($h(n) \le h^*(n)$)
Because all cost components ($t_{\text{ff}}$, $\text{traffic\_penalty}$, $\text{flood\_risk}$) and weights $w_i$ are non-negative:
$$c(e) \ge w_{\text{dist}} \cdot d(e)$$
For any path $P = (n = v_0, v_1, \dots, v_k = \text{goal})$, the total cost satisfies:
$$\text{Cost}(P) = \sum_{i=0}^{k-1} c(v_i, v_{i+1}) \ge w_{\text{dist}} \sum_{i=0}^{k-1} d(v_i, v_{i+1}) \ge w_{\text{dist}} \cdot D_{\text{Haversine}}(n, \text{goal}) = h(n)$$
(by the triangle inequality of geodesic distance on Earth's surface).
Since $h(n) \le h^*(n)$ for all nodes $n$, the heuristic is **admissible**.

### 2. Consistency (Monotonicity: $h(u) \le c(u, v) + h(v)$)
For any directed edge $e = (u, v)$:
By triangle inequality of Haversine distance:
$$D_{\text{Haversine}}(u, \text{goal}) \le d(u, v) + D_{\text{Haversine}}(v, \text{goal})$$
Multiplying through by non-negative $w_{\text{dist}}$:
$$w_{\text{dist}} \cdot D_{\text{Haversine}}(u, \text{goal}) \le w_{\text{dist}} \cdot d(u, v) + w_{\text{dist}} \cdot D_{\text{Haversine}}(v, \text{goal}) \le c(u, v) + h(v)$$
$$h(u) \le c(u, v) + h(v)$$
Thus, the heuristic is **consistent (monotonic)**, guaranteeing that A* will never re-expand a closed node.

## Consequences

- A* expands fewer or equal nodes compared to UCS on geographical datasets (`thu_duc_market_v1.0.0`).
- Optimal path costs match UCS identically.
- Re-expansion check overhead is zero due to monotonicity.
- Fallback to $h=0$ maintains backward compatibility for abstract non-geographical fixture graphs.
