# Phase 1 Documentation

This section provides detailed documentation for Phase 1 of PyMapGIS development. Phase 1 focuses on establishing the core MVP (Minimum Viable Product) of the PyMapGIS library.

The following documents outline the key components and functionalities to be implemented in this phase:

*   [Basic Package Structure & Configuration](./01_basic_package_structure_and_configuration.md)
*   [Universal IO (`pmg.read()`)](./02_universal_io.md)
*   [Vector Accessor (`pmg.vector`)](./03_vector_accessor.md)
*   [Raster Accessor (`pmg.raster`)](./04_raster_accessor.md)
*   [Interactive Maps (`.map()` and `.explore()`)](./05_interactive_maps.md)
*   [Basic CLI (`pmg.cli`)](./06_basic_cli.md)
*   [FastAPI `pmg.serve()`](./07_fastapi_serve.md)

These documents are intended to guide developers in implementing the foundational features of PyMapGIS.

---

# Basic Package Structure & Configuration

This document outlines the foundational setup for the PyMapGIS project, covering the repository structure, package configuration, settings management, and CI/CD pipeline for Phase 1.

## 1. GitHub Repository Setup

*   **Initialize Repository:** Create a new public GitHub repository.
*   **`pyproject.toml`:** Choose and configure either Poetry or PDM for dependency management and packaging. This file will define project metadata, dependencies, and build system settings.
*   **`.gitignore`:** Add a comprehensive `.gitignore` file to exclude common Python, IDE, and OS-specific files from version control.
*   **`LICENSE`:** Include an MIT License file.
*   **Basic Package Directory Structure:** Create the main package directory `pymapgis/` with the following initial sub-modules (as empty `__init__.py` files or basic placeholders):
    *   `pymapgis/vector/`
    *   `pymapgis/raster/`
    *   `pymapgis/viz/`
    *   `pymapgis/serve/`
    *   `pymapgis/ml/`
    *   `pymapgis/cli/`
    *   `pymapgis/plugins/`

## 2. Settings Management (`pmg.settings`)

*   **Implementation:** Implement `pmg.settings` using `pydantic-settings`.
*   **Session-Specific Configurations:** Allow for session-specific configurations, primarily:
    *   `cache_dir`: The directory for storing cached data.
    *   `default_crs`: The default Coordinate Reference System to be used.
*   **Configuration Overrides:** Enable settings to be overridden via:
    *   Environment variables (e.g., `PYMAPGIS_CACHE_DIR`).
    *   A `.pymapgis.toml` file in the user's home directory or project root.

## 3. CI/CD with GitHub Actions

*   **Workflow Setup:** Configure basic GitHub Actions workflows for:
    *   **Testing:** Automatically run the test suite (e.g., using `pytest`) on every push and pull request to the main branches.
    *   **Linting:** Enforce code style (e.g., using Black, Flake8) to maintain code quality.
    *   **Type Checking:** Perform static type checking (e.g., using MyPy) to catch type errors early.
