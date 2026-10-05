"""One validated export of every downloadable evidence file."""

import json
from pathlib import Path

import pandas as pd


def strict_json(path):
    return json.loads(
        path.read_text(),
        parse_constant=lambda x: (_ for _ in ()).throw(ValueError("non-finite JSON")),
    )


MANAGER_NAMES = {"state": "State-controlled (TMR)", "council": "Council", "mixed": "Mixed"}


def shortlist_table(results, roads):
    """The downloadable shortlist: the frozen ranking plus road names and road manager."""
    rows = []
    for item in results["shortlist"]:
        cell = roads["cells"].get(item["cell_id"])
        if cell is None:
            raise ValueError(f"road context missing for {item['cell_id']}")
        rows.append(
            {
                "rank": item["rank"],
                "cell_id": item["cell_id"],
                "main_roads": " & ".join(cell["roads"]),
                "road_manager": MANAGER_NAMES[cell["manager"]],
                "suburbs": item["suburbs"],
                "serious_crashes_2021_2023": item["serious_count"],
                "serious_crashes_2024": item["holdout_serious_count"],
                "area_in_city_km2": round(item["clipped_area_km2"], 4),
            }
        )
    return pd.DataFrame(rows)


def export_site(source, target, manifest):
    source, target, manifest = Path(source), Path(target), Path(manifest)
    parsed = {
        name: strict_json(source / name)
        for name in [
            "results.json",
            "boundary.geojson",
            "shortlist.geojson",
            "clusters.geojson",
            "roads.json",
        ]
    }
    parsed["source-manifest.json"] = strict_json(manifest)
    result = parsed["results.json"]
    if parsed["clusters.geojson"].get("snapshot_id") != result["snapshot_id"]:
        raise ValueError("cluster export snapshot mismatch")
    if parsed["roads.json"].get("snapshot_id") != result["snapshot_id"]:
        raise ValueError("road export snapshot mismatch")
    if parsed["source-manifest.json"]["snapshot_id"] != result["snapshot_id"]:
        raise ValueError("export snapshot mismatch")
    validated = {
        name: json.dumps(content, allow_nan=False, separators=(",", ":")) + "\n"
        for name, content in parsed.items()
    }
    # Recreate CSVs from the same canonical result, never from stale copies.
    validated["monthly.csv"] = pd.DataFrame(result["monthly"]).to_csv(index=False)
    validated["shortlist.csv"] = shortlist_table(result, parsed["roads.json"]).to_csv(index=False)
    target.mkdir(parents=True, exist_ok=True)
    for name, content in validated.items():
        (target / name).write_text(content)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    export_site(root / "exports", root / "site/data", root / "evidence/source-manifest.json")
