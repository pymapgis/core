"""
Cloud-Optimized Data Formats Module

This module provides support for cloud-optimized geospatial data formats:
- Cloud Optimized GeoTIFF (COG)
- Parquet/GeoParquet for vector data
- Zarr for multidimensional arrays
- Delta Lake for versioned datasets
- FlatGeobuf for streaming vector data

These formats are designed for efficient cloud access with:
- Partial reading capabilities
- Optimized compression
- Metadata in headers
- Chunked/tiled organization
"""

import logging
from pathlib import Path
from typing import Optional, Union, Dict, Any, List, Tuple
import tempfile

try:
    import geopandas as gpd
    import pandas as pd

    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import xarray as xr
    import rioxarray

    XARRAY_AVAILABLE = True
except ImportError:
    XARRAY_AVAILABLE = False

try:
    import zarr

    ZARR_AVAILABLE = True
except ImportError:
    ZARR_AVAILABLE = False

try:
    import pyarrow as pa
    import pyarrow.parquet as pq

    ARROW_AVAILABLE = True
except ImportError:
    ARROW_AVAILABLE = False

logger = logging.getLogger(__name__)

__all__ = [
    "CloudOptimizedWriter",
    "CloudOptimizedReader",
    "convert_to_cog",
    "convert_to_geoparquet",
    "convert_to_zarr",
    "optimize_for_cloud",
]


