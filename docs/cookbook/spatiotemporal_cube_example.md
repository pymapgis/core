# Creating Spatio-Temporal Cubes

PyMapGIS allows you to combine multiple 2D spatial raster datasets (as `xarray.DataArray` objects) taken at different times into a single 3D spatio-temporal data cube. This is useful for analyzing time-series raster data.

## 1. Setup

Ensure you have PyMapGIS installed, along with `xarray` and `numpy`.

```python
import pymapgis.raster as pmg_raster
import xarray as xr
import numpy as np
import pandas as pd # For creating datetime objects
import rioxarray # To add CRS info to sample DataArrays
```

## 2. Preparing Your Data

You need a list of 2D `xarray.DataArray` objects. Each DataArray should represent a spatial slice (e.g., a satellite image or a weather model output for a specific area) at a particular time.

**Important Considerations:**
- All DataArrays in the list must have the **same spatial dimensions** (e.g., same number of pixels for height/width).
- They must have **identical spatial coordinates** for these dimensions (e.g., the 'y' and 'x' coordinates must align perfectly).
- It's highly recommended that they share the **same Coordinate Reference System (CRS)**. The CRS of the first DataArray in the list will be assigned to the resulting cube.

```python
# Example: Create two sample 2D DataArrays
# In a real scenario, these might be read from GeoTIFF files or other sources.

# Define spatial coordinates (e.g., latitude and longitude)
y_coords = np.array([50.0, 50.1, 50.2])
x_coords = np.array([10.0, 10.1, 10.2, 10.3])

# Create data for time 1
data_t1 = np.random.rand(len(y_coords), len(x_coords)) # 3x4 array
da_t1 = xr.DataArray(
    data_t1,
    coords={'y': y_coords, 'x': x_coords},
    dims=['y', 'x'],
    name='temperature'
)
# Add CRS information using rioxarray (optional but good practice)
da_t1 = da_t1.rio.write_crs("EPSG:4326")
da_t1.rio.set_spatial_dims(x_dim='x', y_dim='y', inplace=True)


# Create data for time 2 (same spatial grid)
data_t2 = np.random.rand(len(y_coords), len(x_coords)) + 0.5 # Slightly different data
da_t2 = xr.DataArray(
    data_t2,
    coords={'y': y_coords, 'x': x_coords}, # Must match da_t1's spatial coords
    dims=['y', 'x'],
    name='temperature'
)
da_t2 = da_t2.rio.write_crs("EPSG:4326") # Match CRS
da_t2.rio.set_spatial_dims(x_dim='x', y_dim='y', inplace=True)


# List of your DataArrays
data_arrays_list = [da_t1, da_t2]

# Corresponding list of times for each DataArray
# These should be np.datetime64 objects
times_list = [
    np.datetime64('2023-07-15T10:00:00'),
    np.datetime64('2023-07-15T12:00:00')
]
```

## 3. Creating the Spatio-Temporal Cube

Use the `create_spatiotemporal_cube` function from `pymapgis.raster`.

```python
try:
    spatiotemporal_cube = pmg_raster.create_spatiotemporal_cube(
        data_arrays=data_arrays_list,
        times=times_list,
        time_dim_name="time" # You can customize the name of the time dimension
    )

    print("Spatio-temporal cube created successfully:")
    print(spatiotemporal_cube)

    # Verify dimensions and coordinates
    print("\nDimensions:", spatiotemporal_cube.dims) # Expected: ('time', 'y', 'x')
    print("Time coordinates:", spatiotemporal_cube.coords['time'].values)
    print("Y coordinates:", spatiotemporal_cube.coords['y'].values)
    print("X coordinates:", spatiotemporal_cube.coords['x'].values)

    # Verify CRS
    if hasattr(spatiotemporal_cube, 'rio'):
        print("CRS:", spatiotemporal_cube.rio.crs)

    # You can now perform time-series analysis, select slices, etc.
    # For example, select data for the first time point:
    first_time_slice = spatiotemporal_cube.sel(time=times_list[0])
    # print("\nData for first time point:")
    # print(first_time_slice)

except ValueError as e:
    print(f"Error creating cube: {e}")
except TypeError as e:
    print(f"Type error during cube creation: {e}")

```

## Alternative: Creating from NumPy arrays

If your raw data is in NumPy arrays (e.g. from sensor streams), `pymapgis.streaming` also provides a `create_spatiotemporal_cube_from_numpy` function. This is useful for constructing a cube from raw numerical data and associated coordinate arrays.

```python
from pymapgis.streaming import create_spatiotemporal_cube_from_numpy

# Example data (matches dimensions of TIMESTAMPS, Y_COORDS, X_COORDS from above)
raw_data_np = np.random.rand(len(times_list), len(y_coords), len(x_coords))

numpy_cube = create_spatiotemporal_cube_from_numpy(
    data=raw_data_np,
    timestamps=times_list,
    x_coords=x_coords,
    y_coords=y_coords,
    variable_name="numpy_derived_temp",
    attrs={"source": "numpy_array"}
)
print("\nCube from NumPy array:")
print(numpy_cube)
```

This cube can then be used for analysis, visualization (e.g., with `pymapgis.viz.deckgl_utils.view_3d_cube`), or saved to formats like NetCDF.
```
