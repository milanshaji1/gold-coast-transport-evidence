# Website copy edit — 5 October 2026

Applied the avoid-ai-writing skill in edit mode, using a plain technical voice. Reviewed the dashboard, its generated labels and the linked decision brief. Data files, calculations and controls were kept intact.

The edits remove vague self-praise, repeated contrast formulas, a three-part slogan and the generic footer. Technical explanations now name the period, measure or action. Necessary limits remain explicit. The decision brief also distinguishes crash events from casualty people.

## Before and after

- `site/index.html:1`
  - Before: Independent Gold Coast road-safety investigation shortlist, with reproducible crash analysis and honest model comparisons.
  - After: Gold Coast road-safety investigation shortlist using Queensland crash data, a fixed 500 m grid and a 2024 evaluation.
- `site/index.html:3`
  - Before: A transparent shortlist of places to examine, with the evidence—and limitations—visible.
  - After: Explore 500 m grid cells ranked by serious crashes in 2021–2023, then check the shortlist against 2024.
- `site/index.html:3`
  - Before: The density-based comparator did not improve the primary held-out result. Investigate the context of these locations before proposing any road treatment.
  - After: At 20 cells, the count shortlist captured 55 serious crashes in 2024; clustering captured 54. Check local road conditions before proposing a treatment.
- `site/index.html:7`
  - Before: Schematic geographic view without a street basemap. Cells show investigation areas, not road-segment risk. Optional points use only 2021–2023 serious crashes; separate events at identical coordinates overlap. Cluster colours repeat; point labels identify each cluster.
  - After: Each square is an investigation area. The map has no street basemap or road-level risk estimates. Optional points show 2021–2023 serious crashes. Events at the same coordinates overlap. Cluster colours repeat; labels identify each cluster.
- `site/index.html:7`
  - Before: Most subsequent serious crashes occurred outside this shortlist. Counts are not risk per trip.
  - After: Most serious crashes in 2024 occurred outside the shortlist. Traffic-volume data would be needed to estimate risk per trip.
- `site/index.html:8`
  - Before: Accessible shortlist table and source export
  - After: Shortlist table and CSV
- `site/index.html:8`
  - Before: Accessible cluster evidence
  - After: Cluster counts and extent
- `site/index.html:9`
  - Before: Same fixed grid, same area budget, same untouched year.
  - After: Both methods use the same grid and number of cells. The comparison uses 2024, which was held out when choosing settings.
- `site/index.html:9`
  - Before: Settings selected using 2023 only, then refitted on 2021–2023. The differences are small; they do not establish model superiority.
  - After: Settings were chosen using 2023 results, then the methods were fitted again on 2021–2023 data. The small differences in 2024 do not establish that either method is better.
- `site/index.html:10`
  - Before: <h3>Descriptive counts</h3>
  - After: <h3>Crash counts by year and severity</h3>
- `site/index.html:10`
  - Before: These filters change descriptive counts only. The frozen shortlist and held-out comparison above remain unchanged.
  - After: These filters affect the counts below. They do not change the shortlist or its 2024 evaluation.
- `site/index.html:11`
  - Before: Police-reported casualty crashes only. 2025 is excluded because the source has only six months. Current revised source data cannot recreate what an analyst knew in each historical year.
  - After: The data covers police-reported casualty crashes. The snapshot includes only six months of 2025, so that year is excluded. Later source revisions mean these records may differ from those available to analysts at the time.
- `site/index.html:11`
  - Before: The current boundary may differ from source jurisdiction. All geocoded source-LGA serious crashes stay in the evaluation denominator.
  - After: The source's Gold Coast classification can differ from the current boundary. The evaluation includes every serious crash with coordinates that the source assigns to the Gold Coast.
- `site/index.html:11`
  - Before: Common-prior smoothing preserves count order. This is a documented experiment, not a ranking improvement.
  - After: Smoothing each count with the same prior leaves the ranking unchanged.
- `site/index.html:11`
  - Before: Real read-only MCP tools and lexical retrieval are implemented. Live AI is pending. A saved Power BI report and BigQuery batch/spatial reconciliation are verified against this frozen snapshot.
  - After: Four read-only tools use MCP (Model Context Protocol) to return data and search documents. A live AI model is still pending. The Power BI report and BigQuery spatial queries were checked against this data snapshot.
