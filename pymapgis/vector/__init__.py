import geopandas

def buffer(gdf: geopandas.GeoDataFrame, distance: float, **kwargs) -> geopandas.GeoDataFrame:
  """Creates buffer polygons around geometries in a GeoDataFrame.

  Args:
      gdf (geopandas.GeoDataFrame): The input GeoDataFrame.
      distance (float): The buffer distance. The units of the distance
          are assumed to be the same as the CRS of the gdf.
      **kwargs: Additional arguments to be passed to GeoPandas' buffer method
          (e.g., resolution, cap_style, join_style).

  Returns:
      geopandas.GeoDataFrame: A new GeoDataFrame with the buffered geometries.
  """
  buffered_geometries = gdf.geometry.buffer(distance, **kwargs)
  new_gdf = gdf.copy()
  new_gdf.geometry = buffered_geometries
  return new_gdf
