# Verified cloud reload pack

Snapshot `8c293a52745057c4`, verified 5 October 2026. Data © State of Queensland, used under CC BY 4.0. This independent analysis does not imply City or TMR endorsement. Exact source provenance is included in the project's source manifest and frozen input release.

These are the exact public CSVs used in the executed account checks. They contain no user credentials.

1. In the existing BigQuery sandbox, use dataset `transport_evidence` in `australia-southeast1`. Check whether each table still exists before uploading; the dataset's observed default expiry is 60 days.
2. Create missing `monthly`, `events` and `cells` tables from the matching CSV. Paste its `*-schema.json` into **Edit as text**, skip one header row, and leave allowed errors at zero. Do not enable billing, streaming or a trial.
3. Run `verified-spatial-reconciliation.sql`. Replace `YOUR_PROJECT_ID` consistently with your own authorised project ID. The public SQL preserves the executed query structure; its account identifier is omitted. Expected result is retained in `spatial-result.txt` and `platform-verification.json`.

The dashboard's shortlist download is `site/data/shortlist.csv`; it was not loaded as a cloud table. `power-query-import.m` is the actual typed Power Query import expression captured from the saved Power BI monthly model. That report used the supported paste/manual-entry web route.

`events.csv` has 8,142 2020–2024 casualty crash events. Coordinates were explicitly transformed from the verified local EPSG:7856 frame to EPSG:4326. `cells.csv` has all 5,774 fixed grid squares and separate in-boundary area metadata. WKT serialisation rounds geographic coordinates to six decimal places; the executed geography join agreed uniquely for every actual snapshot point. The local metre-based half-open assignment remains the analytical definition.

The `load-manifest.json` hashes identify the exact loaded files. Preserve this pack when cloud tables expire. The main project README explains rebuilding the canonical local analysis from its frozen raw input release; do not reacquire current upstream bytes and call them the same historical release.
