-- Prepared; not yet executed against the transport dataset.
-- Upload exports/monthly.csv as monthly and exports/shortlist.csv as shortlist.
-- Dataset location: australia-southeast1. Use sandbox; do not enable billing.
-- Expected exact result: 8142 / 3407 / 4079.
SELECT SUM(crashes) AS casualty_crashes,
       SUM(serious_crashes) AS serious_crashes,
       SUM(serious_casualties) AS serious_casualties
FROM `YOUR_PROJECT_ID.transport_evidence.monthly`
WHERE year BETWEEN 2020 AND 2024;

-- Grain and window calculation: one year/month after summing severity categories.
WITH monthly AS (
  SELECT year, month, SUM(crashes) AS crashes
  FROM `YOUR_PROJECT_ID.transport_evidence.monthly`
  GROUP BY year, month
)
SELECT *, LAG(crashes) OVER (ORDER BY year, month) AS preceding_month_crashes
FROM monthly ORDER BY year, month;

-- This is the already-executed spatial smoke query, not a source-data spatial join.
SELECT ST_DISTANCE(ST_GEOGPOINT(153.4, -28.0),
                   ST_GEOGPOINT(153.4, -28.001)) AS metres,
       2 AS fixture_crashes;
