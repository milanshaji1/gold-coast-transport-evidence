CREATE OR REPLACE TABLE dim_month AS
SELECT DISTINCT year*100+month AS month_id, year, month FROM input_crashes;
ALTER TABLE dim_month ADD PRIMARY KEY (month_id);
CREATE OR REPLACE TABLE dim_location AS
SELECT row_number() OVER (ORDER BY suburb) AS location_id, suburb
FROM (SELECT DISTINCT suburb FROM input_crashes);
ALTER TABLE dim_location ADD PRIMARY KEY (location_id);
CREATE OR REPLACE TABLE fact_crash AS
SELECT c.* EXCLUDE (suburb), m.month_id, l.location_id
FROM input_crashes c
JOIN dim_month m ON c.year=m.year AND c.month=m.month
JOIN dim_location l ON c.suburb=l.suburb;
ALTER TABLE fact_crash ADD PRIMARY KEY (crash_id);
CREATE OR REPLACE VIEW monthly_patterns AS
SELECT m.year,m.month,count(*) AS crashes,sum(CASE WHEN serious THEN 1 ELSE 0 END) AS serious_crashes,
       sum(serious_casualties) AS serious_casualties,
       lag(count(*)) OVER (ORDER BY m.year,m.month) AS previous_observed_month_crashes
FROM fact_crash f JOIN dim_month m USING(month_id)
GROUP BY m.year,m.month;
