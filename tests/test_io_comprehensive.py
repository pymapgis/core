"""
Comprehensive tests for PyMapGIS Universal IO (pmg.read()) functionality.

This module tests all aspects of the pmg.read() function including:
- All supported data formats (vector and raster)
- Local and remote data sources
- Caching mechanisms
- Error handling
- Edge cases and performance scenarios
"""

import pytest
import numpy as np
import pandas as pd
import geopandas as gpd
import xarray as xr
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import shutil
from shapely.geometry import Point, Polygon

# Import the function under test
from pymapgis.io import read
import pymapgis as pmg


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_geodataframe():
    """Create a sample GeoDataFrame for testing."""
    points = [Point(0, 0), Point(1, 1), Point(2, 2)]
    data = {"id": [1, 2, 3], "name": ["A", "B", "C"], "value": [10, 20, 30]}
    return gpd.GeoDataFrame(data, geometry=points, crs="EPSG:4326")


@pytest.fixture
def sample_raster_data():
    """Create sample raster data for testing."""
    # Create sample data
    data = np.random.rand(3, 4).astype(np.float32)
    x_coords = np.array([0.0, 1.0, 2.0, 3.0])
    y_coords = np.array([2.0, 1.0, 0.0])

    da = xr.DataArray(
        data, coords={"y": y_coords, "x": x_coords}, dims=["y", "x"], name="test_raster"
    )

    # Add CRS if rioxarray is available
    try:
        import rioxarray

        da = da.rio.write_crs("EPSG:4326")
    except ImportError:
        pass

    return da


@pytest.fixture
def sample_dataset():
    """Create a sample xarray Dataset for testing."""
    # Create sample data
    temp_data = np.random.rand(2, 3).astype(np.float32)
    precip_data = np.random.rand(2, 3).astype(np.float32)

    x_coords = np.array([0.0, 1.0, 2.0])
    y_coords = np.array([1.0, 0.0])

    temp_da = xr.DataArray(
        temp_data,
        coords={"y": y_coords, "x": x_coords},
        dims=["y", "x"],
        name="temperature",
    )

    precip_da = xr.DataArray(
        precip_data,
        coords={"y": y_coords, "x": x_coords},
        dims=["y", "x"],
        name="precipitation",
    )

    ds = xr.Dataset({"temperature": temp_da, "precipitation": precip_da})

    # Add CRS if rioxarray is available
    try:
        import rioxarray

        ds = ds.rio.write_crs("EPSG:4326")
    except ImportError:
        pass

    return ds


# Tests for Vector Formats


def test_read_shapefile(temp_dir, sample_geodataframe):
    """Test reading Shapefile format."""
    # Create test shapefile
    shp_path = temp_dir / "test.shp"
    sample_geodataframe.to_file(shp_path)

    # Test reading
    result = read(shp_path)

    # Verify result
    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == len(sample_geodataframe)
    assert result.crs is not None
    assert "geometry" in result.columns


def test_read_geojson(temp_dir, sample_geodataframe):
    """Test reading GeoJSON format."""
    # Create test GeoJSON
    geojson_path = temp_dir / "test.geojson"
    sample_geodataframe.to_file(geojson_path, driver="GeoJSON")

    # Test reading
    result = read(geojson_path)

    # Verify result
    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == len(sample_geodataframe)
    assert result.crs is not None


def test_read_geopackage(temp_dir, sample_geodataframe):
    """Test reading GeoPackage format."""
    # Create test GeoPackage
    gpkg_path = temp_dir / "test.gpkg"
    sample_geodataframe.to_file(gpkg_path, driver="GPKG")

    # Test reading
    result = read(gpkg_path)

    # Verify result
    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == len(sample_geodataframe)
    assert result.crs is not None


def test_read_geoparquet(temp_dir, sample_geodataframe):
    """Test reading GeoParquet format."""
    # Create test GeoParquet
    parquet_path = temp_dir / "test.parquet"
    sample_geodataframe.to_parquet(parquet_path)

    # Test reading
    result = read(parquet_path)

    # Verify result
    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == len(sample_geodataframe)
    assert result.crs is not None


def test_read_csv_with_coordinates(temp_dir):
    """Test reading CSV with longitude/latitude columns."""
    # Create test CSV with coordinates
    csv_path = temp_dir / "test.csv"
    csv_data = "longitude,latitude,name,value\n0,0,A,10\n1,1,B,20\n2,2,C,30\n"
    csv_path.write_text(csv_data)

    # Test reading
    result = read(csv_path)

    # Verify result
    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == 3
    assert result.crs.to_epsg() == 4326
    assert "geometry" in result.columns
    assert result.geometry.iloc[0].x == 0
    assert result.geometry.iloc[0].y == 0


