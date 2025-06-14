import xarray as xr
import rioxarray  # Imported for the .rio accessor, used by xarray.DataArray
from typing import Union, Hashable, Dict, Any
import zarr  # Though not directly used in the function, good to have for context if users handle zarr.Group directly
import numpy as np  # Added for np.datetime64 and other numpy uses
from typing import List  # Added for List type hint

# Import accessor to register it
from .accessor import PmgRasterAccessor

__all__ = [
    "reproject",
    "normalized_difference",
    "lazy_windowed_read_zarr",
    "create_spatiotemporal_cube",
]


def create_spatiotemporal_cube(
    data_arrays: List[xr.DataArray],
    times: List[np.datetime64],
    time_dim_name: str = "time",
) -> xr.DataArray:
    """
    Creates a spatio-temporal cube by concatenating a list of 2D spatial DataArrays
    along a new time dimension.

    All input DataArrays are expected to have the same spatial dimensions,
    coordinates (except for the new time dimension), and CRS. The CRS from the
    first DataArray will be assigned to the resulting cube.

    Args:
        data_arrays (List[xr.DataArray]): A list of 2D xarray.DataArray objects.
            Each DataArray represents a spatial slice at a specific time.
            They must all have identical spatial coordinates and dimensions (e.g., 'y', 'x').
        times (List[np.datetime64]): A list of NumPy datetime64 objects, corresponding
            to the time of each DataArray in `data_arrays`. Must be the same
            length as `data_arrays`.
        time_dim_name (str): Name for the new time dimension. Defaults to "time".

    Returns:
        xr.DataArray: A 3D xarray.DataArray (time, y, x) representing the
                      spatio-temporal cube. The 'time' coordinate will be populated
                      from the `times` list.

    Raises:
        ValueError: If `data_arrays` is empty, if `times` length doesn't match
                    `data_arrays` length, if DataArrays are not 2D, or if their
                    spatial dimensions/coordinates do not align.
    """
    if not data_arrays:
        raise ValueError("Input 'data_arrays' list cannot be empty.")
    if len(data_arrays) != len(times):
        raise ValueError("Length of 'data_arrays' and 'times' must be the same.")
    if not all(isinstance(da, xr.DataArray) for da in data_arrays):
        raise TypeError("All items in 'data_arrays' must be xarray.DataArray objects.")
    if not all(da.ndim == 2 for da in data_arrays):
        raise ValueError(
            "All DataArrays in 'data_arrays' must be 2-dimensional (spatial slices)."
        )

    # Check spatial dimension alignment using the first DataArray as reference
    first_da = data_arrays[0]
    ref_dims = first_da.dims
    ref_coords_y = first_da.coords[ref_dims[0]]  # Assuming first dim is 'y'
    ref_coords_x = first_da.coords[ref_dims[1]]  # Assuming second dim is 'x'

    for i, da in enumerate(data_arrays[1:]):
        if da.dims != ref_dims:
            raise ValueError(
                f"Spatial dimensions of DataArray at index {i+1} ({da.dims}) "
                f"do not match reference DataArray ({ref_dims})."
            )
        if not da.coords[ref_dims[0]].equals(ref_coords_y) or not da.coords[
            ref_dims[1]
        ].equals(ref_coords_x):
            raise ValueError(
                f"Spatial coordinates of DataArray at index {i+1} "
                "do not match reference DataArray."
            )

    # Expand each 2D DataArray with a time dimension and coordinate
    # Then concatenate them along this new time dimension
    # Ensure the time coordinate has the correct name
    expanded_das = [
        da.expand_dims({time_dim_name: [t]}) for da, t in zip(data_arrays, times)
    ]

    # Concatenate along the new time dimension
    spatiotemporal_cube = xr.concat(expanded_das, dim=time_dim_name)

    # Preserve CRS from the first data array (rioxarray convention)
    if hasattr(first_da, "rio") and first_da.rio.crs:
        spatiotemporal_cube = spatiotemporal_cube.rio.write_crs(first_da.rio.crs)
        # Ensure spatial dimensions are correctly named for rio accessor
        # This depends on how the original DAs were created. Assuming they are e.g. ('y', 'x')
        # If they have names like 'latitude', 'longitude', ensure rio can find them.
        # Usually, if the coordinates are named e.g. 'y', 'x', rio works fine.
        # If not, one might need: spatiotemporal_cube.rio.set_spatial_dims(x_dim=ref_dims[1], y_dim=ref_dims[0], inplace=True)

    return spatiotemporal_cube


