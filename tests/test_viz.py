import pytest
import numpy as np
import xarray as xr
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
from unittest.mock import patch, MagicMock

# Attempt to import pydeck, skip tests if not available
try:
    import importlib.util
    PYDECK_AVAILABLE = importlib.util.find_spec("pydeck") is not None
except ImportError:
    PYDECK_AVAILABLE = False

# Attempt to import leafmap, skip tests if not available
try:
    import leafmap.leafmap as leafmap
    LEAFMAP_AVAILABLE = True
except ImportError:
    LEAFMAP_AVAILABLE = False
    # Create a mock leafmap for testing
    class MockLeafmap:
        class Map:
            def __init__(self, **kwargs):
                pass
            def add_gdf(self, *args, **kwargs):
                pass
            def add_raster(self, *args, **kwargs):
                pass
    leafmap = MockLeafmap()

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


# Tests for Core Visualization Functions (Phase 1 - Part 3)

@pytest.fixture
def sample_geodataframe():
    """Create a sample GeoDataFrame for testing."""
    # Create sample points
    points = [Point(0, 0), Point(1, 1), Point(2, 2)]
    data = {'id': [1, 2, 3], 'value': [10, 20, 30]}
    gdf = gpd.GeoDataFrame(data, geometry=points, crs="EPSG:4326")
    return gdf


@pytest.fixture
def sample_raster_dataarray():
    """Create a sample raster DataArray for testing."""
    # Create sample raster data
    data = np.random.rand(3, 4).astype(np.float32)
    x_coords = np.array([0.0, 1.0, 2.0, 3.0])
    y_coords = np.array([2.0, 1.0, 0.0])

    da = xr.DataArray(
        data,
        coords={'y': y_coords, 'x': x_coords},
        dims=['y', 'x'],
        name='test_raster'
    )

    # Add CRS using rioxarray if available
    try:
        import rioxarray
        da = da.rio.write_crs("EPSG:4326")
    except ImportError:
        pass

    return da


@pytest.fixture
def sample_dataset():
    """Create a sample Dataset for testing."""
    # Create sample data
    temp_data = np.random.rand(2, 3).astype(np.float32)
    precip_data = np.random.rand(2, 3).astype(np.float32)

    x_coords = np.array([0.0, 1.0, 2.0])
    y_coords = np.array([1.0, 0.0])

    temp_da = xr.DataArray(
        temp_data,
        coords={'y': y_coords, 'x': x_coords},
        dims=['y', 'x'],
        name='temperature'
    )

    precip_da = xr.DataArray(
        precip_data,
        coords={'y': y_coords, 'x': x_coords},
        dims=['y', 'x'],
        name='precipitation'
    )

    ds = xr.Dataset({'temperature': temp_da, 'precipitation': precip_da})

    # Add CRS if rioxarray is available
    try:
        import rioxarray
        ds = ds.rio.write_crs("EPSG:4326")
    except ImportError:
        pass

    return ds


# Tests for standalone visualization functions

@patch('leafmap.leafmap.Map')
def test_explore_geodataframe(MockMap, sample_geodataframe):
    """Test explore function with GeoDataFrame."""
    from pymapgis.viz import explore

    # Create mock map instance
    mock_map = MagicMock()
    MockMap.return_value = mock_map

    gdf = sample_geodataframe

    # Test basic explore
    result = explore(gdf)

    # Check that Map was created
    MockMap.assert_called_once()

    # Check that add_gdf was called
    mock_map.add_gdf.assert_called_once_with(gdf)

    # Check return value
    assert result == mock_map


@patch('leafmap.leafmap.Map')
def test_explore_dataarray(MockMap, sample_raster_dataarray):
    """Test explore function with DataArray."""
    from pymapgis.viz import explore

    # Create mock map instance
    mock_map = MagicMock()
    MockMap.return_value = mock_map

    da = sample_raster_dataarray

    # Test basic explore
    result = explore(da)

    # Check that Map was created
    MockMap.assert_called_once()

    # Check that add_raster was called
    mock_map.add_raster.assert_called_once_with(da)

    # Check return value
    assert result == mock_map


