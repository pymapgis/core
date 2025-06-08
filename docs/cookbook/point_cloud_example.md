# Working with Point Clouds (LAS/LAZ)

PyMapGIS supports reading point cloud data from LAS and LAZ files using PDAL (Point Data Abstraction Library). This cookbook demonstrates how to read point cloud files and access their data and metadata.

## 1. PDAL Installation - Very Important!

PDAL can be tricky to install using pip alone due to its complex dependencies (GDAL, libLAS, etc.). **It is highly recommended to install PDAL using Conda:**

```bash
conda install -c conda-forge pdal python-pdal
```

Ensure that the Python environment where you run PyMapGIS has access to the `pdal` Python bindings installed by Conda. If PDAL is not correctly installed and found by Python, the point cloud functionalities in PyMapGIS will raise errors.

## 2. Reading Point Cloud Files

You can read LAS/LAZ files using the main `pymapgis.read()` function or by using functions directly from the `pymapgis.pointcloud` module for more control.

### Using `pymapgis.read()`

This is the simplest way to get point data as a NumPy structured array.

```python
import pymapgis as pmg
import numpy as np

# Assume you have a LAS or LAZ file: "path/to/your/data.las"
try:
    # Replace with the actual path to your LAS/LAZ file
    # points_array = pmg.read("path/to/your/data.las")

    # For this example, let's create a dummy LAS file first
    # (Requires PDAL to be working for create_las_from_numpy)
    from pymapgis.pointcloud import create_las_from_numpy
    dummy_points = np.array([
        (10, 20, 30, 100),
        (11, 21, 31, 120),
        (12, 22, 32, 110)
    ], dtype=[('X', float), ('Y', float), ('Z', float), ('Intensity', int)])
    dummy_las_path = "dummy_test_file.las"
    create_las_from_numpy(dummy_points, dummy_las_path) # SRS can be added too

    points_array = pmg.read(dummy_las_path)

    if points_array.size > 0:
        print(f"Successfully read {len(points_array)} points.")
        print("First 3 points (X, Y, Z, Intensity):")
        for i in range(min(3, len(points_array))):
            # Accessing fields depends on the exact dimension names from PDAL
            # Common names are 'X', 'Y', 'Z', 'Intensity', 'ReturnNumber', etc.
            # Check points_array.dtype.names for available fields.
            print(f"  {points_array['X'][i]}, {points_array['Y'][i]}, {points_array['Z'][i]}, {points_array['Intensity'][i]}")
        print("\nAvailable dimensions (fields):", points_array.dtype.names)
    else:
        print("No points found or file is empty.")

except RuntimeError as e:
    print(f"Error reading point cloud: {e}")
    print("Please ensure PDAL is correctly installed and the file path is correct.")
except FileNotFoundError:
    print(f"Error: File not found at {dummy_las_path} (or your specified path).")
finally:
    import os
    if os.path.exists(dummy_las_path):
        os.remove(dummy_las_path) # Clean up dummy file
```

### Using `pymapgis.pointcloud` Module

For more detailed access to the PDAL pipeline, metadata, and SRS information, use the functions in `pymapgis.pointcloud`.

```python
import pymapgis.pointcloud as pmg_pc
import numpy as np # ensure it's imported

# Assume dummy_las_path from previous example, or use your own file path
dummy_las_path = "dummy_test_file_for_pc_module.las"
# Recreate for this example block if needed:
from pymapgis.pointcloud import create_las_from_numpy
dummy_points_pc = np.array([(15,25,35,90)], dtype=[('X',float),('Y',float),('Z',float),('Intensity',int)])
create_las_from_numpy(dummy_points_pc, dummy_las_path, srs_wkt="EPSG:4326")


try:
    # 1. Read the point cloud file into a PDAL pipeline object
    pipeline = pmg_pc.read_point_cloud(dummy_las_path)
    print("PDAL Pipeline executed.")

    # 2. Get points as a NumPy structured array
    points = pmg_pc.get_point_cloud_points(pipeline)
    if points.size > 0:
        print(f"\nRead {len(points)} points using pointcloud module.")
        print("First point's X, Y, Z:", points[0]['X'], points[0]['Y'], points[0]['Z'])
        print("Available dimensions:", points.dtype.names)

    # 3. Get metadata
    metadata = pmg_pc.get_point_cloud_metadata(pipeline)
    print("\nPartial Metadata:")
    # print(json.dumps(metadata, indent=2)) # Full metadata can be verbose
    if metadata.get('quickinfo'):
         print(f"  Quickinfo (num points): {metadata['quickinfo'].get('num_points', 'N/A')}")
         print(f"  Quickinfo (bounds): {metadata['quickinfo'].get('bounds', 'N/A')}")
    print(f"  Schema (dimensions): {metadata.get('dimensions')}")


    # 4. Get Spatial Reference System (SRS) information
    srs_wkt = pmg_pc.get_point_cloud_srs(pipeline)
    if srs_wkt:
        print(f"\nSRS (WKT):\n{srs_wkt[:100]}...") # Print first 100 chars
    else:
        print("\nNo SRS information found or parsed.")

except RuntimeError as e:
    print(f"Error with point cloud module: {e}")
except FileNotFoundError:
    print(f"Error: File not found at {dummy_las_path}")
finally:
    import os
    if os.path.exists(dummy_las_path):
        os.remove(dummy_las_path) # Clean up dummy file
```

## 3. Understanding the Output

- **NumPy Structured Array**: When you get points (either from `pmg.read()` or `get_point_cloud_points()`), they are returned as a NumPy structured array. Each element of the array is a point, and the structure fields are the point dimensions (e.g., `X`, `Y`, `Z`, `Intensity`, `ReturnNumber`, `Classification`, `GpsTime`, etc.). The available dimensions depend on the content of your LAS/LAZ file. You can inspect `array.dtype.names` to see all available fields.
- **Metadata**: The metadata dictionary can contain a wealth of information, including point counts, coordinate system details, bounding boxes, histograms (if computed by a PDAL `filters.stats` stage, not added by default in `read_point_cloud`), and LAS header information.
- **SRS/CRS**: The Spatial Reference System is typically provided as a WKT (Well-Known Text) string.

This provides a basic workflow for handling point cloud data in PyMapGIS. For advanced processing, you might need to construct more complex PDAL pipelines manually using the `pdal` Python API directly.
```
