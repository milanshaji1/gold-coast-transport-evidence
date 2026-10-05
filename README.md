# Gold Coast serious crash hotspots

**[Open the dashboard](https://milanshaji.com/gold-coast-transport-evidence/)** · [Read the decision brief](https://milanshaji.com/gold-coast-transport-evidence/decision-brief.html) · [Download the data release](https://github.com/milanshaji1/gold-coast-transport-evidence/releases/tag/v1.0.0)

![Dashboard showing the top 20 crash squares on a Gold Coast street map](evidence/platforms/dashboard-desktop.jpg)

## The question

If the City of Gold Coast could only investigate a handful of places for road safety, where should it start?

## What I did

- Took every police-reported casualty crash on the Gold Coast from 2020 to 2024: **8,142 crashes**, from Queensland Government open data.
- Split the city into 500 m squares and ranked them by **serious crashes** (someone killed or hospitalised) in 2021–2023.
- Kept 2024 aside and checked how many of that year's serious crashes happened inside the top-ranked squares.
- Tested whether DBSCAN clustering builds a better shortlist than simple counts. Its settings were chosen using 2023, so 2024 stayed unseen.
- Added each square's main roads and who manages them (council or state), using fields in the same crash records.

## What I found

- **A small area holds a lot of the harm.** The top 20 squares cover 0.35% of the city but held **55 of 695** serious crashes in 2024 (7.9%). If crashes were spread evenly by area, that space would hold about 2.4, so the shortlist catches about 23 times its share.
- **Clustering didn't help.** DBSCAN caught 54 of 695. The difference is too small to matter, so the simpler count method stays.
- **Most hotspots are on state roads.** 14 of the top 20 squares are mostly on state-controlled roads, nine of them on the Pacific Motorway (M1). TMR manages those, not the City. A separate council-roads shortlist caught **40 of 384** serious crashes on council roads in 2024, against 24 for the combined list. (This split was added after the 2024 check, so it doesn't change the original result.)
- **Limits.** Most serious crashes still happen outside any shortlist, and without traffic volumes the counts can't say which road is riskiest per trip.

**Next step:** send the state-road hotspots to TMR. For the council list, add traffic volumes and road layout so sites can be compared by risk per trip, then inspect the top sites on the ground.

## Tools

Python (pandas, GeoPandas, scikit-learn, SciPy), DuckDB and SQL, BigQuery for an independent spatial check, Power BI, and a static dashboard (JavaScript and Leaflet, hosted on GitHub Pages). A small read-only [MCP server](docs/mcp-tools.md) also lets AI tools query the results.

## How it works

1. **Download and freeze the data** (`acquire.py`). Every source file is saved with a SHA-256 hash so the analysis always uses the same bytes.
2. **Validate** (`ingest.py`). Rows with bad years, severities, casualty totals or coordinates are set aside with a reason, never silently fixed. All 45,266 rows passed. The clean data also goes into a small DuckDB star schema (`sql/schema.sql`).
3. **Build the grid** (`spatial.py`). Coordinates are converted to metres (GDA2020 / MGA zone 56) and each crash is placed in a fixed 500 m square.
4. **Rank and compare** (`analysis.py`, `pipeline.py`). DBSCAN settings are chosen on 2020–2022 → 2023, frozen, then both methods are refitted on 2021–2023 and scored on 2024.
5. **Check uncertainty** (`evaluate.py`). A Gamma-Poisson model was tried and rejected: 85% of squares have no serious crashes, so its intervals say little about any single site.
6. **Add road context** (`roads.py`) and **export the dashboard data** (`exports.py`).

More detail: [methods](docs/methods.md) · [data sources](docs/sources.md) · [Power BI and BigQuery](docs/platforms.md) · [quality checks](docs/quality-checks.md) · [full results](evidence/results.json)

## Run it yourself

You need Python 3.12+ and Node.js 24+.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pytest -q
node --test site/metrics.test.js
```

To rebuild every result from the original data, download `transport-inputs-8c293a52745057c4.tar.gz` from the [release](https://github.com/milanshaji1/gold-coast-transport-evidence/releases/tag/v1.0.0), check its SHA-256 against `evidence/release.json`, then:

```sh
tar -xzf transport-inputs-8c293a52745057c4.tar.gz data/raw
export PYTHONPATH=src
.venv/bin/python -m transport.acquire "$(cat evidence/snapshot-path.txt)"
.venv/bin/python -m transport.pipeline freeze
.venv/bin/python -m transport.pipeline evaluate
.venv/bin/python -m transport.map_layers
.venv/bin/python -m transport.roads
.venv/bin/python -m transport.exports
.venv/bin/python -m http.server 8765 --bind 127.0.0.1 --directory site
```

Then open http://127.0.0.1:8765. The rebuild reproduces the published files exactly. Running `transport.acquire` with no argument downloads fresh data into a new snapshot; the frozen checks will reject it rather than quietly replace the 2024 result.

## Repository layout

| Folder | Contents |
|---|---|
| `src/transport/` | The pipeline, analysis, road context and MCP server |
| `tests/` | Python tests with small hand-checked fixtures |
| `sql/` | DuckDB schema and the BigQuery reconciliation query |
| `site/` | The dashboard (static HTML, CSS and JavaScript) and its data |
| `exports/` | Analysis outputs and the BigQuery/Power BI reload pack |
| `evidence/` | Frozen settings, results, data quality and rebuild records |
| `docs/` | Methods, sources, decision brief and quality checks |

## Data and licence

Crash and boundary data © State of Queensland, used under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Source links and hashes are in `evidence/source-manifest.json`. This is an independent project, not commissioned or endorsed by the City of Gold Coast or TMR.

Built by [Milan Shaji](https://milanshaji.com), with AI coding assistance.
