import geopandas as gpd
from shapely.geometry import Point
from transport.map_layers import training_clusters


def test_map_uses_only_geocoded_training_serious_events_and_retains_duplicates():
    points=gpd.GeoDataFrame({'crash_id':['a','b','c','d','e','f'],'year':[2021,2022,2023,2024,2022,2022],
        'serious':[True,True,True,True,False,True],'cell_id':['1_2']*6,'suburb':['TEST']*6},
        geometry=[Point(540000,6900000)]*5+[None],crs=7856)
    features,summary=training_clusters(points,250,2)
    assert len(features['features'])==3
    assert {f['properties']['year'] for f in features['features']}=={2021,2022,2023}
    assert [f['properties']['cluster'] for f in features['features']]==[0,0,0]
    assert summary=={'noise_events':0,'clusters':[{'cluster':0,'events':3,'bounding_box_diagonal_m':0.0}]}
    assert features['features'][0]['geometry']['coordinates']==features['features'][1]['geometry']['coordinates']
