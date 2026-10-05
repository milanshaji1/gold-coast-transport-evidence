"""Two explicit commands: freeze on validation, then evaluate untouched 2024."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
import geopandas as gpd
import pandas as pd
from transport.acquire import dump,read_snapshot
from transport.ingest import validate
from transport.integrity import verify_analysis_integrity,write_analysis_integrity
from transport.spatial import make_grid,locate
from transport.analysis import rank_cells,capture
from transport.evaluate import uncertainty,verify_freeze


def spatial_quality(pts):
    located=pts.geocoded
    outside=located & ~pts.within_current_boundary
    return {'missing_coordinates':int((~located).sum()),'outside_current_boundary':int(outside.sum()),
            'serious_outside_current_boundary':int((pts.serious & outside).sum()),
            'serious_outside_grid':int((pts.serious & located & pts.cell_id.isna()).sum())}


def load(root):
    raw=root/Path((root/'evidence/snapshot-path.txt').read_text().strip())
    manifest,rows=read_snapshot(raw)
    expected,_,_=validate(rows)
    f=pd.read_parquet(root/'data/curated/crashes.parquet')
    try: pd.testing.assert_frame_equal(f,expected,check_exact=True)
    except AssertionError as exc: raise ValueError('curated data differs from manifested source derivation') from exc
    if (root/'evidence/freeze.json').exists(): verify_analysis_integrity(root,raw)
    if 'boundary.json' not in {source['file'] for source in manifest['sources']}: raise ValueError('boundary absent from source manifest')
    boundary=gpd.read_file(raw/'boundary.json')
    if boundary.crs is None or boundary.crs.to_epsg()!=7844: raise ValueError('boundary CRS not declared GDA2020')
    grid=make_grid(boundary)
    f=f[f.year.between(2020,2024)&(f.severity!='Property damage only')].copy()
    pts=locate(f,grid)
    area=boundary.to_crs(7856).geometry.union_all()
    pts['within_current_boundary']=pts.geometry.covered_by(area)
    grid_hash=hashlib.sha256(b''.join(grid.geometry.to_wkb())+'|'.join(grid.cell_id).encode()).hexdigest()
    contract={'snapshot_id':manifest['snapshot_id'],'grid_hash':grid_hash,'grid_size_m':500,'origin':[0,0],
              'fit_years':[2020,2021,2022],'validation_year':2023,'refit_years':[2021,2022,2023],'holdout_year':2024,
              'k':20,'sensitivity_k':[10,40],'denominator':'All geocoded source-LGA serious crashes, including boundary disagreements',
              'baseline_tie':'serious_count DESC, cell_id ASC','dbscan_tie':'density_count DESC, serious_count DESC, cell_id ASC',
              'eps_candidates':[100,250,500],'min_samples_candidates':[5,10]}
    return pts,grid,boundary,contract


def freeze(root):
    pts,grid,boundary,contract=load(root)
    train=pts[pts.year.between(2020,2022)]; val=pts[pts.year==2023]
    candidates=[]
    for eps in [100,250,500]:
        for min_samples in [5,10]:
            r=rank_cells(train,grid,eps,min_samples)
            candidates.append({'eps':eps,'min_samples':min_samples,**capture(r,val,20)})
    best=sorted(candidates,key=lambda c:(-c['numerator'],c['eps'],-c['min_samples']))[0]
    record={'contract':contract,'selected':{'eps':best['eps'],'min_samples':best['min_samples']},
            'validation_candidates':candidates,'validation_baseline':capture(rank_cells(train,grid),val,20)}
    path=root/'evidence/freeze.json'
    if path.exists(): verify_freeze(json.loads(path.read_text()),record)
    else:
        dump(path,record)
        write_analysis_integrity(root,root/Path((root/'evidence/snapshot-path.txt').read_text().strip()),'pre-holdout')
    print({'frozen':record['selected'],'grid_cells':len(grid),'validation_baseline':record['validation_baseline']})


def run_analysis(input_dir,output_dir):
    root=Path(input_dir); out=Path(output_dir); out.mkdir(exist_ok=True)
    frozen=json.loads((root/'evidence/freeze.json').read_text())
    pts,grid,boundary,contract=load(root); verify_freeze(frozen['contract'],contract)
    train=pts[pts.year.between(2021,2023)]; test=pts[pts.year==2024]
    baseline=rank_cells(train,grid)
    density=rank_cells(train,grid,**frozen['selected'])
    valbase=rank_cells(pts[pts.year.between(2020,2022)],grid)
    valscan=rank_cells(pts[pts.year.between(2020,2022)],grid,**frozen['selected'])
    results={'snapshot_id':contract['snapshot_id'],'freeze_sha256':hashlib.sha256((root/'evidence/freeze.json').read_bytes()).hexdigest(),
             'period':[2020,2024],'primary_method':'count baseline','evaluation':[],'clusters':density.attrs['clusters']}
    for method,r,vr in [('count',baseline,valbase),('density',density,valscan)]:
        for k in [10,20,40]:
            results['evaluation'].append({'method':method,**capture(r,test,k),'validation_refit_overlap':len(set(r.head(k).cell_id)&set(vr.head(k).cell_id))})
    ids=grid.cell_id
    tr=baseline.set_index('cell_id').reindex(ids).serious_count.to_numpy()
    te=test[test.serious].groupby('cell_id').size().reindex(ids,fill_value=0).to_numpy()
    results['uncertainty']=uncertainty(tr,te)
    results['uncertainty'].pop('posterior_means',None)
    results['quality']={'analysis_crashes':len(pts),'serious_crashes':int(pts.serious.sum()),'serious_casualties':int(pts.serious_casualties.sum()),
                        **spatial_quality(pts),'grid_cells':len(grid)}
    selected=baseline.head(40).copy(); selected['rank']=range(1,len(selected)+1)
    names=train[train.serious].groupby('cell_id').suburb.agg(lambda s:', '.join(s.value_counts().head(2).index))
    selected['suburbs']=selected.cell_id.map(names).fillna('No training events')
    selected['holdout_serious_count']=selected.cell_id.map(test[test.serious].groupby('cell_id').size()).fillna(0).astype(int)
    # Full metric outputs share a single canonical aggregation; no BI-specific recreation.
    monthly=pts.groupby(['year','month','severity'],as_index=False).agg(crashes=('crash_id','size'),serious_crashes=('serious','sum'),serious_casualties=('serious_casualties','sum'))
    monthly['snapshot_id']=contract['snapshot_id']
    results['shortlist']=selected.to_dict('records'); results['monthly']=monthly.to_dict('records')
    final=root/'evidence/results.json'
    if final.exists(): verify_freeze(json.loads(final.read_text()),results)
    else: dump(final,results)
    monthly.to_csv(out/'monthly.csv',index=False); selected.to_csv(out/'shortlist.csv',index=False)
    pts.drop(columns='geometry').to_parquet(root/'data/curated/located.parquet',index=False)
    g=grid.merge(selected,on=['cell_id','clipped_area_km2']).to_crs(4326)
    g.to_file(out/'shortlist.geojson',driver='GeoJSON')
    boundary.to_crs(4326).to_file(out/'boundary.geojson',driver='GeoJSON')
    grid.to_parquet(root/'data/curated/grid.parquet',index=False)
    dump(out/'results.json',results)
    print({k:v for k,v in results.items() if k in ['quality','evaluation','uncertainty']})
    return results

if __name__=='__main__':
    root=Path(__file__).resolve().parents[2]
    if sys.argv[1]=='freeze': freeze(root)
    elif sys.argv[1]=='evaluate': run_analysis(root,root/'exports')
    else: raise SystemExit('Use freeze or evaluate')