def test_read_csv_without_coordinates(temp_dir):
    """Test reading CSV without coordinate columns."""
    # Create test CSV without coordinates
    csv_path = temp_dir / "test.csv"
    csv_data = "id,name,value\n1,A,10\n2,B,20\n3,C,30\n"
    csv_path.write_text(csv_data)

    # Test reading
    result = read(csv_path)

    # Verify result
    assert isinstance(result, pd.DataFrame)
    assert not isinstance(result, gpd.GeoDataFrame)
    assert len(result) == 3
    assert "geometry" not in result.columns


def test_read_csv_custom_coordinate_columns(temp_dir):
    """Test reading CSV with custom coordinate column names."""
    # Create test CSV with custom coordinate columns
    csv_path = temp_dir / "test.csv"
    csv_data = "x_coord,y_coord,name,value\n0,0,A,10\n1,1,B,20\n2,2,C,30\n"
    csv_path.write_text(csv_data)

    # Test reading with custom column names
    result = read(csv_path, x="x_coord", y="y_coord")

    # Verify result
    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == 3
    assert result.crs.to_epsg() == 4326
    assert result.geometry.iloc[0].x == 0


# Tests for Raster Formats


def test_read_geotiff(temp_dir, sample_raster_data):
    """Test reading GeoTIFF format."""
    # Create test GeoTIFF
    tiff_path = temp_dir / "test.tif"

    # Save using rioxarray if available
    try:
        sample_raster_data.rio.to_raster(tiff_path)

        # Test reading
        result = read(tiff_path)

        # Verify result
        assert isinstance(result, xr.DataArray)
        assert result.dims == ("band", "y", "x") or result.dims == ("y", "x")
        assert hasattr(result, "rio")
        assert result.rio.crs is not None
    except ImportError:
        pytest.skip("rioxarray not available for GeoTIFF test")


def test_read_cog(temp_dir, sample_raster_data):
    """Test reading Cloud Optimized GeoTIFF format."""
    # Create test COG (same as GeoTIFF for testing purposes)
    cog_path = temp_dir / "test.cog"

    try:
        sample_raster_data.rio.to_raster(cog_path)

        # Test reading
        result = read(cog_path)

        # Verify result
        assert isinstance(result, xr.DataArray)
        assert hasattr(result, "rio")
    except ImportError:
        pytest.skip("rioxarray not available for COG test")


def test_read_netcdf(temp_dir, sample_dataset):
    """Test reading NetCDF format."""
    # Create test NetCDF
    nc_path = temp_dir / "test.nc"
    sample_dataset.to_netcdf(nc_path)

    # Test reading
    result = read(nc_path)

    # Verify result
    assert isinstance(result, xr.Dataset)
    assert "temperature" in result.data_vars
    assert "precipitation" in result.data_vars
    assert "x" in result.coords
    assert "y" in result.coords


# Tests for Data Sources and Caching


@patch("fsspec.filesystem")
@patch("fsspec.utils.infer_storage_options")
def test_read_remote_https_url(mock_infer_storage, mock_filesystem):
    """Test reading from HTTPS URL with caching."""
    # Mock storage options for HTTPS
    mock_infer_storage.return_value = {
        "protocol": "https",
        "path": "/path/to/data.geojson",
    }

    # Mock filesystem
    mock_fs = MagicMock()
    mock_filesystem.return_value = mock_fs
    mock_fs.get_mapper.return_value.root = "/tmp/cached_file.geojson"

    # Mock the file content
    with patch("geopandas.read_file") as mock_read_file:
        mock_gdf = gpd.GeoDataFrame(
            {"id": [1]}, geometry=[Point(0, 0)], crs="EPSG:4326"
        )
        mock_read_file.return_value = mock_gdf

        # Test reading
        result = read("https://example.com/data.geojson")

        # Verify caching was used
        mock_filesystem.assert_called_once()
        assert "filecache" in mock_filesystem.call_args[0]

        # Verify result
        assert isinstance(result, gpd.GeoDataFrame)


@patch("fsspec.filesystem")
@patch("fsspec.utils.infer_storage_options")
def test_read_s3_url(mock_infer_storage, mock_filesystem):
    """Test reading from S3 URL with caching."""
    # Mock storage options for S3
    mock_infer_storage.return_value = {
        "protocol": "s3",
        "path": "/bucket/path/to/data.tif",
    }

    # Mock filesystem
    mock_fs = MagicMock()
    mock_filesystem.return_value = mock_fs
    mock_fs.get_mapper.return_value.root = "/tmp/cached_file.tif"

    # Mock the file content
    with patch("rioxarray.open_rasterio") as mock_open_raster:
        mock_da = xr.DataArray(np.random.rand(3, 4), dims=["y", "x"])
        mock_open_raster.return_value = mock_da

        # Test reading
        result = read("s3://bucket/path/to/data.tif")

        # Verify caching was used
        mock_filesystem.assert_called_once()
        assert "filecache" in mock_filesystem.call_args[0]

        # Verify result
        assert isinstance(result, xr.DataArray)


