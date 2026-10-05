import geopandas as gpd
import pandas as pd
from shapely.geometry import box

from transport.roads import road_context, road_fields
from transport.spatial import make_grid


def events(rows):
    frame = pd.DataFrame(
        rows,
        columns=[
            "crash_id",
            "year",
            "serious",
            "geocoded",
            "cell_id",
            "authority",
            "street",
            "cross_street",
            "state_road",
        ],
    )
    return frame.assign(
        suburb=[
            "Helensvale",
            "Helensvale",
            "Oxenford",
            "Southport",
            "Southport",
            "Helensvale",
            "Southport",
            "Southport",
            "Southport",
        ]
    )


def fixture():
    grid = make_grid(gpd.GeoDataFrame(geometry=[box(530000, 6900000, 531000, 6901000)], crs=7856))
    pts = events(
        [
            [
                "a",
                2021,
                True,
                True,
                "1060_13800",
                "state",
                "Pacific Hwy",
                "Hope Island Rd",
                "Pacific Highway (Pacific Motorway)",
            ],
            [
                "b",
                2022,
                True,
                True,
                "1060_13800",
                "state",
                "Pacific Hwy",
                "",
                "Pacific Highway (Pacific Motorway)",
            ],
            ["c", 2023, True, True, "1060_13800", "council", "Hope Island Rd", "", ""],
            ["d", 2022, True, True, "1061_13800", "council", "Marine Pde", "", ""],
            ["e", 2023, True, True, "1061_13800", "council", "Marine Pde", "", ""],
            ["f", 2024, True, True, "1060_13800", "state", "Pacific Hwy", "", ""],
            ["g", 2024, True, True, "1061_13800", "council", "Marine Pde", "", ""],
            ["h", 2024, True, True, "1061_13801", "council", "Nind St", "", ""],
            ["i", 2020, True, True, "1061_13801", "council", "Nind St", "", ""],
        ]
    )
    results = {
        "snapshot_id": "fixture",
        "shortlist": [{"cell_id": "1060_13800"}, {"cell_id": "1061_13800"}],
        "evaluation": [
            {
                "method": "count",
                "k": 1,
                "clipped_area_km2": 0.25,
                "capture_pct": 100 / 3,
                "denominator": 3,
            },
            {
                "method": "density",
                "k": 1,
                "clipped_area_km2": 0.25,
                "capture_pct": 0,
                "denominator": 3,
            },
        ],
    }
    return pts, grid, results


def test_cells_name_roads_and_manager_from_training_serious_events_only():
    pts, grid, results = fixture()
    cell = road_context(pts, grid, results, k=1, budgets=(1, 2))["cells"]["1060_13800"]
    assert cell["roads"] == ["Hope Island Rd", "Pacific Hwy"]
    assert cell["state_road"] == "Pacific Highway (Pacific Motorway)"
    assert cell["authority_counts"] == {"state": 2, "council": 1, "not_coded": 0}
    assert cell["manager"] == "state" and cell["events"] == 3
    assert cell["suburbs"] == ["Helensvale", "Oxenford"]
    assert len(cell["outline"]) == 5


def test_concentration_compares_capture_with_area_share():
    pts, grid, results = fixture()
    c = road_context(pts, grid, results, k=1, budgets=(1, 2))
    assert c["total_area_km2"] == 1
    assert len(c["concentration"]) == 1
    assert round(c["concentration"][0]["times_city_average"], 6) == round((100 / 3) / 25, 6)


def test_each_manager_gets_its_own_ranking_and_holdout_denominator():
    pts, grid, results = fixture()
    council = road_context(pts, grid, results, k=1, budgets=(1, 2))["by_manager"][0]
    assert council["manager"] == "council" and council["holdout_serious"] == 2
    assert [(r["cell_id"], r["training_serious"]) for r in council["own_shortlist"]] == [
        ("1061_13800", 2),
        ("1060_13800", 1),
    ]
    assert council["budgets"][0] == {
        "k": 1,
        "captured_by_combined_shortlist": 0,
        "captured_by_own_shortlist": 1,
    }


def test_source_authority_labels_are_normalised():
    rows = [
        {
            "Crash_Ref_Number": 1,
            "Crash_Street": "A St ",
            "Crash_Street_Intersecting": None,
            "State_Road_Name": None,
            "Crash_Controlling_Authority": "Locally-controlled",
        },
        {
            "Crash_Ref_Number": 2,
            "Crash_Street": "B Rd",
            "Crash_Street_Intersecting": "A St",
            "State_Road_Name": "Road",
            "Crash_Controlling_Authority": "Not coded",
        },
    ]
    f = road_fields(rows)
    assert f.crash_id.tolist() == ["1", "2"] and f.street.tolist() == ["A St", "B Rd"]
    assert f.authority.tolist() == ["council", "not_coded"]
