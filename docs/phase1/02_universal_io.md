# Universal IO (`pmg.read()`)

This document describes the `pmg.read()` function, a core component of PyMapGIS designed for seamless ingestion of various geospatial data formats from diverse sources.

## 1. Function Overview

*   **Purpose:** The `pmg.read()` function aims to provide a single, unified interface for reading different types of geospatial data, abstracting away the underlying libraries and data source complexities.
*   **Signature (Conceptual):** `pmg.read(path_or_url: str, **kwargs) -> Union[GeoDataFrame, xr.DataArray]`

## 2. Supported Data Formats

### Vector Formats

The initial implementation in Phase 1 will support the following vector formats:

*   **Shapefile (`.shp`)**
*   **GeoJSON (`.geojson`)**
*   **GeoPackage (`.gpkg`)**
*   **Parquet (with GeoParquet specifications)**

### Raster Formats

The initial implementation in Phase 1 will support the following raster formats:

*   **Cloud Optimized GeoTIFF (COG)**
*   **NetCDF (`.nc`)** (especially for xarray compatibility)

## 3. Data Sources

`pmg.read()` will support reading data from:

*   **Local Files:** Absolute or relative paths to files on the local filesystem.
*   **Remote URLs:**
    *   HTTPS URLs (e.g., `https://example.com/data.geojson`)
    *   Amazon S3 URIs (e.g., `s3://bucket-name/path/to/data.shp`)
    *   Google Cloud Storage URIs (e.g., `gs://bucket-name/path/to/data.tif`)
*   **Underlying Library:** `fsspec` will be used to handle file system operations, enabling access to a wide range of local and remote storage backends.

## 4. Transparent File Caching

*   **Mechanism:** Implement transparent file caching for remote datasets to improve performance on subsequent reads of the same data.
*   **Implementation:** Leverage `fsspec`'s file caching capabilities (e.g., `fsspec.filesystem('filecache', ...)`).
*   **Configuration:** The cache directory will be configurable via `pmg.settings.cache_dir`.
*   **Behavior:** When a remote URL is accessed for the first time, it will be downloaded and stored in the cache directory. Subsequent calls to `pmg.read()` with the same URL will use the cached version, provided it's still valid (cache expiry/validation mechanisms might be basic in v0.1).

## 5. Return Types

*   For vector data, `pmg.read()` will typically return a `geopandas.GeoDataFrame`.
*   For raster data, `pmg.read()` will typically return an `xarray.DataArray` (or `xarray.Dataset` for multi-band/multi-variable NetCDF).

## 6. Error Handling

*   Implement robust error handling for cases like unsupported file formats, invalid paths/URLs, network issues, and corrupted files.
```