@patch('leafmap.leafmap.Map')
def test_plot_interactive_geodataframe(MockMap, sample_geodataframe):
    """Test plot_interactive function with GeoDataFrame."""
    from pymapgis.viz import plot_interactive

    # Create mock map instance
    mock_map = MagicMock()
    MockMap.return_value = mock_map

    gdf = sample_geodataframe

    # Test basic plot_interactive
    result = plot_interactive(gdf)

    # Check that Map was created
    MockMap.assert_called_once()

    # Check that add_gdf was called
    mock_map.add_gdf.assert_called_once_with(gdf)

    # Check return value
    assert result == mock_map


@patch('leafmap.leafmap.Map')
def test_plot_interactive_with_existing_map(MockMap, sample_geodataframe):
    """Test plot_interactive function with existing map."""
    from pymapgis.viz import plot_interactive

    # Create mock map instance
    existing_map = MagicMock()

    gdf = sample_geodataframe

    # Test with existing map
    result = plot_interactive(gdf, m=existing_map)

    # Check that Map was NOT created (using existing)
    MockMap.assert_not_called()

    # Check that add_gdf was called on existing map
    existing_map.add_gdf.assert_called_once_with(gdf)

    # Check return value
    assert result == existing_map


def test_explore_errors():
    """Test error handling in explore function."""
    from pymapgis.viz import explore

    # Test with unsupported data type
    with pytest.raises(TypeError, match="Unsupported data type"):
        explore("not_a_geodataframe")

    # Test with numpy array
    with pytest.raises(TypeError, match="Unsupported data type"):
        explore(np.array([[1, 2], [3, 4]]))


# Tests for accessor functionality

def test_geodataframe_accessor_registration(sample_geodataframe):
    """Test that the .pmg accessor is properly registered for GeoDataFrame."""
    gdf = sample_geodataframe

    # Check that .pmg accessor exists
    assert hasattr(gdf, 'pmg')

    # Check that accessor has expected methods
    assert hasattr(gdf.pmg, 'explore')
    assert hasattr(gdf.pmg, 'map')


@patch('pymapgis.viz.explore')
def test_geodataframe_accessor_explore(mock_explore, sample_geodataframe):
    """Test GeoDataFrame .pmg.explore() accessor method."""
    gdf = sample_geodataframe

    # Mock the return value
    mock_map = MagicMock()
    mock_explore.return_value = mock_map

    # Test accessor method
    result = gdf.pmg.explore(layer_name="Test Layer")

    # Check that underlying function was called correctly
    mock_explore.assert_called_once_with(gdf, m=None, layer_name="Test Layer")

    # Check return value
    assert result == mock_map


@patch('pymapgis.viz.plot_interactive')
def test_geodataframe_accessor_map(mock_plot_interactive, sample_geodataframe):
    """Test GeoDataFrame .pmg.map() accessor method."""
    gdf = sample_geodataframe

    # Mock the return value
    mock_map = MagicMock()
    mock_plot_interactive.return_value = mock_map

    # Test accessor method
    result = gdf.pmg.map(layer_name="Test Layer")

    # Check that underlying function was called correctly
    mock_plot_interactive.assert_called_once_with(gdf, m=None, layer_name="Test Layer")

    # Check return value
    assert result == mock_map


def test_dataarray_accessor_visualization(sample_raster_dataarray):
    """Test that DataArray .pmg accessor has visualization methods."""
    da = sample_raster_dataarray

    # Check that .pmg accessor exists
    assert hasattr(da, 'pmg')

    # Check that accessor has visualization methods
    assert hasattr(da.pmg, 'explore')
    assert hasattr(da.pmg, 'map')


def test_dataset_accessor_visualization(sample_dataset):
    """Test that Dataset .pmg accessor has visualization methods."""
    ds = sample_dataset

    # Check that .pmg accessor exists
    assert hasattr(ds, 'pmg')

    # Check that accessor has visualization methods
    assert hasattr(ds.pmg, 'explore')
    assert hasattr(ds.pmg, 'map')


# Integration tests

@patch('pymapgis.viz.explore')
def test_dataarray_accessor_explore_integration(mock_explore, sample_raster_dataarray):
    """Test DataArray .pmg.explore() integration."""
    da = sample_raster_dataarray

    # Mock the return value
    mock_map = MagicMock()
    mock_explore.return_value = mock_map

    # Test accessor method
    result = da.pmg.explore(colormap="viridis", opacity=0.7)

    # Check that underlying function was called correctly
    mock_explore.assert_called_once_with(da, m=None, colormap="viridis", opacity=0.7)

    # Check return value
    assert result == mock_map


