from pathlib import Path
from typing import Union
import geopandas as gpd
import pandas as pd
import fsspec
from pymapgis.settings import settings
import xarray as xr
import rioxarray # Imported for side-effects and direct use

# Define a more comprehensive return type for the read function
ReadReturnType = Union[gpd.GeoDataFrame, pd.DataFrame, xr.DataArray, xr.Dataset]

def read(uri: str, *, x="longitude", y="latitude", **kw) -> ReadReturnType:
    """
    Universal reader:

    Vector formats:
    • .shp / .geojson / .gpkg     → GeoDataFrame via GeoPandas (gpd.read_file)
    • .parquet / .geoparquet    → GeoDataFrame via GeoPandas (gpd.read_parquet)
    • .csv with lon/lat cols      → GeoDataFrame; else plain DataFrame

    Raster formats:
    • .tif / .tiff / .cog (GeoTIFF/COG) → xarray.DataArray via rioxarray.open_rasterio
    • .nc (NetCDF)                      → xarray.Dataset via xarray.open_dataset

    Supports local paths and remote URLs (e.g., HTTP, HTTPS) via fsspec, with caching.
    The cache directory is configured via pymapgis.settings.
    """

    storage_options = fsspec.utils.infer_storage_options(uri)
    protocol = storage_options.get("protocol", "file")
    cache_fs_path = str(settings.cache_dir)

    if protocol == "file":
        fs = fsspec.filesystem("filecache", cache_storage=cache_fs_path)
    else:
        fs = fsspec.filesystem(
            "filecache",
            target_protocol=protocol,
            target_options=storage_options.get(protocol, {}),
            cache_storage=cache_fs_path
        )

    path_for_suffix = uri
    if fsspec.utils.get_protocol(uri) != "file":
        path_for_suffix = storage_options['path']
    suffix = Path(path_for_suffix).suffix.lower()

    try:
        # Ensure file is cached and get local path
        # This is used for libraries that primarily expect file paths
        with fs.open(uri, "rb"): # Open and close to ensure it's cached
            pass
        cached_file_path = fs.get_mapper(uri).root

        if suffix in {".shp", ".geojson", ".gpkg", ".parquet", ".geoparquet"}:
            if suffix in {".shp", ".geojson", ".gpkg"}:
                return gpd.read_file(cached_file_path, **kw)
            elif suffix in {".parquet", ".geoparquet"}:
                return gpd.read_parquet(cached_file_path, **kw)

        elif suffix in {".tif", ".tiff", ".cog"}:
            # rioxarray.open_rasterio typically returns a DataArray.
            # masked=True is good practice.
            # For COGs, chunking can be passed via kw if needed, e.g., chunks={'x': 256, 'y': 256}
            return rioxarray.open_rasterio(cached_file_path, masked=True, **kw)

        elif suffix == ".nc":
            # xarray.open_dataset returns an xarray.Dataset
            # Specific groups or other NetCDF features can be passed via kw
            return xr.open_dataset(cached_file_path, **kw)

        elif suffix == ".csv":
            # For pandas, using fs.open() to get a file-like object is efficient
            with fs.open(uri, "rt", encoding=kw.pop("encoding", "utf-8")) as f:
                df = pd.read_csv(f, **kw)
            if {x, y}.issubset(df.columns):
                gdf = gpd.GeoDataFrame(
                    df,
                    geometry=gpd.points_from_xy(df[x], df[y]),
                    crs=kw.pop("crs", "EPSG:4326"),
                )
                return gdf
            return df

        else:
            raise ValueError(f"Unsupported format: {suffix} for URI: {uri}")

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found at URI: {uri}")
    except Exception as e:
        raise IOError(f"Error reading {uri} (suffix {suffix}): {e}")
