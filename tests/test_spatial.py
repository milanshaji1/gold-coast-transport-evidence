import geopandas as gpd
import pandas as pd
from shapely.geometry import box,Point
from transport.spatial import make_grid,locate
from transport.analysis import rank_cells,capture


def test_grid_excludes_zero_area_edge_contacts():
    grid=make_grid(gpd.GeoDataFrame(geometry=[box(0,0,1000,1000)],crs=7856))
    assert len(grid)==4
    assert set(grid.cell_id)=={'0_0','0_1','1_0','1_1'}
    assert grid.clipped_area_km2.sum()==1

def test_boundary_half_open_assignment_and_outside_denominator():
    grid=make_grid(gpd.GeoDataFrame(geometry=[box(0,0,1000,1000)],crs=7856))
    pts=gpd.GeoDataFrame({'crash_id':['a','b','c'],'serious':[True]*3},geometry=[Point(10,10),Point(500,10),Point(1000,10)],crs=7856)
    located=locate(pts,grid)
    assert located.cell_id.iloc[:2].tolist()==['0_0','1_0']
    assert pd.isna(located.cell_id.iloc[2])
    ranked=rank_cells(located,grid)
    assert capture(ranked,located,1)['numerator']==1
    assert capture(ranked,located,1)['denominator']==3

def test_gda2020_coordinates_are_projected_to_metres():
    grid=make_grid(gpd.GeoDataFrame(geometry=[box(530000,6900000,550000,6920000)],crs=7856))
    pts=locate(pd.DataFrame({'longitude':[153.4],'latitude':[-28.0],'geocoded':[True]}),grid)
    assert pts.crs.to_epsg()==7856
    assert 530000<pts.geometry.x.iloc[0]<550000
    assert 6890000<pts.geometry.y.iloc[0]<6910000
