import xarray as xr
import rioxarray # Imported for the .rio accessor, used by xarray.DataArray
from typing import Union, Hashable

__all__ = ["reproject", "normalized_difference"]

def reproject(data_array: xr.DataArray, target_crs: Union[str, int], **kwargs) -> xr.DataArray:
    """Reprojects an xarray.DataArray to a new Coordinate Reference System (CRS).

    This function utilizes the `rio.reproject()` method from the `rioxarray` extension.

    Args:
        data_array (xr.DataArray): The input DataArray with geospatial information
            (CRS and transform) typically accessed via `data_array.rio`.
        target_crs (Union[str, int]): The target CRS. Can be specified as an
            EPSG code (e.g., 4326), a WKT string, or any other format accepted
            by `rioxarray.reproject`.
        **kwargs: Additional keyword arguments to pass to `data_array.rio.reproject()`.
            Common examples include `resolution` (e.g., `resolution=10.0` or
            `resolution=(10.0, 10.0)`), `resampling` (from `rioxarray.enums.Resampling`,
            e.g., `resampling=Resampling.bilinear`), and `nodata` (e.g., `nodata=0`).

    Returns:
        xr.DataArray: A new DataArray reprojected to the target CRS.
    """
    if not hasattr(data_array, 'rio'):
        raise ValueError("DataArray does not have 'rio' accessor. Ensure rioxarray is installed and the DataArray has CRS information.")
    if data_array.rio.crs is None:
        raise ValueError("Input DataArray must have a CRS defined to perform reprojection.")

    return data_array.rio.reproject(target_crs, **kwargs)

def normalized_difference(
    array: Union[xr.DataArray, xr.Dataset],
    band1: Hashable,
    band2: Hashable
) -> xr.DataArray:
    """Computes the normalized difference between two bands of a raster.

    The formula is `(band1 - band2) / (band1 + band2)`.
    This is commonly used for indices like NDVI (Normalized Difference Vegetation Index).

    Args:
        array (Union[xr.DataArray, xr.Dataset]): The input raster data.
            - If `xr.DataArray`: Assumes a multi-band DataArray. `band1` and `band2`
              are used to select data along the 'band' coordinate/dimension
              (e.g., `array.sel(band=band1)`).
            - If `xr.Dataset`: Assumes `band1` and `band2` are string names of
              `xr.DataArray` variables within the Dataset (e.g., `array[band1]`).
        band1 (Hashable): Identifier for the first band.
            - For `xr.DataArray`: A value present in the 'band' coordinate
              (e.g., 'red', 'nir', or an integer band number like 4).
            - For `xr.Dataset`: The string name of the DataArray variable
              (e.g., "B4", "SR_B5").
        band2 (Hashable): Identifier for the second band, similar to `band1`.

    Returns:
        xr.DataArray: A DataArray containing the computed normalized difference.
            The result will have the same spatial dimensions as the input bands.
            - Division by zero (`band1` + `band2` == 0) will result in `np.inf`
              (or `-np.inf`) if the numerator is non-zero, and `np.nan` if the
              numerator is also zero, following standard xarray/numpy arithmetic.
            - NaNs in the input bands will propagate to the output; for example,
              if a pixel in `band1` is NaN, the corresponding output pixel
              will also be NaN.

    Raises:
        ValueError: If the input array type is not supported, or if specified
            bands cannot be selected/found.
        TypeError: If band data cannot be subtracted or added (e.g. non-numeric).
    """
    b1: xr.DataArray
    b2: xr.DataArray

    if isinstance(array, xr.DataArray):
        # Try to select using 'band' coordinate, common for rioxarray outputs
        if 'band' in array.coords:
            try:
                b1 = array.sel(band=band1)
                b2 = array.sel(band=band2)
            except KeyError as e:
                raise ValueError(
                    f"Band identifiers '{band1}' or '{band2}' not found in 'band' coordinate. "
                    f"Available bands: {list(array.coords['band'].values)}. Original error: {e}"
                ) from e
        else:
            # This case might occur if the DataArray is single-band or bands are indexed differently.
            # For this function's current design, we expect a 'band' coordinate for DataArray input.
            raise ValueError(
                "Input xr.DataArray must have a 'band' coordinate for band selection. "
                "Alternatively, provide an xr.Dataset with bands as separate DataArrays."
            )
    elif isinstance(array, xr.Dataset):
        if band1 not in array.variables:
            raise ValueError(f"Band '{band1}' not found as a variable in the input Dataset. Available variables: {list(array.variables)}")
        if band2 not in array.variables:
            raise ValueError(f"Band '{band2}' not found as a variable in the input Dataset. Available variables: {list(array.variables)}")

        b1 = array[band1]
        b2 = array[band2]

        if not isinstance(b1, xr.DataArray) or not isinstance(b2, xr.DataArray):
            raise ValueError(f"Selected variables '{band1}' and '{band2}' must be DataArrays.")

    else:
        raise TypeError(f"Input 'array' must be an xr.DataArray or xr.Dataset, got {type(array)}.")

    # Ensure selected bands are not empty or incompatible
    if b1.size == 0 or b2.size == 0:
        raise ValueError("Selected bands are empty or could not be resolved.")

    # Perform calculation
    try:
        # Using xr.where to handle potential division by zero if (b1 + b2) is zero.
        # Where (b1+b2) is 0, result is 0. NDVI typically ranges -1 to 1.
        # Some prefer np.nan where denominator is 0. For now, 0.
        denominator = b1 + b2
        numerator = b1 - b2
        # return xr.where(denominator == 0, 0, numerator / denominator)
        # A common practice is to allow NaNs to propagate, or to mask them.
        # If b1 and b2 are integers, true division might be needed.
        # Xarray handles dtypes promotion, but being explicit can be good.
        # Ensure floating point division
        return (numerator.astype(float)) / (denominator.astype(float))

    except Exception as e:
        raise TypeError(f"Could not perform arithmetic on selected bands. Ensure they are numeric and compatible. Original error: {e}") from e
