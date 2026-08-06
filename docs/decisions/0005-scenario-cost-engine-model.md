# ADR-0005 — Scenario cost engine and edge cost model

## Status

Accepted for BE-02.

## Context

Search algorithms need one deterministic, non-negative edge cost that can change
with traffic, flood risk and closed edges. The graph and scenario contracts are
immutable, and all current fixture metrics are simulated.

## Decision

Implement `ScenarioCostEngine` in `backend/app/core/cost.py` using four preset
weights whose sum must equal 1:

```text
total_cost =
  distance_km * w_distance
  + free_flow_time_min * w_freeflow_time
  + traffic_penalty * w_congestion
  + flood_risk * w_flood_risk
```

`traffic_penalty` is the extra travel time above free-flow time. The engine also
returns `travel_time_min`, `congestion_level_1_5`, the unweighted metrics,
weighted components and `data_status`. This keeps free-flow time separate from
congestion and prevents double counting.

The initial presets are:

- `BALANCED`: distance 0.25, free-flow time 0.30, congestion 0.20, flood risk 0.25.
- `PEAK_TRAFFIC`: distance 0.15, free-flow time 0.25, congestion 0.45, flood risk 0.15.
- `RAIN_SAFE`: distance 0.10, free-flow time 0.25, congestion 0.15, flood risk 0.50.

Scenario edge overrides take precedence over edge attributes, then scenario
defaults. A closed edge still returns its metric breakdown, but has
`is_closed=true` and `total_cost=null`; route aggregation marks the route
unavailable. Negative weights, metrics, penalties, risk and invalid preset
references are rejected.

## Consequences

The engine is framework-independent and can be reused by UCS/A*/other search
algorithms. Cost output is inspectable for explanations and route totals can be
verified as the sum of edge totals. Preset weights are a deliberate simulated
assumption and require review before real OSM/traffic data is presented as
routing guidance.

## Alternatives rejected

- Adding traffic directly to free-flow time and then weighting both again would
  double count congestion.
- Mutating edge objects when applying a scenario would break deterministic
  reuse and the immutable graph contract.
