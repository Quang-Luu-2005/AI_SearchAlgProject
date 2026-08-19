# Changelog

## [Unreleased]

- Streamlined the report around the Lab 1 rubric: removed the internal requirement-mapping table, shortened dataset/provenance and A* exposition, moved fixture context to experiments, removed the duplicate UCS screenshot, and simplified usage instructions.
- Added compact algorithm and A*/UCS result tables so the space is used for direct experimental evidence instead of engineering documentation.
- Added a deterministic route-explanation benchmark with selected/alternative route costs, edge breakdowns, closure handling, and UCS/A* validation for the report.
- Added a student-style Chapter 8 comparison for peak traffic and heavy rain, plus a compact algorithm guarantee table and toy graph figure.
- Fixed the Chapter 5 algorithm-comparison table by using wrapped fixed-width columns, preventing text from collapsing into a narrow vertical strip.
- Revised report wording to use a natural student-report voice while retaining technical terms, formulas, benchmark values, and conclusions.
- Added a captured local GUI map image and an in-report system-flow diagram to the FloodRoute LaTeX report.
- Added captured GUI states for A*, UCS, six-algorithm comparison, and a five-stop Held-Karp/Nearest Neighbor tour.

- Rewrote the LaTeX FloodRoute HCMC report in Vietnamese with an editable XeLaTeX source, a HomeWork_2-style cover, and a repository-local HCMUS logo asset.
- Synced the report scope to the active 65-landmark map and current artifacts: 1,200 search runs and 15 A* lower-bound validation cases.
- Documented the scenario-aware lower-bound heuristic, provenance labels, cost profiles, architecture, multi-location optimization, limitations, and reproducible build commands.
- Preserved the active cost-profile and lower-bound contracts: BALANCED, PEAK_TRAFFIC, RAIN_SAFE, closed edges as hard constraints, and SIMULATED/ASSUMPTION labels for fixtures.

See `docs/progress/` for task-level evidence.
