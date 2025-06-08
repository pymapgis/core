import leafmap.leafmap as leafmap # Common import pattern for leafmap
import geopandas as gpd
import xarray as xr
from typing import Union

__all__ = ["explore", "plot_interactive"]

def explore(
    data: Union[gpd.GeoDataFrame, xr.DataArray, xr.Dataset],
    m: leafmap.Map = None, # Added optional map instance for consistency with plot_interactive
    **kwargs
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
        **kwargs: Additional keyword arguments to be passed to the respective
            leafmap add method (`add_gdf` for GeoDataFrames, `add_raster` for xarray objects).
            Common kwargs include `layer_name`, `style`, `cmap`, `vmin`, `vmax`, etc.

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
        if isinstance(data, xr.DataArray) and data.rio.crs is None :
            if not (hasattr(data, 'rio') and data.rio.crs):
                 print("Warning: xarray.DataArray does not have CRS information via data.rio.crs. Visualization may be incorrect.")
        elif isinstance(data, xr.Dataset):
            # For Datasets, a specific data variable might need to be chosen by the user via kwargs
            # or leafmap handles it by picking the first suitable one.
            # Or, user might need to pass specific bands/variables if not handled by add_raster's kwargs.
            # We assume add_raster handles Dataset appropriately or user uses kwargs.
            # Example: m.add_raster(dataset, bands=['B4', 'B3', 'B2'])
            pass # No explicit check for dataset's CRS here, assume leafmap handles or user provides via kwargs

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
    **kwargs
) -> leafmap.Map:
    """
    Adds a GeoDataFrame, xarray DataArray, or xarray Dataset to an interactive Leafmap map.

    This function is similar to `explore`, but it does not automatically display the map.
    It allows for adding multiple layers to a map instance before displaying it.

    Args:
        data (Union[gpd.GeoDataFrame, xr.DataArray, xr.Dataset]): The geospatial data to add.
        m (leafmap.Map, optional): An existing leafmap.Map instance to add the layer to.
            If None, a new map is created. Defaults to None.
        **kwargs: Additional keyword arguments to be passed to the respective
            leafmap add method (`add_gdf` or `add_raster`).

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
        if isinstance(data, xr.DataArray) and data.rio.crs is None :
             if not (hasattr(data, 'rio') and data.rio.crs):
                print("Warning: xarray.DataArray does not have CRS information via data.rio.crs. Visualization may be incorrect.")
        m.add_raster(data, **kwargs)
    else:
        raise TypeError(
            f"Unsupported data type: {type(data)}. "
            "Must be GeoDataFrame, xarray.DataArray, or xarray.Dataset."
        )

    return m
