# Extending PyMapGIS

PyMapGIS is designed to be extensible, allowing developers to add support for new data sources, processing functions, or even custom plotting capabilities. This guide provides an overview of how to extend PyMapGIS.

## Adding a New Data Source

The most common extension is adding a new data source. PyMapGIS uses a URI-based system to identify and manage data sources (e.g., `census://`, `tiger://`, `file://`).

### Steps to Add a New Data Source:

1.  **Define a URI Scheme**:
    Choose a unique URI scheme for your new data source (e.g., `mydata://`).

2.  **Create a Data Handler Module/Functions**:
    *   This is typically a new Python module (e.g., `pymapgis/mydata_source.py`) or functions within an existing relevant module.
    *   This module will contain the logic to:
        *   Parse parameters from the URI.
        *   Fetch data from the source (e.g., an API, a database, a set of files).
        *   Process/transform the raw data into a GeoDataFrame (or a Pandas DataFrame if non-spatial).
        *   Handle caching if the data is fetched remotely.

3.  **Register the Handler (Conceptual)**:
    Currently, PyMapGIS's `pmg.read()` function in `pymapgis/io/__init__.py` has a dispatch mechanism (e.g., if-elif-else block based on `uri.scheme`). You'll need to modify it to include your new scheme and call your handler.

    *Example (simplified view of `pymapgis/io/__init__.py` modification)*:
    ```python
    # In pymapgis/io/__init__.py (or a similar dispatch location)
    from .. import mydata_source # Your new module

    def read(uri_string: str, **kwargs):
        uri = urllib.parse.urlparse(uri_string)
        # ... other schemes ...
        elif uri.scheme == "mydata":
            return mydata_source.load_data(uri, **kwargs)
        # ...
    ```

4.  **Implement Caching (Optional but Recommended for Remote Sources)**:
    *   If your data source involves network requests, integrate with `pymapgis.cache`.
    *   You can use the `requests_cache` session provided by `pymapgis.cache.get_session()` or implement custom caching logic.

5.  **Write Tests**:
    *   Create tests for your new data source in the `tests/` directory.
    *   Test various parameter combinations, edge cases, and expected outputs.
    *   If it's a remote source, consider how to mock API calls for reliable testing.

### Example: A Simple File-Based Handler

Let's say you want to add a handler for a specific type of CSV file that always has 'latitude' and 'longitude' columns.

*   **URI Scheme**: `points_csv://`
*   **Handler (`pymapgis/points_csv_handler.py`)**:
    ```python
    import pandas as pd
    import geopandas as gpd
    from shapely.geometry import Point

    def load_points_csv(uri_parts, **kwargs):
        file_path = uri_parts.path
        df = pd.read_csv(file_path, **kwargs)
        geometry = [Point(xy) for xy in zip(df.longitude, df.latitude)]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
        return gdf
    ```
*   **Registration (in `pymapgis/io/__init__.py`)**:
    ```python
    # from .. import points_csv_handler # Add this import
    # ...
    # elif uri.scheme == "points_csv":
    #     return points_csv_handler.load_points_csv(uri, **kwargs)
    ```

## Adding New Processing Functions

If you want to add common geospatial operations or analyses that can be chained with PyMapGIS objects (typically GeoDataFrames):

1.  **Identify Where It Fits**:
    *   Could it be a standalone function in a utility module?
    *   Should it be an extension method on GeoDataFrames using the Pandas accessor pattern (e.g., `gdf.pmg.my_function()`)? This is often cleaner for chainable operations.

2.  **Implement the Function**:
    *   Ensure it takes a GeoDataFrame as input and returns a GeoDataFrame or other relevant Pandas/Python structure.
    *   Follow coding standards and include docstrings and type hints.

3.  **Accessor Pattern (Example)**:
    If you want to add `gdf.pmg.calculate_density()`:
    ```python
    # In a relevant module, e.g., pymapgis/processing.py
    import geopandas as gpd

    @gpd.GeoDataFrame.アクセスors.register("pmg") # Name your accessor
    class PmgAccessor:
        def __init__(self, gdf):
            self._gdf = gdf

        def calculate_density(self, population_col, area_col=None):
            gdf = self._gdf.copy()
            if area_col:
                gdf["density"] = gdf[population_col] / gdf[area_col]
            else:
                # Ensure area is calculated if not provided, requires appropriate CRS
                if gdf.crs is None:
                    raise ValueError("CRS must be set to calculate area for density.")
                gdf["density"] = gdf[population_col] / gdf.area
            return gdf
    ```
    Users could then call `my_gdf.pmg.calculate_density("population")`.

## Extending Plotting Capabilities

PyMapGIS's plotting is often a wrapper around libraries like Leafmap or Matplotlib (via GeoPandas).

1.  **Simple Plots**: You might add new methods to the `.plot` accessor similar to how `choropleth` is implemented in `pymapgis/plotting.py`.
2.  **Complex Visualizations**: For highly custom or complex visualizations, you might contribute directly to the underlying libraries or provide functions that help users prepare data for these libraries.

## General Guidelines

*   **Maintain Consistency**: Try to follow the existing patterns and API style of PyMapGIS.
*   **Documentation**: Always document new functionalities, both in code (docstrings) and in the user/developer documentation (`docs/`).
*   **Testing**: Comprehensive tests are crucial.

By following these guidelines, you can effectively extend PyMapGIS to meet new requirements and contribute valuable additions to the library.
