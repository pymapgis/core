import geopandas as gpd
from pymapgis.io import read


def test_read_shp(tmp_path):
    gdf = gpd.GeoDataFrame(geometry=gpd.points_from_xy([0], [0]), crs="EPSG:4326")
    shp = tmp_path / "pts.shp"
    gdf.to_file(shp)
    out = read(shp)
    assert isinstance(out, gpd.GeoDataFrame)


def test_read_csv(tmp_path):
    csv = tmp_path / "pts.csv"
    csv.write_text("longitude,latitude\n1,1\n")
    out = read(csv)
    assert out.geometry.iloc[0].x == 1
