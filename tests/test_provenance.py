"""Cross-layer protection of frozen source, derivation and evaluation evidence."""

import asyncio
import hashlib
import json

import pandas as pd
import pytest
from test_ingest import row

from transport import acquire, eval_tools, pipeline
from transport.ingest import validate


def snapshot(tmp_path):
    raw = tmp_path / "data/raw/fixture"
    raw.mkdir(parents=True)
    payload = {"success": True, "result": {"total": 1, "records": [row()]}}
    page = raw / "crashes_000000.json"
    page.write_text(json.dumps(payload))
    digest = hashlib.sha256(page.read_bytes()).hexdigest()
    manifest = {
        "sources": [{"file": page.name, "sha256": digest}],
        "row_count": 1,
        "snapshot_id": hashlib.sha256(digest.encode()).hexdigest()[:16],
    }
    (raw / "manifest.json").write_text(json.dumps(manifest))
    (tmp_path / "evidence").mkdir()
    (tmp_path / "data/curated").mkdir()
    (tmp_path / "evidence/snapshot-path.txt").write_text("data/raw/fixture")
    return raw, manifest


def test_rebuild_rejects_extra_unmanifested_page(tmp_path):
    raw, _ = snapshot(tmp_path)
    (raw / "crashes_000001.json").write_text(
        json.dumps({"success": True, "result": {"total": 2, "records": [row(2)]}})
    )
    with pytest.raises(ValueError, match="unmanifested"):
        acquire.rebuild(tmp_path, raw)


def test_rebuild_reconciles_manifest_row_count(tmp_path):
    raw, m = snapshot(tmp_path)
    m["row_count"] = 2
    (raw / "manifest.json").write_text(json.dumps(m))
    with pytest.raises(ValueError, match="row count"):
        acquire.rebuild(tmp_path, raw)


def test_pipeline_rejects_changed_curated_year_before_spatial_analysis(tmp_path):
    raw, _ = snapshot(tmp_path)
    import geopandas as gpd
    from shapely.geometry import box

    gpd.GeoDataFrame(geometry=[box(153.39, -28.01, 153.41, -27.99)], crs=7844).to_file(
        raw / "boundary.json", driver="GeoJSON"
    )
    good, _, _ = validate([row()])
    good.loc[0, "year"] = 2024
    good.to_parquet(tmp_path / "data/curated/crashes.parquet")
    with pytest.raises(ValueError, match="curated data"):
        pipeline.load(tmp_path)


def test_acquisition_checks_version_and_second_pass_content():
    before = {
        "id": acquire.RESOURCE,
        "last_modified": "2026-10-01",
        "hash": "abc",
        "metadata_modified": "today",
    }
    acquire.verify_resource_version(before, before)
    for changed in [
        dict(before, hash="def"),
        dict(before, metadata_modified="tomorrow"),
        {"id": acquire.RESOURCE},
    ]:
        with pytest.raises(ValueError):
            acquire.verify_resource_version(before, changed)
    with pytest.raises(ValueError):
        acquire.verify_resource_version({"id": acquire.RESOURCE}, {"id": acquire.RESOURCE})
    # A same-size replacement can evade unique-ID and total checks in one pass.
    with pytest.raises(ValueError, match="content changed"):
        acquire.verify_page_content([row(1), row(3)], [row(1), row(2)])


def tool_freeze_fixture(root):
    for name in eval_tools.FROZEN_INPUTS:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("[]" if name.endswith("final-tool-cases.json") else "{}")
    frozen = {
        name: hashlib.sha256((root / name).read_bytes()).hexdigest()
        for name in eval_tools.FROZEN_INPUTS
    }
    (root / "evidence/ai/system-freeze.json").write_text(json.dumps(frozen))
    (root / "evidence/ai/final-tool-results.json").write_text('{"passed": 29}')


@pytest.mark.parametrize(
    "target", ["data/corpus/documents.json", "evidence/ai/final-tool-cases.json"]
)
def test_tool_evaluation_rejects_changed_frozen_inputs_before_any_tool_call(
    tmp_path, monkeypatch, target
):
    tool_freeze_fixture(tmp_path)
    (tmp_path / target).write_text("[{}]")

    async def forbidden(*args):
        pytest.fail("tool invoked before freeze verification")

    monkeypatch.setattr(eval_tools, "call_tools", forbidden)
    with pytest.raises(ValueError, match=target):
        asyncio.run(eval_tools.evaluate(tmp_path))


def test_evaluation_preserves_original_final_report(tmp_path):
    tool_freeze_fixture(tmp_path)
    final = tmp_path / "evidence/ai/final-tool-results.json"
    original = final.read_bytes()
    report = asyncio.run(eval_tools.evaluate(tmp_path))
    assert report["evaluation_kind"].startswith("regression replay")
    assert final.read_bytes() == original
    assert len(list((tmp_path / "evidence/ai/regressions").glob("*.json"))) == 1


def test_evaluation_rejects_incomplete_freeze(tmp_path):
    tool_freeze_fixture(tmp_path)
    (tmp_path / "evidence/ai/system-freeze.json").write_text("{}")
    with pytest.raises(ValueError, match="freeze"):
        asyncio.run(eval_tools.evaluate(tmp_path))


def test_missing_location_is_not_reported_as_boundary_disagreement():
    f = pd.DataFrame(
        {
            "geocoded": [False, True, True],
            "serious": [True, True, True],
            "within_current_boundary": [False, False, True],
            "cell_id": [None, None, "1_2"],
        }
    )
    assert pipeline.spatial_quality(f) == {
        "missing_coordinates": 1,
        "outside_current_boundary": 1,
        "serious_outside_current_boundary": 1,
        "serious_outside_grid": 1,
    }


def test_acquire_rejects_constant_total_content_replacement(tmp_path, monkeypatch):
    calls = 0

    def download(url):
        nonlocal calls
        if "package_show" in url:
            payload = {
                "result": {
                    "resources": [
                        {"id": acquire.RESOURCE, "last_modified": "2026-10-01", "hash": "same"}
                    ]
                }
            }
        elif "datastore_search" in url:
            calls += 1
            payload = {
                "success": True,
                "result": {"total": 2, "records": [row(1), row(3 if calls == 1 else 2)]},
            }
        else:
            pytest.fail("acquisition continued after inconsistent content")
        return json.dumps(payload).encode()

    monkeypatch.setattr(acquire, "download", download)
    with pytest.raises(ValueError, match="content changed"):
        acquire.acquire(tmp_path)
    assert not list((tmp_path / "data/raw").glob("*/manifest.json"))