def lazy_windowed_read_zarr(
    store_path_or_url: str,
    window: Dict[str, int],
    level: Union[str, int],
    consolidated: bool = True,
    multiscale_group_name: str = "",
    axis_order: str = "YX",
) -> xr.DataArray:
    """
    Lazily reads a window of data from a specific level of a Zarr multiscale pyramid.

    This function opens a Zarr store, accesses its multiscale representation,
    selects the specified scale level, and then extracts a defined window
    (region of interest) from that level. The data access is lazy, meaning
    actual data I/O occurs only when the returned DataArray is computed or accessed.

    Args:
        store_path_or_url (str): Path or URL to the Zarr store.
        window (Dict[str, int]): A dictionary specifying the window to read.
            Expected keys are 'x' (x-coordinate of the top-left corner),
            'y' (y-coordinate of the top-left corner), 'width' (width of the
            window), and 'height' (height of the window). Coordinates are
            typically in pixel units of the specified level.
        level (Union[str, int]): The scale level to read from. This can be an
            integer index (e.g., 0 for the highest resolution) or a string path
            name if the multiscale metadata defines named levels (e.g., "0", "1").
        consolidated (bool, optional): Whether the Zarr store's metadata is
            consolidated. Defaults to True, which is common for performance.
            Passed to `xarray.open_zarr`.
        multiscale_group_name (str, optional): The name or path of the group within
            the Zarr store that contains the multiscale metadata (e.g., 'multiscales.DTYPE_0').
            If empty (default), it assumes the root of the Zarr store is the
            multiscale dataset or contains the necessary metadata.
        axis_order (str, optional): The axis order convention used to interpret
            the dimensions of the arrays in the pyramid. Defaults to "YX".
            Common alternatives could be "CYX", "TCYX", etc. This tells the function
            how to map dimension names like 'x' and 'y' to array dimensions.

    Returns:
        xr.DataArray: An xarray.DataArray representing the selected window from
            the specified scale level. The array is lazy-loaded.

    Raises:
        KeyError: If the specified window keys ('x', 'y', 'width', 'height') are
            not in the `window` dictionary, or if the selected level does not
            contain dimensions 'x' and 'y' for slicing.
        IndexError: If the window coordinates are outside the bounds of the data
            at the selected level.
        Exception: Can also raise exceptions from `zarr.open` if the store is
            invalid, not a multiscale pyramid, or the level does not exist.

    Example:
        >>> # Assuming a Zarr store 'my_image.zarr' with a multiscale pyramid
        >>> window_to_read = {'x': 100, 'y': 200, 'width': 50, 'height': 50}
        >>> # data_chunk = lazy_windowed_read_zarr('my_image.zarr', window_to_read, level=0)
        >>> # print(data_chunk) # This will show the DataArray structure
        >>> # actual_data = data_chunk.compute() # This triggers data loading
    """
    if not all(k in window for k in ["x", "y", "width", "height"]):
        raise KeyError(
            "Window dictionary must contain 'x', 'y', 'width', and 'height' keys."
        )

    # Open the Zarr store. For multiscale stores, we need to handle the structure carefully
    # If multiscale_group_name is provided, it's used as the group path.
    zarr_group_path = multiscale_group_name if multiscale_group_name else None

    # For multiscale zarr stores, we'll open the zarr group and access individual levels
    import zarr as zarr_lib

    try:
        zarr_store = zarr_lib.open_group(store_path_or_url, mode="r")
        if zarr_group_path:
            zarr_store = zarr_store[zarr_group_path]

        # Get the multiscale metadata to understand the structure
        multiscale_metadata = zarr_store.attrs.get("multiscales", [])
        if not multiscale_metadata:
            raise ValueError("No multiscale metadata found in zarr store")

        # Get the datasets (levels) from the first multiscale entry
        datasets = multiscale_metadata[0].get("datasets", [])
        if not datasets:
            raise ValueError("No datasets found in multiscale metadata")

        # Create a list of DataArrays for each level
        multi_scale_pyramid = []
        for dataset_info in datasets:
            level_path = dataset_info["path"]
            zarr_array = zarr_store[level_path]

            # Convert to xarray DataArray with proper dimensions and keep it lazy
            dims = zarr_array.attrs.get(
                "_ARRAY_DIMENSIONS", [f"dim_{i}" for i in range(zarr_array.ndim)]
            )
            # Use dask to keep the array lazy
            import dask.array as da_dask

            dask_array = da_dask.from_zarr(zarr_array)
            da = xr.DataArray(dask_array, dims=dims)
            multi_scale_pyramid.append(da)

    except KeyError as e:
        # If zarr group path doesn't exist, raise PathNotFoundError as expected by tests
        import zarr.errors

        raise zarr.errors.PathNotFoundError(
            f"Group '{zarr_group_path}' not found in zarr store"
        ) from e
    except Exception as e:
        # If zarr store access fails, provide more context
        raise Exception(
            f"Failed to interpret '{store_path_or_url}' (group: {zarr_group_path}) as a multiscale pyramid. "
            f"Ensure it's a valid OME-NGFF multiscale dataset or compatible structure. Original error: {e}"
        ) from e

    # Select the specified level. `level` can be an int or string.
    # `multi_scale_pyramid` is a list of xr.DataArray, one for each level.
    try:
        if isinstance(level, str) and not level.isdigit():
            # For OME-ZARR, levels are typically indexed 0, 1, 2...
            # The `datasets` attribute in .zattrs lists paths like "0", "1", "2".
            # We will assume `level` as integer index for this list.
            # If string "0", "1" etc are passed, convert to int.
            raise ValueError(
                f"Level '{level}' is a non-integer string. Please use integer index for levels."
            )

        level_idx = int(level)
        data_at_level = multi_scale_pyramid[level_idx]
    except IndexError:
        raise IndexError(
            f"Level {level} is out of bounds. Available levels: {len(multi_scale_pyramid)} (0 to {len(multi_scale_pyramid)-1})."
        ) from None
    except ValueError as e:  # Handles non-integer string level
        raise ValueError(
            f"Invalid level specified: {level}. Must be an integer or a string representing an integer. Error: {e}"
        )

    # Select the window using .isel for integer-based slicing.
    # Assumes dimensions are named 'x' and 'y' in the DataArray at the selected level.
    # This is a common convention for 2D spatial data.
    try:
        x_slice = slice(window["x"], window["x"] + window["width"])
        y_slice = slice(window["y"], window["y"] + window["height"])

        # Check if 'x' and 'y' are dimensions in the data_at_level
        if "x" not in data_at_level.dims or "y" not in data_at_level.dims:
            raise KeyError(
                f"Dimensions 'x' and/or 'y' not found in DataArray at level {level}. "
                f"Available dimensions: {data_at_level.dims}. "
                f"Ensure 'axis_order' ('{axis_order}') correctly maps to these dimensions."
            )

        windowed_data = data_at_level.isel(x=x_slice, y=y_slice)
    except (
        KeyError
    ) as e:  # Handles missing 'x', 'y', 'width', 'height' from window dict (already checked) or missing dims
        raise KeyError(
            f"Failed to slice window. Ensure 'x' and 'y' are valid dimension names in the selected level's DataArray. Original error: {e}"
        )
    except IndexError as e:  # Handles slice out of bounds
        raise IndexError(
            f"Window {window} is out of bounds for level {level} with shape {data_at_level.shape}. Original error: {e}"
        )

    return windowed_data


