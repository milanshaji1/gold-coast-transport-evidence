import geopandas as gpd
import pytest
from shapely.geometry import Point, box

from transport.analysis import capture, rank_cells
from transport.spatial import locate, make_grid


def test_distinct_events_at_same_coordinate_count_for_density_and_ties_stable():
    grid = make_grid(gpd.GeoDataFrame(geometry=[box(0, 0, 1000, 1000)], crs=7856))
    pts = locate(
        gpd.GeoDataFrame(
            {"crash_id": ["a", "b", "c"], "serious": [True] * 3},
            geometry=[Point(10, 10), Point(10, 10), Point(600, 600)],
            crs=7856,
        ),
        grid,
    )
    r = rank_cells(pts, grid, 100, 2)
    assert r.cell_id.tolist() == ["0_0", "1_1", "0_1", "1_0"]
    assert r.density_count.tolist() == [2, 0, 0, 0]
    assert r.serious_count.tolist() == [2, 1, 0, 0]
    assert len(r.head(4)) == 4
    assert capture(r, pts, 4)["numerator"] == 3
    with pytest.raises(ValueError):
        capture(r, pts, 5)
