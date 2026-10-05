import pytest

from transport.ingest import collect_pages, validate
from transport.warehouse import build_warehouse


def row(id=1, **changes):
    r = {
        "_id": id,
        "Crash_Ref_Number": str(id),
        "Crash_Year": "2022",
        "Crash_Month": "January",
        "Crash_Severity": "Hospitalisation",
        "Crash_Longitude": "153.4",
        "Crash_Latitude": "-28",
        "Loc_Local_Government_Area": "Gold Coast City",
        "Loc_Suburb": "TEST",
        "Count_Casualty_Fatality": "0",
        "Count_Casualty_Hospitalised": "2",
        "Count_Casualty_MedicallyTreated": "0",
        "Count_Casualty_MinorInjury": "0",
        "Count_Casualty_Total": "2",
    }
    return r | changes


def test_pagination_collects_short_final_page():
    records = [row(i) for i in range(1, 4)]
    assert (
        len(
            collect_pages(
                lambda o, n: {
                    "success": True,
                    "result": {"total": 3, "records": records[o : o + n]},
                },
                2,
            )
        )
        == 3
    )


@pytest.mark.parametrize(
    "pages",
    [
        [{"total": 3, "records": [row(1), row(2)]}, {"total": 4, "records": [row(3)]}],
        [{"total": 3, "records": [row(1), row(2)]}, {"total": 3, "records": [row(2)]}],
        [{"total": 3, "records": [row(1), row(2)]}, {"total": 3, "records": []}],
    ],
)
def test_pagination_rejects_mutation_repetition_or_early_end(pages):
    with pytest.raises(ValueError):
        collect_pages(lambda o, n: {"success": True, "result": pages[o // 2]}, 2)


def test_missing_coordinates_retained_and_distinct_events_not_deduplicated_by_position():
    good, bad, q = validate([row(1), row(2), row(3, Crash_Longitude="", Crash_Latitude="")])
    assert len(good) == 3 and len(bad) == 0
    assert good.serious_casualties.sum() == 6 and good.geocoded.sum() == 2


@pytest.mark.parametrize(
    "change",
    [
        {"Count_Casualty_Total": "-1"},
        {"Count_Casualty_Total": "7"},
        {"Crash_Severity": "Surprise"},
        {"Crash_Month": "Smarch"},
        {"Crash_Longitude": "-28", "Crash_Latitude": "153.4"},
        {"Count_Casualty_Hospitalised": "1.5"},
    ],
)
def test_invalid_rows_quarantined(change):
    good, bad, q = validate([row(**change)])
    assert len(good) == 0 and len(bad) == 1 and bad.iloc[0]["reason"]


def test_schema_drift_fails_closed():
    r = row()
    del r["Crash_Year"]
    with pytest.raises(ValueError, match="schema"):
        validate([r])


def test_identical_event_duplicate_removed_but_collision_rejected():
    good, bad, q = validate([row(), row()])
    assert len(good) == 1 and q["identical_duplicates"] == 1
    with pytest.raises(ValueError, match="collision"):
        validate([row(), row(Crash_Year="2023")])


def test_warehouse_grains_and_people_reconcile(tmp_path):
    frame, _, _ = validate([row(1), row(2)])
    result = build_warehouse(frame, tmp_path / "test.duckdb")
    assert result["crashes"] == 2 and result["serious_casualties"] == 4
    assert result["months"] == 1 and result["locations"] == 1
