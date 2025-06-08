from pathlib import Path
from typing import Union
import geopandas as gpd
import pandas as pd
import fsspec
from pymapgis.settings import settings
import xarray as xr
import rioxarray # Imported for side-effects and direct use
import numpy as np
from pymapgis.pointcloud import read_point_cloud as pmg_read_point_cloud
from pymapgis.pointcloud import get_point_cloud_points as pmg_get_point_cloud_points

# Define a more comprehensive return type for the read function
ReadReturnType = Union[gpd.GeoDataFrame, pd.DataFrame, xr.DataArray, xr.Dataset, np.ndarray]

def read(uri: str, *, x="longitude", y="latitude", **kw) -> ReadReturnType:
    """
    Universal reader:

    Reads various geospatial and tabular file formats, attempting to infer the
    correct library and return type. Supports local paths and remote URLs
    (e.g., HTTP, S3) via fsspec, with local caching.

    Vector formats:
    • .shp / .geojson / .gpkg: → GeoDataFrame (via `gpd.read_file`)
    • .parquet / .geoparquet: → GeoDataFrame (via `gpd.read_parquet`)
    • .csv with lon/lat cols: → GeoDataFrame (from `pd.read_csv`, then `gpd.GeoDataFrame`)
        - If a CSV is converted to a GeoDataFrame, the default CRS applied is
          "EPSG:4326" unless overridden by `kw['crs']`.
    • .csv without lon/lat:   → DataFrame (via `pd.read_csv`)


    Raster formats:
    • .tif / .tiff / .cog (GeoTIFF/COG): → `xarray.DataArray` (via `rioxarray.open_rasterio`)
        - Note: `rioxarray.open_rasterio` defaults to `masked=True`, which means
          nodata values in the raster are represented as `np.nan` in the DataArray.
          This can affect calculations if not handled explicitly.
    • .nc (NetCDF): → `xarray.Dataset` (via `xr.open_dataset`)

    Point Cloud formats:
    • .las / .laz (ASPRS LAS/LAZ): → `np.ndarray` (structured NumPy array via PDAL)
        - Returns a structured array where fields correspond to dimensions
          (e.g., 'X', 'Y', 'Z', 'Intensity').
        - PDAL installation is required (see PyMapGIS documentation).

    Args:
        uri (str): Path or URL to the file.
        x (str, optional): Column name for longitude if reading a CSV to GeoDataFrame.
            Defaults to "longitude".
        y (str, optional): Column name for latitude if reading a CSV to GeoDataFrame.
            Defaults to "latitude".
        **kw: Additional keyword arguments passed to the underlying reading function.
            Common uses include:
            - For CSVs: `crs` (e.g., `crs="EPSG:32632"`) to set the CRS if converting
              to a GeoDataFrame. Other `pd.read_csv` arguments like `sep`, `header`,
              `encoding` are also valid.
            - For COGs/GeoTIFFs: `chunks` (e.g., `chunks={'x': 256, 'y': 256}`) for
              dask-backed lazy loading, `overview_level` to read a specific overview.
              Other `rioxarray.open_rasterio` arguments like `band`, `masked`
              are also valid.
            - For general vector files (`gpd.read_file`): `engine` (e.g., `engine="pyogrio"`),
              `layer`, `bbox`.
            - For Parquet files (`gpd.read_parquet`): e.g., `columns=['geometry', 'attribute1']`.
            - For NetCDF files (`xr.open_dataset`): `engine` (e.g., `engine="h5netcdf"`),
              `group`, `decode_times`.

    Returns:
        Union[gpd.GeoDataFrame, pd.DataFrame, xr.DataArray, xr.Dataset, np.ndarray]:
        The data read from the file, in its most appropriate geospatial type.

    Raises:
        ValueError: If the file format is unsupported.
        FileNotFoundError: If the file at the URI is not found.
        IOError: For other reading-related errors.

    The cache directory is configured via `pymapgis.settings.cache_dir`.
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
            with fs.open(uri, "rt", encoding=kw.pop("encoding", "utf-8")) as f: # type: ignore
                df = pd.read_csv(f, **kw)
            if {x, y}.issubset(df.columns):
                gdf = gpd.GeoDataFrame(
                    df,
                    geometry=gpd.points_from_xy(df[x], df[y]),
                    crs=kw.pop("crs", "EPSG:4326"),
                )
                return gdf
            return df

        elif suffix in {".las", ".laz"}:
            # For point clouds, PDAL typically works best with local file paths.
            # The cached_file_path from fsspec should provide this.
            # kwargs for read_point_cloud can be passed via **kw
            pdal_pipeline = pmg_read_point_cloud(cached_file_path, **kw)
            return pmg_get_point_cloud_points(pdal_pipeline)

        else:
            raise ValueError(f"Unsupported format: {suffix} for URI: {uri}")

    except FileNotFoundError:
        raise FileNotFoundError(f"File not found at URI: {uri}")
    except Exception as e:
        raise IOError(f"Failed to read {uri} with format {suffix}. Original error: {e}")
