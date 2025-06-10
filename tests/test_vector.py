import pytest
import pyarrow as pa
import geoarrow.pyarrow as ga
import geopandas
from shapely.geometry import Point, LineString, Polygon, MultiPoint, GeometryCollection
from pandas.testing import assert_frame_equal
from pymapgis.vector import buffer
from pymapgis.vector.geoarrow_utils import geodataframe_to_geoarrow, geoarrow_to_geodataframe

# Conditional import for older geopandas versions
try:
    from geopandas.testing import assert_geodataframe_equal
except ImportError:
    # A basic fallback for older GeoPandas if assert_geodataframe_equal is not available
    # This is not a complete replacement but can help in some CI environments.
    def assert_geodataframe_equal(left, right, check_geom_type=True, check_crs=True, **kwargs):
        assert_frame_equal(left.drop(columns=left.geometry.name), right.drop(columns=right.geometry.name), **kwargs)
        if check_crs:
            assert left.crs == right.crs, f"CRS mismatch: {left.crs} != {right.crs}"
        if check_geom_type:
            assert (left.geom_type == right.geom_type).all(), "Geometry type mismatch"
        # For actual geometry comparison, Shapely's equals_exact or equals might be needed
        # This basic fallback does not compare geometry values directly in detail.
        assert left.geometry.equals(right.geometry).all(), "Geometry values mismatch"


def test_buffer_simple():
    """Tests the buffer function with a simple Point geometry."""
    # Create a simple GeoDataFrame
    data = {'id': [1], 'geometry': [Point(0, 0)]}
    gdf = geopandas.GeoDataFrame(data, crs="EPSG:4326")

    # Call the buffer function
    result = buffer(gdf, distance=10)

    # Assertions
    assert isinstance(result, geopandas.GeoDataFrame)
    assert not result.empty
    assert result.geometry.iloc[0].geom_type == 'Polygon'
    assert result.crs == gdf.crs

@pytest.fixture
def sample_gdf_all_types():
    """GeoDataFrame with various geometry types, attributes, CRS, and some nulls."""
    data = {
        'id': [1, 2, 3, 4, 5, 6, 7],
        'name': ['Point A', 'Line B', 'Poly C', 'MultiPoint D', 'None E', 'Empty Poly F', 'GeomCollection G'],
        'geometry': [
            Point(0, 0),
            LineString([(1, 1), (2, 2)]),
            Polygon([(3, 3), (4, 3), (4, 4), (3, 4)]),
            MultiPoint([(0,0), (1,1)]),
            None, # Null geometry
            Polygon(), # Empty geometry
            GeometryCollection([Point(5,5), LineString([(6,6),(7,7)])]) # Geometry Collection
        ]
    }
    gdf = geopandas.GeoDataFrame(data, crs="EPSG:4326")
    return gdf

@pytest.fixture
def empty_gdf():
    """An empty GeoDataFrame."""
    return geopandas.GeoDataFrame({'id': [], 'geometry': []}, geometry='geometry', crs="EPSG:3857")


def test_geodataframe_to_geoarrow_conversion(sample_gdf_all_types):
    gdf = sample_gdf_all_types
    arrow_table = geodataframe_to_geoarrow(gdf)

    assert isinstance(arrow_table, pa.Table)
    assert 'geometry' in arrow_table.column_names
    assert 'id' in arrow_table.column_names
    assert 'name' in arrow_table.column_names

    # Check schema for GeoArrow extension type (specific type depends on geoarrow-py version and content)
    geom_field = arrow_table.schema.field('geometry')
    # Check that it's a GeoArrow extension type
    assert isinstance(geom_field.type, ga.GeometryExtensionType)

    # Verify CRS is preserved in the extension type
    # In geoarrow-pyarrow, CRS is stored in the extension type itself, not field metadata
    assert geom_field.type.crs is not None
    # The CRS representation might be wrapped, so check if it contains the expected EPSG code
    crs_str = str(geom_field.type.crs)
    assert 'EPSG:4326' in crs_str  # Should contain the original GDF CRS

