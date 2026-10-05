# Sources and reproducibility

Frozen snapshot `8c293a52745057c4`, retrieved 5 October 2026 AEST. Raw responses and hashes are in the local data/raw directory; `evidence/source-manifest.json` records every URL, retrieval time and hash. Source identifiers are release-specific.

- Queensland Department of Transport and Main Roads: [Crash data](https://www.data.qld.gov.au/dataset/crash-data-from-queensland-roads), resource e88943c0-5968-4972-a15f-38e120d72ec0. CC BY 4.0. Exact source LGA filter `Gold Coast City`. GDA2020 EPSG:7844.
- Queensland Government: [Local government boundaries](https://www.data.qld.gov.au/dataset/local-government-area-boundaries-queensland), CC BY 4.0. Official AdministrativeBoundaries MapServer layer 1, case-sensitive label `Gold Coast City`, code 3430. Service native EPSG:3857; requested explicit EPSG:7844 response and retain its declared spatialReference.

All 45,266 historical source rows accepted; no key duplicates, invalid rows or missing coordinates. Main 2020–2024 subset: 1,514 / 1,672 / 1,626 / 1,642 / 1,688 records respectively; each has all 12 months. 2025 has six months and is excluded from comparative results. Publisher coverage through June 2025 and reported nonfatal detail availability through July 2025 support using 2024 as the latest full year. Completeness is assessed, not guaranteed: police reporting omissions and later revisions remain possible. Source notes say recent 12 months are preliminary. Property-damage-only recording stopped after 2010.

This is a current revised source snapshot temporal holdout, not an historical as-of backtest. Pandemic-related changes in exposure are not controlled. Boundary vintage is current and may disagree with historical source jurisdiction.

Rebuild frozen data: `PYTHONPATH=src .venv/bin/python -m transport.acquire $(cat evidence/snapshot-path.txt)`.
Refresh upstream into a NEW timestamped raw folder: `PYTHONPATH=src .venv/bin/python -m transport.acquire`. Refresh invalidates analytical freeze and requires a new evaluation release; never silently replace published results.

Local release packaging will include exact permitted raw inputs, source manifest and these attributions. Do not commit the large raw dataset to Git. Failed incomplete acquisitions have no manifest and are not analysis inputs.
