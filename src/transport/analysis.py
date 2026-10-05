"""Counts are the primary shortlist; DBSCAN supplies density-filtered counts."""
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN


def rank_cells(points,grid,eps=None,min_samples=5):
    if points.crs.to_epsg()!=7856: raise ValueError('distance calculations require EPSG:7856')
    points=points[points.serious].copy()
    if 'crash_id' in points and points.crash_id.duplicated().any(): raise ValueError('duplicate event key')
    points=points[points.geometry.notna() & ~points.geometry.is_empty].copy()
    finite=np.isfinite(points.geometry.x)&np.isfinite(points.geometry.y)
    points=points[finite].copy()
    labels=np.full(len(points),-1,dtype=int)
    if eps is not None and len(points):
        labels=DBSCAN(eps=eps,min_samples=min_samples).fit_predict(np.column_stack([points.geometry.x,points.geometry.y]))
    points['cluster']=labels
    r=grid[['cell_id','clipped_area_km2']].copy()
    r['serious_count']=r.cell_id.map(points.groupby('cell_id').size()).fillna(0).astype(int)
    r['density_count']=r.cell_id.map(points[points.cluster>=0].groupby('cell_id').size()).fillna(0).astype(int)
    sort=['serious_count','cell_id'] if eps is None else ['density_count','serious_count','cell_id']
    r=r.sort_values(sort,ascending=[False]*(len(sort)-1)+[True]).reset_index(drop=True)
    spans=[]
    for label,p in points[points.cluster>=0].groupby('cluster'):
        bounds=p.total_bounds
        spans.append({'cluster':int(label),'events':len(p),'bounding_box_diagonal_m':float(np.hypot(bounds[2]-bounds[0],bounds[3]-bounds[1]))})
    r.attrs['clusters']={'noise_events':int((labels==-1).sum()),'clusters':spans}
    return r


def capture(ranking,holdout,k):
    if not isinstance(k,int) or k<1 or k>len(ranking): raise ValueError('invalid cell budget')
    h=holdout[holdout.serious].copy()
    finite=h.geometry.notna() & ~h.geometry.is_empty
    h=h[finite]
    h=h[np.isfinite(h.geometry.x)&np.isfinite(h.geometry.y)]
    selected=ranking.head(k)
    num=int(h.cell_id.isin(selected.cell_id).sum()); den=len(h)
    return {'k':k,'numerator':num,'denominator':den,'capture_pct':100*num/den if den else None,
            'nominal_area_km2':k*.25,'clipped_area_km2':float(selected.clipped_area_km2.sum()),
            'zero_count_cells':int((selected.serious_count==0).sum()),'zero_density_cells':int((selected.density_count==0).sum())}
