"""
Comprehensive tests for PyMapGIS serve module (pmg.serve) - Phase 1 Part 7.

Tests the FastAPI-based web service functionality for serving geospatial data
as XYZ tile services.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
import geopandas as gpd
import xarray as xr
import numpy as np
from shapely.geometry import Point, Polygon
import json

# Import serve components
try:
    from pymapgis.serve import serve, gdf_to_mvt, _app
    from fastapi.testclient import TestClient
    SERVE_AVAILABLE = True
except ImportError as e:
    SERVE_AVAILABLE = False
    serve = None
    gdf_to_mvt = None
    _app = None
    print(f"Serve module not available: {e}")


@pytest.fixture
def sample_geodataframe():
    """Create a sample GeoDataFrame for testing."""
    data = {
        'id': [1, 2, 3],
        'name': ['Point A', 'Point B', 'Point C'],
        'value': [10, 20, 30],
        'geometry': [
            Point(0, 0),
            Point(1, 1), 
            Point(2, 2)
        ]
    }
    return gpd.GeoDataFrame(data, crs="EPSG:4326")


@pytest.fixture
def sample_polygon_geodataframe():
    """Create a sample polygon GeoDataFrame for testing."""
    data = {
        'id': [1, 2],
        'name': ['Polygon A', 'Polygon B'],
        'area': [100, 200],
        'geometry': [
            Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]),
            Polygon([(2, 2), (3, 2), (3, 3), (2, 3), (2, 2)])
        ]
    }
    return gpd.GeoDataFrame(data, crs="EPSG:4326")


@pytest.fixture
def sample_dataarray():
    """Create a sample xarray DataArray for testing."""
    # Create a simple 2D array with spatial coordinates
    data = np.random.rand(10, 10)
    coords = {
        'y': np.linspace(40, 41, 10),
        'x': np.linspace(-74, -73, 10)
    }
    da = xr.DataArray(data, coords=coords, dims=['y', 'x'])
    da.attrs['crs'] = 'EPSG:4326'
    return da


@pytest.fixture
def temp_geojson_file(sample_geodataframe):
    """Create a temporary GeoJSON file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.geojson', delete=False) as f:
        sample_geodataframe.to_file(f.name, driver='GeoJSON')
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def temp_shapefile(sample_geodataframe):
    """Create a temporary Shapefile for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        shp_path = os.path.join(tmpdir, 'test.shp')
        sample_geodataframe.to_file(shp_path)
        yield shp_path


# ============================================================================
# SERVE MODULE STRUCTURE TESTS
# ============================================================================

def test_serve_module_structure():
    """Test that serve module has proper structure."""
    if not SERVE_AVAILABLE:
        pytest.skip("Serve module not available")
    
    # Check that serve module exists and has expected functions
    assert serve is not None, "serve function should be available"
    assert gdf_to_mvt is not None, "gdf_to_mvt function should be available"
    assert _app is not None, "FastAPI app should be available"


def test_serve_module_imports():
    """Test that serve module can be imported correctly."""
    if not SERVE_AVAILABLE:
        pytest.skip("Serve module not available")
    
    # Test importing from pymapgis.serve
    from pymapgis.serve import serve as serve_func
    assert serve_func is not None
    
    # Test that it's accessible from main pymapgis module
    try:
        import pymapgis
        assert hasattr(pymapgis, 'serve'), "serve should be available in main pymapgis module"
    except ImportError:
        pytest.skip("Main pymapgis module not available")


# ============================================================================
# GDF_TO_MVT FUNCTION TESTS
# ============================================================================

@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_gdf_to_mvt_basic(sample_geodataframe):
    """Test basic gdf_to_mvt functionality."""
    # Convert to Web Mercator for MVT
    gdf_3857 = sample_geodataframe.to_crs(epsg=3857)
    
    # Test MVT generation for a specific tile
    mvt_data = gdf_to_mvt(gdf_3857, x=0, y=0, z=1, layer_name="test_layer")
    
    assert isinstance(mvt_data, bytes), "MVT data should be bytes"
    assert len(mvt_data) > 0, "MVT data should not be empty"


@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_gdf_to_mvt_empty_tile(sample_geodataframe):
    """Test gdf_to_mvt with empty tile (no intersecting features)."""
    # Convert to Web Mercator
    gdf_3857 = sample_geodataframe.to_crs(epsg=3857)
    
    # Test with a tile that shouldn't intersect with our small test data
    mvt_data = gdf_to_mvt(gdf_3857, x=1000, y=1000, z=10, layer_name="test_layer")
    
    assert isinstance(mvt_data, bytes), "MVT data should be bytes even for empty tiles"


@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_gdf_to_mvt_polygon_data(sample_polygon_geodataframe):
    """Test gdf_to_mvt with polygon data."""
    # Convert to Web Mercator
    gdf_3857 = sample_polygon_geodataframe.to_crs(epsg=3857)
    
    # Test MVT generation
    mvt_data = gdf_to_mvt(gdf_3857, x=0, y=0, z=1, layer_name="polygon_layer")
    
    assert isinstance(mvt_data, bytes), "MVT data should be bytes"
    assert len(mvt_data) > 0, "MVT data should not be empty"


# ============================================================================
# SERVE FUNCTION PARAMETER TESTS
# ============================================================================

@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_serve_function_signature():
    """Test that serve function has correct signature."""
    import inspect
    
    sig = inspect.signature(serve)
    params = sig.parameters
    
    # Check required parameters
    assert 'data' in params, "serve should have 'data' parameter"
    assert 'service_type' in params, "serve should have 'service_type' parameter"
    assert 'layer_name' in params, "serve should have 'layer_name' parameter"
    assert 'host' in params, "serve should have 'host' parameter"
    assert 'port' in params, "serve should have 'port' parameter"
    
    # Check default values
    assert params['service_type'].default == 'xyz', "service_type should default to 'xyz'"
    assert params['layer_name'].default == 'layer', "layer_name should default to 'layer'"
    assert params['host'].default == '127.0.0.1', "host should default to '127.0.0.1'"
    assert params['port'].default == 8000, "port should default to 8000"


@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_serve_geodataframe_input_validation(sample_geodataframe):
    """Test serve function input validation with GeoDataFrame."""
    # Mock uvicorn.run to prevent actual server startup
    with patch('uvicorn.run') as mock_run:
        # Test that function accepts GeoDataFrame without error
        try:
            serve(sample_geodataframe, layer_name="test_vector", port=8001)
            mock_run.assert_called_once()
        except Exception as e:
            pytest.fail(f"serve should accept GeoDataFrame input: {e}")


@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_serve_string_input_validation(temp_geojson_file):
    """Test serve function input validation with file path."""
    # Mock uvicorn.run to prevent actual server startup
    with patch('uvicorn.run') as mock_run:
        # Test that function accepts file path without error
        try:
            serve(temp_geojson_file, layer_name="test_file", port=8002)
            mock_run.assert_called_once()
        except Exception as e:
            pytest.fail(f"serve should accept file path input: {e}")


@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_serve_xarray_input_validation(sample_dataarray):
    """Test serve function input validation with xarray DataArray."""
    # Mock uvicorn.run to prevent actual server startup
    with patch('uvicorn.run') as mock_run:
        # Test that function handles xarray input (may raise NotImplementedError for in-memory arrays)
        try:
            serve(sample_dataarray, layer_name="test_raster", port=8003)
            mock_run.assert_called_once()
        except NotImplementedError:
            # This is expected for in-memory xarray objects in Phase 1
            pytest.skip("In-memory xarray serving not yet implemented")


@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_serve_invalid_input():
    """Test serve function with invalid input types."""
    # Mock uvicorn.run to prevent actual server startup
    with patch('uvicorn.run'):
        # Test with invalid input type
        with pytest.raises(TypeError):
            serve([1, 2, 3], layer_name="invalid")  # List is not supported


@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_serve_invalid_file_path():
    """Test serve function with invalid file path."""
    # Mock uvicorn.run to prevent actual server startup
    with patch('uvicorn.run'):
        # Test with non-existent file
        with pytest.raises(ValueError):
            serve("/nonexistent/file.geojson", layer_name="invalid")


# ============================================================================
# FASTAPI ENDPOINT TESTS
# ============================================================================

@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_fastapi_app_structure():
    """Test that FastAPI app has correct structure."""
    from fastapi import FastAPI
    
    assert isinstance(_app, FastAPI), "App should be FastAPI instance"
    
    # Check that app has routes
    routes = [route.path for route in _app.routes]
    assert "/" in routes, "App should have root route"


@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_vector_tile_endpoint_mock(sample_geodataframe):
    """Test vector tile endpoint with mocked data."""
    # Set up global state as serve() would
    import pymapgis.serve as serve_module
    serve_module._tile_server_data_source = sample_geodataframe.to_crs(epsg=3857)
    serve_module._tile_server_layer_name = "test_layer"
    serve_module._service_type = "vector"
    
    # Create test client
    client = TestClient(_app)
    
    # Test vector tile endpoint
    response = client.get("/xyz/test_layer/0/0/1.mvt")
    
    assert response.status_code == 200, "Vector tile endpoint should return 200"
    assert response.headers["content-type"] == "application/vnd.mapbox-vector-tile"
    assert len(response.content) > 0, "Response should have content"


@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_vector_tile_endpoint_wrong_layer():
    """Test vector tile endpoint with wrong layer name."""
    # Set up global state
    import pymapgis.serve as serve_module
    serve_module._tile_server_layer_name = "correct_layer"
    serve_module._service_type = "vector"
    
    # Create test client
    client = TestClient(_app)
    
    # Test with wrong layer name
    response = client.get("/xyz/wrong_layer/0/0/1.mvt")
    
    assert response.status_code == 404, "Wrong layer name should return 404"


@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_root_viewer_endpoint():
    """Test root viewer endpoint."""
    # Set up global state
    import pymapgis.serve as serve_module
    serve_module._tile_server_layer_name = "test_layer"
    serve_module._service_type = "vector"
    serve_module._tile_server_data_source = MagicMock()
    
    # Create test client
    client = TestClient(_app)
    
    # Test root endpoint
    response = client.get("/")
    
    assert response.status_code == 200, "Root endpoint should return 200"
    assert "text/html" in response.headers["content-type"]
    assert "PyMapGIS" in response.text, "Response should contain PyMapGIS branding"


@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_root_viewer_no_layer():
    """Test root viewer endpoint with no layer configured."""
    # Reset global state
    import pymapgis.serve as serve_module
    serve_module._tile_server_layer_name = None
    serve_module._service_type = None

    # Create test client
    client = TestClient(_app)

    # Test root endpoint
    response = client.get("/")

    assert response.status_code == 200, "Root endpoint should return 200"
    # The response might be a leafmap HTML page or a simple message
    assert ("No layer configured" in response.text or
            "PyMapGIS" in response.text), "Should indicate no layer configured or show PyMapGIS branding"


# ============================================================================
# SERVICE TYPE INFERENCE TESTS
# ============================================================================

@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_service_type_inference_vector_file(temp_geojson_file):
    """Test service type inference for vector files."""
    # Mock uvicorn.run and pymapgis.read
    with patch('uvicorn.run') as mock_run, \
         patch('pymapgis.read') as mock_read:
        
        # Mock read to return GeoDataFrame
        mock_gdf = MagicMock(spec=gpd.GeoDataFrame)
        mock_read.return_value = mock_gdf
        
        serve(temp_geojson_file, layer_name="test")

        # Check that service type was inferred as vector
        import pymapgis.serve as serve_module
        assert serve_module._service_type == "vector"


@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_service_type_inference_raster_file():
    """Test service type inference for raster files."""
    # Mock uvicorn.run
    with patch('uvicorn.run') as mock_run:
        
        # Test with .tif file (should be inferred as raster)
        serve("test_raster.tif", layer_name="test")
        
        # Check that service type was inferred as raster
        import pymapgis.serve as serve_module
        assert serve_module._service_type == "raster"


@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_service_type_inference_geodataframe(sample_geodataframe):
    """Test service type inference for GeoDataFrame."""
    # Mock uvicorn.run
    with patch('uvicorn.run') as mock_run:
        
        serve(sample_geodataframe, layer_name="test")
        
        # Check that service type was inferred as vector
        import pymapgis.serve as serve_module
        assert serve_module._service_type == "vector"


@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_service_type_inference_xarray(sample_dataarray):
    """Test service type inference for xarray DataArray."""
    # Mock uvicorn.run
    with patch('uvicorn.run') as mock_run:

        try:
            serve(sample_dataarray, layer_name="test")

            # Check that service type was inferred as raster
            import pymapgis.serve as serve_module
            assert serve_module._service_type == "raster"
        except NotImplementedError:
            # This is expected for in-memory xarray objects in Phase 1
            pytest.skip("In-memory xarray serving not yet implemented")


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_serve_error_handling_invalid_file():
    """Test error handling for invalid file paths."""
    with patch('uvicorn.run'):
        with pytest.raises(ValueError, match="Could not read or infer type"):
            serve("nonexistent_file.xyz", layer_name="test")


@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_gdf_to_mvt_error_handling():
    """Test error handling in gdf_to_mvt function."""
    # Test with invalid input
    with pytest.raises(Exception):
        gdf_to_mvt("not_a_geodataframe", 0, 0, 1)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_serve_integration_vector(sample_geodataframe):
    """Integration test for serving vector data."""
    # Mock uvicorn.run to prevent actual server startup
    with patch('uvicorn.run') as mock_run:
        
        # Test complete serve workflow
        serve(
            sample_geodataframe,
            service_type="xyz",
            layer_name="integration_test",
            host="localhost",
            port=9000
        )
        
        # Verify uvicorn was called with correct parameters
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert kwargs['host'] == 'localhost'
        assert kwargs['port'] == 9000
        
        # Verify global state was set correctly
        import pymapgis.serve as serve_module
        assert serve_module._tile_server_layer_name == "integration_test"
        assert serve_module._service_type == "vector"


@pytest.mark.integration
@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_serve_integration_file_path(temp_geojson_file):
    """Integration test for serving from file path."""
    # Mock uvicorn.run and pymapgis.read
    with patch('uvicorn.run') as mock_run, \
         patch('pymapgis.read') as mock_read:
        
        # Mock read to return GeoDataFrame
        mock_gdf = MagicMock(spec=gpd.GeoDataFrame)
        mock_read.return_value = mock_gdf
        
        # Test complete serve workflow
        serve(
            temp_geojson_file,
            service_type="xyz",
            layer_name="file_test",
            port=9001
        )
        
        # Verify file was read
        mock_read.assert_called_once_with(temp_geojson_file)
        
        # Verify server was started
        mock_run.assert_called_once()


# ============================================================================
# REQUIREMENTS COMPLIANCE TESTS
# ============================================================================

@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available")
def test_phase1_part7_requirements_compliance():
    """Test compliance with Phase 1 Part 7 requirements."""
    
    # Test 1: pmg.serve() function exists and is accessible
    import pymapgis
    assert hasattr(pymapgis, 'serve'), "pmg.serve() should be available"
    
    # Test 2: Function accepts required parameter types
    import inspect
    sig = inspect.signature(serve)
    
    # Check parameter types in docstring/annotations
    assert 'data' in sig.parameters, "Should accept 'data' parameter"
    assert 'service_type' in sig.parameters, "Should accept 'service_type' parameter"
    
    # Test 3: XYZ service type is supported
    assert sig.parameters['service_type'].default == 'xyz', "Should default to 'xyz' service"
    
    # Test 4: FastAPI is used for implementation
    from fastapi import FastAPI
    assert isinstance(_app, FastAPI), "Should use FastAPI for web service"
    
    # Test 5: Function accepts GeoDataFrame, xarray, and string inputs
    # (This is tested in other test functions)
    
    print("✅ Phase 1 Part 7 requirements compliance verified")


@pytest.mark.skipif(not SERVE_AVAILABLE, reason="Serve module not available") 
def test_conceptual_usage_examples():
    """Test that conceptual usage examples from requirements work."""
    
    # Mock uvicorn.run to prevent actual server startup
    with patch('uvicorn.run') as mock_run:
        
        # Example 1: Serve GeoDataFrame as vector tiles
        gdf = gpd.GeoDataFrame({
            'id': [1],
            'geometry': [Point(0, 0)]
        }, crs="EPSG:4326")
        
        # This should work as per requirements
        serve(gdf, service_type='xyz', layer_name='my_vector_layer', port=8080)
        
        # Verify it was called
        mock_run.assert_called()
        
        # Example 2: Serve file path
        with patch('pymapgis.read') as mock_read:
            mock_read.return_value = gdf
            serve("my_data.geojson", service_type='xyz', layer_name='my_layer')
            mock_read.assert_called_with("my_data.geojson")


print("✅ Serve module tests defined successfully")
