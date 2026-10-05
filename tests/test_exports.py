import json
from pathlib import Path
import pandas as pd
import pytest
from transport.exports import export_site


def test_export_preserves_canonical_counts_and_rejects_nan(tmp_path):
    source=tmp_path/'source'; source.mkdir()
    (source/'results.json').write_text(json.dumps({'snapshot_id':'test','monthly':[{'crashes':7}],'shortlist':[{'cell_id':'1_2'}]}))
    for f in ['boundary.geojson','shortlist.geojson']: (source/f).write_text('{"type":"FeatureCollection","features":[]}')
    (source/'clusters.geojson').write_text('{"type":"FeatureCollection","features":[],"snapshot_id":"test"}')
    (source/'roads.json').write_text('{"snapshot_id":"test","cells":{}}')
    manifest=tmp_path/'manifest.json'; manifest.write_text('{"snapshot_id":"test"}')
    export_site(source,tmp_path/'web',manifest)
    assert json.loads((tmp_path/'web/results.json').read_text())['monthly'][0]['crashes']==7
    assert pd.read_csv(tmp_path/'web/monthly.csv').crashes.sum()==7
    assert pd.read_csv(tmp_path/'web/shortlist.csv').cell_id.tolist()==['1_2']
    assert json.loads((tmp_path/'web/source-manifest.json').read_text())['snapshot_id']=='test'
    (source/'results.json').write_text('{"x": NaN}')
    with pytest.raises(ValueError): export_site(source,tmp_path/'bad',manifest)

def test_real_snapshot_exports_reconcile_with_independent_curated_event_counts():
    root=Path(__file__).resolve().parents[1]
    if not (root/'data/curated/crashes.parquet').exists(): pytest.skip('full snapshot integration; fixtures run in CI')
    f=pd.read_parquet(root/'data/curated/crashes.parquet'); f=f[f.year.between(2020,2024)]
    csv=pd.read_csv(root/'exports/monthly.csv'); r=json.loads((root/'evidence/results.json').read_text())
    assert int(csv.crashes.sum())==len(f)==8142
    assert int(csv.serious_crashes.sum())==int(f.serious.sum())==3407
    assert int(csv.serious_casualties.sum())==int(f.serious_casualties.sum())==4079
    geo=json.loads((root/'exports/shortlist.geojson').read_text())
    assert {x['properties']['cell_id'] for x in geo['features']}=={x['cell_id'] for x in r['shortlist']}


def test_export_rejects_road_context_from_another_snapshot(tmp_path):
    source=tmp_path/'source'; source.mkdir()
    (source/'results.json').write_text(json.dumps({'snapshot_id':'test','monthly':[],'shortlist':[]}))
    for f in ['boundary.geojson','shortlist.geojson']: (source/f).write_text('{"type":"FeatureCollection","features":[]}')
    (source/'clusters.geojson').write_text('{"type":"FeatureCollection","features":[],"snapshot_id":"test"}')
    (source/'roads.json').write_text('{"snapshot_id":"other","cells":{}}')
    manifest=tmp_path/'manifest.json'; manifest.write_text('{"snapshot_id":"test"}')
    with pytest.raises(ValueError,match='road export'): export_site(source,tmp_path/'web',manifest)
