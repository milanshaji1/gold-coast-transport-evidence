"""One event per fact, one calendar month per dimension row, one suburb per location."""

from pathlib import Path

import duckdb


def build_warehouse(frame, path):
    with duckdb.connect(str(path)) as con:
        con.register("input_crashes", frame)
        con.execute((Path(__file__).resolve().parents[2] / "sql/schema.sql").read_text())
        totals = con.execute("SELECT count(*),sum(serious_casualties) FROM fact_crash").fetchone()
        return {
            "crashes": totals[0],
            "serious_casualties": totals[1] or 0,
            "months": con.execute("SELECT count(*) FROM dim_month").fetchone()[0],
            "locations": con.execute("SELECT count(*) FROM dim_location").fetchone()[0],
        }
