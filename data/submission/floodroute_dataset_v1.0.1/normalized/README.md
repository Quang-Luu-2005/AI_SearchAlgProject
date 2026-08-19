# Thu Duc major landmarks road graph v1.0.1

Selectable nodes are named major OSM places. Directed edges are aggregated UTraffic shortest road paths with frozen polyline geometry. This is a MIXED, historical academic demo and not real-time navigation.

This release preserves the fixed topology of 65 nodes and 178 directed edges. It adds the `ASSUMPTION` scenario `LANDMARK_HARD_CLOSURE_DETOUR`, which hard-closes exactly `LM_EDGE_0001`; algorithms must detour or return `NO_ROUTE`.

Closure is defined at the landmark aggregate-edge level only. It is not propagated to other aggregate edges whose source road segments or geometry overlap.
