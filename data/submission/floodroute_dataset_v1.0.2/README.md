# FloodRoute HCMC - dataset submission v1.0.2

This bundle contains the collected raw snapshot in `raw_collected/` and the
normalized routing data in `normalized/`.

The normalized graph keeps 65 landmark nodes and expands the topology to 283
directed aggregate road-path edges. Each landmark has up to four nearest outgoing
road-path alternatives, improving the chance of finding 2-3 detours after one edge
is blocked. The `ASSUMPTION` scenario `LANDMARK_HARD_CLOSURE_DETOUR` closes
`LM_EDGE_0001`.

Closures apply only to exact landmark aggregate-edge IDs. They do not propagate to
other aggregate edges with overlapping source segments or geometry. The snapshot is
historical, not real-time, and is intended for academic use only.
