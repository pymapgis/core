#!/usr/bin/env python3
"""
Test script to verify PyMapGIS functionality that the QGIS plugin depends on.
This script tests the core functionality without requiring QGIS.
"""

import sys
import tempfile
import os
from pathlib import Path
import traceback

def test_pymapgis_import():
    """Test that PyMapGIS can be imported successfully."""
    print("🔍 Testing PyMapGIS import...")
    try:
        import pymapgis
        import geopandas as gpd
        import xarray as xr
        import rioxarray
        print("✅ All required libraries imported successfully")
        print(f"   - PyMapGIS version: {pymapgis.__version__}")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_local_file_reading():
    """Test reading local files (similar to what the plugin would do)."""
    print("\n🔍 Testing local file reading...")
    try:
        import pymapgis as pmg
        import geopandas as gpd
        from shapely.geometry import Point

        # Create a test GeoDataFrame
        test_data = gpd.GeoDataFrame({
            'id': [1, 2, 3],
            'name': ['Point A', 'Point B', 'Point C'],
            'geometry': [Point(0, 0), Point(1, 1), Point(2, 2)]
        }, crs='EPSG:4326')

        # Save to temporary files in different formats
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test GeoJSON
            geojson_path = Path(temp_dir) / "test.geojson"
            test_data.to_file(geojson_path, driver="GeoJSON")

            # Test reading with PyMapGIS
            loaded_geojson = pmg.read(str(geojson_path))
            assert isinstance(loaded_geojson, gpd.GeoDataFrame)
            assert len(loaded_geojson) == 3
            print("✅ GeoJSON reading works")

            # Test GPKG (what the plugin uses for vector data)
            gpkg_path = Path(temp_dir) / "test.gpkg"
            test_data.to_file(gpkg_path, driver="GPKG")

            loaded_gpkg = pmg.read(str(gpkg_path))
            assert isinstance(loaded_gpkg, gpd.GeoDataFrame)
            assert len(loaded_gpkg) == 3
            print("✅ GPKG reading works")

        return True
    except Exception as e:
        print(f"❌ Local file reading error: {e}")
        traceback.print_exc()
        return False

def test_raster_functionality():
    """Test raster functionality that the plugin uses."""
    print("\n🔍 Testing raster functionality...")
    try:
        import xarray as xr
        import rioxarray
        import numpy as np

        # Create a test raster
        data = np.random.rand(10, 10)
        x_coords = np.linspace(-180, 180, 10)
        y_coords = np.linspace(-90, 90, 10)

        da = xr.DataArray(
            data,
            coords={'y': y_coords, 'x': x_coords},
            dims=['y', 'x'],
            name='test_data'
        )

        # Set CRS (required for the plugin)
        da.rio.write_crs("EPSG:4326", inplace=True)

        # Test saving to GeoTIFF (what the plugin does)
        with tempfile.TemporaryDirectory() as temp_dir:
            tiff_path = Path(temp_dir) / "test.tif"
            da.rio.to_raster(tiff_path, tiled=True)

            # Verify the file was created and can be read
            assert tiff_path.exists()

            # Test reading back
            import pymapgis as pmg
            loaded_raster = pmg.read(str(tiff_path))
            assert isinstance(loaded_raster, xr.DataArray)
            print("✅ Raster creation and reading works")

        return True
    except Exception as e:
        print(f"❌ Raster functionality error: {e}")
        traceback.print_exc()
        return False

def test_plugin_data_processing_logic():
    """Test the data processing logic used in the plugin."""
    print("\n🔍 Testing plugin data processing logic...")
    try:
        import geopandas as gpd
        import xarray as xr
        import tempfile
        import os
        from shapely.geometry import Point

        # Test vector data processing (mimicking plugin logic)
        gdf = gpd.GeoDataFrame({
            'id': [1, 2],
            'name': ['Test A', 'Test B'],
            'geometry': [Point(0, 0), Point(1, 1)]
        }, crs='EPSG:4326')

        with tempfile.TemporaryDirectory() as temp_dir:
            # Test layer name generation (from plugin code)
            uri = "test://data/sample.geojson"
            uri_basename = uri.split('/')[-1].split('?')[0]
            layer_name_base = os.path.splitext(uri_basename)[0] if uri_basename else "pymapgis_layer"
            assert layer_name_base == "sample"

            # Test filename sanitization (from plugin code)
            layer_name = "test layer with spaces & special chars!"
            safe_filename = "".join(c if c.isalnum() else "_" for c in layer_name)
            assert safe_filename == "test_layer_with_spaces___special_chars_"

            # Test GPKG export (what plugin does for vector data)
            temp_gpkg_path = os.path.join(temp_dir, safe_filename + ".gpkg")
            gdf.to_file(temp_gpkg_path, driver="GPKG")
            assert os.path.exists(temp_gpkg_path)

            print("✅ Vector data processing logic works")

        # Test raster data processing
        import numpy as np
        data = np.random.rand(5, 5)
        da = xr.DataArray(
            data,
            coords={'y': np.linspace(0, 4, 5), 'x': np.linspace(0, 4, 5)},
            dims=['y', 'x']
        )
        da.rio.write_crs("EPSG:4326", inplace=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_tiff_path = os.path.join(temp_dir, "test_raster.tif")
            da.rio.to_raster(temp_tiff_path, tiled=True)
            assert os.path.exists(temp_tiff_path)

            print("✅ Raster data processing logic works")

        return True
    except Exception as e:
        print(f"❌ Plugin data processing logic error: {e}")
        traceback.print_exc()
        return False

def test_error_conditions():
    """Test error conditions that the plugin should handle."""
    print("\n🔍 Testing error conditions...")
    try:
        import pymapgis as pmg

        # Test reading non-existent file
        try:
            pmg.read("non_existent_file.geojson")
            print("❌ Should have raised an error for non-existent file")
            return False
        except (FileNotFoundError, IOError):
            print("✅ Correctly handles non-existent files")

        # Test unsupported format
        try:
            with tempfile.NamedTemporaryFile(suffix=".unsupported", delete=False) as f:
                f.write(b"test data")
                temp_path = f.name

            pmg.read(temp_path)
            print("❌ Should have raised an error for unsupported format")
            return False
        except (ValueError, IOError):
            print("✅ Correctly handles unsupported formats")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

        return True
    except Exception as e:
        print(f"❌ Error condition testing failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 Testing PyMapGIS functionality for QGIS plugin compatibility\n")

    tests = [
        test_pymapgis_import,
        test_local_file_reading,
        test_raster_functionality,
        test_plugin_data_processing_logic,
        test_error_conditions
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            traceback.print_exc()
            results.append(False)

    print(f"\n📊 Test Results: {sum(results)}/{len(results)} tests passed")

    if all(results):
        print("🎉 All tests passed! PyMapGIS functionality is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. There may be issues with the PyMapGIS setup.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
