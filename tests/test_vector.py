import pytest
import pyarrow as pa
import geoarrow.pyarrow as ga
import geopandas
from shapely.geometry import Point, LineString, Polygon, MultiPoint, GeometryCollection
from pandas.testing import assert_frame_equal
from pymapgis.vector import buffer, clip, overlay, spatial_join
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


# ============================================================================
# COMPREHENSIVE VECTOR OPERATIONS TESTS
# ============================================================================

@pytest.fixture
def sample_points():
    """Create a simple GeoDataFrame with points."""
    data = {
        'id': [1, 2, 3],
        'name': ['Point A', 'Point B', 'Point C'],
        'geometry': [Point(0, 0), Point(1, 1), Point(2, 2)]
    }
    return geopandas.GeoDataFrame(data, crs="EPSG:4326")


@pytest.fixture
def sample_polygons():
    """Create a simple GeoDataFrame with polygons."""
    data = {
        'id': [1, 2],
        'name': ['Poly A', 'Poly B'],
        'geometry': [
            Polygon([(0, 0), (2, 0), (2, 2), (0, 2)]),  # Square covering points 1 and 2
            Polygon([(1.5, 1.5), (3, 1.5), (3, 3), (1.5, 3)])  # Square covering point 3
        ]
    }
    return geopandas.GeoDataFrame(data, crs="EPSG:4326")


@pytest.fixture
def mask_polygon():
    """Create a mask polygon for clipping tests."""
    return Polygon([(0.5, 0.5), (1.5, 0.5), (1.5, 1.5), (0.5, 1.5)])


# ============================================================================
# CLIP FUNCTION TESTS
# ============================================================================

def test_clip_with_polygon_mask(sample_points, mask_polygon):
    """Test clip function with a Shapely polygon mask."""
    result = clip(sample_points, mask_polygon)

    assert isinstance(result, geopandas.GeoDataFrame)
    assert result.crs == sample_points.crs
    # Should only contain point B (1, 1) which is inside the mask
    assert len(result) == 1
    assert result.iloc[0]['name'] == 'Point B'


def test_clip_with_geodataframe_mask(sample_points, sample_polygons):
    """Test clip function with a GeoDataFrame mask."""
    # Use first polygon as mask
    mask_gdf = sample_polygons.iloc[[0]]
    result = clip(sample_points, mask_gdf)

    assert isinstance(result, geopandas.GeoDataFrame)
    assert result.crs == sample_points.crs
    # Should contain at least 2 points (boundary conditions may vary)
    assert len(result) >= 2
    assert len(result) <= len(sample_points)


def test_clip_empty_result(sample_points):
    """Test clip function that results in empty GeoDataFrame."""
    # Create a mask that doesn't intersect with any points
    mask = Polygon([(10, 10), (11, 10), (11, 11), (10, 11)])
    result = clip(sample_points, mask)

    assert isinstance(result, geopandas.GeoDataFrame)
    assert len(result) == 0
    assert result.crs == sample_points.crs


def test_clip_with_kwargs(sample_polygons, mask_polygon):
    """Test clip function with additional kwargs."""
    result = clip(sample_polygons, mask_polygon, keep_geom_type=True)

    assert isinstance(result, geopandas.GeoDataFrame)
    assert result.crs == sample_polygons.crs


# ============================================================================
# OVERLAY FUNCTION TESTS
# ============================================================================

def test_overlay_intersection(sample_polygons):
    """Test overlay function with intersection operation."""
    # Create overlapping polygon
    overlap_poly = Polygon([(1, 1), (3, 1), (3, 3), (1, 3)])
    overlap_gdf = geopandas.GeoDataFrame(
        {'id': [1], 'geometry': [overlap_poly]},
        crs="EPSG:4326"
    )

    result = overlay(sample_polygons, overlap_gdf, how='intersection')

    assert isinstance(result, geopandas.GeoDataFrame)
    assert result.crs == sample_polygons.crs
    assert len(result) >= 1  # Should have at least one intersection


def test_overlay_union(sample_polygons):
    """Test overlay function with union operation."""
    # Create adjacent polygon
    adjacent_poly = Polygon([(2, 0), (4, 0), (4, 2), (2, 2)])
    adjacent_gdf = geopandas.GeoDataFrame(
        {'id': [1], 'geometry': [adjacent_poly]},
        crs="EPSG:4326"
    )

    result = overlay(sample_polygons, adjacent_gdf, how='union')

    assert isinstance(result, geopandas.GeoDataFrame)
    assert result.crs == sample_polygons.crs


def test_overlay_difference(sample_polygons):
    """Test overlay function with difference operation."""
    # Create overlapping polygon
    overlap_poly = Polygon([(1, 1), (3, 1), (3, 3), (1, 3)])
    overlap_gdf = geopandas.GeoDataFrame(
        {'id': [1], 'geometry': [overlap_poly]},
        crs="EPSG:4326"
    )

    result = overlay(sample_polygons, overlap_gdf, how='difference')

    assert isinstance(result, geopandas.GeoDataFrame)
    assert result.crs == sample_polygons.crs


