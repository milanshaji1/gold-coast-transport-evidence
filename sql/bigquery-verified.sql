WITH e AS (
 SELECT *, ST_GEOGPOINT(longitude_wgs84,latitude_wgs84) AS point
 FROM `YOUR_PROJECT_ID.transport_evidence.events`
), c AS (
 SELECT *, SAFE.ST_GEOGFROMTEXT(geometry_wkt) AS cell
 FROM `YOUR_PROJECT_ID.transport_evidence.cells`
), spatial_matches AS (
 SELECT e.crash_id,e.cell_id AS assigned_cell,c.cell_id AS spatial_cell,e.year,e.serious
 FROM e JOIN c ON ST_COVERS(c.cell,e.point)
), per_crash AS (
 SELECT crash_id,COUNT(*) AS matches,COUNTIF(assigned_cell=spatial_cell) AS correct
 FROM spatial_matches GROUP BY crash_id
), monthly_from_events AS (
 SELECT year,month,severity,COUNT(*) AS crashes,COUNTIF(serious) AS serious_crashes,SUM(serious_casualties) AS serious_casualties
 FROM e GROUP BY year,month,severity
), monthly_compare AS (
 SELECT COALESCE(a.year,b.year) AS year
 FROM monthly_from_events a FULL JOIN `YOUR_PROJECT_ID.transport_evidence.monthly` b USING(year,month,severity)
 WHERE a.crashes IS DISTINCT FROM b.crashes OR a.serious_crashes IS DISTINCT FROM b.serious_crashes OR a.serious_casualties IS DISTINCT FROM b.serious_casualties
), training_counts AS (
 SELECT c.cell_id,COUNTIF(e.serious AND e.year BETWEEN 2021 AND 2023) AS train_serious
 FROM c LEFT JOIN e USING(cell_id) GROUP BY c.cell_id
), ranked AS (
 SELECT *,ROW_NUMBER() OVER(ORDER BY train_serious DESC,cell_id ASC) AS rank FROM training_counts
)
SELECT (SELECT COUNT(*) FROM e) AS crash_events,
 (SELECT COUNT(DISTINCT crash_id) FROM e) AS unique_events,
 (SELECT COUNTIF(serious) FROM e) AS serious_crash_events,
 (SELECT SUM(serious_casualties) FROM e) AS serious_casualties,
 (SELECT COUNT(*) FROM c) AS grid_cells,
 (SELECT COUNT(DISTINCT cell_id) FROM c) AS unique_cells,
 (SELECT COUNTIF(cell IS NULL) FROM c) AS invalid_cell_geometries,
 (SELECT COUNT(*) FROM per_crash) AS spatially_matched_events,
 (SELECT COUNTIF(matches!=1 OR correct!=1) FROM per_crash) AS spatial_assignment_mismatches,
 (SELECT COUNT(*) FROM monthly_compare) AS monthly_grain_mismatches,
 (SELECT COUNT(*) FROM spatial_matches s JOIN ranked r ON s.spatial_cell=r.cell_id WHERE s.serious AND s.year=2024 AND r.rank<=20) AS heldout_serious_in_top20,
 (SELECT COUNTIF(serious AND year=2024) FROM e) AS heldout_serious_denominator,
 (SELECT COUNT(DISTINCT snapshot_id) FROM e) AS event_snapshots,
 (SELECT MIN(snapshot_id) FROM e) AS snapshot_id;
