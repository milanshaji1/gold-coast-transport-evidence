# Power BI and BigQuery execution evidence

Both integrations were run and checked on 5 October 2026 against data snapshot `8c293a52745057c4`. The records below describe that run; the private accounts are not kept online permanently.

## Power BI

A saved descriptive report imports 223 monthly rows with explicit types and year/severity filters. All-year totals were 8,142 casualty crashes, 3,407 serious crash events and 4,079 serious casualties. The 2024 view gave 1,688 / 695 / 818. Fatal-severity totals were 81 / 81 / 117. Event counts and people counts are labelled separately.

The report uses one aggregate table and implicit sums. No custom DAX measure, relationships or Power BI map are claimed. The public dashboard is a separate implementation of the same validated data. The private report and account screenshots are not published.

## BigQuery

Three sandbox tables held 223 monthly rows, 8,142 events and 5,774 cells in the Sydney region. The executed spatial join matched every event to exactly one cell with zero assignment mismatches. Monthly reaggregation also had zero mismatches, and SQL reproduced the top-20 result of 55 / 695 serious events in 2024.

[Public execution record](../evidence/platforms/platform-verification.json) · [SQL with account ID replaced](../sql/bigquery-verified.sql) · [CSV and schema reload pack](../exports/cloud/README.md)

The sandbox's observed expiry was 60 days. Preserved CSVs and SQL support reload into an authorised project. Geographic WKT approximates the transformed full grid; every snapshot point agreed with the local metre-based assignment.

## Public evidence scope

The public execution record leaves out account and job IDs but keeps the counts and query timings. Account screenshots are kept private. The dashboard and all analysis results can be checked without account access.
