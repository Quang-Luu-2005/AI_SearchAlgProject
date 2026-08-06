# ADR-0006 — Search API contract and zero-heuristic A*

## Status

Accepted for BE-03.

## Context

The backend must expose locations, scenarios, two-point search and algorithm
comparison while keeping validation/serialization separate from algorithm code.
The repository does not yet have a reviewed geographic heuristic for the weighted
multi-component cost defined by ADR-0005.

## Decision

- Add `GET /api/v1/locations`, `GET /api/v1/scenarios`,
  `POST /api/v1/search` and `POST /api/v1/compare`.
- Keep FastAPI/Pydantic code in `backend/app/api`; orchestration lives in
  `backend/app/services`, and algorithms live in `backend/app/algorithms`.
- Support `UCS` and `A_STAR` in the initial registry. Unknown names return 422
  with the supported values.
- Implement A* with `h=0`. It is admissible and consistent, so A* has the same
  optimality result as UCS for non-negative edge costs, but no performance claim.
- Use deterministic priority ordering by cumulative cost and then `node_id`.
- Return 404 for unknown nodes/scenarios and unreachable routes; malformed input,
  invalid algorithms and invalid cost configuration return 422.
- Default `graph_id` to `toy_graph_v0.1`, allowing the required four-field request
  body to run unchanged.
- Return path, edge IDs, metrics, trace, guarantee, explanation, edge breakdown,
  data status and limitations. Runtime is measured only around algorithm execution.
- `compare` runs each algorithm through the same `SearchService`, graph, scenario
  and cost engine.

## Consequences

Swagger/OpenAPI exposes concrete request/response schemas and a runnable example.
Search remains testable without HTTP and API routes contain no search logic. A*
is correct but currently offers no speed advantage over UCS; introducing a
geographic heuristic requires a later ADR with unit/admissibility evidence.
