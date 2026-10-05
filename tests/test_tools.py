import pytest

from transport.tools import EvidenceTools


@pytest.fixture
def tools():
    return EvidenceTools(
        {
            "snapshot_id": "fixture",
            "monthly": [
                {
                    "year": 2022,
                    "month": 1,
                    "severity": "Hospitalisation",
                    "crashes": 2,
                    "serious_crashes": 2,
                    "serious_casualties": 3,
                }
            ],
            "shortlist": [{"cell_id": "1_2", "rank": 1, "serious_count": 2}],
            "quality": {"analysis_crashes": 2},
        },
        [],
    )


def test_numeric_answer_uses_canonical_metrics(tools):
    r = tools.aggregate_stats(2022, 2022)
    assert r["crashes"] == 2 and r["serious_casualties"] == 3 and r["snapshot_id"] == "fixture"


@pytest.mark.parametrize(
    "args",
    [(2019, 2022), (2024, 2020), (2020, 2025), (True, 2022), (2020, 2021, "All; DROP TABLE x")],
)
def test_bad_periods_and_sql_strings_rejected(tools, args):
    with pytest.raises(ValueError):
        tools.aggregate_stats(*args)


def test_area_identifiers_cannot_be_sql_or_paths(tools):
    assert tools.inspect_area("1_2")["area"]["rank"] == 1
    for v in ["' OR 1=1", "../../secret", "999_999"]:
        with pytest.raises(ValueError):
            tools.inspect_area(v)


def test_empty_period_returns_zero_with_explicit_empty_state(tools):
    r = tools.aggregate_stats(2024, 2024)
    assert r["crashes"] == 0 and r["status"] == "no_records"
