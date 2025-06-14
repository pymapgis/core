# 3D Visualization with deck.gl

PyMapGIS integrates with `pydeck` to offer interactive 3D and 2.5D visualizations directly within Jupyter environments. This is particularly useful for visualizing point clouds and spatio-temporal raster data cubes.

## 1. Prerequisites

- **`pydeck` Library:** Install `pydeck` for deck.gl support:
  ```bash
  pip install pydeck
  ```
- **Jupyter Environment:** For rendering, you'll need Jupyter Notebook or JupyterLab.
    - **JupyterLab:** You might need to install the JupyterLab extension for pydeck:
      ```bash
      jupyter labextension install @deck.gl/jupyter-widget
      ```
    - **Jupyter Notebook:** Ensure widgets are enabled:
      ```bash
      jupyter nbextension enable --py --sys-prefix widgetsnbextension
      ```
- **Mapbox API Token (Optional):** PyDeck uses Mapbox for base maps by default. You might need to set a Mapbox API token as an environment variable (`MAPBOX_API_KEY`) for some base map styles if you encounter issues or use it frequently. However, some default styles work without an explicit token for limited use.

## 2. Visualizing Point Clouds (3D)

If you have point cloud data (e.g., from a LAS/LAZ file loaded via `pymapgis.read()` or `pymapgis.pointcloud` module), you can visualize it in 3D.

```python
import pymapgis as pmg
import pymapgis.viz as pmg_viz # Contains deck.gl utilities
import numpy as np

# Example: Create a sample point cloud NumPy array
# (In a real scenario, load this from a LAS/LAZ file using pmg.read())
points_data = np.array([
    (13.3886, 52.5163, 10.0, 255, 0, 0, 150), # Berlin - Red
    (13.3890, 52.5160, 12.5, 0, 255, 0, 150), # Berlin - Green
    (13.3882, 52.5157, 11.0, 0, 0, 255, 150), # Berlin - Blue
    (2.3522, 48.8566, 15.0, 255, 255, 0, 180), # Paris - Yellow
    (2.3525, 48.8563, 17.0, 255, 0, 255, 180)  # Paris - Magenta
], dtype=[('X', float), ('Y', float), ('Z', float),
          ('Red', np.uint8), ('Green', np.uint8), ('Blue', np.uint8), ('Alpha', np.uint8)])

# Ensure your X, Y coordinates are typically longitude and latitude for map alignment.
# Z is elevation/height.

try:
    # Create a 3D point cloud view
    # The 'get_color' argument uses field names from the NumPy array.
    deck_view_points = pmg_viz.view_point_cloud_3d(
        points_data,
        point_size=5,
        get_color='[Red, Green, Blue, Alpha]', # Use R,G,B,A columns for color
        # You can set initial view parameters, otherwise they are inferred
        latitude=50.5, # Centroid of Europe (approx)
        longitude=8.0,
        zoom=3.5
    )

    # To display in Jupyter:
    # deck_view_points.show()
    # Or, if it's the last line in a cell:
    # deck_view_points

    print("Point cloud deck.gl view object created. Call .show() in Jupyter to display.")
    # For automated environments, we can't .show(). We can check its properties.
    assert deck_view_points is not None
    assert len(deck_view_points.layers) == 1
    assert deck_view_points.layers[0].type == 'PointCloudLayer'
    print(f"Layer type: {deck_view_points.layers[0].type}")
    print(f"Initial view state latitude: {deck_view_points.initial_view_state.latitude}")


except ImportError:
    print("pydeck is not installed. Please install it: pip install pydeck")
except Exception as e:
    print(f"An error occurred creating point cloud view: {e}")

```

## 3. Visualizing Spatio-Temporal Cubes (2.5D)

A 3D spatio-temporal data cube (e.g., time, y, x) created with `pymapgis.raster.create_spatiotemporal_cube` can be visualized one time-slice at a time. This creates a 2.5D view where the values of the selected slice can be mapped to elevation and/or color on a grid.

```python
import pymapgis.raster as pmg_raster
# pmg_viz already imported
import xarray as xr
import numpy as np
import pandas as pd

# Example: Create a sample spatio-temporal cube
y_coords = np.arange(52.50, 52.52, 0.005) # Latitudes (e.g., Berlin area)
x_coords = np.arange(13.38, 13.40, 0.005) # Longitudes
times = pd.to_datetime(['2023-08-01T12:00:00', '2023-08-01T13:00:00'])

data_t1 = np.random.rand(len(y_coords), len(x_coords)) * 100 # e.g., sensor readings
data_t2 = np.random.rand(len(y_coords), len(x_coords)) * 120

da1 = xr.DataArray(data_t1, coords={'y': y_coords, 'x': x_coords}, dims=['y', 'x'], name="measurement")
da2 = xr.DataArray(data_t2, coords={'y': y_coords, 'x': x_coords}, dims=['y', 'x'], name="measurement")

# Ensure they have CRS if they are georeferenced for map alignment
# da1.rio.write_crs("epsg:4326", inplace=True)
# da2.rio.write_crs("epsg:4326", inplace=True)

cube = pmg_raster.create_spatiotemporal_cube([da1, da2], times)

try:
    # View the first time slice (time_index=0)
    deck_view_cube = pmg_viz.view_3d_cube(
        cube,
        time_index=0,
        variable_name="measurement", # Matches the 'name' of the DataArrays
        cell_size=30,          # Size of grid cells in meters (approx for lat/lon)
        elevation_scale=1,     # Scale factor for height
        opacity=0.7,
        # Optional: Provide specific view parameters
        latitude=y_coords.mean(),
        longitude=x_coords.mean(),
        zoom=11
    )

    # To display in Jupyter:
    # deck_view_cube.show()
    # Or, if it's the last line in a cell:
    # deck_view_cube

    print("\nSpatio-temporal cube deck.gl view object created. Call .show() in Jupyter.")
    assert deck_view_cube is not None
    assert len(deck_view_cube.layers) == 1
    assert deck_view_cube.layers[0].type == 'GridLayer' # Default
    print(f"Layer type: {deck_view_cube.layers[0].type}")
    print(f"Initial view state latitude: {deck_view_cube.initial_view_state.latitude}")


    # Example using HeatmapLayer instead
    # deck_view_heatmap = pmg_viz.view_3d_cube(
    #     cube,
    #     time_index=1,
    #     variable_name="measurement",
    #     type="HeatmapLayer", # Specify layer type
    #     opacity=0.9
    # )
    # deck_view_heatmap.show()

except ImportError:
    print("pydeck is not installed. Please install it: pip install pydeck")
except Exception as e:
    print(f"An error occurred creating cube view: {e}")

```

## Customization

Both `view_point_cloud_3d` and `view_3d_cube` accept `**kwargs_pydeck_layer` which are passed directly to the `pydeck.Layer` constructor. This allows for extensive customization of the layer's appearance and behavior. Refer to the [PyDeck Layer documentation](https://deck.gl/docs/api-reference/pydeck/layer) and the [deck.gl website](https://deck.gl/docs/api-reference/layers) for available layer types and properties.

For example, for `PointCloudLayer`, you can pass `get_normal='[normX, normY, normZ]'` if your point data has normal vector attributes, or for `GridLayer`, you can customize `color_range` or `color_domain` (though color mapping might require data preprocessing for complex colormaps).
```
