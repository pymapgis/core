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
