"""
xarray accessor for PyMapGIS raster operations.

This module provides the .pmg accessor for xarray.DataArray and xarray.Dataset objects,
enabling convenient access to PyMapGIS raster operations.
"""

import xarray as xr
from typing import Union, Hashable


@xr.register_dataarray_accessor("pmg")
class PmgRasterAccessor:
    """
    PyMapGIS accessor for xarray.DataArray objects.
    
    Provides convenient access to PyMapGIS raster operations via the .pmg accessor.
    
    Examples:
        >>> import xarray as xr
        >>> import pymapgis as pmg
        >>> 
        >>> # Load a raster
        >>> data = pmg.read("path/to/raster.tif")
        >>> 
        >>> # Reproject using accessor
        >>> reprojected = data.pmg.reproject("EPSG:3857")
        >>> 
        >>> # Calculate NDVI using accessor (for multi-band data)
        >>> ndvi = data.pmg.normalized_difference("nir", "red")
    """
    
    def __init__(self, xarray_obj: xr.DataArray):
        """Initialize the accessor with an xarray.DataArray."""
        self._obj = xarray_obj
    
    def reproject(self, target_crs: Union[str, int], **kwargs) -> xr.DataArray:
        """
        Reproject the DataArray to a new Coordinate Reference System (CRS).
        
        This is a convenience method that calls pymapgis.raster.reproject() on the
        DataArray.
        
        Args:
            target_crs (Union[str, int]): The target CRS. Can be specified as an
                EPSG code (e.g., 4326), a WKT string, or any other format accepted
                by rioxarray.reproject.
            **kwargs: Additional keyword arguments to pass to data_array.rio.reproject().
                Common examples include resolution, resampling, and nodata.
        
        Returns:
            xr.DataArray: A new DataArray reprojected to the target CRS.
        
        Examples:
            >>> # Reproject to Web Mercator
            >>> reprojected = data.pmg.reproject("EPSG:3857")
            >>> 
            >>> # Reproject with custom resolution
            >>> reprojected = data.pmg.reproject("EPSG:4326", resolution=0.01)
        """
        # Import here to avoid circular imports
        from . import reproject as _reproject
        return _reproject(self._obj, target_crs, **kwargs)
    
    def normalized_difference(self, band1: Hashable, band2: Hashable) -> xr.DataArray:
        """
        Compute the normalized difference between two bands.
        
        This is a convenience method that calls pymapgis.raster.normalized_difference()
        on the DataArray.
        
        The formula is (band1 - band2) / (band1 + band2).
        This is commonly used for indices like NDVI (Normalized Difference Vegetation Index).
        
        Args:
            band1 (Hashable): Identifier for the first band. For DataArrays with a 'band'
                coordinate, this should be a value present in that coordinate.
            band2 (Hashable): Identifier for the second band, similar to band1.
        
        Returns:
            xr.DataArray: A DataArray containing the computed normalized difference.
        
        Examples:
            >>> # Calculate NDVI (assuming bands are named)
            >>> ndvi = data.pmg.normalized_difference("nir", "red")
            >>> 
            >>> # Calculate NDVI (assuming bands are numbered)
            >>> ndvi = data.pmg.normalized_difference(4, 3)  # NIR=band4, Red=band3
        """
        # Import here to avoid circular imports
        from . import normalized_difference as _normalized_difference
        return _normalized_difference(self._obj, band1, band2)


@xr.register_dataset_accessor("pmg")
class PmgDatasetAccessor:
    """
    PyMapGIS accessor for xarray.Dataset objects.
    
    Provides convenient access to PyMapGIS raster operations via the .pmg accessor
    for Dataset objects containing multiple DataArrays.
    
    Examples:
        >>> import xarray as xr
        >>> import pymapgis as pmg
        >>> 
        >>> # Load a multi-band dataset
        >>> dataset = pmg.read("path/to/multiband.nc")
        >>> 
        >>> # Calculate NDVI using accessor (for datasets with separate band variables)
        >>> ndvi = dataset.pmg.normalized_difference("B4", "B3")
    """
    
    def __init__(self, xarray_obj: xr.Dataset):
        """Initialize the accessor with an xarray.Dataset."""
        self._obj = xarray_obj
    
    def normalized_difference(self, band1: Hashable, band2: Hashable) -> xr.DataArray:
        """
        Compute the normalized difference between two bands in the Dataset.
        
        This is a convenience method that calls pymapgis.raster.normalized_difference()
        on the Dataset.
        
        The formula is (band1 - band2) / (band1 + band2).
        This is commonly used for indices like NDVI (Normalized Difference Vegetation Index).
        
        Args:
            band1 (Hashable): The string name of the first DataArray variable in the Dataset.
            band2 (Hashable): The string name of the second DataArray variable in the Dataset.
        
        Returns:
            xr.DataArray: A DataArray containing the computed normalized difference.
        
        Examples:
            >>> # Calculate NDVI from Landsat bands
            >>> ndvi = dataset.pmg.normalized_difference("B5", "B4")  # NIR, Red
            >>> 
            >>> # Calculate NDWI (water index)
            >>> ndwi = dataset.pmg.normalized_difference("B3", "B5")  # Green, NIR
        """
        # Import here to avoid circular imports
        from . import normalized_difference as _normalized_difference
        return _normalized_difference(self._obj, band1, band2)
