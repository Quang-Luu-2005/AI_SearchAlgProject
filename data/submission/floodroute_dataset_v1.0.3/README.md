# FloodRoute HCMC - dataset submission v1.0.3

The normalized graph contains 65 landmark nodes and 283 directed aggregate road-path
edges. It provides four fixed cost scenarios: `LANDMARK_NORMAL`, `LANDMARK_FLOOD`,
`LANDMARK_CONGESTION`, and `LANDMARK_HARD_CLOSURE_DETOUR`.

Flood and congestion overrides are labelled `ASSUMPTION` demonstrations, not live
measurements. The frontend also provides a dynamic random scenario that returns the
affected edges for display. Closure applies only to exact landmark edge IDs.
