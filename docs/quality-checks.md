# Quality checks

How the project is tested, how rebuilds are protected, what a code review changed, and what the dashboard checks covered.

## Automated checks

Every push to `main` runs these in GitHub Actions before the dashboard is deployed:

- **Formatting and lint:** `ruff format --check`, `ruff check` and Prettier keep the Python and dashboard code in one readable style.
- **Python tests (pytest):** small hand-checked fixtures for pagination, row validation, duplicates, grid edges, map projection, ranking ties, capture counts, the uncertainty model, exports, road context and the MCP tool limits.
- **JavaScript tests (node --test):** the dashboard's count filters, the method comparison lookup, road-manager labels and the council/state shortlists.
- **Full-data test:** one test reconciles the real snapshot (8,142 crashes, 3,407 serious crashes, 4,079 people killed or hospitalised). It runs only when the frozen data has been downloaded, so CI never fetches changing external data.

## How rebuilds are protected

The checks look at outputs, not at the code itself:

1. Every raw file must match its SHA-256 hash in the manifest, only manifest files are read, and the total row count must match.
2. The cleaned table must exactly equal a fresh derivation from those raw files.
3. `pipeline freeze` must reproduce `evidence/freeze.json` exactly: the DBSCAN settings chosen on 2023.
4. `pipeline evaluate` must reproduce `evidence/results.json` exactly: the 2024 result.
5. `scripts/verify_rebuild.py` copies the committed code and the v1.0.0 data archive into an empty folder, reruns every step and compares each dashboard data file byte for byte. The latest run is in `evidence/reproducibility.json`.

Any code change that alters a result fails step 3, 4 or 5. Version 1.0.0 also fingerprinted the source files, which added no protection beyond this and meant the code couldn't be reformatted. Version 1.1.0 removed it, reformatted the code and removed unused BigQuery client packages from `requirements.lock`. The frozen settings and the 2024 result came out identical.

## Fixes from code review

| Problem found | Fix |
|---|---|
| The cleaned Parquet file could change without the frozen settings noticing | Before any analysis, the pipeline rebuilds the table from the hashed raw pages and requires an exact match. |
| A rebuild could read page files that weren't in the manifest | Only manifest files are read. Extra, missing or duplicate pages, changed hashes and wrong row counts all stop the rebuild. |
| An upstream change that kept the row count the same could slip past the pagination checks | New downloads check the publisher's version metadata and compare two complete passes before saving anything. |
| Re-running the MCP tool evaluation could overwrite the original results | Reruns write new, uniquely named files to `evidence/ai/regressions/` and first check that the 30 cases and the documents match the originals. The original result files are never rewritten. |
| Crashes with missing coordinates were counted as boundary disagreements | They are now counted separately. This snapshot has none, so the published numbers didn't change. |
| Dashboard downloads could go stale | Every dashboard data file is exported in one validated step from the canonical results. |

None of these fixes changed a method, a setting, the 2024 test year or a result.

### Limits that remain

- The DBSCAN settings were frozen using 2023 before the 2024 evaluation (`evidence/freeze.json`, first recorded in private commit `43726a8`).
- The original download was a single pass. Its raw bytes, hashes and row counts are kept, but a second pass can't be done retroactively. Downloading again would create a new snapshot.
- The MCP tool score is 29/30 with a corrected scorer. The original 17/30 scoring is kept next to it (see [MCP tools](mcp-tools.md)).
- The road-manager breakdown and the area-concentration figures (`exports/roads.json`) were added after the 2024 evaluation. They describe the frozen shortlist and don't change it.

## Dashboard checks

**6 October 2026, version 1.1.0** (local copy of `site/`, Chrome):

- Default totals: 8,142 casualty crashes, 3,407 serious crashes, 4,079 people killed or hospitalised. 2024: 1,688 / 695 / 818. 2024 fatal: 17 / 17 / 27.
- Top 10, 20 and 40 squares caught 30, 55 and 82 of 695 serious crashes in 2024.
- Council-roads list, top 20: 40 of 384 council-road serious crashes in 2024 (the original list caught 24). State-roads list: 36 of 311 (original: 31).
- The road list, square count, crash-point and square selectors all update the map, table and summary. Table buttons select the matching square and highlight it on the map.
- At 375 px wide the page has no horizontal scroll. The selectors and table buttons give a keyboard route to every square without using the map.

**5 October 2026, before the street map:** every one of the 40 shortlist entries, 90 cluster choices and 30 year/severity combinations was checked against independent sums from the monthly CSV. All five downloads matched the canonical files byte for byte. A 1.5 px overflow on mobile was fixed.

Not covered: screen-reader testing and a full WCAG audit.

## Public copy

This repository is a cleaned public copy of the working project, and its history starts at the first public commit. Commit hashes in the evidence files (such as `43726a8`) refer to the private working history. The BigQuery SQL uses `YOUR_PROJECT_ID` instead of the real project ID, and account screenshots aren't published. The raw source data is in the [v1.0.0 release](https://github.com/milanshaji1/gold-coast-transport-evidence/releases/tag/v1.0.0), not in Git.
