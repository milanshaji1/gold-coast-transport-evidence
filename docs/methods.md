# Analytical contract

See `design.md`, `sources.md`, `evidence/freeze.json` and the code. Projection is GDA2020 geographic → GDA2020/MGA zone 56. Grid origin (0,0) is independent of outcomes. Cells are half-open for unique membership and included only for positive intersection area with the boundary. Capture uses whole cells, while clipped area is reported separately.

Distinct events at identical coordinates remain separate observations. Event IDs are unique within a snapshot, not across source revisions. The database has one crash fact per event, one month row per year/month and one location row per suburb; key joins are many-to-one. Coordinates may be null and remain in descriptive totals, excluded only from geocoded capture denominators. Quarantines retain source rows and reasons.

DBSCAN uses eps 100/250/500 m and min_samples 5/10. The validation-selected setting is 250 m / 5 events; neighbourhood distance does not cap cluster span. Selection uses 2023 capture at K=20, ties smaller eps then larger min_samples. Ranking is density count, total serious count, then stable cell ID. Baseline ranks count then ID. Equal budgets include zero-score cells if necessary. Baseline zero-density fields are not a DBSCAN diagnostic.

Gamma-Poisson empirical Bayes uses training mean and variance; positive overdispersion estimates a shared Gamma prior. Prediction is negative binomial for the following year. Diagnostics include all cells and the subset with training events. The conservative rejection rule is >80% training-zero cells or <80% coverage among training-active cells. It is a project interpretation rule, not a formal goodness-of-fit test. Discrete central nominal-90% intervals can exceed 90% empirical coverage; high coverage does not prove calibration. No formal road-network exposure or stationarity test is available.

The model settings and count rankings were frozen before 2024 performance was inspected. Rebuilds verify immutable source hashes, grid contract and result equality. A refreshed source needs a new release, not reuse of the old holdout. Current revisions prevent historical as-of performance claims.

## Reproduction safeguards added after independent review

The pipeline now compares curated contents exactly with a fresh derivation from manifested raw pages before analysis, and verifies a separate code/configuration/source-manifest integrity record. This record was added after the original holdout run; the original parameter freeze and results remain unchanged. Future acquisition compares two full sorted passes and resource version metadata, but the original download was single-pass. Neither process claims a publisher-provided transactional snapshot. See `review-resolution.md` for the historical limitations and tests.
