# ADR-0012 — Geographic Weighted Haversine Distance Heuristic and Modular Weighted Search Engine

## Status

Accepted.

## Context

Search algorithms in road network routing require high modularity, explicit documentation, clean pseudocode, and mathematical evidence of optimality. In multi-component cost scenarios (combining distance, free-flow time, traffic delay, and flood risk), $h(n) = 0$ degenerates A* to Uniform Cost Search (UCS), resulting in higher node expansion counts.

## Decision

1. **Modular Search Engine Architecture in `backend/app/algorithms/weighted.py`**:
   - `haversine_distance_km(lat1, lon1, lat2, lon2)`: Modular WGS84 great-circle distance calculator.
   - `compute_geographic_heuristic(graph, cost_engine, node_id, goal_id, scenario_id)`: Modular heuristic evaluation function.
   - `_weighted_search()`: Parameterized priority queue engine supporting both UCS ($h=0$) and A* ($h(n) \ge 0$).
   - `uniform_cost_search()` and `a_star_search()`: Explicit entry point functions.

2. **Heuristic Formulation**:
   $$h(n) = w_{\text{distance}} \cdot D_{\text{Haversine}}(n, \text{goal})$$
   where $D_{\text{Haversine}}(n, \text{goal})$ is the great-circle distance in kilometers, and $w_{\text{distance}} \ge 0$ is the scenario's distance weight factor.

3. **Mathematical Evidence**:
   - **Admissibility**: Since straight-line distance is the physical minimum distance between two geographical points ($D_{\text{Haversine}}(n, \text{goal}) \le d^*(n, \text{goal})$) and total cost $c(e) \ge w_{\text{dist}} \cdot d(e)$, $h(n) \le c^*(n, \text{goal}) = h^*(n)$ holds for all nodes $n$.
   - **Consistency (Monotonicity)**: By the geographical triangle inequality, $D_{\text{Haversine}}(n, \text{goal}) \le D_{\text{Haversine}}(n, n') + D_{\text{Haversine}}(n', \text{goal})$. Multiplying by $w_{\text{dist}} \ge 0$ yields $h(n) \le c(n, n') + h(n')$.
   - **Optimality**: **100% Globally Optimal** (not near-optimal) because $h(n)$ is admissible and consistent, and edge costs $c(e) \ge 0$ are non-negative.
   - **Completeness**: Complete on finite graphs with edge costs bounded below by $\epsilon > 0$.

## Consequences

- Pseudocode is embedded directly in function docstrings for easy readability.
- A* prunes search directions effectively, reducing node expansions while maintaining exact optimal path costs.
- Unit tests (`backend/tests/test_weighted_algorithms.py`) verify distance accuracy, admissibility, consistency, optimality match, and pruning performance.
