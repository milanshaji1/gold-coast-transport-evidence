"""Presentation-only labels for the already selected training-period DBSCAN fit."""

import json
from pathlib import Path

import numpy as np
from sklearn.cluster import DBSCAN

from transport.acquire import dump
from transport.pipeline import load


def training_clusters(points, eps, min_samples):
    if points.crs.to_epsg() != 7856:
        raise ValueError("projected metres required")
    p = points[points.year.between(2021, 2023) & points.serious].copy()
    p = p[p.geometry.notna() & ~p.geometry.is_empty].copy()
    p = p[np.isfinite(p.geometry.x) & np.isfinite(p.geometry.y)].copy()
    if p.crash_id.duplicated().any():
        raise ValueError("duplicate event key")
    p["cluster"] = (
        DBSCAN(eps=eps, min_samples=min_samples).fit_predict(
            np.column_stack([p.geometry.x, p.geometry.y])
        )
        if len(p)
        else np.array([], dtype=int)
    )
    spans = []
    for label, group in p[p.cluster >= 0].groupby("cluster"):
        bounds = group.total_bounds
        spans.append(
            {
                "cluster": int(label),
                "events": len(group),
                "bounding_box_diagonal_m": float(
                    np.hypot(bounds[2] - bounds[0], bounds[3] - bounds[1])
                ),
            }
        )
    summary = {"noise_events": int((p.cluster == -1).sum()), "clusters": spans}
    geo = json.loads(
        p[["year", "cell_id", "suburb", "cluster", "geometry"]]
        .to_crs(4326)
        .to_json(drop_id=True, na="null")
    )
    return geo, summary


def export_clusters(root):
    pts, _, _, _ = load(root)
    frozen = json.loads((root / "evidence/freeze.json").read_text())
    result = json.loads((root / "evidence/results.json").read_text())
    geo, summary = training_clusters(pts, **frozen["selected"])
    if summary != result["clusters"]:
        raise ValueError("presentation clusters differ from frozen evaluation")
    geo["snapshot_id"] = result["snapshot_id"]
    geo["period"] = [2021, 2023]
    geo["method"] = (
        "DBSCAN training serious events; noise=-1; overlapping points remain distinct events"
    )
    dump(root / "exports/clusters.geojson", geo)
    return {
        "mapped_events": len(geo["features"]),
        "clusters": len(summary["clusters"]),
        "noise_events": summary["noise_events"],
    }


if __name__ == "__main__":
    print(export_clusters(Path(__file__).resolve().parents[2]))
