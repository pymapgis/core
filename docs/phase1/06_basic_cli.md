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