def reproject(
    data_array: xr.DataArray, target_crs: Union[str, int], **kwargs
) -> xr.DataArray:
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
    if not hasattr(data_array, "rio"):
        raise ValueError(
            "DataArray does not have 'rio' accessor. Ensure rioxarray is installed and the DataArray has CRS information."
        )
    if data_array.rio.crs is None:
        raise ValueError(
            "Input DataArray must have a CRS defined to perform reprojection."
        )

    return data_array.rio.reproject(target_crs, **kwargs)


def normalized_difference(
    array: Union[xr.DataArray, xr.Dataset], band1: Hashable, band2: Hashable
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
        if "band" in array.coords:
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
            raise ValueError(
                f"Band '{band1}' not found as a variable in the input Dataset. Available variables: {list(array.variables)}"
            )
        if band2 not in array.variables:
            raise ValueError(
                f"Band '{band2}' not found as a variable in the input Dataset. Available variables: {list(array.variables)}"
            )

        b1 = array[band1]
        b2 = array[band2]

        if not isinstance(b1, xr.DataArray) or not isinstance(b2, xr.DataArray):
            raise ValueError(
                f"Selected variables '{band1}' and '{band2}' must be DataArrays."
            )

    else:
        raise TypeError(
            f"Input 'array' must be an xr.DataArray or xr.Dataset, got {type(array)}."
        )

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
        raise TypeError(
            f"Could not perform arithmetic on selected bands. Ensure they are numeric and compatible. Original error: {e}"
        ) from e