class CloudOptimizedWriter:
    """Writer for cloud-optimized formats."""

    def __init__(self, compression: str = "lz4", chunk_size: int = 1024):
        self.compression = compression
        self.chunk_size = chunk_size

    def write_cog(self, data: xr.DataArray, output_path: str, **kwargs) -> None:
        """
        Write Cloud Optimized GeoTIFF.

        Args:
            data: Raster data as xarray DataArray
            output_path: Output file path
            **kwargs: Additional COG options
        """
        if not XARRAY_AVAILABLE:
            raise ImportError("xarray and rioxarray required for COG writing")

        # Set COG-specific options
        cog_options = {
            "tiled": True,
            "blockxsize": kwargs.get("blockxsize", 512),
            "blockysize": kwargs.get("blockysize", 512),
            "compress": kwargs.get("compress", "lzw"),
            "interleave": "pixel",
            "BIGTIFF": "IF_SAFER",
        }

        # Add overviews for efficient zooming
        if kwargs.get("add_overviews", True):
            cog_options["OVERVIEW_RESAMPLING"] = kwargs.get(
                "overview_resampling", "average"
            )

        # Write with COG profile
        data.rio.to_raster(output_path, **cog_options)
        logger.info(f"Wrote Cloud Optimized GeoTIFF: {output_path}")

    def write_geoparquet(
        self, data: gpd.GeoDataFrame, output_path: str, **kwargs
    ) -> None:
        """
        Write GeoParquet format.

        Args:
            data: Vector data as GeoDataFrame
            output_path: Output file path
            **kwargs: Additional Parquet options
        """
        if not PANDAS_AVAILABLE or not ARROW_AVAILABLE:
            raise ImportError("geopandas and pyarrow required for GeoParquet writing")

        # Set GeoParquet-specific options
        parquet_options = {
            "compression": kwargs.get("compression", self.compression),
            "row_group_size": kwargs.get("row_group_size", 50000),
            "use_dictionary": kwargs.get("use_dictionary", True),
            "write_covering_bbox": kwargs.get("write_covering_bbox", True),
        }

        # Write GeoParquet
        data.to_parquet(output_path, **parquet_options)
        logger.info(f"Wrote GeoParquet: {output_path}")

    def write_zarr(self, data: xr.Dataset, output_path: str, **kwargs) -> None:
        """
        Write Zarr format for multidimensional arrays.

        Args:
            data: Multidimensional data as xarray Dataset
            output_path: Output directory path
            **kwargs: Additional Zarr options
        """
        if not XARRAY_AVAILABLE or not ZARR_AVAILABLE:
            raise ImportError("xarray and zarr required for Zarr writing")

        # Set Zarr-specific options
        zarr_options = {"mode": "w", "consolidated": True, "compute": True}
        zarr_options.update(kwargs)

        # Configure chunking for cloud access
        if "chunks" not in zarr_options:
            # Auto-chunk based on data dimensions
            chunks = {}
            for dim, size in data.dims.items():
                if dim in ["time"]:
                    chunks[dim] = min(10, size)  # Small time chunks
                elif dim in ["x", "y", "lon", "lat"]:
                    chunks[dim] = min(self.chunk_size, size)  # Spatial chunks
                else:
                    chunks[dim] = min(100, size)  # Other dimensions
            zarr_options["chunks"] = chunks

        # Write Zarr
        data.to_zarr(output_path, **zarr_options)  # type: ignore
        logger.info(f"Wrote Zarr dataset: {output_path}")

    def write_flatgeobuf(
        self, data: gpd.GeoDataFrame, output_path: str, **kwargs
    ) -> None:
        """
        Write FlatGeobuf format for streaming vector data.

        Args:
            data: Vector data as GeoDataFrame
            output_path: Output file path
            **kwargs: Additional FlatGeobuf options
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("geopandas required for FlatGeobuf writing")

        try:
            # Write FlatGeobuf (if driver is available)
            data.to_file(output_path, driver="FlatGeobuf", **kwargs)
            logger.info(f"Wrote FlatGeobuf: {output_path}")
        except Exception as e:
            logger.warning(
                f"FlatGeobuf writing failed, falling back to GeoParquet: {e}"
            )
            # Fallback to GeoParquet
            parquet_path = str(Path(output_path).with_suffix(".parquet"))
            self.write_geoparquet(data, parquet_path, **kwargs)


class CloudOptimizedReader:
    """Reader for cloud-optimized formats with partial reading capabilities."""

    def __init__(self, cache_chunks: bool = True):
        self.cache_chunks = cache_chunks

    def read_cog_window(
        self, file_path: str, window: Tuple[int, int, int, int], overview_level: int = 0
    ) -> Union[xr.DataArray, xr.Dataset]:
        """
        Read a spatial window from Cloud Optimized GeoTIFF.

        Args:
            file_path: Path to COG file
            window: (min_x, min_y, max_x, max_y) in pixel coordinates
            overview_level: Overview level to read (0 = full resolution)

        Returns:
            Windowed raster data
        """
        if not XARRAY_AVAILABLE:
            raise ImportError("xarray and rioxarray required for COG reading")

        # Open with rioxarray for efficient windowed reading
        da = rioxarray.open_rasterio(file_path, overview_level=overview_level)
        min_x, min_y, max_x, max_y = window
        if hasattr(da, "isel"):
            windowed = da.isel(x=slice(min_x, max_x), y=slice(min_y, max_y))
            return windowed.load()
        else:
            return da  # type: ignore

    def read_geoparquet_filtered(
        self,
        file_path: str,
        bbox: Optional[Tuple[float, float, float, float]] = None,
        columns: Optional[List[str]] = None,
    ) -> gpd.GeoDataFrame:
        """
        Read GeoParquet with spatial and column filtering.

        Args:
            file_path: Path to GeoParquet file
            bbox: Bounding box filter (min_x, min_y, max_x, max_y)
            columns: Columns to read (None for all)

        Returns:
            Filtered GeoDataFrame
        """
        if not PANDAS_AVAILABLE or not ARROW_AVAILABLE:
            raise ImportError("geopandas and pyarrow required for GeoParquet reading")

        # Read with column selection
        gdf = gpd.read_parquet(file_path, columns=columns)

        # Apply spatial filter if provided
        if bbox:
            min_x, min_y, max_x, max_y = bbox
            mask = (
                (gdf.geometry.bounds.minx <= max_x)
                & (gdf.geometry.bounds.maxx >= min_x)
                & (gdf.geometry.bounds.miny <= max_y)
                & (gdf.geometry.bounds.maxy >= min_y)
            )
            gdf = gdf[mask]

        return gdf

    def read_zarr_slice(
        self,
        zarr_path: str,
        time_slice: Optional[slice] = None,
        spatial_slice: Optional[Dict[str, slice]] = None,
    ) -> xr.Dataset:
        """
        Read a slice from Zarr dataset.

        Args:
            zarr_path: Path to Zarr dataset
            time_slice: Time slice to read
            spatial_slice: Spatial slices (e.g., {'x': slice(0, 100), 'y': slice(0, 100)})

        Returns:
            Sliced dataset
        """
        if not XARRAY_AVAILABLE or not ZARR_AVAILABLE:
            raise ImportError("xarray and zarr required for Zarr reading")

        # Open Zarr dataset
        ds = xr.open_zarr(zarr_path)

        # Apply slicing
        slices = {}
        if time_slice and "time" in ds.dims:
            slices["time"] = time_slice

        if spatial_slice:
            slices.update(spatial_slice)

        if slices:
            ds = ds.isel(slices)

        return ds


# Convenience functions
def convert_to_cog(input_path: str, output_path: str, **kwargs) -> None:
    """
    Convert raster to Cloud Optimized GeoTIFF.

    Args:
        input_path: Input raster file
        output_path: Output COG file
        **kwargs: COG options
    """
    if not XARRAY_AVAILABLE:
        raise ImportError("xarray and rioxarray required for COG conversion")

    # Read input raster
    data = rioxarray.open_rasterio(input_path)

    # Write as COG
    writer = CloudOptimizedWriter()
    writer.write_cog(data, output_path, **kwargs)  # type: ignore


def convert_to_geoparquet(input_path: str, output_path: str, **kwargs) -> None:
    """
    Convert vector data to GeoParquet.

    Args:
        input_path: Input vector file
        output_path: Output GeoParquet file
        **kwargs: Parquet options
    """
    if not PANDAS_AVAILABLE:
        raise ImportError("geopandas required for GeoParquet conversion")

    # Read input vector data
    gdf = gpd.read_file(input_path)

    # Write as GeoParquet
    writer = CloudOptimizedWriter()
    writer.write_geoparquet(gdf, output_path, **kwargs)


def convert_to_zarr(input_path: str, output_path: str, **kwargs) -> None:
    """
    Convert NetCDF/raster to Zarr format.

    Args:
        input_path: Input file (NetCDF, GeoTIFF, etc.)
        output_path: Output Zarr directory
        **kwargs: Zarr options
    """
    if not XARRAY_AVAILABLE:
        raise ImportError("xarray required for Zarr conversion")

    # Read input data
    if input_path.endswith(".nc"):
        data = xr.open_dataset(input_path)
    else:
        raster_data = rioxarray.open_rasterio(input_path)
        if hasattr(raster_data, "to_dataset"):
            data = raster_data.to_dataset(name="data")
        else:
            data = raster_data  # type: ignore

    # Write as Zarr
    writer = CloudOptimizedWriter()
    writer.write_zarr(data, output_path, **kwargs)


def optimize_for_cloud(
    input_path: str, output_dir: str, formats: List[str] = None
) -> Dict[str, str]:
    """
    Convert data to multiple cloud-optimized formats.

    Args:
        input_path: Input data file
        output_dir: Output directory
        formats: List of formats to create ('cog', 'geoparquet', 'zarr', 'flatgeobuf')

    Returns:
        Dictionary mapping format names to output paths
    """
    if formats is None:
        formats = ["geoparquet", "cog"]  # Default formats

    input_path_obj = Path(input_path)
    output_dir_obj = Path(output_dir)
    output_dir_obj.mkdir(exist_ok=True)

    results = {}

    # Determine input data type
    suffix = input_path_obj.suffix.lower()

    if suffix in [".shp", ".geojson", ".gpkg", ".gml"]:
        # Vector data
        if "geoparquet" in formats:
            output_path = output_dir_obj / f"{input_path_obj.stem}.parquet"
            convert_to_geoparquet(str(input_path_obj), str(output_path))
            results["geoparquet"] = str(output_path)

        if "flatgeobuf" in formats:
            output_path = output_dir_obj / f"{input_path_obj.stem}.fgb"
            gdf = gpd.read_file(str(input_path_obj))
            writer = CloudOptimizedWriter()
            writer.write_flatgeobuf(gdf, str(output_path))
            results["flatgeobuf"] = str(output_path)

    elif suffix in [".tif", ".tiff", ".jp2"]:
        # Raster data
        if "cog" in formats:
            output_path = output_dir_obj / f"{input_path_obj.stem}_cog.tif"
            convert_to_cog(str(input_path_obj), str(output_path))
            results["cog"] = str(output_path)

    elif suffix == ".nc":
        # NetCDF data
        if "zarr" in formats:
            output_path = output_dir_obj / f"{input_path_obj.stem}.zarr"
            convert_to_zarr(str(input_path_obj), str(output_path))
            results["zarr"] = str(output_path)

        if "cog" in formats:
            # Convert first variable to COG
            ds = xr.open_dataset(str(input_path_obj))
            first_var = list(ds.data_vars)[0]
            da = ds[first_var]
            if "x" in da.dims and "y" in da.dims:
                output_path = (
                    output_dir_obj / f"{input_path_obj.stem}_{first_var}_cog.tif"
                )
                writer = CloudOptimizedWriter()
                writer.write_cog(da, str(output_path))  # type: ignore
                results["cog"] = str(output_path)

    logger.info(f"Optimized {input_path_obj} for cloud access: {list(results.keys())}")
    return results
