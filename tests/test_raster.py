import os
import shutil
import tempfile
import json

import numpy as np
import xarray as xr
import zarr
import pytest
import dask.array as da # For checking if it's a dask array

from pymapgis.raster import lazy_windowed_read_zarr


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
from pymapgis.raster import create_spatiotemporal_cube
import pandas as pd # For creating datetime objects for testing

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
