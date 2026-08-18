# ADR-0015 — Scenario-aware Cost Lower-Bound Heuristic for A*

## Status

Accepted. Supersedes the heuristic formulation in ADR-0012.

## Context

The previous A* heuristic used only the scenario distance weight multiplied by
Haversine distance. The cost function also includes free-flow time, congestion
and flood-risk terms, so that scale is valid but can be unnecessarily weak.
The project needs a scenario-aware lower bound that remains explainable and
preserves UCS's optimal cost.

## Decision

For a frozen graph/scenario snapshot `s`, calculate the scale once before A*
starts:

```text
rho_s = min(Cost_s(e) / Haversine(from(e), to(e)))
```

The minimum is taken over open edges with finite endpoint coordinates and
Haversine distance greater than `1e-6 km`. Edges closed by the scenario or by
an edge override are excluded. If no usable edge remains, `rho_s = 0`.

The A* heuristic is:

```text
h_s(n) = rho_s * Haversine(n, goal)
f(n) = g(n) + h_s(n)
```

The implementation lives in the framework-independent weighted-search module.
It uses immutable graph/scenario contracts, computes `rho_s` once per search,
and keeps deterministic `(f, g, node_id)` queue ordering. Greedy Best-First
Search uses the same scale for comparability; UCS remains `h(n) = 0`.

## Correctness conditions

When edge costs are non-negative, the scenario is static during a search, and
the active edges have valid geographic coordinates, every open edge satisfies
`Cost_s(e) >= rho_s * d_geo(e)`. The Haversine triangle inequality then gives
admissibility and consistency. Missing coordinates safely produce `h = 0`,
while a zero/near-zero edge denominator is ignored only during rho estimation.

## Consequences

- Traffic and flood penalties influence the lower-bound scale through the same
  `ScenarioCostEngine` cost used by `g(n)`.
- Road closures cannot artificially lower `rho_s`.
- `rho_s` may be small, so A* can still explore nearly as many nodes as UCS;
  optimality is the guarantee, not a promise of speedup.
- The reproducible fixture benchmark is stored in
  `experiments/results/astar_ucs_lower_bound_v1.md` and is labelled
  `DERIVED_BENCHMARK` over `SIMULATED` data.