@patch('pymapgis.viz.plot_interactive')
def test_dataset_accessor_map_integration(mock_plot_interactive, sample_dataset):
    """Test Dataset .pmg.map() integration."""
    ds = sample_dataset

    # Mock the return value
    mock_map = MagicMock()
    mock_plot_interactive.return_value = mock_map

    # Test accessor method
    result = ds.pmg.map(layer_name="Climate Data")

    # Check that underlying function was called correctly
    mock_plot_interactive.assert_called_once_with(ds, m=None, layer_name="Climate Data")

    # Check return value
    assert result == mock_map


def test_real_world_workflow_simulation():
    """Test a realistic workflow using the visualization accessors."""
    # Create realistic sample data

    # Vector data (counties)
    counties_geom = [
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
        Polygon([(0, 1), (1, 1), (1, 2), (0, 2)])
    ]
    counties_data = {
        'NAME': ['County A', 'County B', 'County C'],
        'population': [10000, 15000, 8000],
        'income': [50000, 60000, 45000]
    }
    counties = gpd.GeoDataFrame(counties_data, geometry=counties_geom, crs="EPSG:4326")

    # Raster data (elevation)
    elevation_data = np.array([[100, 150, 200],
                               [120, 180, 220],
                               [90, 140, 190]], dtype=np.float32)
    x_coords = np.array([0.5, 1.0, 1.5])
    y_coords = np.array([1.5, 1.0, 0.5])

    elevation = xr.DataArray(
        elevation_data,
        coords={'y': y_coords, 'x': x_coords},
        dims=['y', 'x'],
        name='elevation'
    )

    # Test that accessors are available
    assert hasattr(counties, 'pmg')
    assert hasattr(elevation, 'pmg')

    # Test that methods are available
    assert hasattr(counties.pmg, 'explore')
    assert hasattr(counties.pmg, 'map')
    assert hasattr(elevation.pmg, 'explore')
    assert hasattr(elevation.pmg, 'map')


def test_accessor_method_signatures():
    """Test that accessor methods have the correct signatures."""
    # Create simple test data
    points = [Point(0, 0), Point(1, 1)]
    gdf = gpd.GeoDataFrame({'id': [1, 2]}, geometry=points, crs="EPSG:4326")

    da = xr.DataArray(np.random.rand(2, 2), dims=['y', 'x'])

    # Test that methods exist and are callable
    assert callable(gdf.pmg.explore)
    assert callable(gdf.pmg.map)
    assert callable(da.pmg.explore)
    assert callable(da.pmg.map)

    # Test method signatures by checking they accept common parameters
    import inspect

    # Check GeoDataFrame methods
    gdf_explore_sig = inspect.signature(gdf.pmg.explore)
    assert 'm' in gdf_explore_sig.parameters

    gdf_map_sig = inspect.signature(gdf.pmg.map)
    assert 'm' in gdf_map_sig.parameters

    # Check DataArray methods
    da_explore_sig = inspect.signature(da.pmg.explore)
    assert 'm' in da_explore_sig.parameters

    da_map_sig = inspect.signature(da.pmg.map)
    assert 'm' in da_map_sig.parameters


# Performance and edge case tests

def test_empty_geodataframe_visualization():
    """Test visualization with empty GeoDataFrame."""
    # Create empty GeoDataFrame
    empty_gdf = gpd.GeoDataFrame(columns=['geometry'], crs="EPSG:4326")

    # Test that accessor is still available
    assert hasattr(empty_gdf, 'pmg')
    assert hasattr(empty_gdf.pmg, 'explore')
    assert hasattr(empty_gdf.pmg, 'map')


def test_large_coordinate_values():
    """Test visualization with large coordinate values (real-world coordinates)."""
    # Create data with realistic geographic coordinates
    points = [
        Point(-122.4194, 37.7749),  # San Francisco
        Point(-74.0060, 40.7128),   # New York
        Point(-87.6298, 41.8781)    # Chicago
    ]

    gdf = gpd.GeoDataFrame(
        {'city': ['SF', 'NYC', 'CHI'], 'population': [884000, 8400000, 2700000]},
        geometry=points,
        crs="EPSG:4326"
    )

    # Test that accessor works with realistic coordinates
    assert hasattr(gdf, 'pmg')
    assert hasattr(gdf.pmg, 'explore')
    assert hasattr(gdf.pmg, 'map')
