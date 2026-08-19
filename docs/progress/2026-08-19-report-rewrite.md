# Report rewrite and cover update

## Scope

- Replaced the LaTeX report chapters with a Vietnamese report aligned to the Lab 1 requirements.
- Added editable metadata macros in `docs/reports/main.tex`.
- Replaced the cover with the requested HCMUS layout and copied the logo to `docs/reports/figures/logo-khtn.png`.
- Synced claims to the active 65-landmark dataset and current benchmark artifacts.

## Evidence

- `npm run test:data`: PASS; active map is 65 selectable landmarks and no 90-node processed map.
- `npm run test:backend`: 89 passed.
- `npm run test:frontend`: 53 passed.
- `npm run benchmark:search`: 10 OD pairs, 6 algorithms, 20 repetitions, 1,200 measured runs.
- `npm run benchmark:lower-bound`: 15 cases, zero A*/UCS cost mismatch, A* explored no more nodes than UCS in 15/15 cases.
- `npm run benchmark:cost-profiles`: PASS; three profiles and two route examples generated.
- XeLaTeX compiled `docs/reports/main.tex` twice successfully; output is 10 pages.
- First two PDF pages were rendered and visually checked for cover, logo, headers, and table of contents.
- Captured the running local React/MapLibre GUI with the active 65-node map and added it to the architecture chapter, together with a TikZ system-flow diagram. Rendered pages containing both figures were checked visually.
- Captured four additional local GUI states: A*, UCS, Compare all six algorithms, and five-stop tour optimization; inserted them into the experiments chapter and verified the final 14-page PDF.
- Revised the prose to sound like a student report written for the instructor: first-person group wording, clearer explanations, and fewer unexplained engineering-style English phrases. Final XeLaTeX build is 17 pages.
- Fixed the Chapter 5 table layout with wrapped columns; the table now fits the page and was visually checked after rebuilding.
