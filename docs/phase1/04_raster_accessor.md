# Raster Accessor (`pmg.raster`)

This document outlines the `pmg.raster` module, which will provide core raster operations for PyMapGIS, primarily utilizing `xarray` and `rioxarray`.

## 1. Module Overview

*   **Purpose:** The `pmg.raster` module is designed to offer functionalities for common raster data manipulations and analysis.
*   **Data Structures:** Raster data will primarily be handled as `xarray.DataArray` or `xarray.Dataset` objects, leveraging their powerful multi-dimensional data handling capabilities.
*   **Underlying Libraries:** `rioxarray` will be used as the primary engine for CRS management, reprojection, and other GIS-specific raster operations on top of `xarray`.

## 2. Core Raster Operations

The following core raster operations are planned for Phase 1.

### Reprojection

*   **Functionality:** Re-project a raster dataset from its original Coordinate Reference System (CRS) to a target CRS.
*   **Interface (Conceptual):**
    ```python
    # As a method on an xarray accessor
    # data_array.pmg.reproject(target_crs: str) -> xr.DataArray

    # Or as a standalone function
    # pmg.raster.reproject(data_array: xr.DataArray, target_crs: str) -> xr.DataArray
    ```
*   **Details:** This will use `rioxarray.reproject` or `rioxarray.reproject_match` internally. Users should be able to specify the target CRS as an EPSG code, WKT string, or Proj string.

### Basic Algebra

*   **Functionality:** Perform common band math and raster algebra operations.
*   **Normalized Difference (Example):** Implement a helper function or an accessor method for common indices like NDVI (Normalized Difference Vegetation Index).
    *   **Interface (Conceptual):**
        ```python
        # As a method on an xarray accessor, assuming bands are named or indexed
        # data_array.pmg.normalized_difference(band1: Union[str, int], band2: Union[str, int]) -> xr.DataArray

        # Or, if bands are explicitly passed (e.g., for multi-band DataArray)
        # dataset.pmg.normalized_difference(nir_band_name='NIR', red_band_name='RED') -> xr.DataArray
        ```
    *   **Formula:** `(band1 - band2) / (band1 + band2)`
*   **General Algebra:** Leverage `xarray`'s native element-wise operations (e.g., `+`, `-`, `*`, `/`) for custom algebra. The `pmg.raster` module might provide convenience functions or accessors to simplify these tasks where appropriate.

## 3. Integration

*   Raster operations will typically be exposed as methods via an `xarray` accessor (e.g., `data_array.pmg.operation()`) or as functions within the `pmg.raster` namespace (e.g., `pmg.raster.operation(...)`).
*   The primary data structure for raster data will be `xarray.DataArray` (for single-band) or `xarray.Dataset` (for multi-band).
*   Input rasters are expected to be read via `pmg.read()`, which would return appropriately structured `xarray` objects.
```
