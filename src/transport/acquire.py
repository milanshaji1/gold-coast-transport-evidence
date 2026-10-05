"""Freeze public source responses; rebuilds read these bytes without contacting upstream."""
import hashlib
import json
import time
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urlencode
from transport.ingest import collect_pages,validate
from transport.warehouse import build_warehouse

CRASH_API='https://www.data.qld.gov.au/api/3/action/'
RESOURCE='e88943c0-5968-4972-a15f-38e120d72ec0'
BOUNDARY='https://spatial-gis.information.qld.gov.au/arcgis/rest/services/Boundaries/AdministrativeBoundaries/MapServer/1'


def download(url):
    for attempt in range(3):
        try:
            with urlopen(url,timeout=60) as response: return response.read()
        except (OSError,TimeoutError):
            if attempt==2: raise
            time.sleep(2**attempt)


def dump(path,data):
    path.write_text(json.dumps(data,indent=2,sort_keys=True,allow_nan=False)+'\n')


def acquire(root):
    raw=root/'data/raw'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    raw.mkdir(parents=True,exist_ok=False)
    sources=[]
    def save(name,url):
        content=download(url); (raw/name).write_bytes(content)
        sources.append({'file':name,'url':url,'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content),'retrieved_utc':datetime.now(timezone.utc).isoformat()})
        return json.loads(content)
    metadata=save('crash_metadata.json',CRASH_API+'package_show?'+urlencode({'id':'crash-data-from-queensland-roads'}))
    def page(offset,limit):
        result=save(f'crashes_{offset:06d}.json',CRASH_API+'datastore_search?'+urlencode({'resource_id':RESOURCE,'filters':json.dumps({'Loc_Local_Government_Area':'Gold Coast City'}),'sort':'_id asc','offset':offset,'limit':limit}))
        print(f'Acquired offset {offset}: {len(result.get("result",{}).get("records",[]))} rows',flush=True)
        return result
    rows=collect_pages(page)
    after=save('crash_metadata_after.json',CRASH_API+'package_show?'+urlencode({'id':'crash-data-from-queensland-roads'}))
    before_resource=next(r for r in metadata['result']['resources'] if r['id']==RESOURCE)
    after_resource=next(r for r in after['result']['resources'] if r['id']==RESOURCE)
    verify_resource_version(before_resource,after_resource)
    # Datastore has no snapshot token: compare a second complete sorted pass.
    def confirm_page(offset,limit):
        return save(f'verify_{offset:06d}.json',CRASH_API+'datastore_search?'+urlencode({'resource_id':RESOURCE,'filters':json.dumps({'Loc_Local_Government_Area':'Gold Coast City'}),'sort':'_id asc','offset':offset,'limit':limit}))
    confirmed=collect_pages(confirm_page)
    verify_page_content(rows,confirmed)
    final_metadata=save('crash_metadata_confirmed.json',CRASH_API+'package_show?'+urlencode({'id':'crash-data-from-queensland-roads'}))
    verify_resource_version(before_resource,next(r for r in final_metadata['result']['resources'] if r['id']==RESOURCE))
    save('boundary_metadata.json',BOUNDARY+'?f=pjson')
    # Native ArcGIS service is Web Mercator; request explicit GDA2020 output.
    boundary=save('boundary.json',BOUNDARY+'/query?'+urlencode({'where':"lga='Gold Coast City'",'outFields':'*','returnGeometry':'true','outSR':'7844','f':'json'}))
    if boundary.get('exceededTransferLimit') or len(boundary.get('features',[]))!=1: raise ValueError('expected exactly one official LGA polygon')
    save('boundary_licence.json',CRASH_API+'package_show?'+urlencode({'id':'local-government-area-boundaries-queensland'}))
    snapshot=hashlib.sha256(''.join(s['sha256'] for s in sources).encode()).hexdigest()[:16]
    dump(raw/'manifest.json',{'snapshot_id':snapshot,'resource_id':RESOURCE,'row_count':len(rows),'crash_crs':'EPSG:7844','boundary_requested_crs':'EPSG:7844','consistency_check':'two matching complete sorted passes and stable resource metadata; not a transactional snapshot','publisher':'Queensland Government','crash_licence':metadata['result'].get('license_title'),'sources':sources})
    rebuild(root,raw)
    print(raw,flush=True)
    return raw


def verify_resource_version(before,after):
    fields=('id','last_modified','hash','metadata_modified')
    if not before.get('id') or not any(before.get(k) for k in ('last_modified','hash')):
        raise ValueError('trustworthy resource version metadata unavailable')
    if any(before.get(k)!=after.get(k) for k in fields):
        raise ValueError('publisher resource changed during download')


def verify_page_content(first,second):
    if first!=second: raise ValueError('source content changed between complete passes')


def read_snapshot(raw):
    manifest=json.loads((raw/'manifest.json').read_text())
    sources=manifest['sources']; names=[s['file'] for s in sources]
    if len(set(names))!=len(names) or any(Path(n).name!=n for n in names):
        raise ValueError('invalid manifest file names')
    for source in sources:
        if hashlib.sha256((raw/source['file']).read_bytes()).hexdigest()!=source['sha256']:
            raise ValueError('snapshot hash mismatch')
    identity=hashlib.sha256(''.join(s['sha256'] for s in sources).encode()).hexdigest()[:16]
    if identity!=manifest['snapshot_id']: raise ValueError('snapshot identity mismatch')
    pages=sorted(n for n in names if n.startswith('crashes_') and n.endswith('.json'))
    if {p.name for p in raw.glob('crashes_*.json')}!=set(pages):
        raise ValueError('unmanifested crash page')
    if not pages: raise ValueError('no manifested crash pages')
    by_offset={}
    for name in pages:
        offset=int(Path(name).stem.split('_')[1])
        if offset in by_offset: raise ValueError('duplicate page offset')
        by_offset[offset]=json.loads((raw/name).read_text())
    consumed=set()
    def page(offset,limit):
        if offset not in by_offset: raise ValueError('missing page offset')
        consumed.add(offset)
        return by_offset[offset]
    rows=collect_pages(page)
    if consumed!=set(by_offset): raise ValueError('unused manifested page')
    if len(rows)!=manifest['row_count']: raise ValueError('manifest row count mismatch')
    return manifest,rows


def rebuild(root,raw):
    manifest,rows=read_snapshot(raw)
    good,bad,quality=validate(rows)
    out=root/'data/curated'; out.mkdir(exist_ok=True)
    good.to_parquet(out/'crashes.parquet',index=False); bad.to_parquet(out/'quarantine.parquet',index=False)
    quality['snapshot_id']=manifest['snapshot_id']; quality['warehouse']=build_warehouse(good,out/'transport.duckdb')
    quality['year_month_counts']=[{'year':int(y),'month':int(m),'crashes':int(n)} for (y,m),n in good.groupby(['year','month']).size().items()]
    dump(root/'evidence/quality.json',quality)
    dump(root/'evidence/source-manifest.json',manifest)
    (root/'evidence/snapshot-path.txt').write_text(str(raw.relative_to(root))+'\n')
    print({k:v for k,v in quality.items() if k!='year_month_counts'},flush=True)

if __name__=='__main__':
    import sys
    root=Path(__file__).resolve().parents[2]
    if len(sys.argv)>1: rebuild(root,root/sys.argv[1])
    else: acquire(root)
