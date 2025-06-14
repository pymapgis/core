# GeoArrow DataFrames Example

This example demonstrates how `pymapgis` (leveraging `geopandas` and `pyarrow`) can work with GeoArrow-backed data structures for efficient geospatial operations. It shows how to load data from a GeoParquet file, which `geopandas` (version >= 0.14) can automatically represent in memory using PyArrow-backed geometry arrays.

## Functionality

The `geoarrow_example.py` script performs the following:

1.  **Loads Data:** It reads a sample GeoParquet file (`sample_data.parquet`) into a `geopandas.GeoDataFrame`.
2.  **Checks Backend:** It inspects the geometry column to infer if it's backed by PyArrow, which is indicative of GeoArrow usage. Modern `geopandas` versions enable this by default when `pyarrow` is installed.
3.  **Performs Operations:**
    *   Calculates the area of polygon geometries.
    *   Filters the GeoDataFrame based on the calculated area.
    *   Filters the GeoDataFrame based on an attribute value.
    These operations can be more efficient when data is stored in columnar formats like Arrow.
4.  **Prints Results:** The script outputs the head of the loaded GeoDataFrame, information about its geometry array type, and the results of the filtering operations.

## `sample_data.parquet`

The `sample_data.parquet` file included in this directory is a GeoParquet file containing a mix of 5 point and polygon geometries with the following attributes:

*   `id`: An integer identifier.
*   `name`: A string name for the feature.
*   `value`: A floating-point value associated with the feature.
*   `geometry`: The geometry column (points and polygons), stored in WGS84 (EPSG:4326).

It was created programmatically using `geopandas`.

## Dependencies

To run this example, you will need:

*   `pymapgis`: The core library (assumed to be in your environment).
*   `geopandas>=0.14.0`: For GeoDataFrame functionality and reading GeoParquet. Version 0.14.0+ has improved GeoArrow integration.
*   `pyarrow`: The library that provides the Arrow memory format and Parquet reading/writing capabilities.
*   `shapely>=2.0`: For geometry objects and operations (often a dependency of `geopandas`).

You can typically install these using pip:

```bash
pip install geopandas pyarrow shapely pandas
```
(`pandas` is included as `geopandas` depends on it).

## How to Run

1.  **Navigate to the example directory:**
    ```bash
    cd path/to/your/pymapgis/docs/examples/geoarrow_example/
    ```
2.  **Run the script:**
    ```bash
    python geoarrow_example.py
    ```

## Expected Output

The script will print information about the loaded GeoDataFrame, its internal geometry representation, and the results of the analysis. The output will look something like this (exact geometry representations and types might vary slightly based on library versions):

```
Starting GeoArrow example...
Loading GeoParquet file: docs/examples/geoarrow_example/sample_data.parquet

Original GeoDataFrame loaded:
   id       name  value                                           geometry
0   1    Point A   10.5                                  POINT (1.00000 1.00000)
1   2    Point B   20.3                                  POINT (2.00000 2.00000)
2   3  Polygon C   30.1  POLYGON ((3.00000 3.00000, 4.00000 3.00000, 4....
3   4  Polygon D   40.8  POLYGON ((5.00000 5.00000, 6.00000 5.00000, 6....
4   5    Point E   50.2                                  POINT (7.00000 7.00000)
Geometry column type: <class 'geopandas.geoseries.GeoSeries'>
Internal geometry array type: <class 'geopandas.array.GeometryArrowArray'>
\nGeoDataFrame geometry is likely backed by GeoArrow (PyArrow).

GeoDataFrame with calculated area for polygons:
   id       name  value                                           geometry      area
2   3  Polygon C   30.1  POLYGON ((3.00000 3.00000, 4.00000 3.00000, 4....  1.000000
3   4  Polygon D   40.8  POLYGON ((5.00000 5.00000, 6.00000 5.00000, 6....  0.750000

Filtered GeoDataFrame (polygons with area > 0.5):
   id       name  value                                           geometry    area
2   3  Polygon C   30.1  POLYGON ((3.00000 3.00000, 4.00000 3.00000, 4....   1.0
3   4  Polygon D   40.8  POLYGON ((5.00000 5.00000, 6.00000 5.00000, 6....   0.75


Filtered GeoDataFrame (features with 'value' > 25):
   id       name  value                                           geometry      area
2   3  Polygon C   30.1  POLYGON ((3.00000 3.00000, 4.00000 3.00000, 4....  1.000000
3   4  Polygon D   40.8  POLYGON ((5.00000 5.00000, 6.00000 5.00000, 6....  0.750000
4   5    Point E   50.2                                  POINT (7.00000 7.00000)       NaN

GeoArrow example finished.
```
Note: The 'area' column will only be present for polygon features in the "Filtered GeoDataFrame (features with 'value' > 25)" if those features were polygons. The exact output for the last filtering step will depend on which features meet the criteria.
The `Internal geometry array type` might show `GeometryArrowArray` or similar, confirming Arrow backing.
If you see `SettingWithCopyWarning`, it's a pandas warning that can often be ignored for simple examples but is good to be aware of for more complex data manipulations.
