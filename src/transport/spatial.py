"""Fixed-origin 500 m lattice; source and analysis CRS are explicit."""
import math
import geopandas as gpd
import pandas as pd
from shapely.geometry import box

CRS=7856
SIZE=500


def make_grid(boundary):
    if boundary.crs is None: raise ValueError('boundary CRS required')
    area=boundary.to_crs(CRS).geometry.union_all()
    if area.is_empty or not area.is_valid: raise ValueError('invalid boundary')
    xmin,ymin,xmax,ymax=area.bounds
    cells=[]
    for x in range(math.floor(xmin/SIZE),math.ceil(xmax/SIZE)):
        for y in range(math.floor(ymin/SIZE),math.ceil(ymax/SIZE)):
            geom=box(x*SIZE,y*SIZE,(x+1)*SIZE,(y+1)*SIZE)
            clipped=geom.intersection(area).area
            if clipped>0: cells.append({'cell_id':f'{x}_{y}','clipped_area_km2':clipped/1e6,'geometry':geom})
    return gpd.GeoDataFrame(cells,crs=CRS).sort_values('cell_id').reset_index(drop=True)


def locate(frame,grid):
    if isinstance(frame,gpd.GeoDataFrame):
        if frame.crs is None: raise ValueError('point CRS required')
        pts=frame.to_crs(CRS).copy()
    else:
        pts=gpd.GeoDataFrame(frame.copy(),geometry=gpd.points_from_xy(frame.longitude,frame.latitude),crs=7844).to_crs(CRS)
    allowed=set(grid.cell_id)
    def cell(geom):
        if geom is None or geom.is_empty or not math.isfinite(geom.x) or not math.isfinite(geom.y): return None
        key=f'{math.floor(geom.x/SIZE)}_{math.floor(geom.y/SIZE)}'
        return key if key in allowed else None
    pts['cell_id']=[cell(g) for g in pts.geometry]
    return pts
