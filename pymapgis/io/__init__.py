from pathlib import Path
import geopandas as gpd
import pandas as pd


def read(uri: str, *, x="longitude", y="latitude", **kw):
    """
    Universal reader (MVP):

    • .shp / .geojson / .gpkg  → GeoDataFrame via GeoPandas
    • .csv with lon/lat cols   → GeoDataFrame; else plain DataFrame
    """
    path = Path(uri)

    if path.suffix.lower() in {".shp", ".geojson", ".gpkg"}:
        return gpd.read_file(uri, **kw)

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(uri, **kw)
        if {x, y}.issubset(df.columns):
            gdf = gpd.GeoDataFrame(
                df,
                geometry=gpd.points_from_xy(df[x], df[y]),
                crs="EPSG:4326",
            )
            return gdf
        return df

    raise ValueError(f"Unsupported format: {uri}")
