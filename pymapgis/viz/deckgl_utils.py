"""
deck.gl Utilities for 3D Visualization in PyMapGIS.

This module provides functions to generate pydeck.Deck objects for visualizing
spatio-temporal data cubes and point clouds.

**Important Note on PyDeck Installation:**
PyDeck can be installed via pip:
  ```bash
  pip install pydeck
  ```
Ensure it's installed in your environment to use these visualization functions.
You'll also need a compatible Jupyter environment (Jupyter Notebook or JupyterLab
with the appropriate pydeck extension enabled) to render the maps.
"""

import pydeck
import xarray as xr
import numpy as np
import pandas as pd
from typing import Optional

# Define a default map style for deck.gl visualizations
DEFAULT_MAP_STYLE = "mapbox://styles/mapbox/light-v9"


def view_3d_cube(
    cube: xr.DataArray,
    time_index: int = 0,
    variable_name: str = "value",
    colormap: str = "viridis",
    opacity: float = 0.8,
    cell_size: int = 1000,
    elevation_scale: float = 100,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    zoom: Optional[float] = None,
    **kwargs_pydeck_layer,
) -> pydeck.Deck:
    """
    Visualizes a 2D slice of a 3D (time, y, x) xarray DataArray using deck.gl.

    This function creates a 2.5D visualization where the selected 2D slice
    is rendered as a GridLayer or HeatmapLayer, with cell values potentially
    mapped to elevation and color.

    Args:
        cube (xr.DataArray): Input 3D DataArray with dimensions (time, y, x).
                             Coordinates 'y' and 'x' should be present and represent
                             latitude and longitude if rendering on a map.
        time_index (int): Index of the time slice to visualize. Defaults to 0.
        variable_name (str): Name of the variable in the DataArray (cube.name).
                             Used for legend or if data needs to be extracted by name.
                             If None, defaults to "value".
        colormap (str): Colormap to use for visualizing the data.
                        Can be a string name of a Matplotlib colormap or a custom
                        list of [R,G,B,A] lists.
        opacity (float): Opacity of the layer (0 to 1). Defaults to 0.8.
        cell_size (int): Size of grid cells in meters. Defaults to 1000.
                         Used for GridLayer.
        elevation_scale (float): Scaling factor for elevation if `get_elevation` is used.
                                 Defaults to 100.
        latitude (Optional[float]): Central latitude for the map view.
                                    If None, inferred from data.
        longitude (Optional[float]): Central longitude for the map view.
                                     If None, inferred from data.
        zoom (Optional[float]): Initial zoom level of the map.
                                If None, PyDeck attempts to auto-fit.
        **kwargs_pydeck_layer: Additional keyword arguments to pass to the
                               pydeck.Layer (e.g., `GridLayer` or `HeatmapLayer`).

    Returns:
        pydeck.Deck: A pydeck.Deck object ready for display in a Jupyter environment.

    Raises:
        IndexError: If `time_index` is out of bounds.
        ValueError: If the cube is not 3-dimensional or lacks 'x', 'y' coordinates.
    """
    if cube.ndim != 3:
        raise ValueError("Input DataArray 'cube' must be 3-dimensional (time, y, x).")
    if "y" not in cube.coords or "x" not in cube.coords:
        raise ValueError("Cube must have 'y' and 'x' coordinates.")

    # Select the 2D slice for the given time index
    try:
        spatial_slice = cube.isel(time=time_index)
    except IndexError:
        raise IndexError(
            f"time_index {time_index} is out of bounds for time dimension of size {cube.shape[0]}."
        )

    # Convert the xarray DataArray slice to a Pandas DataFrame suitable for PyDeck
    # PyDeck layers often expect 'latitude', 'longitude' columns or specific geometry.
    # For GridLayer/HeatmapLayer, a list of [longitude, latitude, value] can be used.
    df = spatial_slice.to_dataframe(
        name=variable_name if variable_name else "value"
    ).reset_index()

    # Assuming 'y' is latitude and 'x' is longitude
    df.rename(columns={"y": "latitude", "x": "longitude"}, inplace=True)

    # Ensure the value column is not NaN for pydeck layers that require valid numbers
    value_col = variable_name if variable_name else "value"
    df = df.dropna(subset=["latitude", "longitude", value_col])
    if df.empty:
        raise ValueError(
            "DataFrame is empty after dropping NaNs from coordinates or value column. Cannot visualize."
        )

    # Determine view state if not fully provided
    if latitude is None:
        latitude = df["latitude"].mean()
    if longitude is None:
        longitude = df["longitude"].mean()
    if zoom is None:
        # Basic auto-zoom heuristic (very rough)
        lat_span = df["latitude"].max() - df["latitude"].min()
        lon_span = df["longitude"].max() - df["longitude"].min()
        if lat_span == 0 and lon_span == 0:  # Single point
            zoom = 12
        else:
            # This is a very simplified zoom calculation. PyDeck often does this better.
            # Based on deck.gl's WebMercatorViewport.fitBounds logic (conceptual)
            import math

            max_span = max(lat_span, lon_span)
            if max_span > 0:
                zoom = math.log2(360 / max_span) - 1  # Rough global scale to span
                zoom = max(0, min(zoom, 18))  # Clamp zoom
            else:  # Should not happen if df is not empty and spans are zero (single point)
                zoom = 10

    initial_view_state = pydeck.ViewState(
        latitude=latitude,
        longitude=longitude,
        zoom=zoom if zoom is not None else 6,  # Default zoom if still None
        pitch=45,  # Tilt the view for a 2.5D perspective
        bearing=0,
    )

    # Create a PyDeck GridLayer by default
    # Users can pass 'type' in kwargs_pydeck_layer to change layer type
    layer_type = kwargs_pydeck_layer.pop("type", "GridLayer")

    if layer_type == "GridLayer":
        layer = pydeck.Layer(
            "GridLayer",
            data=df,
            get_position="[longitude, latitude]",
            get_elevation=value_col,  # Map data value to elevation
            get_fill_color=f"{value_col} / {df[value_col].max()} * 255",  # Example: scale color by value
            # Colormap usage with GridLayer is more complex, often involves pre-calculating colors
            # or using deck.gl expressions if supported by pydeck for get_fill_color.
            # For simplicity, this example maps value to a shade of a single color or uses a fixed color.
            # A more advanced version would use a colormap function.
            # Example fixed color: get_fill_color=[255,0,0,150]
            # Or use pydeck's built-in color scales if applicable or pass pre-computed colors.
            # For now, let's use a simple intensity-based color (e.g., shades of blue based on value)
            # The expression below assumes value_col is normalized (0-1) then scaled to 255 for color component.
            # This needs careful handling of data range.
            # Example: color_range for HeatmapLayer, or manually create color mapping for GridLayer.
            # Let's use a simpler fixed color and map elevation to value.
            # Color can be: [R, G, B, A] or a deck.gl color expression string.
            # pydeck.types.Color can also be used.
            # Using a simple color scale based on value:
            # fill_color_scaled = df[value_col] / df[value_col].max()
            # df['color_r'] = fill_color_scaled * 255
            # df['color_g'] = (1 - fill_color_scaled) * 255
            # df['color_b'] = 120
            # get_fill_color = '[color_r, color_g, color_b, 200]' # Use precomputed color columns
            # This is too complex for default. Let's use a fixed color or simple expression.
            # Simpler: use elevation for value, and a fixed color or simple ramp based on elevation
            # `color_range` is typical for HeatmapLayer, not directly for GridLayer's get_fill_color.
            # We can use an expression if values are in a known range e.g. 0-255.
            # If not, we might need to normalize or bin data to apply colormaps.
            # For now, this is a placeholder for more advanced color mapping.
            # A common pattern is to use `get_elevation` for the value and a fixed/simple color.
            pickable=True,
            extruded=True,
            cell_size=cell_size,  # In meters
            elevation_scale=elevation_scale,
            opacity=opacity,
            **kwargs_pydeck_layer,
        )
    elif layer_type == "HeatmapLayer":
        layer = pydeck.Layer(
            "HeatmapLayer",
            data=df,
            get_position="[longitude, latitude]",
            get_weight=value_col,  # Map data value to heatmap intensity
            opacity=opacity,
            # `color_range` is a common way to specify colormap for HeatmapLayer
            # Example: color_range=[[255,255,178,25],[254,204,92,85],[253,141,60,135],[240,59,32,185],[189,0,38,255]] (YlOrRd)
            **kwargs_pydeck_layer,
        )
    else:
        raise ValueError(
            f"Unsupported layer_type: {layer_type}. Choose 'GridLayer' or 'HeatmapLayer', or implement others."
        )

    deck_view = pydeck.Deck(
        layers=[layer],
        initial_view_state=initial_view_state,
        map_style=DEFAULT_MAP_STYLE,
        tooltip=(
            {"text": f"{value_col}: {{{value_col}}}"}
            if value_col in df.columns
            else None
        ),
    )
    return deck_view


