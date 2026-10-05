"""Road names, road authority and area concentration for the published shortlist.

Added after the 2024 evaluation. It reads the same verified snapshot and frozen
results, and never changes the original ranking or its held-out score.
"""

import json
from pathlib import Path

import pandas as pd

from transport.acquire import dump, read_snapshot
from transport.pipeline import load

AUTHORITY = {"State-controlled": "state", "Locally-controlled": "council"}
TRAIN = (2021, 2023)
HOLDOUT = 2024


def road_fields(rows):
    """Source fields that validation does not keep: street names and controlling authority."""
    f = pd.DataFrame(rows)
    return pd.DataFrame(
        {
            "crash_id": f.Crash_Ref_Number.astype(str),
            "street": f.Crash_Street.fillna("").str.strip(),
            "cross_street": f.Crash_Street_Intersecting.fillna("").str.strip(),
            "state_road": f.State_Road_Name.fillna("").str.strip(),
            "authority": f.Crash_Controlling_Authority.map(AUTHORITY).fillna("not_coded"),
        }
    )


def rank_counts(events, k):
    counts = (
        events.dropna(subset=["cell_id"]).groupby("cell_id").size().rename("count").reset_index()
    )
    return (
        counts.sort_values(["count", "cell_id"], ascending=[False, True]).head(k).cell_id.tolist()
    )


def most_common(values, n):
    counts = values[values != ""].value_counts()
    return [name for name, _ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]]


def cell_context(events):
    """Most-mentioned roads and the authority share for one cell's training serious crashes."""
    share = {a: int((events.authority == a).sum()) for a in ("state", "council", "not_coded")}
    coded = share["state"] + share["council"]
    state_share = share["state"] / coded if coded else None
    label = (
        "mixed"
        if state_share is None or 1 / 3 < state_share < 2 / 3
        else ("state" if state_share >= 2 / 3 else "council")
    )
    state_road = most_common(events.state_road, 1)
    return {
        "roads": most_common(pd.concat([events.street, events.cross_street]), 2),
        "state_road": state_road[0] if state_road else None,
        "suburbs": most_common(events.suburb, 2),
        "events": len(events),
        "authority_counts": share,
        "manager": label,
    }


def authority_split(events):
    counts = events.authority.value_counts()
    state, council = int(counts.get("state", 0)), int(counts.get("council", 0))
    return {
        "state": state,
        "council": council,
        "not_coded": int(counts.get("not_coded", 0)),
        "state_share": state / (state + council) if state + council else None,
    }


def road_context(points, grid, results, k=20, budgets=(10, 20, 40)):
    serious = points[points.serious & points.geocoded]
    train = serious[serious.year.between(*TRAIN)]
    test = serious[serious.year == HOLDOUT]
    total_area = float(grid.clipped_area_km2.sum())
    concentration = []
    for row in (r for r in results["evaluation"] if r["method"] == "count"):
        share = row["clipped_area_km2"] / total_area
        concentration.append(
            {
                "k": row["k"],
                "area_km2": row["clipped_area_km2"],
                "area_share_pct": 100 * share,
                "capture_pct": row["capture_pct"],
                "times_city_average": row["capture_pct"] / (100 * share),
                "expected_if_spread_by_area": row["denominator"] * share,
            }
        )
    combined = [s["cell_id"] for s in results["shortlist"]]
    by_manager = []
    for authority in ("council", "state"):
        own_train = train[train.authority == authority]
        own_test = test[test.authority == authority]
        own = rank_counts(own_train, max(budgets))
        by_manager.append(
            {
                "manager": authority,
                "holdout_serious": len(own_test),
                "budgets": [
                    {
                        "k": b,
                        "captured_by_combined_shortlist": int(
                            own_test.cell_id.isin(combined[:b]).sum()
                        ),
                        "captured_by_own_shortlist": int(own_test.cell_id.isin(own[:b]).sum()),
                    }
                    for b in budgets
                ],
                "own_shortlist": [
                    {
                        "rank": i + 1,
                        "cell_id": c,
                        "training_serious": int((own_train.cell_id == c).sum()),
                        "holdout_serious": int((own_test.cell_id == c).sum()),
                    }
                    for i, c in enumerate(own)
                ],
            }
        )
    listed = set(combined).union(*({r["cell_id"] for r in m["own_shortlist"]} for m in by_manager))
    shapes = grid[grid.cell_id.isin(listed)].to_crs(4326).set_index("cell_id").geometry
    cells = {
        c: cell_context(train[train.cell_id == c])
        | {
            "clipped_area_km2": float(grid.set_index("cell_id").clipped_area_km2[c]),
            "outline": [[round(x, 6), round(y, 6)] for x, y in shapes[c].exterior.coords],
        }
        for c in sorted(listed)
    }
    top = combined[:k]
    return {
        "snapshot_id": results["snapshot_id"],
        "k": k,
        "training_years": list(TRAIN),
        "holdout_year": HOLDOUT,
        "note": "Added after the 2024 evaluation. Describes the frozen shortlist; it was not used to choose it.",
        "total_area_km2": total_area,
        "concentration": concentration,
        "managers": {
            "citywide_training": authority_split(train),
            "shortlist_training": authority_split(train[train.cell_id.isin(top)]),
            "shortlist_cells": {
                m: sum(cells[c]["manager"] == m for c in top) for m in ("state", "council", "mixed")
            },
        },
        "by_manager": by_manager,
        "cells": cells,
    }


def export_roads(root):
    pts, grid, _, _ = load(root)
    raw = root / Path((root / "evidence/snapshot-path.txt").read_text().strip())
    _, rows = read_snapshot(raw)
    fields = road_fields(rows)
    if fields.crash_id.duplicated().any():
        raise ValueError("duplicate event key")
    joined = pts.merge(fields, on="crash_id", how="left", validate="one_to_one")
    if joined.authority.isna().any():
        raise ValueError("road fields missing for analysed events")
    results = json.loads((root / "evidence/results.json").read_text())
    context = road_context(joined, grid, results)
    dump(root / "exports/roads.json", context)
    return context


if __name__ == "__main__":
    c = export_roads(Path(__file__).resolve().parents[2])
    print(
        {
            "concentration": c["concentration"][1],
            "managers": c["managers"],
            "by_manager": [
                {
                    "manager": m["manager"],
                    "holdout_serious": m["holdout_serious"],
                    "budgets": m["budgets"],
                }
                for m in c["by_manager"]
            ],
        }
    )