def test_overlay_invalid_how():
    """Test overlay function with invalid 'how' parameter."""
    gdf1 = geopandas.GeoDataFrame({'geometry': [Point(0, 0)]}, crs="EPSG:4326")
    gdf2 = geopandas.GeoDataFrame({'geometry': [Point(1, 1)]}, crs="EPSG:4326")

    with pytest.raises(ValueError, match="Unsupported overlay type"):
        overlay(gdf1, gdf2, how='invalid_operation')


# ============================================================================
# SPATIAL_JOIN FUNCTION TESTS
# ============================================================================

def test_spatial_join_intersects(sample_points, sample_polygons):
    """Test spatial_join function with intersects predicate."""
    result = spatial_join(sample_points, sample_polygons, op='intersects', how='inner')

    assert isinstance(result, geopandas.GeoDataFrame)
    assert result.crs == sample_points.crs
    # Should have joined records where points intersect polygons
    assert len(result) >= 1
    # Check that join columns are present
    assert 'id_left' in result.columns or 'id_right' in result.columns


def test_spatial_join_contains(sample_polygons, sample_points):
    """Test spatial_join function with contains predicate."""
    result = spatial_join(sample_polygons, sample_points, op='contains', how='inner')

    assert isinstance(result, geopandas.GeoDataFrame)
    assert result.crs == sample_polygons.crs


def test_spatial_join_within(sample_points, sample_polygons):
    """Test spatial_join function with within predicate."""
    result = spatial_join(sample_points, sample_polygons, op='within', how='inner')

    assert isinstance(result, geopandas.GeoDataFrame)
    assert result.crs == sample_points.crs


def test_spatial_join_left_join(sample_points, sample_polygons):
    """Test spatial_join function with left join."""
    result = spatial_join(sample_points, sample_polygons, how='left')

    assert isinstance(result, geopandas.GeoDataFrame)
    assert result.crs == sample_points.crs
    # Left join should preserve all points
    assert len(result) >= len(sample_points)


def test_spatial_join_invalid_op():
    """Test spatial_join function with invalid predicate operation."""
    gdf1 = geopandas.GeoDataFrame({'geometry': [Point(0, 0)]}, crs="EPSG:4326")
    gdf2 = geopandas.GeoDataFrame({'geometry': [Point(1, 1)]}, crs="EPSG:4326")

    with pytest.raises(ValueError, match="Unsupported predicate operation"):
        spatial_join(gdf1, gdf2, op='invalid_predicate')


def test_spatial_join_invalid_how():
    """Test spatial_join function with invalid join type."""
    gdf1 = geopandas.GeoDataFrame({'geometry': [Point(0, 0)]}, crs="EPSG:4326")
    gdf2 = geopandas.GeoDataFrame({'geometry': [Point(1, 1)]}, crs="EPSG:4326")

    with pytest.raises(ValueError, match="Unsupported join type"):
        spatial_join(gdf1, gdf2, how='invalid_join')


# ============================================================================
# BUFFER FUNCTION TESTS (ADDITIONAL)
# ============================================================================

def test_buffer_with_kwargs(sample_points):
    """Test buffer function with additional kwargs."""
    result = buffer(sample_points, distance=1.0, resolution=16, cap_style=1)

    assert isinstance(result, geopandas.GeoDataFrame)
    assert result.crs == sample_points.crs
    assert all(result.geometry.geom_type == 'Polygon')


def test_buffer_zero_distance(sample_points):
    """Test buffer function with zero distance."""
    result = buffer(sample_points, distance=0)

    assert isinstance(result, geopandas.GeoDataFrame)
    assert result.crs == sample_points.crs
    # Zero buffer should return the original geometries
    assert len(result) == len(sample_points)


def test_buffer_negative_distance(sample_points):
    """Test buffer function with negative distance."""
    # Create a polygon to test negative buffer
    poly_data = {
        'id': [1],
        'geometry': [Polygon([(0, 0), (2, 0), (2, 2), (0, 2)])]
    }
    poly_gdf = geopandas.GeoDataFrame(poly_data, crs="EPSG:4326")

    result = buffer(poly_gdf, distance=-0.1)

    assert isinstance(result, geopandas.GeoDataFrame)
    assert result.crs == poly_gdf.crs


def test_buffer_preserves_attributes(sample_points):
    """Test that buffer function preserves non-geometry attributes."""
    result = buffer(sample_points, distance=1.0)

    assert isinstance(result, geopandas.GeoDataFrame)
    assert 'id' in result.columns
    assert 'name' in result.columns
    assert list(result['id']) == list(sample_points['id'])
    assert list(result['name']) == list(sample_points['name'])


