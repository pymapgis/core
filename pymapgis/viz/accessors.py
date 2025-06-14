"""
Visualization accessors for PyMapGIS.

This module provides .pmg accessor methods for GeoDataFrame objects,
enabling convenient access to PyMapGIS visualization operations.
"""

import geopandas as gpd
import pandas as pd
import leafmap.leafmap as leafmap
from typing import Optional, Union
from shapely.geometry.base import BaseGeometry


@pd.api.extensions.register_dataframe_accessor("pmg")
class PmgVizAccessor:
    """
    PyMapGIS accessor for GeoDataFrame objects.

    Provides convenient access to PyMapGIS visualization and vector operations via the .pmg accessor.

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
        >>>
        >>> # Vector operations
        >>> buffered = gdf.pmg.buffer(1000)
        >>> clipped = gdf.pmg.clip(mask_geometry)
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

    # Vector operations
    def buffer(self, distance: float, **kwargs) -> gpd.GeoDataFrame:
        """
        Create buffer polygons around geometries in the GeoDataFrame.

        Args:
            distance (float): The buffer distance. The units of the distance
                are assumed to be the same as the CRS of the GeoDataFrame.
            **kwargs: Additional arguments to be passed to GeoPandas' buffer method
                (e.g., resolution, cap_style, join_style).

        Returns:
            gpd.GeoDataFrame: A new GeoDataFrame with the buffered geometries.

        Examples:
            >>> # Buffer by 1000 units (meters if in projected CRS)
            >>> buffered = gdf.pmg.buffer(1000)
            >>>
            >>> # Buffer with custom parameters
            >>> buffered = gdf.pmg.buffer(500, resolution=32, cap_style=1)
        """
        # Import here to avoid circular imports
        from ..vector import buffer as _buffer

        return _buffer(self._obj, distance, **kwargs)

    def clip(
        self,
        mask_geometry: Union[gpd.GeoDataFrame, BaseGeometry],
        **kwargs,
    ) -> gpd.GeoDataFrame:
        """
        Clip the GeoDataFrame to the boundaries of a mask geometry.

        Args:
            mask_geometry (Union[gpd.GeoDataFrame, BaseGeometry]): The geometry used for clipping.
                This can be another GeoDataFrame or a Shapely geometry object.
            **kwargs: Additional arguments to be passed to GeoPandas' clip method.

        Returns:
            gpd.GeoDataFrame: A new GeoDataFrame containing the geometries clipped to the mask.

        Examples:
            >>> # Clip to a polygon boundary
            >>> clipped = gdf.pmg.clip(boundary_polygon)
            >>>
            >>> # Clip to another GeoDataFrame
            >>> clipped = gdf.pmg.clip(study_area_gdf)
        """
        # Import here to avoid circular imports
        from ..vector import clip as _clip

        return _clip(self._obj, mask_geometry, **kwargs)

    def overlay(
        self,
        other: gpd.GeoDataFrame,
        how: str = "intersection",
        **kwargs,
    ) -> gpd.GeoDataFrame:
        """
        Perform a spatial overlay with another GeoDataFrame.

        Args:
            other (gpd.GeoDataFrame): The other GeoDataFrame to overlay with.
            how (str): The type of overlay to perform. Supported values are:
                'intersection', 'union', 'identity', 'symmetric_difference',
                'difference'. Defaults to 'intersection'.
            **kwargs: Additional arguments to be passed to GeoPandas' overlay method.

        Returns:
            gpd.GeoDataFrame: A new GeoDataFrame with the result of the overlay operation.

        Examples:
            >>> # Find intersection with another layer
            >>> intersection = gdf.pmg.overlay(other_gdf, how="intersection")
            >>>
            >>> # Find difference (areas in gdf but not in other)
            >>> difference = gdf.pmg.overlay(other_gdf, how="difference")
        """
        # Import here to avoid circular imports
        from ..vector import overlay as _overlay

        return _overlay(self._obj, other, how=how, **kwargs)

    def spatial_join(
        self,
        other: gpd.GeoDataFrame,
        op: str = "intersects",
        how: str = "inner",
        **kwargs,
    ) -> gpd.GeoDataFrame:
        """
        Perform a spatial join with another GeoDataFrame.

        Args:
            other (gpd.GeoDataFrame): The other GeoDataFrame to join with.
            op (str): The spatial predicate to use for the join. Supported values are:
                'intersects', 'contains', 'within'. Defaults to 'intersects'.
            how (str): The type of join to perform. Supported values are:
                'left', 'right', 'inner'. Defaults to 'inner'.
            **kwargs: Additional arguments to be passed to geopandas.sjoin method.

        Returns:
            gpd.GeoDataFrame: A new GeoDataFrame with the result of the spatial join.

        Examples:
            >>> # Join points with polygons they intersect
            >>> joined = points_gdf.pmg.spatial_join(polygons_gdf, op="intersects")
            >>>
            >>> # Left join to keep all original features
            >>> joined = gdf.pmg.spatial_join(other_gdf, how="left")
        """
        # Import here to avoid circular imports
        from ..vector import spatial_join as _spatial_join

        return _spatial_join(self._obj, other, op=op, how=how, **kwargs)
