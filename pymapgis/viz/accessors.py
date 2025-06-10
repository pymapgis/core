"""
Visualization accessors for PyMapGIS.

This module provides .pmg accessor methods for GeoDataFrame objects,
enabling convenient access to PyMapGIS visualization operations.
"""

import geopandas as gpd
import pandas as pd
import leafmap.leafmap as leafmap
from typing import Optional


@pd.api.extensions.register_dataframe_accessor("pmg")
class PmgVizAccessor:
    """
    PyMapGIS accessor for GeoDataFrame objects.

    Provides convenient access to PyMapGIS visualization operations via the .pmg accessor.

    Examples:
        >>> import geopandas as gpd
        >>> import pymapgis as pmg
        >>>
        >>> # Load vector data
        >>> gdf = pmg.read("census://acs/acs5?year=2022&geography=county&variables=B01003_001E")
        >>>
        >>> # Quick exploration
        >>> gdf.pmg.explore()
        >>>
        >>> # Build a map
        >>> m = gdf.pmg.map(layer_name="Counties")
        >>> m.add_basemap("OpenStreetMap")
    """

    def __init__(self, gdf_obj: gpd.GeoDataFrame):
        """Initialize the accessor with a GeoDataFrame."""
        self._obj = gdf_obj

    def explore(self, m: Optional[leafmap.Map] = None, **kwargs) -> leafmap.Map:
        """
        Interactively explore the GeoDataFrame on a Leafmap map.

        This method creates a new map (or uses an existing one if provided) and adds
        the GeoDataFrame as a vector layer. The map is optimized for quick exploration
        with sensible defaults.

        Args:
            m (leafmap.Map, optional): An existing leafmap.Map instance to add the layer to.
                If None, a new map is created. Defaults to None.
            **kwargs: Additional keyword arguments passed to leafmap's add_gdf() method.
                Common kwargs include:
                - layer_name (str): Name for the layer
                - style (dict): Styling for vector features, e.g., {'color': 'red', 'fillOpacity': 0.5}
                - hover_style (dict): Styling when hovering over features
                - popup (list): Column names to show in popup
                - tooltip (str or list): Tooltip configuration

        Returns:
            leafmap.Map: The leafmap.Map instance with the added layer.

        Examples:
            >>> # Quick exploration with defaults
            >>> gdf.pmg.explore()
            >>>
            >>> # With custom styling
            >>> gdf.pmg.explore(style={'color': 'blue', 'fillOpacity': 0.3})
            >>>
            >>> # Add to existing map
            >>> m = leafmap.Map()
            >>> gdf.pmg.explore(m=m, layer_name="My Data")
        """
        # Import here to avoid circular imports
        from . import explore as _explore

        return _explore(self._obj, m=m, **kwargs)

    def map(self, m: Optional[leafmap.Map] = None, **kwargs) -> leafmap.Map:
        """
        Add the GeoDataFrame to an interactive Leafmap map for building complex visualizations.

        This method is similar to explore() but is designed for building more complex maps
        by adding multiple layers. It does not automatically display the map, allowing for
        further customization before display.

        Args:
            m (leafmap.Map, optional): An existing leafmap.Map instance to add the layer to.
                If None, a new map is created. Defaults to None.
            **kwargs: Additional keyword arguments passed to leafmap's add_gdf() method.
                Refer to the explore() method's docstring for common kwargs.

        Returns:
            leafmap.Map: The leafmap.Map instance with the added layer.

        Examples:
            >>> # Create a map for further customization
            >>> m = gdf.pmg.map(layer_name="Base Layer")
            >>> m.add_basemap("Satellite")
            >>>
            >>> # Add multiple layers
            >>> m = gdf1.pmg.map(layer_name="Layer 1")
            >>> m = gdf2.pmg.map(m=m, layer_name="Layer 2")
            >>> m  # Display the map
        """
        # Import here to avoid circular imports
        from . import plot_interactive as _plot_interactive

        return _plot_interactive(self._obj, m=m, **kwargs)