```

---

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

---

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

---

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

---

# Interactive Maps (`.map()` and `.explore()`)

PyMapGIS will integrate with [Leafmap](https://leafmap.org/) to provide easy-to-use interactive mapping capabilities for visualizing geospatial data (both vector and raster) directly within a Jupyter environment or similar interactive Python console.

## 1. Integration with Leafmap

*   **Core Library:** Leafmap, built upon ipyleaflet and folium, will be the primary engine for generating interactive maps.
*   **Purpose:** To allow users to quickly visualize `GeoDataFrame`s and `xarray.DataArray`s (or `Dataset`s) on an interactive map.

## 2. Key Visualization Methods

PyMapGIS data objects (or accessors associated with them) will provide two main methods for interactive visualization:

### `.map()` Method

*   **Purpose:** To create a more persistent `Leafmap.Map` object associated with the PyMapGIS data object. This allows for a map to be created and then iteratively updated or have more layers added to it.
*   **Interface (Conceptual):**
    ```python
    # For a GeoDataFrame object (or accessor)
    # m = geo_dataframe.pmg.map(**kwargs)
    # m.add_basemap(...)
    # m.add_vector(other_gdf)

    # For an xarray.DataArray object (or accessor)
    # m = data_array.pmg.map(**kwargs)
    # m.add_raster(other_raster_data_array)
    ```
*   **Behavior:**
    *   When called on a `GeoDataFrame`, it would add that `GeoDataFrame` to a new or existing Leafmap `Map` instance.
    *   When called on an `xarray.DataArray`, it would add that raster layer to a new or existing Leafmap `Map` instance.
    *   The method should return the `Leafmap.Map` instance so it can be further manipulated or displayed.
*   **Customization:** `**kwargs` can be passed to customize the map appearance and layer properties (e.g., basemap, layer styling for vectors, colormap for rasters).

### `.explore()` Method

*   **Purpose:** To provide a quick, ad-hoc way to generate an interactive Leaflet map for a single geospatial object with sensible defaults. This is meant for rapid exploration rather than building complex maps.
*   **Interface (Conceptual):**
    ```python
    # For a GeoDataFrame object (or accessor)
    # geo_dataframe.pmg.explore(**kwargs)

    # For an xarray.DataArray object (or accessor)
    # data_array.pmg.explore(**kwargs)
    ```
*   **Behavior:**
    *   This method will directly render an interactive map displaying the data object it's called upon.
    *   It will create a new `Leafmap.Map` instance internally and display it.
    *   It's a convenience wrapper around `.map()` with immediate display and less emphasis on returning the map object for further modification, though it might still return it.
*   **Customization:** `**kwargs` can be passed to Leafmap for quick customization (e.g., `tiles`, `cmap`, `popup` fields for vectors).

## 3. Underlying Implementation

*   These methods will internally call appropriate Leafmap functions:
    *   For vector data: `Map.add_gdf()` or `Map.add_vector()`.
    *   For raster data: `Map.add_raster()` or `Map.add_cog_layer()` (if dealing with COGs directly).
*   Sensible defaults for styling, popups (for vector data), and raster rendering (e.g., colormaps) will be applied but should be overridable.

## 4. Requirements

*   PyMapGIS will have `leafmap` as a core dependency for these visualization features.
*   Users will need to be in an environment that can render ipyleaflet maps (e.g., Jupyter Notebook, JupyterLab).
```

---

# Basic CLI (`pmg.cli`)

This document describes the basic Command Line Interface (CLI) for PyMapGIS, implemented within the `pmg.cli` module. The CLI provides utility functions for managing PyMapGIS and interacting with geospatial data from the terminal.

## 1. Module Overview

*   **Purpose:** To offer a set of simple command-line tools for common tasks related to PyMapGIS.
*   **Implementation:** Likely built using a library like `Typer` or `Click` for robust CLI argument parsing and command structuring.
*   **Entry Point:** The CLI will be accessible via a main command, e.g., `pymapgis` or `pmg`.

## 2. Core CLI Commands (Phase 1)

The following core commands will be implemented in Phase 1:

### `pymapgis info`

*   **Purpose:** Display basic information about the PyMapGIS installation, its dependencies, and configuration.
*   **Output (Example):**
    ```
    PyMapGIS Version: 0.1.0
    Installation Path: /path/to/pymapgis
    Python Version: 3.9.x
    Cache Directory: /home/user/.cache/pymapgis
    Default CRS: EPSG:4326
    Core Dependencies:
      - GeoPandas: 1.x.x
      - RasterIO: 1.x.x
      - Xarray: 0.x.x
      - Leafmap: 0.x.x
      - FastAPI: 0.x.x
      - fsspec: 202x.x.x
    ```
*   **Functionality:** This command will gather version information from PyMapGIS and its key dependencies, and display current settings like `cache_dir` and `default_crs`.

### `pymapgis cache`

*   **Purpose:** Interact with the PyMapGIS file cache (managed by `fsspec`).
*   **Subcommands (Initial for Phase 1 - more in Phase 2):
    *   `pymapgis cache dir`: Display the path to the cache directory.
        *   *(Note: More advanced cache management like `clear`, `list`, `info` might be deferred to Phase 2 as per the roadmap, but `dir` is a simple start.)*
*   **Example Usage:**
    ```bash
    $ pymapgis cache dir
    /home/user/.cache/pymapgis
    ```

### `pymapgis rio` (Pass-through)

*   **Purpose:** Provide a convenient pass-through to `rasterio`'s CLI (`rio`). This allows users to leverage `rio` commands without needing to separately manage its installation or path, assuming `rasterio` is a core dependency of PyMapGIS.
*   **Functionality:** Any arguments passed after `pymapgis rio` will be directly forwarded to the `rio` command.
*   **Example Usage:**
    ```bash
    $ pymapgis rio info my_raster.tif
    # Equivalent to running: rio info my_raster.tif

    $ pymapgis rio calc "(A - B) / (A + B)" --name A=band1.tif --name B=band2.tif output_ndvi.tif
    # Equivalent to running: rio calc ...
    ```
