import os
import tempfile
import pytest
import numpy as np
import laspy # For creating test LAS files

from pymapgis.pointcloud import read_las

# Define known point data to be written to the test LAS file
# Using a simple set of coordinates and intensities
# laspy requires scaled and offset values for X, Y, Z if not using raw integers.
# For simplicity, we'll use integer coordinates that don't require scaling for this test.
# PDAL will read them as scaled floats by default if scale/offset are 0.01/0,
# or as integers if scale/offset are 1.0/0. We'll aim for integer representation.
# For laspy, header.scales = [1.0, 1.0, 1.0] and header.offsets = [0.0, 0.0, 0.0]
# will mean that the integer values we store are the actual coordinate values.
TEST_POINTS_DATA = {
    'X': np.array([100, 200, 300], dtype=np.int32),
    'Y': np.array([1000, 2000, 3000], dtype=np.int32),
    'Z': np.array([10, 20, 30], dtype=np.int32),
    'intensity': np.array([1, 2, 3], dtype=np.uint16),
    'return_number': np.array([1, 1, 1], dtype=np.uint8), # Example field
    'number_of_returns': np.array([1, 1, 1], dtype=np.uint8) # Example field
}
# For laspy point_format_id 0, only X, Y, Z, intensity, return_number, number_of_returns,
# classification, scan_angle_rank, user_data, point_source_id are typically standard.
# We'll use a simple point format. laspy defaults to point format 3 if not specified,
# which includes GPS time and RGB. Let's use point format 0 or 1 for simplicity.

@pytest.fixture(scope="module") # Use module scope for efficiency if file creation is slow
def valid_las_file_path():
    """Creates a temporary, valid LAS file with known points."""
    with tempfile.NamedTemporaryFile(suffix=".las", delete=False) as tmpfile:
        las_path = tmpfile.name

    # Create a new LAS file with laspy
    # Using LAS version 1.2 and Point Format 0 for simplicity
    header = laspy.LasHeader(version="1.2", point_format=laspy.PointFormat(0))
    header.scales = np.array([1.0, 1.0, 1.0]) # Store X, Y, Z as raw integers
    header.offsets = np.array([0.0, 0.0, 0.0])

    # Populate the header with some basic information (optional but good practice)
    header.point_count = len(TEST_POINTS_DATA['X'])
    # Min/max values should be calculated from the data
    header.x_min, header.y_min, header.z_min = TEST_POINTS_DATA['X'].min(), TEST_POINTS_DATA['Y'].min(), TEST_POINTS_DATA['Z'].min()
    header.x_max, header.y_max, header.z_max = TEST_POINTS_DATA['X'].max(), TEST_POINTS_DATA['Y'].max(), TEST_POINTS_DATA['Z'].max()

    las = laspy.LasData(header)

    las.X = TEST_POINTS_DATA['X']
    las.Y = TEST_POINTS_DATA['Y']
    las.Z = TEST_POINTS_DATA['Z']
    las.intensity = TEST_POINTS_DATA['intensity']
    las.return_number = TEST_POINTS_DATA['return_number']
    las.number_of_returns = TEST_POINTS_DATA['number_of_returns']
    # Other fields for point format 0 will be default (0)

    las.write(las_path)

    yield las_path

    os.remove(las_path) # Cleanup the file


@pytest.fixture(scope="module")
def invalid_las_file_path():
    """Creates a temporary, invalid (empty) LAS file."""
    with tempfile.NamedTemporaryFile(suffix=".las", delete=False) as tmpfile:
        invalid_path = tmpfile.name
    # Create an empty file
    open(invalid_path, 'w').close()

    yield invalid_path

    os.remove(invalid_path)


def test_read_las_valid_file(valid_las_file_path):
    """Tests reading a valid LAS file with known content."""
    arrays = read_las(valid_las_file_path)

    assert arrays is not None, "Result from read_las should not be None"
    assert isinstance(arrays, list), "Result should be a list"
    assert len(arrays) > 0, "Result list should not be empty"

    point_data_array = arrays[0]
    assert isinstance(point_data_array, np.ndarray), "Items in result list should be NumPy arrays"

    # Check for expected fields (PDAL might rename or use specific casing)
    # Common PDAL dimension names for LAS: X, Y, Z, Intensity, ReturnNumber, NumberOfReturns
    # Classification, ScanAngleRank (or ScanAngle), UserData, PointSourceId, GpsTime
    # The exact names depend on the PDAL reader and the LAS point format.
    # For Point Format 0, we expect at least X, Y, Z, Intensity, ReturnNumber, NumberOfReturns.
    expected_fields = ['X', 'Y', 'Z', 'Intensity', 'ReturnNumber', 'NumberOfReturns']
    for field in expected_fields:
        assert field in point_data_array.dtype.names, f"Field '{field}' not found in output array"

    # Assert data content matches the known values
    # PDAL applies scale and offset. Since we set scale=1, offset=0, values should match.
    # If las.X, las.Y, las.Z were stored as floats, direct comparison is fine.
    # If stored as scaled integers, PDAL reader output is typically float.
    # Our TEST_POINTS_DATA used np.int32 for X,Y,Z and laspy stored them as such with scale 1.0.
    # PDAL's readers.las will output them as float64 by default if no scale/offset transform is applied
    # in the PDAL pipeline itself, or if the file indicates they are floats (not our case).
    # However, if the LAS header indicates scale=1, offset=0, PDAL might output integers or floats.
    # Let's check the dtype from PDAL and compare accordingly.

    # For X, Y, Z (coordinates)
    np.testing.assert_array_almost_equal(point_data_array['X'], TEST_POINTS_DATA['X'], decimal=1,
                                         err_msg="X coordinates mismatch")
    np.testing.assert_array_almost_equal(point_data_array['Y'], TEST_POINTS_DATA['Y'], decimal=1,
                                         err_msg="Y coordinates mismatch")
    np.testing.assert_array_almost_equal(point_data_array['Z'], TEST_POINTS_DATA['Z'], decimal=1,
                                         err_msg="Z coordinates mismatch")

    # For other attributes (usually integers or specific types)
    np.testing.assert_array_equal(point_data_array['Intensity'], TEST_POINTS_DATA['intensity'],
                                  err_msg="Intensity values mismatch")
    np.testing.assert_array_equal(point_data_array['ReturnNumber'], TEST_POINTS_DATA['return_number'],
                                  err_msg="ReturnNumber values mismatch")
    np.testing.assert_array_equal(point_data_array['NumberOfReturns'], TEST_POINTS_DATA['number_of_returns'],
                                  err_msg="NumberOfReturns values mismatch")

    assert len(point_data_array) == len(TEST_POINTS_DATA['X']), "Number of points mismatch"


def test_read_las_non_existent_file():
    """Tests reading a non-existent LAS file."""
    non_existent_path = "this_file_does_not_exist_ever.las"
    with pytest.raises(FileNotFoundError, match=f"The LAS/LAZ file was not found: {non_existent_path}"):
        read_las(non_existent_path)


def test_read_las_invalid_file(invalid_las_file_path):
    """Tests reading an invalid (e.g., empty) LAS file."""
    # PDAL errors are typically wrapped in RuntimeError by the read_las function
    with pytest.raises(RuntimeError, match="PDAL pipeline execution failed"):
        read_las(invalid_las_file_path)

# To run these tests:
# Ensure pymapgis is in PYTHONPATH
# pytest tests/test_pointcloud.py
