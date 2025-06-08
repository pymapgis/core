import pytest
import numpy as np
import os
import tempfile
import json

# Attempt to import pdal, skip tests if not available
try:
    import pdal
    PDAL_AVAILABLE = True
except ImportError:
    PDAL_AVAILABLE = False

# Imports from pymapgis
from pymapgis.pointcloud import (
    read_point_cloud,
    get_point_cloud_metadata,
    get_point_cloud_points,
    get_point_cloud_srs,
    create_las_from_numpy # Helper to create test files
)
from pymapgis.io import read as pmg_io_read # For testing the main read() integration

# Skip all tests in this module if PDAL is not available
pytestmark = pytest.mark.skipif(not PDAL_AVAILABLE, reason="PDAL library not found, skipping point cloud tests.")

# Define known point data for creating test LAS file
# Using a simple set of coordinates and common attributes
TEST_POINTS_NP_ARRAY = np.array([
    (100, 1000, 10, 1, 1, 1), # X, Y, Z, Intensity, ReturnNumber, NumberOfReturns
    (200, 2000, 20, 2, 1, 1),
    (300, 3000, 30, 3, 1, 1)
], dtype=[('X', np.float64), ('Y', np.float64), ('Z', np.float64),
          ('Intensity', np.uint16), ('ReturnNumber', np.uint8), ('NumberOfReturns', np.uint8)])

# Define a sample WKT SRS for testing
SAMPLE_SRS_WKT = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'


@pytest.fixture(scope="module")
def las_file_path_fixture():
    """Creates a temporary LAS file with known points and SRS for testing."""
    with tempfile.NamedTemporaryFile(suffix=".las", delete=False) as tmpfile:
        las_path = tmpfile.name

    create_las_from_numpy(TEST_POINTS_NP_ARRAY, las_path, srs_wkt=SAMPLE_SRS_WKT)

    yield las_path

    os.remove(las_path) # Cleanup

@pytest.fixture(scope="module")
def laz_file_path_fixture():
    """Creates a temporary LAZ file. For now, just re-uses LAS creation logic.
    PDAL's writers.las can write .laz if filename ends with .laz and LAZ driver is available.
    """
    with tempfile.NamedTemporaryFile(suffix=".laz", delete=False) as tmpfile:
        laz_path = tmpfile.name

    # Note: This assumes PDAL installation includes LAZ support for writing.
    # If not, this fixture might fail to create a compressed LAZ.
    # For robust testing, one might need a pre-existing small LAZ file.
    try:
        create_las_from_numpy(TEST_POINTS_NP_ARRAY, laz_path, srs_wkt=SAMPLE_SRS_WKT)
        laz_created = True
    except RuntimeError as e:
        # PDAL might not have LAZ support compiled in for writing in all environments
        print(f"Could not create LAZ file for testing, PDAL error: {e}. Skipping LAZ-specific write test.")
        laz_created = False
        # To ensure tests can run, we might yield None or raise SkipTest if LAZ is critical
        # For now, let the test that uses it handle the potential missing file.
        # yield None
        # For the purpose of this test, if LAZ cannot be created, we can't test LAZ reading.
        # So, if it fails, we'll yield the path anyway and let read test fail, or skip.
        # A better approach for CI would be to have a tiny pre-made LAZ file.

    if laz_created:
        yield laz_path
        os.remove(laz_path)
    else:
        # If LAZ creation failed, skip tests that require it.
        # This is tricky in a fixture. Better to handle in the test itself or use a marker.
        yield None # Test using this fixture should check for None

# --- Tests for pymapgis.pointcloud functions ---

def test_read_point_cloud_las(las_file_path_fixture):
    pipeline = read_point_cloud(las_file_path_fixture)
    assert isinstance(pipeline, pdal.Pipeline)
    assert pipeline.executed
    points = pipeline.arrays[0]
    assert len(points) == len(TEST_POINTS_NP_ARRAY)

def test_read_point_cloud_laz(laz_file_path_fixture):
    if laz_file_path_fixture is None:
        pytest.skip("LAZ file could not be created for testing (PDAL LAZ writer likely unavailable).")

    pipeline = read_point_cloud(laz_file_path_fixture)
    assert isinstance(pipeline, pdal.Pipeline)
    assert pipeline.executed
    points = pipeline.arrays[0]
    assert len(points) == len(TEST_POINTS_NP_ARRAY)

