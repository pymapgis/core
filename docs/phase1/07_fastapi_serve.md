# FastAPI `pmg.serve()`

This document describes the `pmg.serve` module and its primary function `pmg.serve()`, which is designed to expose geospatial data and analysis results as web micro-services (XYZ tile services, WMS) using FastAPI.

## 1. Module Overview

*   **Purpose:** To allow users to easily share their geospatial data or the results of their PyMapGIS analyses as standard web mapping services.
*   **Technology:** Built on [FastAPI](https://fastapi.tiangolo.com/) for creating high-performance web APIs.
*   **Core Functionality:** `pmg.serve(data: Union[GeoDataFrame, xr.DataArray, str], service_type: str = 'xyz', **options)`

## 2. `pmg.serve()` Function

*   **Description:** This function will take a geospatial data object (e.g., a `GeoDataFrame` loaded via `pmg.read()`, or an `xarray.DataArray` representing a raster) or a path to a file, and serve it as a web service.
*   **Parameters (Conceptual for Phase 1):
    *   `data`: The input geospatial data. This could be:
        *   A `geopandas.GeoDataFrame`.
        *   An `xarray.DataArray` (for raster data).
        *   A string path to a file that `pmg.read()` can understand (e.g., a GeoPackage, Shapefile, COG). The function would internally read this data.
    *   `service_type` (str): Specifies the type of web service to create. Initially, this might focus on:
        *   `'xyz'` (Tile Map Service for vector and raster)
        *   `'wms'` (Web Map Service - might be more complex and could be a stretch goal for v0.1 or lean towards v0.2 for full compliance)
    *   `**options`: Additional options for configuring the service, such as:
        *   `port` (int): Port to run the FastAPI server on (e.g., `8000`).
        *   `host` (str): Host address (e.g., `0.0.0.0` to make it accessible on the network).
        *   `name` (str): A name for the layer/service endpoint.
        *   Styling options for vector tiles (e.g., default color, fill, stroke).
        *   Colormap or band selection for raster tiles.

## 3. Service Types (Phase 1 Focus)

### XYZ Tile Service

*   **Vector Tiles:**
    *   For `GeoDataFrame` inputs, `pmg.serve()` could dynamically generate vector tiles (e.g., in MVT - Mapbox Vector Tile format).
    *   Libraries like `fastapi-mvt` or custom implementations using `mercantile` and `vtzero` (or similar) could be used.
    *   Endpoint example: `http://localhost:8000/layer_name/{z}/{x}/{y}.mvt`
*   **Raster Tiles:**
    *   For `xarray.DataArray` inputs (especially COGs or easily tileable rasters), `pmg.serve()` could dynamically generate raster tiles (e.g., PNGs).
    *   Libraries like `titiler` (or components from it) or custom implementations using `rio-tiler` could be leveraged.
    *   Endpoint example: `http://localhost:8000/layer_name/{z}/{x}/{y}.png`

### WMS (Web Map Service)

*   **Functionality:** Serve data according to OGC WMS standards. This typically involves `GetCapabilities`, `GetMap`, and optionally `GetFeatureInfo` requests.
*   **Complexity:** Implementing a fully compliant WMS can be involved. Phase 1 might offer a very basic WMS for raster data, potentially leveraging `rioxarray` or `xarray` capabilities with a FastAPI wrapper.
*   **Consideration:** Full WMS might be better suited for Phase 2 enhancements.

## 4. Usage Example (Conceptual)

```python
import pymapgis as pmg

# Load some vector data
gdf = pmg.read("my_data.geojson")

# Serve it as an XYZ vector tile service
# This would start a FastAPI server in the background or foreground
pmg.serve(gdf, service_type='xyz', name='my_vector_layer', port=8080)
# User can then access tiles at http://localhost:8080/my_vector_layer/{z}/{x}/{y}.mvt

# Load some raster data
raster = pmg.read("my_raster.tif")

# Serve it as an XYZ raster tile service
pmg.serve(raster, service_type='xyz', name='my_raster_layer', port=8081)
# User can then access tiles at http://localhost:8081/my_raster_layer/{z}/{x}/{y}.png
```

## 5. Technical Implementation Notes

*   The `pmg.serve()` function will likely start a `uvicorn` server programmatically to run the FastAPI application.
*   It needs to handle graceful startup and shutdown of the web service.
*   For simplicity in Phase 1, it might serve one layer at a time per `pmg.serve()` call, or manage multiple layers if a more complex API is designed within `pmg.serve` itself.
```
