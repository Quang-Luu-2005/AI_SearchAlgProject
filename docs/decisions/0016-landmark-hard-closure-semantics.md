# ADR 0016: Hard closure semantics for landmark edges

## Status

Accepted - 2026-08-19

## Decision

The `thu_duc_landmarks_v1.0.2` release keeps the existing 65 nodes and expands the
graph to 283 directed aggregate edges, adding up to four nearest outgoing road-path
alternatives per landmark. A scenario closes an edge when its ID appears in `closed_edge_ids` or
when its `edge_overrides` entry has `is_closed: true`. The immutable `Graph` contract
normalizes this union and filters it from `neighbors()`, `list_edges()`, edge lookup,
and every algorithm-facing graph operation.

Search must never traverse a closed edge. If the remaining directed graph has no route,
the service returns `RouteNotFoundError`, surfaced by the API as `NO_ROUTE`.

## Consequences

- No node is added; the denser release adds only aggregate edges derived from existing
  source-road routes.
- The fixed `ASSUMPTION` scenario `LANDMARK_HARD_CLOSURE_DETOUR` closes `LM_EDGE_0001`.
- Closure is intentionally limited to exact landmark aggregate edge IDs. It does not
  propagate to other aggregate edges whose geometry or source road segments overlap.
- The closure contract is independent of FastAPI and remains usable by all algorithms
  and tests.
