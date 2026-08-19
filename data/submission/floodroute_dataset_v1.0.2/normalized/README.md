# Thu Duc major landmarks road graph v1.0.2

Selectable nodes are named major OSM places. Directed edges are aggregated UTraffic shortest road paths with frozen polyline geometry. This is a MIXED, historical academic demo and not real-time navigation.

This release keeps 65 nodes and expands the graph to 283 directed edges by adding up to four nearest outgoing road-path alternatives per landmark. The additional choices improve detours when one edge is closed. The `ASSUMPTION` scenario `LANDMARK_HARD_CLOSURE_DETOUR` closes `LM_EDGE_0001`.

Closure applies to exact landmark aggregate-edge IDs only; it does not propagate to other aggregate edges whose source segments or geometry overlap.
