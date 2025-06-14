import geopandas
import pandas as pd
import pyarrow as pa

def demonstrate_geoarrow_functionality():
    """
    Demonstrates loading data that might be GeoArrow-backed and performing
    simple operations.
    """
    import os

    # Try multiple possible paths for the parquet file
    possible_paths = [
        "sample_data.parquet",  # When running from the script's directory
        "docs/examples/geoarrow_example/sample_data.parquet",  # When running from repo root
        os.path.join(os.path.dirname(__file__), "sample_data.parquet")  # Relative to script location
    ]

    parquet_path = None
    for path in possible_paths:
        if os.path.exists(path):
            parquet_path = path
            break

    if parquet_path is None:
        print("Error: sample_data.parquet not found in any expected location")
        print("Please ensure 'sample_data.parquet' exists in the same directory and dependencies are installed.")
        return

    print(f"Loading GeoParquet file: {parquet_path}")
    try:
        gdf = geopandas.read_parquet(parquet_path)
    except Exception as e:
        print(f"Error reading GeoParquet file: {e}")
        print("Please ensure 'sample_data.parquet' exists in the same directory and dependencies are installed.")
        return

    print("\\nOriginal GeoDataFrame loaded:")
    print(gdf.head())
    print(f"Geometry column type: {type(gdf.geometry)}")
    if hasattr(gdf.geometry, 'array'):
        print(f"Internal geometry array type: {type(gdf.geometry.array)}")

    # Geopandas >=0.14.0 automatically uses PyArrow-backed arrays for geometry
    # when reading from GeoParquet if PyArrow is installed.
    # We can inspect the geometry array to see if it's a PyArrow-backed one.
    # Common types are geopandas.array.GeometryDtype (older) or specific pyarrow chunked arrays.

    # For demonstration, let's assume pymapgis aims to expose or ensure that
    # operations are efficient due to Arrow backing.
    # If a `to_geoarrow()` method were explicitly available in pymapgis or geopandas,
    # it would be called here.
    # e.g., `geoarrow_table = gdf.to_geoarrow()` or `geoarrow_table = pymapgis.to_geoarrow(gdf)`

    # Current geopandas versions (>=0.14) with pyarrow often default to Arrow-backed geometry.
    # Let's verify this by checking the type of the geometry array.
    is_arrow_backed = False
    if hasattr(gdf.geometry, 'array'):
        # Check if the geometry array is a PyArrow-backed extension array
        # geopandas.array.GeometryArrowArray is the new type
        if "GeometryArrowArray" in str(type(gdf.geometry.array)):
            is_arrow_backed = True
            print("\\nGeoDataFrame geometry is likely backed by GeoArrow (PyArrow).")
        else:
            print("\\nGeoDataFrame geometry array type is not the latest GeoArrow-backed type, but operations might still leverage Arrow.")

    # Perform a simple spatial operation: Filter by area
    # This operation would benefit from efficient in-memory formats like Arrow
    if 'Polygon' in gdf.geom_type.unique() or 'MultiPolygon' in gdf.geom_type.unique():
        # Ensure there are polygons to calculate area for
        gdf_polygons = gdf[gdf.geometry.type.isin(['Polygon', 'MultiPolygon'])].copy() # Use .copy() to avoid SettingWithCopyWarning
        if not gdf_polygons.empty:
            gdf_polygons['area'] = gdf_polygons.geometry.area
            print("\\nGeoDataFrame with calculated area for polygons:")
            print(gdf_polygons.head())

            # Example of a filter that could leverage Arrow's efficiency
            if not gdf_polygons[gdf_polygons['area'] > 0.5].empty:
                filtered_gdf = gdf_polygons[gdf_polygons['area'] > 0.5]
                print("\\nFiltered GeoDataFrame (polygons with area > 0.5):")
                print(filtered_gdf)
            else:
                print("\\nNo polygons found with area > 0.5.")
        else:
            print("\\nNo polygon geometries found to calculate area.")
    else:
        print("\\nNo polygon geometries found in the dataset to demonstrate area calculation and filtering.")

    # Demonstrate a non-spatial operation that also benefits from Arrow:
    # Filtering by attribute
    filtered_by_attribute = gdf[gdf['value'] > 25]
    print("\\nFiltered GeoDataFrame (features with 'value' > 25):")
    print(filtered_by_attribute)

    # If there was an explicit GeoArrow table object, we might print its head:
    # `print(geoarrow_table.head())`
    # For now, we work with the GeoDataFrame that is Arrow-backed.

    print("\\nGeoArrow example finished.")

if __name__ == "__main__":
    print("Starting GeoArrow example...")
    # Ensure necessary packages are available for the user running the script
    try:
        import geopandas
        import pyarrow
        import shapely
    except ImportError as e:
        print(f"Import Error: {e}. Please ensure geopandas, pyarrow, and shapely are installed.")
        print("You can typically install them using: pip install geopandas pyarrow shapely")
    else:
        demonstrate_geoarrow_functionality()
