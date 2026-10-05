"""Fail-closed source validation. Missing locations are retained, not guessed."""

import calendar
import json
import math

import pandas as pd

COUNT_FIELDS = [
    "Count_Casualty_Fatality",
    "Count_Casualty_Hospitalised",
    "Count_Casualty_MedicallyTreated",
    "Count_Casualty_MinorInjury",
    "Count_Casualty_Total",
]
REQUIRED = {
    "_id",
    "Crash_Ref_Number",
    "Crash_Year",
    "Crash_Month",
    "Crash_Severity",
    "Crash_Longitude",
    "Crash_Latitude",
    "Loc_Local_Government_Area",
    "Loc_Suburb",
    *COUNT_FIELDS,
}
SEVERITIES = {
    "Fatal",
    "Hospitalisation",
    "Medical treatment",
    "Minor injury",
    "Property damage only",
}


def collect_pages(fetch, limit=5000):
    if limit < 1:
        raise ValueError("positive limit required")
    records = []
    seen = set()
    total = None
    while total is None or len(records) < total:
        payload = fetch(len(records), limit)
        if not payload.get("success"):
            raise ValueError("upstream failure")
        result = payload["result"]
        if total is not None and total != result["total"]:
            raise ValueError("total changed during pagination")
        total = result["total"]
        if not isinstance(total, int) or total < 0:
            raise ValueError("invalid total")
        page = result["records"]
        if not page and len(records) < total:
            raise ValueError("premature empty page")
        for row in page:
            key = row["_id"]
            if key in seen:
                raise ValueError("repeated source key during pagination")
            seen.add(key)
        records.extend(page)
        if len(records) > total:
            raise ValueError("records exceed total")
    return records


def validate(rows):
    seen = {}
    clean = []
    quarantine = []
    duplicates = 0
    for row in rows:
        if not REQUIRED.issubset(row):
            raise ValueError(f"schema missing {sorted(REQUIRED - set(row))}")
        key = str(row["Crash_Ref_Number"])
        canonical = json.dumps({k: v for k, v in row.items() if k != "_id"}, sort_keys=True)
        if key in seen:
            if seen[key] != canonical:
                raise ValueError(f"source event collision {key}")
            duplicates += 1
            continue
        seen[key] = canonical
        try:
            if not key.strip():
                raise ValueError("missing event ID")
            if row["Loc_Local_Government_Area"] != "Gold Coast City":
                raise ValueError("wrong source jurisdiction")
            year = int(row["Crash_Year"])
            if not 2001 <= year <= 2026:
                raise ValueError("invalid year")
            month = list(calendar.month_name).index(row["Crash_Month"])
            if month == 0:
                raise ValueError("invalid month")
            severity = row["Crash_Severity"]
            if severity not in SEVERITIES:
                raise ValueError("invalid severity")
            counts = [int(row[k]) for k in COUNT_FIELDS]
            if min(counts) < 0 or sum(counts[:4]) != counts[4]:
                raise ValueError("casualties do not reconcile")
            lon_raw = row["Crash_Longitude"]
            lat_raw = row["Crash_Latitude"]
            missing = lon_raw in (None, "") or lat_raw in (None, "")
            lon = lat = None
            if not missing:
                lon, lat = float(lon_raw), float(lat_raw)
                if not (
                    math.isfinite(lon)
                    and math.isfinite(lat)
                    and 138 <= lon <= 154
                    and -30 <= lat <= -9
                ):
                    raise ValueError("coordinates outside Queensland bounds")
            clean.append(
                {
                    "crash_id": key,
                    "source_row_id": int(row["_id"]),
                    "year": year,
                    "month": month,
                    "severity": severity,
                    "serious": severity in ("Fatal", "Hospitalisation"),
                    "serious_casualties": counts[0] + counts[1],
                    "casualties": counts[4],
                    "fatalities": counts[0],
                    "hospitalised": counts[1],
                    "longitude": lon,
                    "latitude": lat,
                    "geocoded": not missing,
                    "suburb": row["Loc_Suburb"] or "Unknown",
                    "road": row.get("Crash_Street", "Unknown"),
                    "crash_type": row.get("Crash_Type", "Unknown"),
                    "lighting": row.get("Crash_Lighting_Condition", "Unknown"),
                    "road_surface": row.get("Crash_Road_Surface_Condition", "Unknown"),
                }
            )
        except (ValueError, TypeError) as exc:
            quarantine.append(
                {
                    "source_row_id": row["_id"],
                    "crash_id": key,
                    "reason": str(exc),
                    "raw": json.dumps(row, sort_keys=True),
                }
            )
    columns = [
        "crash_id",
        "source_row_id",
        "year",
        "month",
        "severity",
        "serious",
        "serious_casualties",
        "casualties",
        "fatalities",
        "hospitalised",
        "longitude",
        "latitude",
        "geocoded",
        "suburb",
        "road",
        "crash_type",
        "lighting",
        "road_surface",
    ]
    good = pd.DataFrame(clean, columns=columns)
    if len(good):
        for col in ["longitude", "latitude"]:
            good[col] = pd.to_numeric(good[col], errors="raise").astype(float)
    bad = pd.DataFrame(quarantine, columns=["source_row_id", "crash_id", "reason", "raw"])
    quality = {
        "source_rows": len(rows),
        "accepted_rows": len(good),
        "quarantined_rows": len(bad),
        "identical_duplicates": duplicates,
        "missing_coordinates": int((~good.geocoded).sum()) if len(good) else 0,
    }
    assert sum(
        quality[k] for k in ["accepted_rows", "quarantined_rows", "identical_duplicates"]
    ) == len(rows)
    return good, bad, quality
