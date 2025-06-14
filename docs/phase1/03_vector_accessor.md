# Vector Accessor (`pmg.vector`)

This document details the `pmg.vector` module, which will provide essential vector operations for PyMapGIS, primarily leveraging GeoPandas and Shapely 2.

## 1. Module Overview

*   **Purpose:** The `pmg.vector` module will act as an accessor or a collection of functions to perform common geospatial operations on vector data (typically `geopandas.GeoDataFrame` objects).
*   **Underlying Libraries:** Operations will be implemented using `GeoPandas` for data structures and spatial operations, and `Shapely 2` for its performance benefits in geometric operations.

## 2. Core Vector Operations

The following essential vector operations will be implemented in Phase 1. These functions will typically take one or more `GeoDataFrame` objects as input and return a new `GeoDataFrame` as output.

### `clip(gdf: GeoDataFrame, mask_geometry: Union[GeoDataFrame, Geometry]) -> GeoDataFrame`

*   **Description:** Clips a GeoDataFrame to the bounds of a mask geometry. Only the parts of features in `gdf` that fall within the `mask_geometry` will be returned.
*   **Parameters:**
    *   `gdf`: The input GeoDataFrame to be clipped.
    *   `mask_geometry`: The geometry (can be a Shapely geometry object or another GeoDataFrame whose union of geometries is used) to clip `gdf`.

### `overlay(gdf1: GeoDataFrame, gdf2: GeoDataFrame, how: str) -> GeoDataFrame`

*   **Description:** Performs a spatial overlay operation between two GeoDataFrames.
*   **Parameters:**
    *   `gdf1`, `gdf2`: The GeoDataFrames to be overlaid.
    *   `how`: The type of overlay operation. Supported values will include standard GeoPandas options: `'intersection'`, `'union'`, `'identity'`, `'symmetric_difference'`, `'difference'`.

### `buffer(gdf: GeoDataFrame, distance: float, **kwargs) -> GeoDataFrame`

*   **Description:** Creates buffer polygons around geometries in a GeoDataFrame.
*   **Parameters:**
    *   `gdf`: The input GeoDataFrame.
    *   `distance`: The buffer distance. The units of the distance are assumed to be the same as the CRS of the `gdf`.
    *   `**kwargs`: Additional arguments to be passed to GeoPandas' `buffer` method (e.g., `resolution`, `cap_style`, `join_style`).

### `spatial_join(left_gdf: GeoDataFrame, right_gdf: GeoDataFrame, op: str = 'intersects', how: str = 'inner') -> GeoDataFrame`

*   **Description:** Performs a spatial join between two GeoDataFrames.
*   **Parameters:**
    *   `left_gdf`, `right_gdf`: The GeoDataFrames to be joined.
    *   `op`: The spatial predicate for the join. Supported values will include standard GeoPandas options: `'intersects'`, `'contains'`, `'within'`. Defaults to `'intersects'`.
    *   `how`: The type of join. Supported values will include standard GeoPandas options: `'left'`, `'right'`, `'inner'`. Defaults to `'inner'`.

## 3. Integration

*   These operations might be exposed as methods on a PyMapGIS-specific vector data object (if one is introduced) or as standalone functions within the `pmg.vector` namespace (e.g., `pmg.vector.clip(...)`).
*   The primary data structure for vector data will be `geopandas.GeoDataFrame`.
```