*   **Implementation Note:** This requires finding the `rio` executable bundled with the `rasterio` Python package or ensuring `rio` is in the system's PATH when PyMapGIS's environment is active.

## 3. Future Enhancements

*   Phase 2 will introduce more sophisticated cache management commands (`pymapgis cache info`, `pymapgis cache clear`) and plugin management commands.
```

---

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

---

# PyMapGIS Phase 2 Documentation

This section provides documentation for the features and enhancements planned for PyMapGIS Phase 2 (v0.2).

Phase 2 focuses on improving cache management, introducing a plugin system, enhancing the CLI, and expanding documentation with practical cookbook examples.

## Key Features in Phase 2:

- **[Cache Management](./01_cache_management.md)**: Tools and APIs for managing the data cache effectively.
- **[Plugin System](./02_plugin_system.md)**: An extensible plugin architecture for drivers, algorithms, and visualization backends.
- **[Enhanced CLI](./03_enhanced_cli.md)**: New CLI commands like `pymapgis doctor` and improved plugin management.
- **[Documentation & Cookbook](./04_documentation_and_cookbook.md)**: Comprehensive documentation using MkDocs-Material and practical cookbook examples.

These documents aim to guide developers in implementing these features.

---

# Phase 2: Cache Management

This document outlines the requirements for cache management in PyMapGIS Phase 2.

## CLI Helpers

- `pymapgis cache info`: Display statistics about the cache, such as total size, number of files, and cache location.
- `pymapgis cache clear`: Clear all items from the cache. Optionally, allow clearing specific files or files older than a certain date.

## API Helpers

- `pmg.cache.stats()`: Programmatic access to cache statistics.
- `pmg.cache.purge()`: Programmatic way to clear all or parts of the cache.

---

# Phase 2: Plugin System

This document describes the plugin system to be implemented in PyMapGIS Phase 2.

## Plugin Registry

- Implement a plugin registry using Python entry points. This allows third-party packages to extend PyMapGIS functionality.

## Base Interfaces

Define base interfaces for the following extension points:
- `pymapgis.drivers`: For adding new data format drivers.
- `pymapgis.algorithms`: For adding new processing algorithms.
- `pymapgis.viz_backends`: For adding new visualization backends.

## Cookie-Cutter Templates

- Provide cookie-cutter templates to simplify the development of new plugins. These templates should include basic file structure, example code, and test setups.

---

# Phase 2: Enhanced CLI

This document details the enhancements for the PyMapGIS Command Line Interface (CLI) in Phase 2.

## `pymapgis doctor`

- Implement `pymapgis doctor` command.
- This command will perform checks on the user's environment to ensure all dependencies are correctly installed and configured.
- It should report any issues found and suggest potential solutions.

## `pymapgis plugin`

- Enhance the `pymapgis plugin` command for managing third-party plugins.
- Subcommands could include:
    - `list`: List installed plugins.
    - `install`: Install a new plugin (e.g., from PyPI or a git repository).
    - `uninstall`: Uninstall a plugin.
    - `info`: Display information about a specific plugin.

---

# Phase 2: Documentation & Cookbook

This document outlines the plan for documentation and example cookbooks for PyMapGIS Phase 2.

## MkDocs-Material Setup

- Set up MkDocs-Material for generating the project documentation.
- Include a gallery of examples to showcase PyMapGIS capabilities. This could involve using something like `mkdocs-gallery`.

## Cookbook Examples

Create "Cookbook" style examples for common geospatial workflows. These should be detailed, step-by-step guides.
Initial cookbook examples to include:
- **Site Selection Analysis**: A tutorial on how to use PyMapGIS for identifying suitable locations based on multiple criteria.
- **Sentinel-2 NDVI Calculation**: A guide on fetching Sentinel-2 satellite imagery and calculating the Normalized Difference Vegetation Index (NDVI).
- **Isochrones Generation**: An example of how to generate isochrones (reachability maps) for a given location and travel mode.

---

# Phase 3: Advanced Capabilities (v0.3+)

This section outlines the advanced capabilities planned for Phase 3 (v0.3 and beyond) of PyMapGIS. These features aim to expand the library's functionality into more specialized areas of geospatial analysis.

## Features

- [Cloud-Native Analysis](./01_cloud_native_analysis.md)
- [GeoArrow DataFrames](./02_geoarrow_dataframes.md)
- [Network Analysis](./03_network_analysis.md)
- [Point Cloud Support](./04_point_cloud_support.md)
- [3D & Time Streaming Sensor Ingestion](./05_3d_time_streaming_sensor_ingestion.md)
- [QGIS Plugin](./06_qgis_plugin.md)

---

# Cloud-Native Analysis

Phase 3 aims to enhance PyMapGIS's capabilities for working with large-scale, cloud-hosted geospatial datasets.

## Key Objectives:

*   **Lazy Windowed Compute over Zarr:** Implement support for efficient processing of large Zarr datasets through lazy, windowed computations. This will leverage `xarray-multiscale` or similar libraries to enable analysis on data chunks without needing to load the entire dataset into memory.
*   **Optimized Cloud Data Access:** Further optimize reading and writing data to cloud storage backends (S3, GS, Azure Blob Storage).

---

# GeoArrow DataFrames

To improve performance and interoperability, Phase 3 includes plans to integrate GeoArrow.

## Key Objectives:

*   **Integrate `geoarrow-py`:** Once `geoarrow-py` reaches a mature state, it will be integrated into PyMapGIS.
*   **Efficient Data Interchange:** Leverage GeoArrow for efficient in-memory representation of geospatial vector data.
*   **Zero-Copy Slicing:** Enable zero-copy slicing and data access for improved performance in vector operations.
*   **Interoperability:** Enhance interoperability with other systems and libraries that support the Apache Arrow format.

---

# Network Analysis

Phase 3 will introduce network analysis capabilities into PyMapGIS, enabling routing and accessibility analyses.

## Key Objectives:

*   **`pmg.network` Module:** Develop a new `pmg.network` module dedicated to network analysis functionalities.
*   **Shortest Path Calculations:** Implement algorithms for finding the shortest path between points in a network.
*   **Isochrones:** Implement functionality to generate isochrones (areas reachable within a given travel time or distance).
*   **Contraction Hierarchies:** Utilize contraction hierarchies or similar techniques for efficient routing on large networks.
*   **Data Integration:** Allow usage of common network data formats (e.g., OpenStreetMap data).

---

# Point Cloud Support

To broaden the scope of supported geospatial data types, Phase 3 will add support for point cloud data.

## Key Objectives:

*   **LAS/LAZ Data Support:** Implement reading and basic processing of point cloud data in LAS (LASer) and LAZ (compressed LAS) formats.
*   **PDAL Integration:** Leverage the PDAL (Point Data Abstraction Library) Python bindings for robust point cloud processing.
*   **Basic Operations:** Enable common point cloud operations such as filtering, tiling, and DEM generation.
*   **Visualization (Basic):** Explore options for basic 3D visualization of point clouds, potentially integrating with existing visualization backends.

---

# 3D & Time Streaming Sensor Ingestion

Phase 3 aims to incorporate capabilities for handling dynamic, multi-dimensional geospatial data, particularly from streaming sensors.

## Key Objectives:

*   **Spatio-Temporal Cubes:** Implement support for creating and analyzing spatio-temporal data cubes using `xarray`. This will allow for representing data with spatial dimensions (x, y, z) and a time dimension.
*   **deck.gl 3D Viewers:** Integrate `deck.gl` or similar libraries for advanced 3D visualization of spatio-temporal data.
*   **Kafka/MQTT Connectors:** Develop connectors for ingesting real-time data streams from sensor networks using protocols like Kafka or MQTT.
*   **Time Series Analysis:** Provide basic tools for time series analysis on the ingested sensor data.

---

# QGIS Plugin

To make PyMapGIS functionalities accessible to a wider audience, including those who prefer a GUI-based workflow, Phase 3 includes the development of a QGIS plugin.

## Key Objectives:

*   **Core Functionality Exposure:** Expose key PyMapGIS processing functions and algorithms through the QGIS interface.
*   **User-Friendly Interface:** Design an intuitive user interface within QGIS for configuring and running PyMapGIS operations.
*   **Data Integration:** Ensure seamless integration with QGIS data layers (vector, raster).
*   **Processing Provider:** Implement the plugin as a QGIS Processing provider for easy integration into QGIS workflows and models.
*   **Documentation and Examples:** Provide clear documentation and examples for using the PyMapGIS QGIS plugin.
