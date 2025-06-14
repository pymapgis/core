import os
import shutil
import tempfile
import json

import numpy as np
import xarray as xr
import zarr
import pytest
import pandas as pd
import dask.array as da # For checking if it's a dask array
import rioxarray  # For CRS operations

from pymapgis.raster import lazy_windowed_read_zarr, create_spatiotemporal_cube, reproject, normalized_difference
import pymapgis as pmg  # For testing accessor


@pytest.fixture
def ome_zarr_store_path_3d_cyx():
    """
    Creates a temporary 3D (C,Y,X) OME-Zarr multiscale store for testing.
    Yields the path to the root of the Zarr store.
    Cleans up the temporary directory afterwards.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        zarr_root_path = os.path.join(tmpdir, "test_image_3d.zarr")
        root_group = zarr.open_group(zarr_root_path, mode='w')

        num_channels = 3
        base_y_dim, base_x_dim = 256, 256

        # Define scales and data
        # Level 0: (3, 256, 256), chunks (1, 64, 64)
        data_l0_np = np.arange(num_channels * base_y_dim * base_x_dim, dtype=np.uint16).reshape((num_channels, base_y_dim, base_x_dim))
        # Level 1: (3, 128, 128), chunks (1, 64, 64)
        data_l1_np = (data_l0_np[:, ::2, ::2] + data_l0_np[:, 1::2, ::2] + data_l0_np[:, ::2, 1::2] + data_l0_np[:, 1::2, 1::2]) / 4
        data_l1_np = data_l1_np.astype(np.uint16)
        # Level 2: (3, 64, 64), chunks (1, 32, 32)
        data_l2_np = (data_l1_np[:, ::2, ::2] + data_l1_np[:, 1::2, ::2] + data_l1_np[:, ::2, 1::2] + data_l1_np[:, 1::2, 1::2]) / 4
        data_l2_np = data_l2_np.astype(np.uint16)

        datasets_metadata = []
        # Store all level data in a dictionary to access in tests if needed
        fixture_data = {
            "0": data_l0_np,
            "1": data_l1_np,
            "2": data_l2_np
        }

        levels_config = {
            "0": {"data": data_l0_np, "chunks": (1, 64, 64), "scale": [1, 1, 1]}, # c, y, x scale
            "1": {"data": data_l1_np, "chunks": (1, 64, 64), "scale": [1, 2, 2]},
            "2": {"data": data_l2_np, "chunks": (1, 32, 32), "scale": [1, 4, 4]},
        }

        for path_name, level_info in levels_config.items():
            arr = root_group.create_dataset(
                path_name,
                data=level_info["data"],
                chunks=level_info["chunks"],
                dtype=level_info["data"].dtype,
                overwrite=True
            )
            # OME-Zarr standard dimension names for C, Y, X
            arr.attrs['_ARRAY_DIMENSIONS'] = ['c', 'y', 'x']

            datasets_metadata.append({
                "path": path_name,
                "coordinateTransformations": [{
                    "type": "scale",
                    "scale": [ # Order should match axes order: c, y, x
                        float(level_info["scale"][0]), # c scale
                        float(level_info["scale"][1]), # y scale
                        float(level_info["scale"][2]), # x scale
                    ]
                }]
            })

        # Write OME-NGFF multiscale metadata
        root_group.attrs['multiscales'] = [{
            "version": "0.4",
            "name": "test_image_3d",
            "axes": [
                {"name": "c", "type": "channel"},
                {"name": "y", "type": "space", "unit": "pixel"},
                {"name": "x", "type": "space", "unit": "pixel"}
            ],
            "datasets": datasets_metadata,
            "type": "mean",
        }]

        zarr.consolidate_metadata(root_group.store)
        # Yield path and the original numpy data for easy access in tests
        yield zarr_root_path, fixture_data
        # tmpdir is automatically cleaned up


def test_lazy_windowed_read_zarr_3d_cyx(ome_zarr_store_path_3d_cyx):
    """
    Tests lazy_windowed_read_zarr with a 3D (C,Y,X) Zarr store.
    """
    store_path, original_data = ome_zarr_store_path_3d_cyx

    # Test on Level 1 (3, 128, 128 original size)
    level_to_test = 1
    # Window applies to Y,X dimensions. Channels are usually fully included or selected separately.
    # The current lazy_windowed_read_zarr function slices spatial dimensions 'x' and 'y'.
    # If channels need slicing, the function would need a 'c_slice' or similar.
    # For now, we assume all channels in the spatial window are returned.
    window_to_read = {'x': 10, 'y': 20, 'width': 30, 'height': 40} # Slices (y: 20-60, x: 10-40)

    data_l1_np = original_data[str(level_to_test)] # Shape (3, 128, 128)

    expected_slice_y = slice(window_to_read['y'], window_to_read['y'] + window_to_read['height'])
    expected_slice_x = slice(window_to_read['x'], window_to_read['x'] + window_to_read['width'])
    # Expected data will have all channels for the selected YX window
    expected_data_np = data_l1_np[:, expected_slice_y, expected_slice_x] # Shape (3, 40, 30)

    # Use lazy_windowed_read_zarr. Critical: axis_order must match data layout.
    # The Zarr store has arrays with dims ['c', 'y', 'x'].
    # xarray_multiscale needs to know this. 'CYX' is a common convention.
    result_array = lazy_windowed_read_zarr(
        store_path,
        window_to_read,
        level=level_to_test,
        axis_order="CYX" # This tells multiscale how to interpret dimensions
    )

    # 1. Assert Laziness
    import dask
    assert dask.is_dask_collection(result_array.data), "Data should be a Dask array (lazy)."

    # 2. Assert correct shape. Should be (num_channels, height, width)
    # The function currently only slices x and y. Channels are preserved.
    assert result_array.shape == (data_l1_np.shape[0], window_to_read['height'], window_to_read['width']), \
        f"Shape mismatch: expected {(data_l1_np.shape[0], window_to_read['height'], window_to_read['width'])}, got {result_array.shape}"

    # 3. Compute the data
    computed_data = result_array.compute()

    # 4. Assert data content
    assert isinstance(computed_data, xr.DataArray), "Computed data should be an xarray.DataArray"
    np.testing.assert_array_equal(computed_data.data, expected_data_np,
                                   err_msg="Data content mismatch for CYX data after compute()")

    # 5. Test string level
    result_array_str_level = lazy_windowed_read_zarr(
        store_path, window_to_read, level=str(level_to_test), axis_order="CYX")
    computed_data_str_level = result_array_str_level.compute()
    np.testing.assert_array_equal(computed_data_str_level.data, expected_data_np,
                                   err_msg="Data content mismatch with string level for CYX")

    # 6. Test error handling for invalid level
    with pytest.raises(IndexError, match="Level 99 is out of bounds"):
        lazy_windowed_read_zarr(store_path, window_to_read, level=99, axis_order="CYX")

    with pytest.raises(ValueError, match="Level 'invalid_level' is a non-integer string"):
        lazy_windowed_read_zarr(store_path, window_to_read, level="invalid_level", axis_order="CYX")

    # 7. Test error handling for incorrect window keys
    with pytest.raises(KeyError, match="Window dictionary must contain"):
        lazy_windowed_read_zarr(store_path, {'x': 0, 'y': 0, 'w': 10, 'h': 10}, level=0, axis_order="CYX")

    # 8. Test reading from level 0
    data_l0_np = original_data["0"] # Shape (3, 256, 256)
    level0_window = {'x': 5, 'y': 15, 'width': 20, 'height': 25}
    expected_data_l0 = data_l0_np[:, 15:15+25, 5:5+20] # c, y, x
    result_l0 = lazy_windowed_read_zarr(store_path, level0_window, level=0, axis_order="CYX")
    np.testing.assert_array_equal(result_l0.compute().data, expected_data_l0,
                                   err_msg="Data content mismatch for level 0 CYX")

    # 9. Test reading from a different group (multiscale metadata not there)
    root_zarr_group = zarr.open_group(store_path, mode='a')
    if "subgroup" not in root_zarr_group: # Ensure idempotent if test runs multiple times
        sub_group = root_zarr_group.create_group("subgroup")
        sub_group.array("data", data=np.array([1,2,3]), chunks=(1,))
        zarr.consolidate_metadata(root_zarr_group.store) # Re-consolidate

    with pytest.raises(Exception, match="Failed to interpret"):
        lazy_windowed_read_zarr(store_path, window_to_read, level=0,
                                multiscale_group_name="subgroup", axis_order="CYX")

    # 10. Test with a non-existent group
    with pytest.raises(zarr.errors.PathNotFoundError): # This is if open_zarr fails
         lazy_windowed_read_zarr(store_path, window_to_read, level=0,
                                multiscale_group_name="nonexistent_group", axis_order="CYX")

    # 11. Test full extent read for a level
    level_to_test_full = 2 # Data shape (3, 64, 64)
    data_l2_np = original_data[str(level_to_test_full)]
    full_window = {'x': 0, 'y': 0, 'width': data_l2_np.shape[2], 'height': data_l2_np.shape[1]}
    result_full = lazy_windowed_read_zarr(store_path, full_window, level=level_to_test_full, axis_order="CYX")
    assert result_full.shape == data_l2_np.shape
    np.testing.assert_array_equal(result_full.compute().data, data_l2_np,
                                   err_msg="Data content mismatch for full extent read")

    # 12. Test 1x1 pixel window
    one_by_one_window = {'x': 5, 'y': 5, 'width': 1, 'height': 1}
    expected_one_by_one = data_l1_np[:, 5:6, 5:6] # c, y, x
    result_one_by_one = lazy_windowed_read_zarr(store_path, one_by_one_window, level=level_to_test, axis_order="CYX")
    assert result_one_by_one.shape == (data_l1_np.shape[0], 1, 1)
    np.testing.assert_array_equal(result_one_by_one.compute().data, expected_one_by_one,
                                   err_msg="Data content mismatch for 1x1 window")

    # 13. Test window out of bounds (partial) - xarray.isel behavior
    #    isel will typically truncate the selection to the valid range.
    #    Level 1 is (3, 128, 128). Window from x=120, width=20 (i.e., x from 120 to 140)
    #    This should effectively read x from 120 to 127.
    #    The function itself doesn't add explicit out-of-bounds checks for window coords beyond what isel does.
    #    This test verifies the underlying xarray behavior is as expected.
    window_partially_out = {'x': 120, 'y': 120, 'width': 20, 'height': 20} # x: 120-140, y: 120-140
    data_shape_l1 = original_data[str(level_to_test)].shape # (3, 128, 128)

    expected_partial_data = data_l1_np[:, 120:128, 120:128] # xarray.isel behavior

    result_partial_out = lazy_windowed_read_zarr(store_path, window_partially_out, level=level_to_test, axis_order="CYX")

    # Expected shape after isel truncation by xarray
    assert result_partial_out.shape == (data_shape_l1[0], 8, 8), \
        f"Shape mismatch for partially out-of-bounds window. Expected {(data_shape_l1[0], 8, 8)}, got {result_partial_out.shape}"
    np.testing.assert_array_equal(result_partial_out.compute().data, expected_partial_data,
                                   err_msg="Data content mismatch for partially out-of-bounds window")

    # 14. Test window completely out of bounds - xarray.isel behavior
    #    isel typically returns an empty slice if the start of the slice is out of bounds.
    window_fully_out = {'x': 300, 'y': 300, 'width': 10, 'height': 10} # Way outside 128x128
    # xarray.isel with slice(300, 310) on an axis of size 128 will result in an empty slice.
    # The resulting shape for this dimension will be 0.

    # We expect an error from our function if the window implies negative size or invalid start before isel,
    # but if x,y are positive and width,height positive, it goes to isel.
    # xarray_multiscale might raise an error earlier if the window is completely out of any level's bounds
    # before even reaching the xarray.isel stage within our function.
    # Let's check the behavior. The current code passes window dict to isel.
    # xarray.DataArray.isel(x=slice(300,310)) on a dim of size 128 results in shape 0 for x.
    result_fully_out = lazy_windowed_read_zarr(store_path, window_fully_out, level=level_to_test, axis_order="CYX")
    assert result_fully_out.shape == (data_shape_l1[0], 0, 0), \
        f"Shape mismatch for fully out-of-bounds window. Expected {(data_shape_l1[0], 0, 0)}, got {result_fully_out.shape}"
    assert result_fully_out.compute().size == 0, "Data should be empty for fully out-of-bounds window"

    # 15. Test with YX axis_order on CYX data (should cause issues or misinterpret data)
    #    If axis_order="YX" is passed, xarray_multiscale will look for 'y' and 'x' named dimensions
    #    in the arrays from the Zarr store. Our store has 'c', 'y', 'x'.
    #    The multiscale function will still find 'y' and 'x'.
    #    The issue might be subtle, e.g. if 'c' was first and not named, or if scales were different.
    #    In our case, `lazy_windowed_read_zarr` gets a list of DataArrays from `multiscale()`.
    #    These DataArrays will have dims ('c', 'y', 'x').
    #    Then `.isel(x=..., y=...)` is called. This should still work because 'x' and 'y' dims exist.
    #    The `axis_order` primarily tells `xarray_multiscale` how to build its pyramid representation
    #    and what names to expect for spatial axes. If these names exist, it should work.
    #    A more robust test would be if the Zarr store itself had different dim names like 'dim0', 'dim1', 'dim2'
    #    and `axis_order` was crucial for mapping them.
    #    For now, this will likely work but it's conceptually a mismatch if the user intends
    #    to process a 2D slice from a 3D dataset without specifying channel behavior.
    #    The current function implicitly takes all data along other dimensions (like 'c').
    result_yx_on_cyx = lazy_windowed_read_zarr(
        store_path,
        window_to_read,
        level=level_to_test,
        axis_order="YX" # This is the 'type' for xarray_multiscale
    )
    # This should still work because the DataArrays at each level *do* have 'y' and 'x' dimensions.
    # The shape and data should be the same as the CYX test because 'c' is preserved.
    assert result_yx_on_cyx.shape == (data_l1_np.shape[0], window_to_read['height'], window_to_read['width'])
    np.testing.assert_array_equal(result_yx_on_cyx.compute().data, expected_data_np,
                                   err_msg="Data content mismatch for YX axis_order on CYX data")

    # 16. Test with invalid axis_order - since our implementation doesn't actually use axis_order
    #     for multiscale processing (we read the zarr metadata directly), this should still work
    #     The axis_order parameter is currently ignored in our implementation
    result_invalid_axis = lazy_windowed_read_zarr(
        store_path, window_to_read, level=level_to_test, axis_order="UnsupportedOrder")
    # Should still work and return the same data
    assert result_invalid_axis.shape == (data_l1_np.shape[0], window_to_read['height'], window_to_read['width'])
    np.testing.assert_array_equal(result_invalid_axis.compute().data, expected_data_np,
                                   err_msg="Data content mismatch for invalid axis_order")


# Example of how to run this test with pytest:
# Ensure PYTHONPATH includes the pymapgis directory.
# pytest tests/test_raster.py


# Tests for SpatioTemporal Cube creation

def test_create_spatiotemporal_cube_valid():
    """Tests successful creation of a spatiotemporal cube."""
    data1 = np.random.rand(3, 4) # y, x
    data2 = np.random.rand(3, 4)
    y_coords = np.arange(3)
    x_coords = np.arange(4)

    da1 = xr.DataArray(data1, coords={'y': y_coords, 'x': x_coords}, dims=['y', 'x'], name="slice1")
    da1.rio.write_crs("epsg:4326", inplace=True)
    da2 = xr.DataArray(data2, coords={'y': y_coords, 'x': x_coords}, dims=['y', 'x'], name="slice2")
    da2.rio.write_crs("epsg:4326", inplace=True)

    times = [np.datetime64('2023-01-01T00:00:00'), np.datetime64('2023-01-01T01:00:00')]

    cube = create_spatiotemporal_cube([da1, da2], times, time_dim_name="custom_time")

    assert isinstance(cube, xr.DataArray)
    assert cube.ndim == 3
    assert cube.dims == ("custom_time", "y", "x")
    assert len(cube.coords["custom_time"]) == 2
    assert len(cube.coords["y"]) == 3
    assert len(cube.coords["x"]) == 4
    assert pd.Timestamp(cube.coords["custom_time"].values[0]) == pd.Timestamp(times[0])
    assert cube.rio.crs is not None
    assert cube.rio.crs.to_epsg() == 4326

    # Check data integrity (optional, but good for sanity)
    np.testing.assert_array_equal(cube.sel(custom_time=times[0]).data, da1.data)
    np.testing.assert_array_equal(cube.sel(custom_time=times[1]).data, da2.data)

def test_create_spatiotemporal_cube_errors():
    """Tests error handling in create_spatiotemporal_cube."""
    # Empty list of data arrays
    with pytest.raises(ValueError, match="Input 'data_arrays' list cannot be empty"):
        create_spatiotemporal_cube([], [])

    # Mismatched lengths of data_arrays and times
    da1 = xr.DataArray(np.random.rand(2,2), dims=['y','x'])
    with pytest.raises(ValueError, match="Length of 'data_arrays' and 'times' must be the same"):
        create_spatiotemporal_cube([da1], [np.datetime64('2023-01-01'), np.datetime64('2023-01-02')])

    # Non-2D DataArray
    da_3d = xr.DataArray(np.random.rand(2,2,2), dims=['time','y','x'])
    with pytest.raises(ValueError, match="All DataArrays in 'data_arrays' must be 2-dimensional"):
        create_spatiotemporal_cube([da_3d], [np.datetime64('2023-01-01')])

    # Mismatched spatial dimensions
    da_a = xr.DataArray(np.random.rand(2,2), coords={'y':[1,2],'x':[3,4]}, dims=['y','x'])
    da_b = xr.DataArray(np.random.rand(2,3), coords={'y':[1,2],'x':[3,4,5]}, dims=['y','x']) # Different x dim
    with pytest.raises(ValueError, match="Spatial coordinates of DataArray at index 1 do not match"):
        create_spatiotemporal_cube([da_a, da_b], [np.datetime64('2023-01-01'), np.datetime64('2023-01-01')])

    # Mismatched spatial coordinates
    da_c = xr.DataArray(np.random.rand(2,2), coords={'y':[1,2],'x':[3,4]}, dims=['y','x'])
    da_d = xr.DataArray(np.random.rand(2,2), coords={'y':[5,6],'x':[7,8]}, dims=['y','x']) # Different coords
    with pytest.raises(ValueError, match="Spatial coordinates of DataArray at index 1 do not match"):
        create_spatiotemporal_cube([da_c, da_d], [np.datetime64('2023-01-01'), np.datetime64('2023-01-01')])

    # Non-DataArray object in list
    with pytest.raises(TypeError, match="All items in 'data_arrays' must be xarray.DataArray objects"):
        create_spatiotemporal_cube([da_a, "not_a_dataarray"], [np.datetime64('2023-01-01'), np.datetime64('2023-01-01')])


# Tests for Core Raster Operations (Phase 1 - Part 2)

@pytest.fixture
def sample_raster_data():
    """Create a sample raster DataArray with CRS for testing."""
    # Create sample data (3x4 grid)
    data = np.array([[1, 2, 3, 4],
                     [5, 6, 7, 8],
                     [9, 10, 11, 12]], dtype=np.float32)

    # Create coordinates
    x_coords = np.array([0.0, 1.0, 2.0, 3.0])
    y_coords = np.array([3.0, 2.0, 1.0])

    # Create DataArray
    da = xr.DataArray(
        data,
        coords={'y': y_coords, 'x': x_coords},
        dims=['y', 'x'],
        name='test_raster'
    )

    # Add CRS using rioxarray
    da = da.rio.write_crs("EPSG:4326")

    return da


@pytest.fixture
def sample_multiband_data():
    """Create a sample multi-band DataArray for testing normalized difference."""
    # Create sample data for 3 bands (band, y, x)
    nir_data = np.array([[0.8, 0.7, 0.9],
                         [0.6, 0.8, 0.7]], dtype=np.float32)
    red_data = np.array([[0.2, 0.3, 0.1],
                         [0.4, 0.2, 0.3]], dtype=np.float32)
    green_data = np.array([[0.3, 0.4, 0.2],
                           [0.5, 0.3, 0.4]], dtype=np.float32)

    # Stack bands
    data = np.stack([red_data, green_data, nir_data], axis=0)  # Shape: (3, 2, 3)

    # Create coordinates
    x_coords = np.array([0.0, 1.0, 2.0])
    y_coords = np.array([1.0, 0.0])
    band_coords = ['red', 'green', 'nir']

    # Create DataArray
    da = xr.DataArray(
        data,
        coords={'band': band_coords, 'y': y_coords, 'x': x_coords},
        dims=['band', 'y', 'x'],
        name='multiband_raster'
    )

    # Add CRS
    da = da.rio.write_crs("EPSG:4326")

    return da


@pytest.fixture
def sample_dataset():
    """Create a sample Dataset with separate band variables for testing."""
    # Create sample data
    nir_data = np.array([[0.8, 0.7], [0.6, 0.8]], dtype=np.float32)
    red_data = np.array([[0.2, 0.3], [0.4, 0.2]], dtype=np.float32)

    # Create coordinates
    x_coords = np.array([0.0, 1.0])
    y_coords = np.array([1.0, 0.0])

    # Create DataArrays
    nir_da = xr.DataArray(
        nir_data,
        coords={'y': y_coords, 'x': x_coords},
        dims=['y', 'x'],
        name='B5'
    ).rio.write_crs("EPSG:4326")

    red_da = xr.DataArray(
        red_data,
        coords={'y': y_coords, 'x': x_coords},
        dims=['y', 'x'],
        name='B4'
    ).rio.write_crs("EPSG:4326")

    # Create Dataset
    ds = xr.Dataset({'B5': nir_da, 'B4': red_da})

    return ds


# Tests for reproject function

def test_reproject_basic(sample_raster_data):
    """Test basic reprojection functionality."""
    original_data = sample_raster_data

    # Test reprojection to Web Mercator
    reprojected = reproject(original_data, "EPSG:3857")

    # Check that result is a DataArray
    assert isinstance(reprojected, xr.DataArray)

    # Check that CRS has changed
    assert reprojected.rio.crs.to_epsg() == 3857
    assert original_data.rio.crs.to_epsg() == 4326

    # Check that data is preserved (shape might change due to reprojection)
    assert reprojected.name == original_data.name


def test_reproject_with_kwargs(sample_raster_data):
    """Test reprojection with additional keyword arguments."""
    original_data = sample_raster_data

    # Test reprojection with resolution parameter
    reprojected = reproject(original_data, "EPSG:3857", resolution=1000.0)

    # Check that result is a DataArray
    assert isinstance(reprojected, xr.DataArray)

    # Check that CRS has changed
    assert reprojected.rio.crs.to_epsg() == 3857


def test_reproject_errors(sample_raster_data):
    """Test error handling in reproject function."""
    # Create a DataArray with rio accessor but no CRS
    data_no_crs = xr.DataArray(
        sample_raster_data.values,
        coords={'y': sample_raster_data.coords['y'], 'x': sample_raster_data.coords['x']},
        dims=sample_raster_data.dims,
        name='test_no_crs'
    )
    # This will have rio accessor but no CRS

    # Test error when no CRS is defined
    with pytest.raises(ValueError, match="Input DataArray must have a CRS defined"):
        reproject(data_no_crs, "EPSG:3857")


def test_reproject_different_crs_formats(sample_raster_data):
    """Test reprojection with different CRS format inputs."""
    original_data = sample_raster_data

    # Test with EPSG integer
    reprojected_int = reproject(original_data, 3857)
    assert reprojected_int.rio.crs.to_epsg() == 3857

    # Test with EPSG string
    reprojected_str = reproject(original_data, "EPSG:3857")
    assert reprojected_str.rio.crs.to_epsg() == 3857


# Tests for normalized_difference function

def test_normalized_difference_dataarray(sample_multiband_data):
    """Test normalized difference calculation with DataArray."""
    multiband_data = sample_multiband_data

    # Calculate NDVI (NIR - Red) / (NIR + Red)
    ndvi = normalized_difference(multiband_data, 'nir', 'red')

    # Check that result is a DataArray
    assert isinstance(ndvi, xr.DataArray)

    # Check dimensions (should lose the band dimension)
    assert 'band' not in ndvi.dims
    assert 'y' in ndvi.dims and 'x' in ndvi.dims

    # Check shape
    expected_shape = (multiband_data.sizes['y'], multiband_data.sizes['x'])
    assert ndvi.shape == expected_shape

    # Manually calculate expected NDVI for verification
    nir_band = multiband_data.sel(band='nir')
    red_band = multiband_data.sel(band='red')
    expected_ndvi = (nir_band - red_band) / (nir_band + red_band)

    # Check that calculated values match expected
    np.testing.assert_array_almost_equal(ndvi.values, expected_ndvi.values, decimal=6)


def test_normalized_difference_dataset(sample_dataset):
    """Test normalized difference calculation with Dataset."""
    dataset = sample_dataset

    # Calculate NDVI using band names from dataset
    ndvi = normalized_difference(dataset, 'B5', 'B4')  # NIR, Red

    # Check that result is a DataArray
    assert isinstance(ndvi, xr.DataArray)

    # Check dimensions
    assert 'y' in ndvi.dims and 'x' in ndvi.dims

    # Check shape
    expected_shape = (dataset.sizes['y'], dataset.sizes['x'])
    assert ndvi.shape == expected_shape

    # Manually calculate expected NDVI
    nir_band = dataset['B5']
    red_band = dataset['B4']
    expected_ndvi = (nir_band - red_band) / (nir_band + red_band)

    # Check that calculated values match expected
    np.testing.assert_array_almost_equal(ndvi.values, expected_ndvi.values, decimal=6)


def test_normalized_difference_errors():
    """Test error handling in normalized_difference function."""
    # Test with unsupported input type
    with pytest.raises(TypeError, match="Input 'array' must be an xr.DataArray or xr.Dataset"):
        normalized_difference(np.array([[1, 2], [3, 4]]), 'band1', 'band2')

    # Test with DataArray without band coordinate
    data_no_band = xr.DataArray(np.random.rand(3, 4), dims=['y', 'x'])
    with pytest.raises(ValueError, match="Input xr.DataArray must have a 'band' coordinate"):
        normalized_difference(data_no_band, 'band1', 'band2')

    # Test with DataArray with invalid band names
    data_with_bands = xr.DataArray(
        np.random.rand(2, 3, 4),
        coords={'band': ['red', 'green'], 'y': [0, 1, 2], 'x': [0, 1, 2, 3]},
        dims=['band', 'y', 'x']
    )
    with pytest.raises(ValueError, match="Band identifiers 'nir' or 'blue' not found"):
        normalized_difference(data_with_bands, 'nir', 'blue')

    # Test with Dataset with missing variables
    dataset = xr.Dataset({
        'B1': xr.DataArray(np.random.rand(2, 3), dims=['y', 'x']),
        'B2': xr.DataArray(np.random.rand(2, 3), dims=['y', 'x'])
    })
    with pytest.raises(ValueError, match="Band 'B5' not found as a variable"):
        normalized_difference(dataset, 'B5', 'B1')


def test_normalized_difference_edge_cases(sample_multiband_data):
    """Test edge cases for normalized_difference function."""
    multiband_data = sample_multiband_data

    # Test with integer band indices (if bands are numbered)
    data_with_int_bands = multiband_data.copy()
    data_with_int_bands = data_with_int_bands.assign_coords(band=[0, 1, 2])

    ndvi = normalized_difference(data_with_int_bands, 2, 0)  # NIR (index 2), Red (index 0)
    assert isinstance(ndvi, xr.DataArray)
    assert ndvi.shape == (multiband_data.sizes['y'], multiband_data.sizes['x'])

    # Test division by zero handling
    # Create data where NIR + Red = 0 for some pixels
    zero_sum_data = multiband_data.copy()
    zero_sum_data.loc[dict(band='nir', y=1.0, x=0.0)] = 0.1
    zero_sum_data.loc[dict(band='red', y=1.0, x=0.0)] = -0.1  # NIR + Red = 0

    ndvi_with_zero = normalized_difference(zero_sum_data, 'nir', 'red')

    # Check that division by zero results in inf or nan
    assert np.isfinite(ndvi_with_zero.values).sum() < ndvi_with_zero.size or np.isinf(ndvi_with_zero.values).any()


# Tests for xarray accessor functionality

def test_dataarray_accessor_reproject(sample_raster_data):
    """Test the .pmg.reproject() accessor method."""
    original_data = sample_raster_data

    # Test accessor method
    reprojected = original_data.pmg.reproject("EPSG:3857")

    # Check that result is a DataArray
    assert isinstance(reprojected, xr.DataArray)

    # Check that CRS has changed
    assert reprojected.rio.crs.to_epsg() == 3857
    assert original_data.rio.crs.to_epsg() == 4326

    # Compare with standalone function
    reprojected_standalone = reproject(original_data, "EPSG:3857")

    # Results should be identical
    np.testing.assert_array_equal(reprojected.values, reprojected_standalone.values)
    assert reprojected.rio.crs == reprojected_standalone.rio.crs


def test_dataarray_accessor_normalized_difference(sample_multiband_data):
    """Test the .pmg.normalized_difference() accessor method."""
    multiband_data = sample_multiband_data

    # Test accessor method
    ndvi_accessor = multiband_data.pmg.normalized_difference('nir', 'red')

    # Check that result is a DataArray
    assert isinstance(ndvi_accessor, xr.DataArray)

    # Compare with standalone function
    ndvi_standalone = normalized_difference(multiband_data, 'nir', 'red')

    # Results should be identical
    np.testing.assert_array_equal(ndvi_accessor.values, ndvi_standalone.values)


def test_dataset_accessor_normalized_difference(sample_dataset):
    """Test the .pmg.normalized_difference() accessor method for Dataset."""
    dataset = sample_dataset

    # Test accessor method
    ndvi_accessor = dataset.pmg.normalized_difference('B5', 'B4')

    # Check that result is a DataArray
    assert isinstance(ndvi_accessor, xr.DataArray)

    # Compare with standalone function
    ndvi_standalone = normalized_difference(dataset, 'B5', 'B4')

    # Results should be identical
    np.testing.assert_array_equal(ndvi_accessor.values, ndvi_standalone.values)


# Integration tests

def test_accessor_registration():
    """Test that the .pmg accessor is properly registered."""
    # Create a simple DataArray
    data = xr.DataArray(np.random.rand(3, 4), dims=['y', 'x'])

    # Check that .pmg accessor exists
    assert hasattr(data, 'pmg')

    # Check that accessor has expected methods
    assert hasattr(data.pmg, 'reproject')
    assert hasattr(data.pmg, 'normalized_difference')

    # Create a simple Dataset
    dataset = xr.Dataset({'var1': data})

    # Check that .pmg accessor exists for Dataset
    assert hasattr(dataset, 'pmg')
    assert hasattr(dataset.pmg, 'normalized_difference')


def test_integration_with_pmg_read():
    """Test integration with pmg.read() function (if available)."""
    # This test would require actual raster files, so we'll create a mock scenario
    # Create a sample raster-like DataArray that mimics what pmg.read() would return

    # Create sample data that looks like a real raster
    data = np.random.rand(10, 10).astype(np.float32)
    x_coords = np.linspace(-180, 180, 10)
    y_coords = np.linspace(-90, 90, 10)

    raster = xr.DataArray(
        data,
        coords={'y': y_coords, 'x': x_coords},
        dims=['y', 'x'],
        name='sample_raster'
    ).rio.write_crs("EPSG:4326")

    # Test that we can use the accessor on this "read" data
    assert hasattr(raster, 'pmg')

    # Test reprojection
    reprojected = raster.pmg.reproject("EPSG:3857")
    assert reprojected.rio.crs.to_epsg() == 3857

    # Test that the workflow works end-to-end
    assert isinstance(reprojected, xr.DataArray)
    assert reprojected.name == 'sample_raster'


def test_real_world_ndvi_calculation():
    """Test a realistic NDVI calculation scenario."""
    # Create realistic Landsat-like data
    # Typical Landsat 8 bands: Red (Band 4), NIR (Band 5)

    # Create sample reflectance values (0-1 range)
    red_values = np.array([[0.1, 0.15, 0.2],
                           [0.12, 0.18, 0.22],
                           [0.08, 0.14, 0.19]], dtype=np.float32)

    nir_values = np.array([[0.4, 0.5, 0.6],
                           [0.45, 0.55, 0.65],
                           [0.35, 0.48, 0.58]], dtype=np.float32)

    # Stack into multi-band array
    bands_data = np.stack([red_values, nir_values], axis=0)

    # Create coordinates
    x_coords = np.array([100.0, 100.1, 100.2])  # Longitude
    y_coords = np.array([40.2, 40.1, 40.0])     # Latitude
    band_names = ['red', 'nir']

    # Create DataArray
    landsat_data = xr.DataArray(
        bands_data,
        coords={'band': band_names, 'y': y_coords, 'x': x_coords},
        dims=['band', 'y', 'x'],
        name='landsat_reflectance'
    ).rio.write_crs("EPSG:4326")

    # Calculate NDVI using accessor
    ndvi = landsat_data.pmg.normalized_difference('nir', 'red')

    # Verify NDVI properties
    assert isinstance(ndvi, xr.DataArray)
    assert ndvi.shape == (3, 3)  # Should match spatial dimensions

    # NDVI should be in range [-1, 1], but for vegetation typically [0, 1]
    assert np.all(ndvi.values >= -1) and np.all(ndvi.values <= 1)

    # For our sample data (vegetation), NDVI should be positive
    assert np.all(ndvi.values > 0)

    # Manually verify one calculation
    expected_ndvi_00 = (0.4 - 0.1) / (0.4 + 0.1)  # (NIR - Red) / (NIR + Red)
    np.testing.assert_almost_equal(ndvi.values[0, 0], expected_ndvi_00, decimal=6)
