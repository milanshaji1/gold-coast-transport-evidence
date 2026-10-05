# Website click audit — 5 October 2026

Every interactive control and link now has a working action in the tested desktop Chrome preview.

| Element | Check |
|---|---|
| Six navigation links | Reached the intended page section or top |
| Three expandable sections | Opened, closed and restored |
| All 40 shortlist buttons | Selected the matching area, highlighted its map cell and showed the correct training/2024 counts |
| All 40 map cells and 40 area options | Changed from a different selected cell and updated the matching details/highlight |
| All 90 cluster choices | Showed the expected point count and labels, including all points, noise and every individual cluster |
| Three investigation budgets | Showed 10/20/40 cells and rows with 30/55/82 of 695 captured events |
| All 30 year/severity combinations | Matched independent sums from the canonical monthly CSV |
| Five evidence downloads | Shortlist CSV, monthly CSV, cluster GeoJSON, source manifest JSON and full evaluation JSON downloaded; all matched canonical bytes |
| Two official source links | Opened the correct Queensland Government dataset pages |
| Decision brief and its two return links | Opened the full readable brief; returned to the dashboard or shortlist |

## Repairs

The brief's original Markdown link and the two raw JSON links led to Chrome's ERR_BLOCKED_BY_CLIENT page. The brief now opens as HTML, generated from the canonical document, and the JSON links explicitly download their files. No browser security setting was changed; the specific client rule was not identified.

The evaluation download label wrapped across two lines. Its bounding-box centre hit the paragraph between the lines, so an automated mouse click missed the anchor. Source links now use inline-block layout. The next mouse click downloaded the evaluation successfully. Keyboard activation was also checked.

The HTML brief's text and every table value match the canonical Markdown after normalising whitespace around inline code. Regenerate it with `python3 scripts/render_brief.py` after editing `docs/decision-brief.md`.

49 Python tests and both Node tests passed. JavaScript syntax and whitespace checks passed. The existing joblib physical-core fallback warning remains. The analytical inputs, freeze and results were not changed.

A browser check was interrupted and its in-memory detailed journal was lost; this report summarises the completed checks recorded in tool outputs. The separately saved 80 map/area transition checks remain available. Final default: 20 cells, all years/severities, point layer off. This is a desktop Chrome audit, not a claim covering every device or accessibility technology.
