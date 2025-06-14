"""
Utilities for converting between GeoPandas GeoDataFrames and GeoArrow-encoded PyArrow Tables.
"""

import geopandas as gpd
import pyarrow as pa
import geoarrow.pyarrow as ga
from typing import Optional


def geodataframe_to_geoarrow(gdf: gpd.GeoDataFrame) -> pa.Table:
    """
    Converts a GeoPandas GeoDataFrame to a PyArrow Table with GeoArrow-encoded geometry.

    The geometry column in the GeoDataFrame is converted to a GeoArrow extension array
    (e.g., WKB, Point, LineString, Polygon) within the PyArrow Table.
    CRS information from the GeoDataFrame is stored in the metadata of the geometry field.

    Args:
        gdf (gpd.GeoDataFrame): The input GeoDataFrame.

    Returns:
        pa.Table: A PyArrow Table with the geometry column encoded in GeoArrow format.
                  Other columns are converted to their PyArrow equivalents.

    Example:
        >>> import geopandas as gpd
        >>> from shapely.geometry import Point
        >>> data = {'id': [1, 2], 'geometry': [Point(0, 0), Point(1, 1)]}
        >>> gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")
        >>> arrow_table = geodataframe_to_geoarrow(gdf)
        >>> print(arrow_table.schema)
        id: int64
        geometry: extension<geoarrow.wkb>
        -- schema metadata --
        pandas: '{"index_columns": [{"kind": "range", "name": null, "start": 0, ...
        geo: '{"columns": {"geometry": {"crs": {"type": "Proj4", "projjson": {...
    """
    if not isinstance(gdf, gpd.GeoDataFrame):
        raise TypeError(f"Input must be a GeoDataFrame, got {type(gdf)}")

    # Identify the active geometry column name
    geometry_col_name = gdf.geometry.name

    # Convert the GeoDataFrame to a PyArrow Table.
    # geopandas.to_arrow() handles the conversion of standard dtypes.
    # For the geometry column, it typically converts to WKB by default if not explicitly handled.
    # We want to leverage geoarrow-py's specific encoding which might be more type-aware.

    # Use the column-by-column approach since ga.to_table() doesn't exist in current geoarrow API
    # Create a list of pyarrow arrays for each column
    arrow_arrays = []
    column_names = []

    for col_name in gdf.columns:
        if col_name == geometry_col_name:
            # Use geoarrow-py to convert the geometry series to a GeoArrow extension array
            # This automatically handles various geometry types and CRS.
            try:
                geo_array = ga.array(gdf[geometry_col_name])
                # Ensure CRS is preserved if the GeoDataFrame has one
                if gdf.crs is not None:
                    geo_array = ga.with_crs(geo_array, gdf.crs)
                arrow_arrays.append(geo_array)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to convert geometry column '{geometry_col_name}' to GeoArrow array. "
                    f"Original error: {e}"
                ) from e
        else:
            # For non-geometry columns, convert using pyarrow from_pandas
            try:
                arrow_arrays.append(pa.Array.from_pandas(gdf[col_name]))
            except Exception as e:
                raise RuntimeError(
                    f"Failed to convert column '{col_name}' to PyArrow array. "
                    f"Original error: {e}"
                ) from e
        column_names.append(col_name)

    # Create the PyArrow Table from the arrays and names
    try:
        arrow_table = pa.Table.from_arrays(arrow_arrays, names=column_names)
    except Exception as e:
        raise RuntimeError(
            "Failed to create PyArrow Table from arrays. " f"Original error: {e}"
        ) from e

    return arrow_table