def test_read_local_file_no_caching(temp_dir, sample_geodataframe):
    """Test that local files don't use caching."""
    # Create test file
    shp_path = temp_dir / "test.shp"
    sample_geodataframe.to_file(shp_path)

    # Mock fsspec.filesystem to ensure it's not called for local files
    with patch("fsspec.filesystem") as mock_filesystem:
        result = read(shp_path)

        # Verify no caching was used for local file
        mock_filesystem.assert_not_called()

        # Verify result
        assert isinstance(result, gpd.GeoDataFrame)


# Tests for Error Handling


def test_read_unsupported_format(temp_dir):
    """Test error handling for unsupported file formats."""
    # Create file with unsupported extension
    unsupported_path = temp_dir / "test.xyz"
    unsupported_path.write_text("some content")

    # Test that ValueError is raised
    with pytest.raises(ValueError, match="Unsupported format"):
        read(unsupported_path)


def test_read_nonexistent_file():
    """Test error handling for non-existent files."""
    # Test that FileNotFoundError is raised
    with pytest.raises(FileNotFoundError, match="File not found"):
        read("/path/that/does/not/exist.shp")


def test_read_corrupted_file(temp_dir):
    """Test error handling for corrupted files."""
    # Create corrupted shapefile
    corrupted_path = temp_dir / "corrupted.shp"
    corrupted_path.write_text("this is not a valid shapefile")

    # Test that IOError is raised
    with pytest.raises(IOError, match="Failed to read"):
        read(corrupted_path)


# Tests for Edge Cases and Special Scenarios


def test_read_with_pathlib_path(temp_dir, sample_geodataframe):
    """Test reading with pathlib.Path objects."""
    # Create test file
    shp_path = temp_dir / "test.shp"
    sample_geodataframe.to_file(shp_path)

    # Test reading with Path object (not string)
    result = read(shp_path)  # shp_path is already a Path object

    # Verify result
    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == len(sample_geodataframe)


def test_read_csv_with_custom_crs(temp_dir):
    """Test reading CSV with custom CRS specification."""
    # Create test CSV
    csv_path = temp_dir / "test.csv"
    csv_data = "longitude,latitude,name\n0,0,A\n1,1,B\n"
    csv_path.write_text(csv_data)

    # Test reading with custom CRS
    result = read(csv_path, crs="EPSG:3857")

    # Verify custom CRS was applied
    assert isinstance(result, gpd.GeoDataFrame)
    assert result.crs.to_epsg() == 3857


def test_read_csv_with_encoding(temp_dir):
    """Test reading CSV with custom encoding."""
    # Create test CSV with special characters
    csv_path = temp_dir / "test.csv"
    csv_data = "longitude,latitude,name\n0,0,Café\n1,1,Naïve\n"
    csv_path.write_bytes(csv_data.encode("utf-8"))

    # Test reading with explicit encoding
    result = read(csv_path, encoding="utf-8")

    # Verify result
    assert isinstance(result, gpd.GeoDataFrame)
    assert "Café" in result["name"].values


def test_read_with_kwargs_passthrough(temp_dir, sample_geodataframe):
    """Test that kwargs are properly passed to underlying functions."""
    # Create test GeoPackage with multiple layers
    gpkg_path = temp_dir / "test.gpkg"
    sample_geodataframe.to_file(gpkg_path, layer="layer1", driver="GPKG")

    # Add another layer
    sample_geodataframe.to_file(gpkg_path, layer="layer2", driver="GPKG", mode="a")

    # Test reading specific layer
    result = read(gpkg_path, layer="layer2")

    # Verify result
    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == len(sample_geodataframe)


def test_read_empty_file_handling(temp_dir):
    """Test handling of empty or minimal files."""
    # Create empty CSV
    empty_csv = temp_dir / "empty.csv"
    empty_csv.write_text("longitude,latitude\n")  # Header only

    # Test reading empty CSV
    result = read(empty_csv)

    # Verify result
    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == 0


# Tests for Performance and Caching Behavior