# ============================================================================
# ACCESSOR FUNCTIONALITY TESTS
# ============================================================================

def test_geodataframe_accessor_registration(sample_points):
    """Test that the .pmg accessor is properly registered for GeoDataFrame."""
    gdf = sample_points

    # Check that .pmg accessor exists
    assert hasattr(gdf, 'pmg')

    # Check that accessor has expected vector methods
    assert hasattr(gdf.pmg, 'buffer')
    assert hasattr(gdf.pmg, 'clip')
    assert hasattr(gdf.pmg, 'overlay')
    assert hasattr(gdf.pmg, 'spatial_join')


def test_accessor_buffer(sample_points):
    """Test GeoDataFrame .pmg.buffer() accessor method."""
    gdf = sample_points

    # Test accessor method
    result = gdf.pmg.buffer(1.0)

    # Check that result is correct
    assert isinstance(result, geopandas.GeoDataFrame)
    assert result.crs == gdf.crs
    assert all(result.geometry.geom_type == 'Polygon')
    assert len(result) == len(gdf)


def test_accessor_clip(sample_points, mask_polygon):
    """Test GeoDataFrame .pmg.clip() accessor method."""
    gdf = sample_points

    # Test accessor method
    result = gdf.pmg.clip(mask_polygon)

    # Check that result is correct
    assert isinstance(result, geopandas.GeoDataFrame)
    assert result.crs == gdf.crs


def test_accessor_overlay(sample_polygons):
    """Test GeoDataFrame .pmg.overlay() accessor method."""
    gdf = sample_polygons

    # Create another GeoDataFrame for overlay
    other_poly = Polygon([(1, 1), (3, 1), (3, 3), (1, 3)])
    other_gdf = geopandas.GeoDataFrame(
        {'id': [1], 'geometry': [other_poly]},
        crs="EPSG:4326"
    )

    # Test accessor method
    result = gdf.pmg.overlay(other_gdf, how='intersection')

    # Check that result is correct
    assert isinstance(result, geopandas.GeoDataFrame)
    assert result.crs == gdf.crs


def test_accessor_spatial_join(sample_points, sample_polygons):
    """Test GeoDataFrame .pmg.spatial_join() accessor method."""
    points_gdf = sample_points
    polygons_gdf = sample_polygons

    # Test accessor method
    result = points_gdf.pmg.spatial_join(polygons_gdf, op='intersects')

    # Check that result is correct
    assert isinstance(result, geopandas.GeoDataFrame)
    assert result.crs == points_gdf.crs


def test_accessor_chaining(sample_points):
    """Test chaining of accessor methods."""
    gdf = sample_points

    # Test chaining buffer and then another operation
    buffered = gdf.pmg.buffer(1.0)

    # Create a mask for clipping
    mask = Polygon([(-0.5, -0.5), (1.5, -0.5), (1.5, 1.5), (-0.5, 1.5)])

    # Chain operations
    result = buffered.pmg.clip(mask)

    assert isinstance(result, geopandas.GeoDataFrame)
    assert result.crs == gdf.crs


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_vector_operations_integration():
    """Test integration of all vector operations in a realistic workflow."""
    # Create test data
    points = geopandas.GeoDataFrame({
        'id': [1, 2, 3, 4],
        'type': ['A', 'B', 'A', 'B'],
        'geometry': [Point(0, 0), Point(1, 1), Point(2, 2), Point(3, 3)]
    }, crs="EPSG:4326")

    study_area = geopandas.GeoDataFrame({
        'name': ['Study Area'],
        'geometry': [Polygon([(0.5, 0.5), (2.5, 0.5), (2.5, 2.5), (0.5, 2.5)])]
    }, crs="EPSG:4326")

    # Workflow: buffer points, clip to study area, then spatial join
    buffered_points = buffer(points, distance=0.3)
    clipped_buffers = clip(buffered_points, study_area)
    final_result = spatial_join(clipped_buffers, study_area, how='left')

    assert isinstance(final_result, geopandas.GeoDataFrame)
    assert final_result.crs == points.crs


def test_vector_operations_with_accessor_integration():
    """Test integration using accessor methods."""
    # Create test data
    points = geopandas.GeoDataFrame({
        'id': [1, 2, 3],
        'geometry': [Point(0, 0), Point(1, 1), Point(2, 2)]
    }, crs="EPSG:4326")

    study_area = geopandas.GeoDataFrame({
        'name': ['Study Area'],
        'geometry': [Polygon([(-0.5, -0.5), (2.5, -0.5), (2.5, 2.5), (-0.5, 2.5)])]
    }, crs="EPSG:4326")

    # Workflow using accessor methods
    result = (points
              .pmg.buffer(0.5)
              .pmg.spatial_join(study_area, how='left'))

    assert isinstance(result, geopandas.GeoDataFrame)
    assert result.crs == points.crs
