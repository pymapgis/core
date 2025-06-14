import geopandas
from typing import Union
from shapely.geometry.base import BaseGeometry
from .geoarrow_utils import geodataframe_to_geoarrow, geoarrow_to_geodataframe

__all__ = [
    "buffer",
    "clip",
    "overlay",
    "spatial_join",
    "geodataframe_to_geoarrow",
    "geoarrow_to_geodataframe",
]


# Register the accessor
try:
    from pandas.api.extensions import register_dataframe_accessor
except ImportError:
    # Fallback for older pandas versions
    from pandas.core.accessor import CachedAccessor
    def register_dataframe_accessor(name):
        def decorator(accessor):
            setattr(geopandas.GeoDataFrame, name, CachedAccessor(name, accessor))
            return accessor
        return decorator

@register_dataframe_accessor("pmg")
class PyMapGISAccessor:
    """PyMapGIS accessor for GeoDataFrame operations."""

    def __init__(self, gdf):
        self._gdf = gdf

    def buffer(self, distance: float, **kwargs) -> geopandas.GeoDataFrame:
        """Creates buffer polygons around geometries."""
        return buffer(self._gdf, distance, **kwargs)

    def clip(self, mask_geometry: Union[geopandas.GeoDataFrame, BaseGeometry], **kwargs) -> geopandas.GeoDataFrame:
        """Clips the GeoDataFrame to the boundaries of a mask geometry."""
        return clip(self._gdf, mask_geometry, **kwargs)

    def overlay(self, other: geopandas.GeoDataFrame, how: str = "intersection", **kwargs) -> geopandas.GeoDataFrame:
        """Performs a spatial overlay with another GeoDataFrame."""
        return overlay(self._gdf, other, how, **kwargs)

    def spatial_join(self, other: geopandas.GeoDataFrame, op: str = "intersects", how: str = "inner", **kwargs) -> geopandas.GeoDataFrame:
        """Performs a spatial join with another GeoDataFrame."""
        return spatial_join(self._gdf, other, op, how, **kwargs)

    def explore(self, **kwargs):
        """Explore the GeoDataFrame interactively using folium."""
        try:
            # Try to use the built-in explore method if available
            return self._gdf.explore(**kwargs)
        except Exception:
            # Fallback for older versions or missing dependencies
            import warnings
            warnings.warn("Interactive exploration not available. Install folium for full functionality.")
            return self._gdf

    def map(self, **kwargs):
        """Create an interactive map of the GeoDataFrame."""
        # Alias for explore method for compatibility
        return self.explore(**kwargs)


def buffer(
    gdf: geopandas.GeoDataFrame, distance: float, **kwargs
) -> geopandas.GeoDataFrame:
    """Creates buffer polygons around geometries in a GeoDataFrame.

    Args:
        gdf (geopandas.GeoDataFrame): The input GeoDataFrame.
        distance (float): The buffer distance. The units of the distance
            are assumed to be the same as the CRS of the gdf.
        **kwargs: Additional arguments to be passed to GeoPandas' `buffer` method
            (e.g., `resolution`, `cap_style`, `join_style`).

    Returns:
        geopandas.GeoDataFrame: A new GeoDataFrame with the buffered geometries.
    """
    buffered_geometries = gdf.geometry.buffer(distance, **kwargs)
    new_gdf = gdf.copy()
    new_gdf.geometry = buffered_geometries
    return new_gdf


def clip(
    gdf: geopandas.GeoDataFrame,
    mask_geometry: Union[geopandas.GeoDataFrame, BaseGeometry],
    **kwargs,
) -> geopandas.GeoDataFrame:
    """Clips a GeoDataFrame to the boundaries of a mask geometry.

    Args:
        gdf (geopandas.GeoDataFrame): The GeoDataFrame to be clipped.
        mask_geometry (Union[geopandas.GeoDataFrame, BaseGeometry]): The geometry used for clipping.
            This can be another GeoDataFrame or a Shapely geometry object.
        **kwargs: Additional arguments to be passed to GeoPandas' `clip` method.
            Common kwargs include `keep_geom_type` (boolean) to control whether
            to return only geometries of the same type as the input.

    Returns:
        geopandas.GeoDataFrame: A new GeoDataFrame containing the geometries clipped to the mask.
    """
    return gdf.clip(mask_geometry, **kwargs)


def overlay(
    gdf1: geopandas.GeoDataFrame,
    gdf2: geopandas.GeoDataFrame,
    how: str = "intersection",
    **kwargs,
) -> geopandas.GeoDataFrame:
    """Performs a spatial overlay between two GeoDataFrames.

    Note: Both GeoDataFrames should ideally be in the same CRS. Geopandas will
    raise an error if they are not.

    Args:
        gdf1 (geopandas.GeoDataFrame): The left GeoDataFrame.
        gdf2 (geopandas.GeoDataFrame): The right GeoDataFrame.
        how (str): The type of overlay to perform. Supported values are:
            'intersection', 'union', 'identity', 'symmetric_difference',
            'difference'. Defaults to 'intersection'.
        **kwargs: Additional arguments to be passed to GeoPandas' `overlay` method
            (e.g., `keep_geom_type`).

    Returns:
        geopandas.GeoDataFrame: A new GeoDataFrame with the result of the overlay operation.
    """
    if how not in [
        "intersection",
        "union",
        "identity",
        "symmetric_difference",
        "difference",
    ]:
        raise ValueError(
            f"Unsupported overlay type: {how}. Must be one of "
            "['intersection', 'union', 'identity', 'symmetric_difference', 'difference']"
        )
    return gdf1.overlay(gdf2, how=how, **kwargs)


def spatial_join(
    left_gdf: geopandas.GeoDataFrame,
    right_gdf: geopandas.GeoDataFrame,
    op: str = "intersects",
    how: str = "inner",
    **kwargs,
) -> geopandas.GeoDataFrame:
    """Performs a spatial join between two GeoDataFrames.

    Note: Both GeoDataFrames should ideally be in the same CRS for meaningful
    results. Geopandas will raise an error if they are not compatible.

    Args:
        left_gdf (geopandas.GeoDataFrame): The left GeoDataFrame.
        right_gdf (geopandas.GeoDataFrame): The right GeoDataFrame.
        op (str): The spatial predicate to use for the join. Supported values are:
            'intersects', 'contains', 'within'. Defaults to 'intersects'.
            This corresponds to the 'predicate' argument in geopandas.sjoin.
        how (str): The type of join to perform. Supported values are:
            'left', 'right', 'inner'. Defaults to 'inner'.
        **kwargs: Additional arguments to be passed to `geopandas.sjoin` method
            (e.g., `lsuffix`, `rsuffix`).

    Returns:
        geopandas.GeoDataFrame: A new GeoDataFrame with the result of the spatial join.
    """
    if op not in ["intersects", "contains", "within"]:
        raise ValueError(
            f"Unsupported predicate operation: {op}. Must be one of "
            "['intersects', 'contains', 'within']"
        )
    if how not in ["left", "right", "inner"]:
        raise ValueError(
            f"Unsupported join type: {how}. Must be one of "
            "['left', 'right', 'inner']"
        )
    return geopandas.sjoin(left_gdf, right_gdf, how=how, predicate=op, **kwargs)
