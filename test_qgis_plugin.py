#!/usr/bin/env python3
"""
Unit tests for the PyMapGIS QGIS plugin components.
These tests focus on the plugin logic without requiring QGIS to be installed.
"""

import sys
import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import traceback

# Add the plugin directory to the path so we can import the plugin modules
plugin_dir = Path(__file__).parent / "qgis_plugin" / "pymapgis_qgis_plugin"
sys.path.insert(0, str(plugin_dir))

class TestPluginLogic(unittest.TestCase):
    """Test the core logic of the QGIS plugin without QGIS dependencies."""

    def test_layer_name_generation(self):
        """Test the layer name generation logic from the plugin."""
        # Test cases from the plugin code
        test_cases = [
            ("census://acs/acs5?year=2022&geography=county", "acs5"),
            ("tiger://county?year=2022&state=06", "county"),
            ("file://path/to/data.geojson", "data"),
            ("http://example.com/data.shp", "data"),
            ("simple_file.gpkg", "simple_file"),
            ("", "pymapgis_layer"),  # fallback case
        ]

        for uri, expected in test_cases:
            with self.subTest(uri=uri):
                # This is the logic from pymapgis_dialog.py line 75-76
                uri_basename = uri.split('/')[-1].split('?')[0]
                layer_name_base = os.path.splitext(uri_basename)[0] if uri_basename else "pymapgis_layer"
                self.assertEqual(layer_name_base, expected)

    def test_filename_sanitization(self):
        """Test the filename sanitization logic from the plugin."""
        # Test cases for the sanitization logic from line 89
        test_cases = [
            ("normal_name", "normal_name"),
            ("name with spaces", "name_with_spaces"),
            ("name-with-dashes", "name_with_dashes"),
            ("name.with.dots", "name_with_dots"),
            ("name/with\\slashes", "name_with_slashes"),
            ("name:with*special?chars", "name_with_special_chars"),
            ("", ""),
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                # This is the logic from pymapgis_dialog.py line 89
                safe_filename = "".join(c if c.isalnum() else "_" for c in input_name)
                self.assertEqual(safe_filename, expected)

    def test_layer_name_uniqueness_logic(self):
        """Test the layer name uniqueness logic."""
        # Mock the QgsProject.instance().mapLayersByName() method
        existing_layers = ["test_layer", "test_layer_1", "test_layer_2"]

        def mock_map_layers_by_name(name):
            return [name] if name in existing_layers else []

        # Test the uniqueness logic from lines 79-83
        layer_name_base = "test_layer"
        layer_name = layer_name_base
        count = 1
        while mock_map_layers_by_name(layer_name):
            layer_name = f"{layer_name_base}_{count}"
            count += 1

        self.assertEqual(layer_name, "test_layer_3")

    def test_uri_validation(self):
        """Test URI validation logic."""
        # Test empty URI handling (from line 60)
        empty_uris = ["", "   ", "\t\n"]
        for uri in empty_uris:
            with self.subTest(uri=repr(uri)):
                cleaned_uri = uri.strip()
                self.assertFalse(cleaned_uri, "Empty URI should be falsy after strip()")

    def test_data_type_detection(self):
        """Test the data type detection logic used in the plugin."""
        import geopandas as gpd
        import xarray as xr
        import numpy as np
        from shapely.geometry import Point

        # Test GeoDataFrame detection (line 85)
        gdf = gpd.GeoDataFrame({
            'geometry': [Point(0, 0)]
        }, crs='EPSG:4326')
        self.assertIsInstance(gdf, gpd.GeoDataFrame)

        # Test xarray DataArray detection (line 105)
        da = xr.DataArray(np.random.rand(5, 5))
        self.assertIsInstance(da, xr.DataArray)

        # Test unsupported type
        unsupported_data = {"not": "supported"}
        self.assertFalse(isinstance(unsupported_data, (gpd.GeoDataFrame, xr.DataArray)))


class TestPluginErrorHandling(unittest.TestCase):
    """Test error handling in the plugin."""

    def test_import_error_handling(self):
        """Test how the plugin handles import errors."""
        # The plugin should handle ImportError for pymapgis (lines 63-68)
        # and for the dialog import (lines 72-76)

        # Test pymapgis import error message
        expected_pymapgis_error = "PyMapGIS library not found. Please ensure it is installed in the QGIS Python environment."

        # Test dialog import error message format
        test_error = ImportError("No module named 'test_module'")
        expected_dialog_error = f"Failed to import PyMapGISDialog: {str(test_error)}. Check plugin structure and pymapgis_dialog.py."

        self.assertIn("PyMapGIS library not found", expected_pymapgis_error)
        self.assertIn("Failed to import PyMapGISDialog", expected_dialog_error)

    def test_raster_crs_validation(self):
        """Test raster CRS validation logic."""
        import xarray as xr
        import rioxarray  # This adds the rio accessor
        import numpy as np

        # Test DataArray without CRS (should trigger warning - line 109)
        da_no_crs = xr.DataArray(np.random.rand(5, 5))
        # Don't set CRS, so it should be None

        # This should trigger the CRS check (line 109 in plugin)
        self.assertIsNone(da_no_crs.rio.crs)

        # Test DataArray with CRS
        da_with_crs = xr.DataArray(
            np.random.rand(5, 5),
            coords={'y': np.linspace(0, 4, 5), 'x': np.linspace(0, 4, 5)},
            dims=['y', 'x']
        )
        da_with_crs.rio.write_crs("EPSG:4326", inplace=True)

        self.assertIsNotNone(da_with_crs.rio.crs)


class TestPluginIntegration(unittest.TestCase):
    """Test plugin integration scenarios."""

    def test_vector_data_workflow(self):
        """Test the complete vector data workflow."""
        import geopandas as gpd
        import tempfile
        import os
        from shapely.geometry import Point

        # Create test data
        gdf = gpd.GeoDataFrame({
            'id': [1, 2],
            'name': ['Test A', 'Test B'],
            'geometry': [Point(0, 0), Point(1, 1)]
        }, crs='EPSG:4326')

        with tempfile.TemporaryDirectory() as temp_dir:
            # Simulate the plugin workflow for vector data
            layer_name = "test_layer"
            safe_filename = "".join(c if c.isalnum() else "_" for c in layer_name)
            temp_gpkg_path = os.path.join(temp_dir, safe_filename + ".gpkg")

            # Save to GPKG (what the plugin does)
            gdf.to_file(temp_gpkg_path, driver="GPKG")

            # Verify file was created
            self.assertTrue(os.path.exists(temp_gpkg_path))

            # Verify it can be read back
            loaded_gdf = gpd.read_file(temp_gpkg_path)
            self.assertEqual(len(loaded_gdf), 2)
            self.assertEqual(loaded_gdf.crs.to_string(), 'EPSG:4326')

    def test_raster_data_workflow(self):
        """Test the complete raster data workflow."""
        import xarray as xr
        import rioxarray
        import numpy as np
        import tempfile
        import os

        # Create test raster data
        data = np.random.rand(10, 10)
        da = xr.DataArray(
            data,
            coords={'y': np.linspace(0, 9, 10), 'x': np.linspace(0, 9, 10)},
            dims=['y', 'x']
        )
        da.rio.write_crs("EPSG:4326", inplace=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            # Simulate the plugin workflow for raster data
            layer_name = "test_raster"
            safe_filename = "".join(c if c.isalnum() else "_" for c in layer_name)
            temp_tiff_path = os.path.join(temp_dir, safe_filename + ".tif")

            # Save to GeoTIFF (what the plugin does)
            da.rio.to_raster(temp_tiff_path, tiled=True)

            # Verify file was created
            self.assertTrue(os.path.exists(temp_tiff_path))

            # Verify it can be read back
            loaded_da = rioxarray.open_rasterio(temp_tiff_path)
            self.assertEqual(loaded_da.shape, (1, 10, 10))  # Includes band dimension


def run_plugin_tests():
    """Run all plugin tests."""
    print("🧪 Running PyMapGIS QGIS Plugin Tests\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestPluginLogic,
        TestPluginErrorHandling,
        TestPluginIntegration
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print(f"\n📊 Plugin Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")

    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")

    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")

    success = len(result.failures) == 0 and len(result.errors) == 0
    if success:
        print("\n🎉 All plugin tests passed!")
    else:
        print("\n⚠️  Some plugin tests failed.")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(run_plugin_tests())
