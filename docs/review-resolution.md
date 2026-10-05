# Independent review and resolution — 5 October 2026

A fresh GPT-6 Astra review covered `fac8733..aa53001`. It found no critical issues, four important provenance/evaluation issues and two minor presentation/quality issues. The fixes below preserve the original analytical and MCP results. No method, selected parameter, holdout period or retrieval threshold was retuned.

| Finding | Resolution and evidence |
|---|---|
| Curated Parquet could change under an unchanged analytical freeze | Before any spatial analysis, recreate the typed frame from verified, manifested source pages and require exact equality. A separate integrity record binds source manifest, transformation/analysis code, dependency lock and historical parameter freeze. A changed-year pipeline test and changed-implementation test reject alterations. |
| Rebuild ingested unmanifested pages | Read only explicit manifest members; reject extra page files, missing/unused offsets, duplicate manifest names, changed hashes/identity and inconsistent totals/manifest row counts. Reproducing extra-page and count tests now pass. |
| Constant-size upstream changes could escape pagination checks | Future acquisition requires usable version metadata, compares ID, hash, last-modified and metadata-modified, and compares two complete sorted content passes before writing a manifest. A constant-total replacement test fails closed. This mitigates drift; the publisher provides no transactional snapshot token. |
| Tool evaluation could overwrite original final evidence | Verify the original runtime/corpus/case hashes plus an explicit scorer amendment. Preserve both original scoring and corrected final artifacts. All reruns append uniquely named regression artifacts. Changed corpus/cases and original-report preservation tests pass. |
| Missing geometry counted as spatial disagreement | Count missing coordinates separately; boundary/grid disagreement requires a geocoded event. Fixture tests distinguish the categories. Current real-data counts are unchanged. |
| Site evidence downloads could become stale | Export every linked JSON/GeoJSON/CSV and the source manifest in one prevalidated operation. Derive both CSVs directly from canonical results and enforce snapshot agreement. |

## Historical limits and decisions

The original pre-holdout parameter freeze remains unchanged in commit `43726a8`. `evidence/analysis-integrity.json` was added **after** the holdout had been evaluated; it protects subsequent reproduction and must not be presented as an original pre-holdout code/data hash record. The original source download was a single pass. Its stable metadata, exact raw bytes, row reconciliation and hashes are retained; a second pass was not performed retroactively. Reacquiring now would be a new snapshot and would not repair historical provenance.

The original MCP system freeze includes modules not used by the MCP runtime. The replay verifies the four relevant client/server/tool/retrieval modules and corpus/cases against that original freeze. The scorer and result bytes are bound by `scorer-amendment.json`; its date and explanation explicitly identify a post-evaluation amendment. The original 17/30 result and corrected 29/30 result remain separate. The sole T29 retrieval failure is retained. Replay results are regression evidence, not a new held-out reliability estimate.

## Scope decisions at the previous review — superseded by the continuation below

- Live model answers, agent tool selection, generated citations and generation-wide deadlines remain deferred by the user. Cost: no completed live LLM/RAG/agent claim.
- At that review, final Power BI/BigQuery integrations and desktop/mobile/keyboard/console verification were pending browser access. Smoke checks could not substitute for final integration acceptance. The verified continuation below resolves those account and focused browser checks.
- Deployment, logged-out hosted access, walkthrough recording and personal-contribution claims remain separate delivery/verification steps. Cost: the local project is not yet a published, user-demonstrated portfolio artifact.
- T29 is disclosed rather than tuned away after final evaluation. Cost: the small tool benchmark remains 29/30.
- Gamma-Poisson interpretation remains rejected because of structural-zero/exposure limitations. Cost: no road-site uncertainty recommendation or ranking improvement claim.
- Baseline zero-density counts remain inapplicable diagnostics, as documented. Cost: explain the field if discussing raw outputs.
- The scorer-only field-name correction is retained with original responses and an amendment. Cost: always identify the reported result as corrected scoring.

No finding from that review was silently deferred. Browser/account work was then an open acceptance item; completion of those local review fixes did not mark the overall project complete.

## Approved presentation scope completion

After the review fixes, the final design check found the required labelled DBSCAN point layer was absent. Added a presentation-only export of the already selected 2021–2023 fit, with an exact check against the frozen cluster summary: 2,086 training serious crash events, 87 clusters and 1,109 noise events. A fixture confirms held-out and non-serious records are excluded and distinct events at identical coordinates remain present. The local map now offers optional labelled points and an accessible cluster summary table. No parameter tuning or changes to historical analytical/tool results occurred. At that stage, browser visual and keyboard inspection was pending; the UI addition had syntax and data tests. The continuation below subsequently inspected the browser presentation and retained screenshots.

## Fresh-chat platform and visual continuation

The browser/account acceptance items above were resolved on 5 October through normal fresh-chat access: actual Power BI report, BigQuery monthly/event/grid batch tables, real spatial/window SQL and exact reconciliation. Desktop/mobile and focused keyboard/download QA are recorded in docs/browser-qa.md, including a corrected mobile overflow, an unverified native-select arrow-key automation path and earlier console message-channel errors. No analytical parameters, core implementation, original freeze or held-out results changed. Live AI and publication/contribution steps remain separate. The original single-pass and post-holdout amendment caveats still apply.

## Independent continuation review

A fresh read-only GPT-6 Astra review of `b029144..fe17fcd`, the accepted design/plan, prior review resolutions and saved execution evidence found no critical or important defects. Its one minor finding was stale present-tense pending wording above; those passages are now explicitly historical. The full verdict is retained in [continuation-review.md](../evidence/platforms/continuation-review.md). The reviewer checked reload hashes/types, decoded Power Query rows, event/monthly agreement, deterministic ranking, independent WKT membership and all six screenshots. It did not reopen accounts or certify live AI, public delivery, screen-reader conformance or personal implementation mastery.
