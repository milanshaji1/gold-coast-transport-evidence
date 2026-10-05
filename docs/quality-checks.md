# Quality checks

How the project is tested, what a code review changed, and what the dashboard checks covered.

## Automated tests

Every push to `main` runs the Python and JavaScript tests in GitHub Actions before the dashboard is deployed.

- **Python (pytest):** small hand-checked fixtures for pagination, row validation, duplicates, grid edges, map projection, ranking ties, capture counts, the uncertainty model, exports, road context and the MCP tool limits.
- **JavaScript (node --test):** the dashboard's count filters, the method comparison lookup, road-manager labels and the council/state shortlists.
- **Full-data test:** one test reconciles the real snapshot (8,142 crashes, 3,407 serious crashes, 4,079 people killed or hospitalised). It runs only when the frozen data has been downloaded, so CI never fetches changing external data.

## Clean rebuild

`scripts/verify_rebuild.py` copies the committed code and the v1.0.0 data archive into an empty folder, reruns every pipeline step, and checks that the results and every dashboard data file match the committed versions byte for byte. The latest run is recorded in `evidence/reproducibility.json`.

## Fixes from code review

| Problem found | Fix |
|---|---|
| The cleaned Parquet file could change without the frozen settings noticing | Before any analysis, the pipeline rebuilds the table from the hashed raw pages and requires an exact match. `evidence/analysis-integrity.json` also fingerprints the analysis code, dependency lock and source manifest. |
| A rebuild could read page files that weren't in the manifest | Only manifest files are read. Extra, missing or duplicate pages, changed hashes and wrong row counts all stop the rebuild. |
| An upstream change that kept the row count the same could slip past the pagination checks | New downloads check the publisher's version metadata and compare two complete passes before saving anything. |
| Re-running the MCP tool evaluation could overwrite the original results | Reruns write new, uniquely named files to `evidence/ai/regressions/`. The original result files are hash-checked and never rewritten. |
| Crashes with missing coordinates were counted as boundary disagreements | They are now counted separately. This snapshot has none, so the published numbers didn't change. |
| Dashboard downloads could go stale | Every dashboard data file is exported in one validated step from the canonical results. |

None of these fixes changed a method, a setting, the 2024 test year or a result.

### Limits that remain

- The DBSCAN settings were frozen using 2023 before the 2024 evaluation (`evidence/freeze.json`, first recorded in private commit `43726a8`). The integrity record was added after that evaluation, so it protects later rebuilds rather than proving the original run.
- The original download was a single pass. Its raw bytes, hashes and row counts are kept, but a second pass can't be done retroactively. Downloading again would create a new snapshot.
- The MCP tool score is 29/30 with a corrected scorer. The original 17/30 scoring is kept next to it (see [MCP tools](mcp-tools.md)).
- The road-manager breakdown and the area-concentration figures (`exports/roads.json`) were added after the 2024 evaluation. They describe the frozen shortlist and don't change it.

## Dashboard checks

**6 October 2026, after adding the street map and road names** (local copy of `site/`, Chrome):

- Default totals: 8,142 casualty crashes, 3,407 serious crashes, 4,079 people killed or hospitalised. 2024: 1,688 / 695 / 818. 2024 fatal: 17 / 17 / 27.
- Top 10, 20 and 40 squares caught 30, 55 and 82 of 695 serious crashes in 2024.
- Council-roads list, top 20: 40 of 384 council-road serious crashes in 2024 (the original list caught 24). State-roads list: 36 of 311 (original: 31).
- The road list, square count, crash-point and square selectors all update the map, table and summary. Table buttons select the matching square and highlight it on the map.
- At 375 px wide the page has no horizontal scroll. The selectors and table buttons give a keyboard route to every square without using the map.

**5 October 2026, before the map change:** every one of the 40 shortlist entries, 90 cluster choices and 30 year/severity combinations was checked against independent sums from the monthly CSV. All five downloads matched the canonical files byte for byte. A 1.5 px overflow on mobile was fixed.

Not covered: screen-reader testing and a full WCAG audit.

## Public copy

This repository is a cleaned public copy of the working project, and its history starts at the first public commit. Commit hashes mentioned in evidence files (such as `43726a8`) refer to the private working history. The BigQuery SQL uses `YOUR_PROJECT_ID` instead of the real project ID, and account screenshots aren't published. The raw source data is in the [v1.0.0 release](https://github.com/milanshaji1/gold-coast-transport-evidence/releases/tag/v1.0.0), not in Git.
