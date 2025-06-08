# Cloud-Native Analysis

Phase 3 aims to enhance PyMapGIS's capabilities for working with large-scale, cloud-hosted geospatial datasets.

## Key Objectives:

*   **Lazy Windowed Compute over Zarr:** Implement support for efficient processing of large Zarr datasets through lazy, windowed computations. This will leverage `xarray-multiscale` or similar libraries to enable analysis on data chunks without needing to load the entire dataset into memory.
*   **Optimized Cloud Data Access:** Further optimize reading and writing data to cloud storage backends (S3, GS, Azure Blob Storage).