@patch("pymapgis.settings.settings")
def test_cache_directory_configuration(mock_settings, temp_dir):
    """Test that cache directory is properly configured."""
    # Mock settings
    mock_settings.cache_dir = str(temp_dir / "custom_cache")

    with patch("fsspec.filesystem") as mock_filesystem:
        with patch("fsspec.utils.infer_storage_options") as mock_infer:
            mock_infer.return_value = {"protocol": "https", "path": "/data.geojson"}

            # Mock filesystem
            mock_fs = MagicMock()
            mock_filesystem.return_value = mock_fs
            mock_fs.get_mapper.return_value.root = "/tmp/cached_file.geojson"

            with patch("geopandas.read_file") as mock_read:
                mock_read.return_value = gpd.GeoDataFrame(
                    {"id": [1]}, geometry=[Point(0, 0)]
                )

                # Test reading remote file
                read("https://example.com/data.geojson")

                # Verify cache directory was used
                mock_filesystem.assert_called_once()
                call_kwargs = mock_filesystem.call_args[1]
                assert "cache_storage" in call_kwargs
                assert str(temp_dir / "custom_cache") in call_kwargs["cache_storage"]


# Integration Tests


def test_read_integration_with_accessors(temp_dir, sample_geodataframe):
    """Test that read() works with PyMapGIS accessors."""
    # Create test file
    shp_path = temp_dir / "test.shp"
    sample_geodataframe.to_file(shp_path)

    # Test reading and using with accessor
    result = read(shp_path)

    # Verify accessor is available
    assert hasattr(result, "pmg")
    assert hasattr(result.pmg, "explore")
    assert hasattr(result.pmg, "map")


def test_read_integration_with_vector_operations(temp_dir, sample_geodataframe):
    """Test that read() results work with vector operations."""
    # Create test file
    shp_path = temp_dir / "test.shp"
    sample_geodataframe.to_file(shp_path)

    # Test reading and using with vector operations
    result = read(shp_path)

    # Test buffer operation
    buffered = pmg.buffer(result, 0.1)
    assert isinstance(buffered, gpd.GeoDataFrame)
    assert len(buffered) == len(result)


def test_read_integration_with_raster_operations(temp_dir, sample_raster_data):
    """Test that read() results work with raster operations."""
    try:
        # Create test GeoTIFF
        tiff_path = temp_dir / "test.tif"
        sample_raster_data.rio.to_raster(tiff_path)

        # Test reading and using with raster operations
        result = read(tiff_path)

        # Verify accessor methods are available
        assert hasattr(result, "pmg")
        assert hasattr(result.pmg, "reproject")
        assert hasattr(result.pmg, "explore")

    except ImportError:
        pytest.skip("rioxarray not available for raster integration test")


# Real-world Scenario Tests


def test_read_realistic_geojson_workflow(temp_dir):
    """Test a realistic GeoJSON workflow."""
    # Create realistic GeoJSON data
    polygons = [
        Polygon([(0, 0), (1, 0), (1, 1), (0, 1)]),
        Polygon([(1, 0), (2, 0), (2, 1), (1, 1)]),
        Polygon([(0, 1), (1, 1), (1, 2), (0, 2)]),
    ]

    realistic_data = {
        "NAME": ["County A", "County B", "County C"],
        "POPULATION": [10000, 15000, 8000],
        "AREA_KM2": [100.5, 150.2, 80.7],
        "DENSITY": [99.5, 99.9, 99.1],
    }

    gdf = gpd.GeoDataFrame(realistic_data, geometry=polygons, crs="EPSG:4326")

    # Save and read
    geojson_path = temp_dir / "counties.geojson"
    gdf.to_file(geojson_path, driver="GeoJSON")

    result = read(geojson_path)

    # Verify realistic workflow
    assert isinstance(result, gpd.GeoDataFrame)
    assert len(result) == 3
    assert "POPULATION" in result.columns
    assert result.crs.to_epsg() == 4326

    # Test that we can perform analysis
    total_population = result["POPULATION"].sum()
    assert total_population == 33000


def test_read_multiple_formats_consistency(temp_dir, sample_geodataframe):
    """Test that the same data reads consistently across formats."""
    # Save in multiple formats
    shp_path = temp_dir / "test.shp"
    geojson_path = temp_dir / "test.geojson"
    gpkg_path = temp_dir / "test.gpkg"

    sample_geodataframe.to_file(shp_path)
    sample_geodataframe.to_file(geojson_path, driver="GeoJSON")
    sample_geodataframe.to_file(gpkg_path, driver="GPKG")

    # Read all formats
    shp_result = read(shp_path)
    geojson_result = read(geojson_path)
    gpkg_result = read(gpkg_path)

    # Verify consistency
    assert len(shp_result) == len(geojson_result) == len(gpkg_result)
    assert all(
        isinstance(r, gpd.GeoDataFrame)
        for r in [shp_result, geojson_result, gpkg_result]
    )

    # Verify data consistency (allowing for minor floating point differences)
    assert (
        shp_result["id"].tolist()
        == geojson_result["id"].tolist()
        == gpkg_result["id"].tolist()
    )