def view_point_cloud_3d(
    points: np.ndarray,
    srs: str = "EPSG:4326",  # Assume WGS84 if not specified, affects map view
    point_size: int = 3,
    color: list = [255, 0, 0, 180],  # Default: Red
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    zoom: Optional[float] = None,
    **kwargs_pydeck_layer,
) -> pydeck.Deck:
    """
    Visualizes a point cloud using deck.gl's PointCloudLayer.

    Args:
        points (np.ndarray): NumPy structured array with at least 'X', 'Y', 'Z' fields.
                             Additional fields like 'Red', 'Green', 'Blue' (0-255) can be
                             used for coloring if `get_color='[Red, Green, Blue]'` is passed
                             in `kwargs_pydeck_layer`.
        srs (str): Spatial Reference System of the input X,Y,Z coordinates.
                   Currently informational, as pydeck primarily expects WGS84 (lon/lat)
                   for its base map. If data is in a projected CRS, it might not align
                   correctly with the base map without re-projection prior to this call.
                   This function assumes X=longitude, Y=latitude for map alignment.
        point_size (int): Size of points in pixels. Defaults to 3.
        color (list): Default color for points as [R, G, B, A] (0-255).
                      Defaults to red. Can be overridden by `get_color` in `kwargs_pydeck_layer`.
        latitude (Optional[float]): Central latitude for the map view. Inferred if None.
        longitude (Optional[float]): Central longitude for the map view. Inferred if None.
        zoom (Optional[float]): Initial zoom level. Auto-calculated if None.
        **kwargs_pydeck_layer: Additional keyword arguments for `pydeck.Layer('PointCloudLayer', ...)`.
                               Common ones: `get_normal=[0,0,1]` for lighting,
                               `get_color='[Red,Green,Blue,255]'` if color columns exist.

    Returns:
        pydeck.Deck: A pydeck.Deck object for display.

    Raises:
        ValueError: If `points` array does not have 'X', 'Y', 'Z' fields.
    """
    required_fields = ["X", "Y", "Z"]
    if not all(field in points.dtype.names for field in required_fields):
        raise ValueError(
            f"Input points array must have 'X', 'Y', 'Z' fields. Found: {points.dtype.names}"
        )

    # Convert structured array to DataFrame for PyDeck
    df = pd.DataFrame(points)
    # PyDeck expects 'position' as [longitude, latitude, altitude]
    # Assuming input X, Y, Z map to this.
    df["position"] = df.apply(lambda row: [row["X"], row["Y"], row["Z"]], axis=1)

    if df.empty:
        # Return an empty deck or raise error? For now, empty deck.
        return pydeck.Deck(
            initial_view_state=pydeck.ViewState(latitude=0, longitude=0, zoom=1)
        )

    # Determine view state
    if latitude is None:
        latitude = df["Y"].mean()
    if longitude is None:
        longitude = df["X"].mean()
    if zoom is None:
        # Basic auto-zoom heuristic (very rough)
        x_span = df["X"].max() - df["X"].min()
        y_span = df["Y"].max() - df["Y"].min()
        if x_span == 0 and y_span == 0:  # Single point effective
            zoom = 15
        else:
            import math

            max_span = max(x_span, y_span)
            if max_span > 0:
                zoom = (
                    math.log2(360 / max_span) - 1
                )  # Rough global scale to span (assuming degrees)
                zoom = max(0, min(zoom, 20))  # Clamp zoom
            else:
                zoom = 12

    initial_view_state = pydeck.ViewState(
        latitude=latitude,
        longitude=longitude,
        zoom=zoom,
        pitch=45,  # Tilt for 3D view
        bearing=0,
    )

    layer = pydeck.Layer(
        "PointCloudLayer",
        data=df,
        get_position="position",
        get_color=kwargs_pydeck_layer.pop(
            "get_color", color
        ),  # Use custom color accessor or default
        get_normal=kwargs_pydeck_layer.pop(
            "get_normal", [0, 0, 1]
        ),  # Default normal for basic lighting
        point_size=point_size,
        **kwargs_pydeck_layer,
    )

    deck_view = pydeck.Deck(
        layers=[layer],
        initial_view_state=initial_view_state,
        map_style=DEFAULT_MAP_STYLE,
        tooltip={"text": "X: {X}\nY: {Y}\nZ: {Z}"},  # Basic tooltip
    )
    return deck_view