- `site/index.html:12`
  - Before: No traffic-volume denominator, causal inference or promised crash reduction. Engineering review and local context are essential.
  - After: Traffic volumes are not included, so the counts cannot measure risk per trip. Choosing a road treatment would also require an engineering assessment; this study does not estimate causes or crash reductions.
- `site/index.html:12`
  - Before: Built to make the decision—and its uncertainty—inspectable.
  - After: Independent analysis of Queensland Government crash data.
- `site/app.js:18`
  - Before: Suburbs name nearby source records. This is a fixed analysis cell, not a street or an intersection.
  - After: Suburb names come from nearby crash records. Each entry covers a fixed 500 m grid cell.
- `site/app.js:23`
  - Before: 2024 serious crashes captured (${b.capture_pct.toFixed(2)}%).
  - After: 2024 serious crashes within the selected cells (${b.capture_pct.toFixed(2)}%).
- `site/app.js:32`
  - Before: % of training cells have zero serious crashes. The Gamma-Poisson model was rejected for site-specific decision support because empty municipal land dominates the population.
  - After: % of grid cells had no serious crashes in the training period. The Gamma-Poisson model pools road and non-road land. Its overall interval coverage was not enough to support decisions about individual sites.
- `docs/decision-brief.md:3`
  - Before: **Recommendation:** Use a transparent 20-cell serious-crash-count shortlist as a starting point for further investigation. Do not claim that density clustering improves it or that these are the highest-risk roads.
  - After: Start with the 20-cell count shortlist. Clustering did not improve capture at this budget, and the data cannot identify the highest-risk roads per trip.
- `docs/decision-brief.md:5`
  - Before: The 2020–2024 source contains **8,142 casualty crashes**, including **3,407 serious crashes** and **4,079 serious casualties**. These are different units.
  - After: The 2020–2024 source contains 8,142 casualty crashes, including 3,407 serious crash events and 4,079 serious casualties. Serious crashes are events classified as Fatal or Hospitalisation; serious casualties are people killed or hospitalised.
- `docs/decision-brief.md:12`
  - Before: At the primary budget, clustering captured one fewer serious crash. Differences are small and do not support superiority claims.
  - After: At 20 cells, clustering captured one fewer serious crash. The small differences across all three budgets do not establish that either method is better.
- `docs/decision-brief.md:12`
  - Before: This is a dispersed problem: most subsequent serious crashes occurred outside the shortlist.
  - After: Most serious crashes in 2024 occurred outside the shortlist.
- `docs/decision-brief.md:14`
  - Before: The Bayesian experiment is retained as a **rejected decision-support extension**. 84.85% of training grid cells have zero serious crashes; pooling road and non-road land makes apparently high overall interval coverage an inadequate basis for site-specific confidence. Common-prior smoothing cannot change the ranking. Report the diagnostic results, not an invented improvement.
  - After: The Gamma-Poisson experiment was rejected for decisions about individual sites. In the training period, 84.85% of grid cells had no serious crashes. Pooling road and non-road land can give high overall interval coverage without reliable estimates for individual sites. Using the same prior for every cell also leaves the ranking unchanged.

The five decision-brief edits also appear in `site/decision-brief.md`, which is kept identical to `docs/decision-brief.md`.

## Second pass

Re-read the edited copy for unsupported emphasis, repetitive sentence patterns and loss of technical meaning. Kept the opening question because it states the study’s purpose. Kept precise technical terms in the methods and cluster table, the necessary event/person distinction, and the limits on causal and per-trip-risk claims. No authorship or detector-evasion claim is made.

## Verification

JavaScript syntax and both existing Node tests passed. The freeze, results and every site data file are byte-identical to the preceding commit. The linked and canonical decision briefs match. Browser checks confirmed the revised static and dynamic text, the 2024 totals (1,688 / 695 / 818), and 40-cell capture (82/695). Desktop width was 1,470 px; the 375 px mobile view had no horizontal overflow. Screenshots were visually inspected. A versioned script URL ensures the browser loads the updated generated text. The original 49-test Python run and independent review were not rerun for this wording change.