def geoarrow_to_geodataframe(
    arrow_table: pa.Table, geometry_col_name: Optional[str] = None
) -> gpd.GeoDataFrame:
    """
    Converts a PyArrow Table (with GeoArrow-encoded geometry) back to a GeoPandas GeoDataFrame.

    The function identifies the GeoArrow-encoded geometry column in the Table.
    It uses this column to construct the GeoSeries for the GeoDataFrame.
    CRS information is expected to be in the metadata of the GeoArrow geometry field.

    Args:
        arrow_table (pa.Table): The input PyArrow Table with a GeoArrow-encoded geometry column.
        geometry_col_name (Optional[str]): The name of the geometry column in the
            Arrow table. If None, the function attempts to auto-detect the
            geometry column by looking for GeoArrow extension types.

    Returns:
        gpd.GeoDataFrame: A GeoPandas GeoDataFrame.

    Raises:
        ValueError: If a geometry column cannot be found or if multiple GeoArrow
                    columns exist and `geometry_col_name` is not specified.
        TypeError: If the input is not a PyArrow Table.

    Example:
        >>> # Assume 'arrow_table' is a PyArrow Table from geodataframe_to_geoarrow()
        >>> # gdf_roundtrip = geoarrow_to_geodataframe(arrow_table)
        >>> # print(gdf_roundtrip.crs)
        >>> # EPSG:4326
    """
    if not isinstance(arrow_table, pa.Table):
        raise TypeError(f"Input must be a PyArrow Table, got {type(arrow_table)}")

    # Auto-detect geometry column if not specified
    if geometry_col_name is None:
        geo_cols = [
            field.name
            for field in arrow_table.schema
            if isinstance(field.type, ga.GeometryExtensionType)
        ]
        if not geo_cols:
            raise ValueError(
                "No GeoArrow geometry column found in the Table. Please ensure one exists or specify 'geometry_col_name'."
            )
        if len(geo_cols) > 1:
            raise ValueError(
                f"Multiple GeoArrow geometry columns found: {geo_cols}. "
                "Please specify the desired 'geometry_col_name'."
            )
        geometry_col_name = geo_cols[0]
    elif geometry_col_name not in arrow_table.column_names:
        raise ValueError(
            f"Specified geometry_col_name '{geometry_col_name}' not found in Table columns: {arrow_table.column_names}"
        )

    # Check if the specified (or detected) column is indeed a GeoArrow type
    geom_field = arrow_table.schema.field(geometry_col_name)
    if not isinstance(geom_field.type, ga.GeometryExtensionType):
        raise ValueError(
            f"Column '{geometry_col_name}' is not a GeoArrow extension type. "
            f"Found type: {geom_field.type}. Cannot convert to GeoDataFrame geometry."
        )

    # Convert the PyArrow Table to GeoDataFrame
    # geoarrow.pyarrow.from_arrow() or from_table() should handle this.
    # The from_arrow function in older geoarrow versions might expect a GeoArrowArray.
    # More recent versions might have a from_table or similar.
    # geopandas.from_arrow() is the standard and should recognize GeoArrow extension types.

    try:
        # GeoPandas' from_arrow should be able to handle tables with GeoArrow extension arrays.
        gdf = gpd.GeoDataFrame.from_arrow(arrow_table)

        # After conversion, ensure the correct column is set as the active geometry column.
        # gpd.GeoDataFrame.from_arrow might not automatically set the geometry column
        # if there are multiple potential geometry columns or if it's ambiguous.
        # However, if there's a GeoArrow extension type, it's usually picked up.
        # We need to ensure that the column `geometry_col_name` is indeed the active geometry.

        if geometry_col_name in gdf.columns and isinstance(
            gdf[geometry_col_name], gpd.GeoSeries
        ):
            gdf = gdf.set_geometry(geometry_col_name)
        else:
            # This case should ideally not be reached if from_arrow works correctly with GeoArrow types
            # and geometry_col_name was validated to be a GeoArrow type.
            raise ValueError(
                f"Failed to correctly establish '{geometry_col_name}' as the geometry column "
                "after converting from Arrow table. Check table structure and GeoArrow types."
            )

    except Exception as e:
        raise RuntimeError(
            f"Failed to convert GeoArrow Table to GeoDataFrame. " f"Original error: {e}"
        ) from e

    return gdf


# Example usage (for testing/dev):
if __name__ == "__main__":
    from shapely.geometry import Point, LineString, Polygon

    # Create a sample GeoDataFrame
    data_dict = {
        "id": [1, 2, 3, 4],
        "name": ["Point A", "Point B", "Line C", "Polygon D"],
        "geometry": [
            Point(0, 0),
            Point(1, 1),
            LineString([(0, 0), (1, 1), (1, 2)]),
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        ],
    }
    sample_gdf = gpd.GeoDataFrame(data_dict, crs="EPSG:4326")
    sample_gdf.loc[1, "geometry"] = None  # Add a missing geometry

    print("Original GeoDataFrame:")
    print(sample_gdf)
    print(f"CRS: {sample_gdf.crs}")
    print(f"Geometry column name: {sample_gdf.geometry.name}")
    print("\n")

    # Convert to GeoArrow Table
    try:
        arrow_table_converted = geodataframe_to_geoarrow(sample_gdf)
        print("Converted PyArrow Table Schema:")
        print(arrow_table_converted.schema)
        # print("\nTable Content (first 5 rows):")
        # print(arrow_table_converted.slice(0, 5))
        print("\n")

        # Convert back to GeoDataFrame
        gdf_roundtrip = geoarrow_to_geodataframe(arrow_table_converted)
        print("Round-tripped GeoDataFrame:")
        print(gdf_roundtrip)
        print(f"CRS: {gdf_roundtrip.crs}")
        print(
            f"Is GDF equal to original (except for potential minor differences like index type)? {sample_gdf.equals(gdf_roundtrip)}"
        )
        print(
            f"Is GDF geometrically equal? {sample_gdf.geometry.equals(gdf_roundtrip.geometry)}"
        )

        # Test CRS and attributes
        assert gdf_roundtrip.crs == sample_gdf.crs, "CRS mismatch"
        assert "id" in gdf_roundtrip.columns
        assert "name" in gdf_roundtrip.columns
        assert gdf_roundtrip["id"].tolist() == sample_gdf["id"].tolist()

        # More rigorous check
        # gpd.testing.assert_geodataframe_equal(sample_gdf, gdf_roundtrip, check_dtype=False, check_index_type=False)
        # print("\nGeoDataFrame roundtrip equality check passed (with type flexibility).")

    except Exception as e:
        print(f"An error occurred during the example run: {e}")
        import traceback

        traceback.print_exc()
