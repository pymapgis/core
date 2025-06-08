import geopandas
from shapely.geometry import Point
from pymapgis.vector import buffer

def test_buffer_simple():
    """Tests the buffer function with a simple Point geometry."""
    # Create a simple GeoDataFrame
    data = {'id': [1], 'geometry': [Point(0, 0)]}
    gdf = geopandas.GeoDataFrame(data, crs="EPSG:4326")

    # Call the buffer function
    result = buffer(gdf, distance=10)

    # Assertions
    assert isinstance(result, geopandas.GeoDataFrame)
    assert not result.empty
    assert result.geometry.iloc[0].geom_type == 'Polygon'
    assert result.crs == gdf.crs
