import pytest
import numpy as np
import xarray as xr
import pandas as pd
from unittest.mock import patch

# Attempt to import pydeck, skip tests if not available
try:
    import importlib.util
    PYDECK_AVAILABLE = importlib.util.find_spec("pydeck") is not None
except ImportError:
    PYDECK_AVAILABLE = False

# Conditional import of the functions to test
if PYDECK_AVAILABLE:
    from pymapgis.viz.deckgl_utils import view_3d_cube, view_point_cloud_3d
else:
    # Define dummy functions if pydeck is not available, so tests can be defined but skipped
    def view_3d_cube(*args, **kwargs): pass
    def view_point_cloud_3d(*args, **kwargs): pass

# Skip all tests in this module if PyDeck is not available
pytestmark = pytest.mark.skipif(not PYDECK_AVAILABLE, reason="pydeck library not found, skipping visualization tests.")


@pytest.fixture
def sample_xarray_cube():
    """Creates a sample 3D xarray DataArray for testing view_3d_cube."""
    data = np.random.rand(2, 3, 4) # time, y, x
    times = pd.to_datetime(['2023-01-01T00:00:00', '2023-01-01T01:00:00'])
    y_coords = np.arange(30, 30+3, dtype=np.float32) # Example latitudes
    x_coords = np.arange(-90, -90+4, dtype=np.float32) # Example longitudes
    cube = xr.DataArray(
        data,
        coords={'time': times, 'y': y_coords, 'x': x_coords},
        dims=['time', 'y', 'x'],
        name="temperature"
    )
    return cube

@pytest.fixture
def sample_point_cloud_array():
    """Creates a sample NumPy structured array for point cloud visualization."""
    points = np.array([
        (10.0, 20.0, 1.0, 255, 0, 0),
        (10.1, 20.1, 1.5, 0, 255, 0),
        (10.2, 20.2, 1.2, 0, 0, 255)
    ], dtype=[('X', np.float64), ('Y', np.float64), ('Z', np.float64),
              ('Red', np.uint8), ('Green', np.uint8), ('Blue', np.uint8)])
    return points

@patch('pydeck.Deck') # Mock the Deck object
@patch('pydeck.Layer') # Mock the Layer object
def test_view_3d_cube(MockLayer, MockDeck, sample_xarray_cube):
    """Tests view_3d_cube function by checking if pydeck objects are called correctly."""
    cube = sample_xarray_cube

    view_3d_cube(cube, time_index=0, colormap="plasma", cell_size=500)

    # Assert Deck was called
    MockDeck.assert_called_once()
    # Assert Layer was called (e.g., GridLayer by default)
    MockLayer.assert_called_once()

    # Check some arguments passed to Layer
    args, kwargs = MockLayer.call_args
    assert args[0] == "GridLayer" # Default layer type
    assert 'data' in kwargs
    assert isinstance(kwargs['data'], pd.DataFrame)
    assert 'get_position' in kwargs
    assert 'get_elevation' in kwargs
    assert 'cell_size' in kwargs and kwargs['cell_size'] == 500

    # Check arguments passed to Deck
    deck_args, deck_kwargs = MockDeck.call_args
    assert 'layers' in deck_kwargs and len(deck_kwargs['layers']) == 1
    assert 'initial_view_state' in deck_kwargs
    assert deck_kwargs['initial_view_state'].latitude is not None
    assert deck_kwargs['initial_view_state'].longitude is not None
    assert deck_kwargs['initial_view_state'].zoom is not None


@patch('pydeck.Deck')
@patch('pydeck.Layer')
def test_view_point_cloud_3d(MockLayer, MockDeck, sample_point_cloud_array):
    """Tests view_point_cloud_3d by checking pydeck calls."""
    points = sample_point_cloud_array

    view_point_cloud_3d(
        points,
        point_size=5,
        get_color='[Red, Green, Blue, 255]' # Use color from data
    )

    MockDeck.assert_called_once()
    MockLayer.assert_called_once()

    args, kwargs = MockLayer.call_args
    assert args[0] == "PointCloudLayer"
    assert 'data' in kwargs
    assert isinstance(kwargs['data'], pd.DataFrame)
    assert 'get_position' in kwargs
    assert 'point_size' in kwargs and kwargs['point_size'] == 5
    assert 'get_color' in kwargs and kwargs['get_color'] == '[Red, Green, Blue, 255]'

    deck_args, deck_kwargs = MockDeck.call_args
    assert 'layers' in deck_kwargs and len(deck_kwargs['layers']) == 1
    assert 'initial_view_state' in deck_kwargs
    assert deck_kwargs['initial_view_state'].latitude == pytest.approx(20.1) # Mean of Y
    assert deck_kwargs['initial_view_state'].longitude == pytest.approx(10.1) # Mean of X


def test_view_3d_cube_errors(sample_xarray_cube):
    """Test error handling in view_3d_cube."""
    # Invalid time_index
    with pytest.raises(IndexError):
        view_3d_cube(sample_xarray_cube, time_index=10)

    # Invalid cube dimensions
    invalid_cube_2d = sample_xarray_cube.isel(time=0)
    with pytest.raises(ValueError, match="Input DataArray 'cube' must be 3-dimensional"):
        view_3d_cube(invalid_cube_2d)

    # Cube missing x, y coordinates
    no_coords_cube_data = np.random.rand(2,3,4)
    no_coords_cube = xr.DataArray(no_coords_cube_data, dims=['time','dim1','dim2'])
    with pytest.raises(ValueError, match="Cube must have 'y' and 'x' coordinates"):
        view_3d_cube(no_coords_cube)


def test_view_point_cloud_3d_errors():
    """Test error handling in view_point_cloud_3d."""
    # Points array missing X, Y, Z
    invalid_points = np.array([(1,2)], dtype=[('A', int), ('B', int)])
    with pytest.raises(ValueError, match="Input points array must have 'X', 'Y', 'Z' fields"):
        view_point_cloud_3d(invalid_points)
