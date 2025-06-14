import leafmap.leafmap as leafmap  # Common import pattern for leafmap
import geopandas as gpd
import xarray as xr
from typing import Union, Optional  # Added Optional
import numpy as np  # Added for type hints if needed by deckgl utils
import pydeck  # Added for type hints if needed by deckgl utils

# Import from deckgl_utils
from .deckgl_utils import view_3d_cube, view_point_cloud_3d

# Import accessors to register them
from .accessors import PmgVizAccessor

__all__ = [
    "explore",
    "plot_interactive",
    "map",  # Existing
    "view_3d_cube",
    "view_point_cloud_3d",  # New deck.gl utils
]


def explore(
    data: Union[gpd.GeoDataFrame, xr.DataArray, xr.Dataset],
    m: leafmap.Map = None,  # Added optional map instance for consistency with plot_interactive
    **kwargs,
) -> leafmap.Map:
    """
    Interactively explore a GeoDataFrame, xarray DataArray, or xarray Dataset on a Leafmap map.

    This function creates a new map (or uses an existing one if provided) and adds the data as a layer.
    The map is then displayed automatically in environments like Jupyter Notebooks/Lab.

    Args:
        data (Union[gpd.GeoDataFrame, xr.DataArray, xr.Dataset]): The geospatial data to visualize.
            - GeoDataFrame: Will be added as a vector layer.
            - DataArray/Dataset: Will be added as a raster layer.
        m (leafmap.Map, optional): An existing leafmap.Map instance to add the layer to.
            If None, a new map is created. Defaults to None.
        **kwargs: Additional keyword arguments passed to the underlying `leafmap` add method.
            - For `gpd.GeoDataFrame` (uses `m.add_gdf()`):
                Common kwargs include `layer_name` (str), `style` (dict for styling vector
                features, e.g., `{'color': 'red', 'fillOpacity': 0.5}`), `hover_style` (dict),
                `popup` (list of column names to show in popup), `tooltip` (str or list).
            - For `xr.DataArray` or `xr.Dataset` (uses `m.add_raster()`):
                Common kwargs include `layer_name` (str), `bands` (list of band indices or
                names, e.g., `[3, 2, 1]` for RGB from a multiband raster if using integer band numbers,
                or `['B4', 'B3', 'B2']` if bands have names), `cmap` (str, colormap name),
                `vmin` (float), `vmax` (float), `nodata` (float, value to treat as nodata).
                Note: For xarray objects, ensure they have CRS information (accessible via `data.rio.crs`).
                If CRS is missing, visualization might be incorrect or fail. A warning is printed
                if `data.rio.crs` is not found on a DataArray.

    Returns:
        leafmap.Map: The leafmap.Map instance with the added layer.
    """
    if m is None:
        m = leafmap.Map()

    if isinstance(data, gpd.GeoDataFrame):
        # Check if 'column' kwarg is more appropriate than 'layer_name' for choropleth-like viz
        # For general vector plotting, add_gdf is fine.
        # leafmap.add_vector might be more general if it handles GDFs.
        # Based on leafmap docs, add_gdf is specific and good.
        m.add_gdf(data, **kwargs)
    elif isinstance(data, (xr.DataArray, xr.Dataset)):
        # For xarray, add_raster is the method.
        # Ensure data has CRS if it's a raster, leafmap might require it.
        # rioxarray typically adds a .rio accessor with crs info.
        if isinstance(data, xr.DataArray):
            has_rio = hasattr(data, "rio")
            if not has_rio or getattr(data.rio, "crs", None) is None:
                print(
                    "Warning: xarray.DataArray does not have CRS information (e.g., via data.rio.crs). Visualization may be incorrect or map extent may not set properly."
                )
        elif isinstance(data, xr.Dataset):
            # For xarray.Dataset, CRS check is more complex as it can be per variable.
            # We rely on leafmap to handle this or the user to ensure variables being plotted have CRS.
            # A general note is in the main docstring.
            pass
        m.add_raster(data, **kwargs)
    else:
        raise TypeError(
            f"Unsupported data type: {type(data)}. "
            "Must be GeoDataFrame, xarray.DataArray, or xarray.Dataset."
        )

    # In Jupyter environments, displaying the map object usually renders it.
    # No explicit display call is needed here as the map object itself is displayed
    # when it's the last expression in a cell.
    return m


def plot_interactive(
    data: Union[gpd.GeoDataFrame, xr.DataArray, xr.Dataset],
    m: leafmap.Map = None,
    **kwargs,
) -> leafmap.Map:
    """
    Adds a GeoDataFrame, xarray DataArray, or xarray Dataset to an interactive Leafmap map.
    Also available as ``.map()``.

    This function is similar to `explore`, but it does not automatically display the map.
    It allows for adding multiple layers to a map instance before displaying it.

    Args:
        data (Union[gpd.GeoDataFrame, xr.DataArray, xr.Dataset]): The geospatial data to add.
        m (leafmap.Map, optional): An existing leafmap.Map instance to add the layer to.
            If None, a new map is created. Defaults to None.
        **kwargs: Additional keyword arguments passed to the underlying `leafmap` add method.
            Refer to the `explore` function's docstring for common `**kwargs` for
            `add_gdf` (for GeoDataFrames) and `add_raster` (for xarray objects).
            Ensure xarray objects have CRS information.

    Returns:
        leafmap.Map: The leafmap.Map instance with the added layer.
    """
    if m is None:
        m = leafmap.Map()

    # The core logic is identical to explore, just without the implicit display assumption.
    # Re-use the same logic but be clear that this function itself doesn't trigger display.
    if isinstance(data, gpd.GeoDataFrame):
        m.add_gdf(data, **kwargs)
    elif isinstance(data, (xr.DataArray, xr.Dataset)):
        if isinstance(data, xr.DataArray):
            has_rio = hasattr(data, "rio")
            if not has_rio or getattr(data.rio, "crs", None) is None:
                print(
                    "Warning: xarray.DataArray does not have CRS information (e.g., via data.rio.crs). Visualization may be incorrect or map extent may not set properly."
                )
        elif isinstance(data, xr.Dataset):
            # For xarray.Dataset, CRS check is more complex. See note in 'explore' function.
            pass
        m.add_raster(data, **kwargs)
    else:
        raise TypeError(
            f"Unsupported data type: {type(data)}. "
            "Must be GeoDataFrame, xarray.DataArray, or xarray.Dataset."
        )

    return m


# Alias for plot_interactive
map = plot_interactive