def test_get_point_cloud_points(las_file_path_fixture):
    pipeline = read_point_cloud(las_file_path_fixture)
    points_array = get_point_cloud_points(pipeline)

    assert isinstance(points_array, np.ndarray)
    assert len(points_array) == len(TEST_POINTS_NP_ARRAY)

    # Check field names (PDAL might change case or add underscores)
    # Common names: X, Y, Z, Intensity, ReturnNumber, NumberOfReturns
    # Let's compare with the original dtype names, accounting for case.
    original_names_lower = {name.lower() for name in TEST_POINTS_NP_ARRAY.dtype.names}
    output_names_lower = {name.lower() for name in points_array.dtype.names}
    assert original_names_lower.issubset(output_names_lower)

    # Check actual values for X, Y, Z
    np.testing.assert_allclose(points_array['X'], TEST_POINTS_NP_ARRAY['X'])
    np.testing.assert_allclose(points_array['Y'], TEST_POINTS_NP_ARRAY['Y'])
    np.testing.assert_allclose(points_array['Z'], TEST_POINTS_NP_ARRAY['Z'])
    np.testing.assert_array_equal(points_array['Intensity'], TEST_POINTS_NP_ARRAY['Intensity'])


def test_get_point_cloud_metadata(las_file_path_fixture):
    pipeline = read_point_cloud(las_file_path_fixture)
    metadata = get_point_cloud_metadata(pipeline)

    assert isinstance(metadata, dict)
    assert 'quickinfo' in metadata
    assert 'schema' in metadata # pipeline.schema
    assert 'srs_wkt' in metadata
    assert SAMPLE_SRS_WKT in metadata['srs_wkt'] # Check if our WKT is present

    # Example: Check point count from metadata if available
    # This depends on PDAL version and how metadata is structured.
    # 'count' is often in pipeline.quickinfo['readers.las']['num_points']
    if metadata.get('quickinfo') and metadata['quickinfo'].get('num_points'):
      assert metadata['quickinfo']['num_points'] == len(TEST_POINTS_NP_ARRAY)


def test_get_point_cloud_srs(las_file_path_fixture):
    pipeline = read_point_cloud(las_file_path_fixture)
    srs_wkt = get_point_cloud_srs(pipeline)

    assert isinstance(srs_wkt, str)
    assert len(srs_wkt) > 0
    # A loose check for WGS 84, as exact WKT string can vary slightly
    assert "WGS 84" in srs_wkt
    assert "6326" in srs_wkt # EPSG code for WGS84 datum

# --- Test for pmg.io.read() integration ---

def test_pmg_io_read_las(las_file_path_fixture):
    points_array = pmg_io_read(las_file_path_fixture)

    assert isinstance(points_array, np.ndarray)
    assert len(points_array) == len(TEST_POINTS_NP_ARRAY)
    original_names_lower = {name.lower() for name in TEST_POINTS_NP_ARRAY.dtype.names}
    output_names_lower = {name.lower() for name in points_array.dtype.names}
    assert original_names_lower.issubset(output_names_lower)

    np.testing.assert_allclose(points_array['X'], TEST_POINTS_NP_ARRAY['X'])

def test_pmg_io_read_laz(laz_file_path_fixture):
    if laz_file_path_fixture is None:
        pytest.skip("LAZ file could not be created for testing.")

    points_array = pmg_io_read(laz_file_path_fixture) # Should use the LAZ file

    assert isinstance(points_array, np.ndarray)
    assert len(points_array) == len(TEST_POINTS_NP_ARRAY)
    np.testing.assert_allclose(points_array['X'], TEST_POINTS_NP_ARRAY['X'])


# --- Test error handling ---
def test_read_point_cloud_non_existent_file():
    with pytest.raises(RuntimeError, match="PDAL pipeline execution failed"): # PDAL raises RuntimeError for file not found
        read_point_cloud("this_file_should_not_exist.las")

def test_create_las_from_numpy_errors():
    # Test invalid array type
    with pytest.raises(TypeError, match="points_array must be a NumPy structured array"):
        create_las_from_numpy(np.array([1,2,3]), "test.las")

    # Test invalid output filename
    with pytest.raises(ValueError, match="output_filepath must end with .las"):
        create_las_from_numpy(TEST_POINTS_NP_ARRAY, "test.txt")

```