def test_geoarrow_to_geodataframe_conversion(sample_gdf_all_types):
    gdf_original = sample_gdf_all_types
    arrow_table = geodataframe_to_geoarrow(gdf_original)
    gdf_roundtrip = geoarrow_to_geodataframe(arrow_table, geometry_col_name='geometry')

    assert isinstance(gdf_roundtrip, geopandas.GeoDataFrame)
    # Using geopandas' testing utility for a more thorough comparison
    # It handles CRS, geometry types, and attribute values.
    # Note: May need to adjust check_dtype or other parameters based on how geoarrow handles types.
    # For example, GeoPandas often uses object dtype for geometry, direct Arrow might be more specific.
    # Null/empty geometry representation can also differ slightly.
    assert_geodataframe_equal(gdf_original, gdf_roundtrip, check_dtype=False, check_like=True)


def test_roundtrip_empty_geodataframe(empty_gdf):
    gdf_original = empty_gdf
    arrow_table = geodataframe_to_geoarrow(gdf_original)
    gdf_roundtrip = geoarrow_to_geodataframe(arrow_table, geometry_col_name='geometry')

    assert isinstance(gdf_roundtrip, geopandas.GeoDataFrame)
    assert gdf_roundtrip.empty
    assert_geodataframe_equal(gdf_original, gdf_roundtrip, check_index_type=False)


def test_roundtrip_with_explicit_geometry_col_name(sample_gdf_all_types):
    gdf_original = sample_gdf_all_types.rename_geometry('geom')
    arrow_table = geodataframe_to_geoarrow(gdf_original)

    # Test auto-detection (if only one geoarrow col)
    if 'geom' in arrow_table.column_names: # Check if rename was effective in arrow table column name
      gdf_roundtrip_auto = geoarrow_to_geodataframe(arrow_table)
      assert_geodataframe_equal(gdf_original, gdf_roundtrip_auto, check_dtype=False, check_like=True)

    # Test with explicit name
    gdf_roundtrip_explicit = geoarrow_to_geodataframe(arrow_table, geometry_col_name='geom')
    assert_geodataframe_equal(gdf_original, gdf_roundtrip_explicit, check_dtype=False, check_like=True)

def test_error_handling_geoarrow_to_geodataframe(sample_gdf_all_types):
    gdf = sample_gdf_all_types
    # Create a plain pyarrow table (non-geoarrow geometry)
    plain_table = pa.Table.from_pandas(gdf.drop(columns=[gdf.geometry.name]))

    with pytest.raises(ValueError, match="No GeoArrow geometry column found"):
        geoarrow_to_geodataframe(plain_table)

    arrow_table_geo = geodataframe_to_geoarrow(gdf)
    with pytest.raises(ValueError, match="Specified geometry_col_name 'non_existent_geom' not found"):
        geoarrow_to_geodataframe(arrow_table_geo, geometry_col_name='non_existent_geom')

    # Create a table with two geoarrow columns to test ambiguity
    geom_col_arrow = geodataframe_to_geoarrow(gdf[['geometry']]).column(0)
    geom_field = arrow_table_geo.schema.field('geometry')
    table_multi_geo = arrow_table_geo.add_column(0, pa.field("geometry2", geom_field.type, metadata=geom_field.metadata), geom_col_arrow)

    with pytest.raises(ValueError, match="Multiple GeoArrow geometry columns found"):
        geoarrow_to_geodataframe(table_multi_geo) # No specific name given

    # Test with a column that exists but isn't geoarrow type for geometry_col_name
    # For this, we'd need a table where 'id' is specified as geometry_col_name
    # but 'id' is not a geoarrow extension type.
    with pytest.raises(ValueError, match="Column 'id' is not a GeoArrow extension type"):
        geoarrow_to_geodataframe(arrow_table_geo, geometry_col_name='id')

def test_geodataframe_to_geoarrow_invalid_input():
    with pytest.raises(TypeError, match="Input must be a GeoDataFrame"):
        geodataframe_to_geoarrow("not a geodataframe")

def test_geoarrow_to_geodataframe_invalid_input():
    with pytest.raises(TypeError, match="Input must be a PyArrow Table"):
        geoarrow_to_geodataframe("not a pyarrow table")
