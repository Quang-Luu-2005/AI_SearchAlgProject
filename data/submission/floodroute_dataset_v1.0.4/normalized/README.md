# Thu Duc major landmarks road graph v1.0.4

Selectable nodes are named major OSM places. Directed edges are aggregated UTraffic shortest road paths with frozen polyline geometry. This is a MIXED, historical academic demo and not real-time navigation.

This release keeps 65 nodes and 283 directed edges. It provides `LANDMARK_NORMAL`, `LANDMARK_FLOOD`, and `LANDMARK_CONGESTION` cost scenarios, plus the hard-closure scenario `LANDMARK_HARD_CLOSURE_DETOUR`. Flood and congestion each affect 57/283 edges (approximately 20 percent) and are labelled `ASSUMPTION` demonstrations, not live measurements.

Closure applies to exact landmark aggregate-edge IDs only; it does not propagate to other aggregate edges whose source segments or geometry overlap.
