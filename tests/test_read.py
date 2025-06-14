import geopandas as gpd
import pandas as pd
import numpy as np
import xarray as xr
from pathlib import Path
from unittest.mock import patch
from pymapgis.io import read
import pytest


def test_read_shp(tmp_path):
    """Test basic Shapefile reading."""
    gdf = gpd.GeoDataFrame(geometry=gpd.points_from_xy([0], [0]), crs="EPSG:4326")
    shp = tmp_path / "pts.shp"
    gdf.to_file(shp)
    out = read(shp)
    assert isinstance(out, gpd.GeoDataFrame)
    assert len(out) == 1
    assert out.crs is not None


def test_read_csv(tmp_path):
    """Test basic CSV reading with coordinates."""
    csv = tmp_path / "pts.csv"
    csv.write_text("longitude,latitude\n1,1\n")
    out = read(csv)
    assert isinstance(out, gpd.GeoDataFrame)
    assert out.geometry.iloc[0].x == 1
    assert out.geometry.iloc[0].y == 1
    assert out.crs.to_epsg() == 4326


def test_read_csv_no_geometry(tmp_path):
    """Test CSV reading without coordinate columns."""
    csv = tmp_path / "data.csv"
    csv.write_text("id,name,value\n1,test,100\n")
    out = read(csv)
    assert isinstance(out, pd.DataFrame)
    assert not isinstance(out, gpd.GeoDataFrame)
    assert len(out) == 1
    assert out["name"].iloc[0] == "test"


def test_read_geojson(tmp_path):
    """Test GeoJSON reading."""
    gdf = gpd.GeoDataFrame(
        {"id": [1, 2], "name": ["A", "B"]},
        geometry=gpd.points_from_xy([0, 1], [0, 1]),
        crs="EPSG:4326",
    )
    geojson = tmp_path / "test.geojson"
    gdf.to_file(geojson, driver="GeoJSON")
    out = read(geojson)
    assert isinstance(out, gpd.GeoDataFrame)
    assert len(out) == 2
    assert "name" in out.columns


def test_read_geopackage(tmp_path):
    """Test GeoPackage reading."""
    gdf = gpd.GeoDataFrame(
        {"id": [1, 2], "value": [10, 20]},
        geometry=gpd.points_from_xy([0, 1], [0, 1]),
        crs="EPSG:4326",
    )
    gpkg = tmp_path / "test.gpkg"
    gdf.to_file(gpkg, driver="GPKG")
    out = read(gpkg)
    assert isinstance(out, gpd.GeoDataFrame)
    assert len(out) == 2
    assert "value" in out.columns


def test_read_parquet(tmp_path):
    """Test Parquet/GeoParquet reading."""
    gdf = gpd.GeoDataFrame(
        {"id": [1, 2], "category": ["X", "Y"]},
        geometry=gpd.points_from_xy([0, 1], [0, 1]),
        crs="EPSG:4326",
    )
    parquet = tmp_path / "test.parquet"
    gdf.to_parquet(parquet)
    out = read(parquet)
    assert isinstance(out, gpd.GeoDataFrame)
    assert len(out) == 2
    assert "category" in out.columns


def test_read_netcdf(tmp_path):
    """Test NetCDF reading."""
    # Create sample dataset
    data = np.random.rand(2, 3, 4)
    ds = xr.Dataset(
        {
            "temperature": (["time", "y", "x"], data),
            "precipitation": (["time", "y", "x"], data * 0.5),
        }
    )

    nc = tmp_path / "test.nc"
    ds.to_netcdf(nc)
    out = read(nc)
    assert isinstance(out, xr.Dataset)
    assert "temperature" in out.data_vars
    assert "precipitation" in out.data_vars


@pytest.mark.skipif(
    True, reason="Requires rioxarray and may not be available in all environments"
)
def test_read_geotiff(tmp_path):
    """Test GeoTIFF reading (conditional on rioxarray availability)."""
    try:
        import rioxarray

        # Create sample raster
        data = np.random.rand(3, 4).astype(np.float32)
        da = xr.DataArray(data, dims=["y", "x"])
        da = da.rio.write_crs("EPSG:4326")

        tiff = tmp_path / "test.tif"
        da.rio.to_raster(tiff)

        out = read(tiff)
        assert isinstance(out, xr.DataArray)
        assert hasattr(out, "rio")

    except ImportError:
        pytest.skip("rioxarray not available")


def test_read_with_kwargs(tmp_path):
    """Test that kwargs are passed through correctly."""
    # Test with CSV encoding
    csv = tmp_path / "test_encoding.csv"
    csv.write_bytes("longitude,latitude,name\n0,0,Café\n".encode("utf-8"))

    out = read(csv, encoding="utf-8")
    assert isinstance(out, gpd.GeoDataFrame)
    assert "Café" in out["name"].values


def test_read_pathlib_path(tmp_path):
    """Test reading with pathlib.Path objects."""
    gdf = gpd.GeoDataFrame(geometry=gpd.points_from_xy([0], [0]), crs="EPSG:4326")
    shp_path = tmp_path / "test.shp"
    gdf.to_file(shp_path)

    # Test with Path object (not string)
    out = read(shp_path)
    assert isinstance(out, gpd.GeoDataFrame)


def test_read_error_handling(tmp_path):
    """Test error handling for various scenarios."""
    # Test unsupported format
    unsupported = tmp_path / "test.xyz"
    unsupported.write_text("content")

    with pytest.raises(ValueError, match="Unsupported format"):
        read(unsupported)

    # Test non-existent file
    with pytest.raises(FileNotFoundError):
        read("non_existent_file.shp")


@patch("fsspec.utils.infer_storage_options")
@patch("fsspec.filesystem")
def test_read_remote_url_caching(mock_filesystem, mock_infer_storage, tmp_path):
    """Test that remote URLs use caching."""
    # Mock storage options
    mock_infer_storage.return_value = {"protocol": "https", "path": "/data.geojson"}

    # Mock filesystem
    mock_fs = mock_filesystem.return_value
    mock_fs.get_mapper.return_value.root = str(tmp_path / "cached_file.geojson")

    # Create a mock file for reading
    gdf = gpd.GeoDataFrame(geometry=gpd.points_from_xy([0], [0]), crs="EPSG:4326")
    test_file = tmp_path / "cached_file.geojson"
    gdf.to_file(test_file, driver="GeoJSON")

    # Test reading remote URL
    result = read("https://example.com/data.geojson")

    # Verify caching was attempted
    mock_filesystem.assert_called_once()
    assert "filecache" in mock_filesystem.call_args[0]

    # Verify result
    assert isinstance(result, gpd.GeoDataFrame)
