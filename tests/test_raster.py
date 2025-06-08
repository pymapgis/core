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
def ome_zarr_store_path():
    """
    Creates a temporary OME-Zarr multiscale store for testing.
    Yields the path to the root of the Zarr store.
    Cleans up the temporary directory afterwards.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        zarr_root_path = os.path.join(tmpdir, "test_image.zarr")
        root_group = zarr.open_group(zarr_root_path, mode='w')

        # Define scales and data
        # Level 0: 256x256, chunks (64,64)
        data_l0_np = np.arange(256 * 256, dtype=np.uint16).reshape((256, 256))
        # Level 1: 128x128, chunks (64,64)
        data_l1_np = data_l0_np[::2, ::2] + data_l0_np[1::2, ::2] + data_l0_np[::2, 1::2] + data_l0_np[1::2, 1::2]
        data_l1_np = (data_l1_np / 4).astype(np.uint16)
        # Level 2: 64x64, chunks (32,32)
        data_l2_np = data_l1_np[::2, ::2] + data_l1_np[1::2, ::2] + data_l1_np[::2, 1::2] + data_l1_np[1::2, 1::2]
        data_l2_np = (data_l2_np / 4).astype(np.uint16)

        datasets_metadata = []
        levels_data = {
            "0": {"data": data_l0_np, "chunks": (64, 64), "scale": [1, 1]},
            "1": {"data": data_l1_np, "chunks": (64, 64), "scale": [2, 2]}, # y,x scale factors
            "2": {"data": data_l2_np, "chunks": (32, 32), "scale": [4, 4]},
        }

        for path_name, level_info in levels_data.items():
            arr = root_group.create_dataset(
                path_name,
                data=level_info["data"],
                chunks=level_info["chunks"],
                dtype=level_info["data"].dtype,
                overwrite=True
            )
            arr.attrs['_ARRAY_DIMENSIONS'] = ['y', 'x'] # OME-Zarr standard dimension names

            datasets_metadata.append({
                "path": path_name,
                "coordinateTransformations": [{
                    "type": "scale",
                    "scale": [
                        float(level_info["scale"][0]), # y scale
                        float(level_info["scale"][1]), # x scale
                    ]
                }]
            })

        # Write OME-NGFF multiscale metadata
        root_group.attrs['multiscales'] = [{
            "version": "0.4", # Using OME-NGFF v0.4 spec
            "name": "test_image",
            "axes": [
                {"name": "y", "type": "space", "unit": "pixel"},
                {"name": "x", "type": "space", "unit": "pixel"}
            ],
            "datasets": datasets_metadata,
            "type": "mean", # Example reducer type
            # "metadata": { # Optional metadata
            #     "description": "A test multiscale image"
            # }
        }]

        # Store original numpy data for assertions later
        # Not strictly part of the fixture's yielded value, but makes sense to keep it tied
        # Alternatively, this could be generated within the test function itself.
        # For simplicity, we'll re-generate or pass it if needed in the test.
        # Or, the test can read it back if it needs to.

        zarr.consolidate_metadata(root_group.store) # Consolidate metadata
        yield zarr_root_path
        # tmpdir is automatically cleaned up


def test_lazy_windowed_read_zarr(ome_zarr_store_path):
    """
    Tests the lazy_windowed_read_zarr function for correct data extraction
    and lazy loading behavior.
    """
    store_path = ome_zarr_store_path

    # Define window and level for testing
    # Test on Level 1 (128x128 original size)
    level_to_test = 1
    window_to_read = {'x': 10, 'y': 20, 'width': 30, 'height': 40} # Slices (y: 20-60, x: 10-40)

    # Expected data from Level 1
    # Recreate level 1 data for assertion
    data_l0_np = np.arange(256 * 256, dtype=np.uint16).reshape((256, 256))
    data_l1_np = (data_l0_np[::2, ::2] + data_l0_np[1::2, ::2] + data_l0_np[::2, 1::2] + data_l0_np[1::2, 1::2]) / 4
    data_l1_np = data_l1_np.astype(np.uint16)

    expected_slice_y = slice(window_to_read['y'], window_to_read['y'] + window_to_read['height'])
    expected_slice_x = slice(window_to_read['x'], window_to_read['x'] + window_to_read['width'])
    expected_data_np = data_l1_np[expected_slice_y, expected_slice_x]

    # Use lazy_windowed_read_zarr
    # Pass axis_order='YX' explicitly as per how data was written (_ARRAY_DIMENSIONS: ['y', 'x'])
    result_array = lazy_windowed_read_zarr(
        store_path,
        window_to_read,
        level=level_to_test,
        axis_order="YX"
    )

    # 1. Assert Laziness (qualitatively)
    # Check if the returned array is a Dask array (typical for lazy xarray operations on Zarr)
    # or if its internal _in_memory flag is False (more of an internal check)
    assert da.is_dask_collection(result_array.data), "Data should be a Dask array (lazy)."
    # For xarray versions where .variable._in_memory is reliable:
    # assert not result_array.variable._in_memory, "Data should not be in memory before compute()"

    # 2. Assert correct shape
    # Expected shape is (height, width) due to YX convention
    assert result_array.shape == (window_to_read['height'], window_to_read['width']), \
        f"Shape mismatch: expected {(window_to_read['height'], window_to_read['width'])}, got {result_array.shape}"

    # 3. Compute the data
    computed_data = result_array.compute()

    # 4. Assert data content matches expected
    assert isinstance(computed_data, xr.DataArray), "Computed data should be an xarray.DataArray"
    np.testing.assert_array_equal(computed_data.data, expected_data_np,
                                   err_msg="Data content mismatch after compute()")

    # 5. Test with string level
    result_array_str_level = lazy_windowed_read_zarr(
        store_path,
        window_to_read,
        level=str(level_to_test), # e.g. "1"
        axis_order="YX"
    )
    assert da.is_dask_collection(result_array_str_level.data)
    computed_data_str_level = result_array_str_level.compute()
    np.testing.assert_array_equal(computed_data_str_level.data, expected_data_np,
                                   err_msg="Data content mismatch with string level")

    # 6. Test error handling for invalid level
    with pytest.raises(IndexError, match="Level 99 is out of bounds"):
        lazy_windowed_read_zarr(store_path, window_to_read, level=99, axis_order="YX")

    with pytest.raises(ValueError, match="Level 'invalid_level' is a non-integer string"):
        lazy_windowed_read_zarr(store_path, window_to_read, level="invalid_level", axis_order="YX")

    # 7. Test error handling for incorrect window keys
    with pytest.raises(KeyError, match="Window dictionary must contain"):
        lazy_windowed_read_zarr(store_path, {'x': 0, 'y': 0, 'w': 10, 'h': 10}, level=0, axis_order="YX")

    # 8. Test reading from level 0
    level0_window = {'x': 0, 'y': 0, 'width': 10, 'height': 10}
    expected_data_l0 = data_l0_np[0:10, 0:10]
    result_l0 = lazy_windowed_read_zarr(store_path, level0_window, level=0, axis_order="YX")
    np.testing.assert_array_equal(result_l0.compute().data, expected_data_l0,
                                   err_msg="Data content mismatch for level 0")

    # 9. Test reading from a different group (should fail if multiscale metadata is not there)
    #    This tests the multiscale_group_name parameter.
    #    First, create a subgroup and put a dummy array there.
    root_zarr_group = zarr.open_group(store_path, mode='a')
    sub_group = root_zarr_group.create_group("subgroup")
    sub_group.array("data", data=np.array([1,2,3]), chunks=(1,))
    zarr.consolidate_metadata(root_zarr_group.store)

    with pytest.raises(Exception, match="Failed to interpret"): # xarray_multiscale.multiscale will fail
        lazy_windowed_read_zarr(store_path, window_to_read, level=0,
                                multiscale_group_name="subgroup", axis_order="YX")

    # Test with a non-existent group
    with pytest.raises(zarr.errors.PathNotFoundError):
         lazy_windowed_read_zarr(store_path, window_to_read, level=0,
                                multiscale_group_name="nonexistent_group", axis_order="YX")


# Example of how to run this test with pytest:
# Ensure PYTHONPATH includes the pymapgis directory.
# pytest tests/test_raster.py
