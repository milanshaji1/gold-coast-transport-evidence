"""One validated export of every downloadable evidence file."""
import json
from pathlib import Path
import pandas as pd


def strict_json(path):
    return json.loads(path.read_text(),parse_constant=lambda x:(_ for _ in ()).throw(ValueError('non-finite JSON')))


def export_site(source,target,manifest):
    source,target,manifest=Path(source),Path(target),Path(manifest)
    parsed={name:strict_json(source/name) for name in ['results.json','boundary.geojson','shortlist.geojson','clusters.geojson','roads.json']}
    parsed['source-manifest.json']=strict_json(manifest)
    result=parsed['results.json']
    if parsed['clusters.geojson'].get('snapshot_id')!=result['snapshot_id']: raise ValueError('cluster export snapshot mismatch')
    if parsed['roads.json'].get('snapshot_id')!=result['snapshot_id']: raise ValueError('road export snapshot mismatch')
    if parsed['source-manifest.json']['snapshot_id']!=result['snapshot_id']: raise ValueError('export snapshot mismatch')
    validated={name:json.dumps(content,allow_nan=False,separators=(',',':'))+'\n' for name,content in parsed.items()}
    # Recreate CSVs from the same canonical result, never from stale copies.
    for name in ('monthly','shortlist'): validated[name+'.csv']=pd.DataFrame(result[name]).to_csv(index=False)
    target.mkdir(parents=True,exist_ok=True)
    for name,content in validated.items(): (target/name).write_text(content)

if __name__=='__main__':
    root=Path(__file__).resolve().parents[2]
    export_site(root/'exports',root/'site/data',root/'evidence/source-manifest.json')
