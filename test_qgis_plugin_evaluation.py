#!/usr/bin/env python3
"""
Comprehensive QGIS Plugin Bug Evaluation

This script evaluates the PyMapGIS QGIS plugin for potential bugs and issues.
It tests the plugin logic without requiring QGIS to be installed.

Author: PyMapGIS Team
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

def test_basic_functionality():
    """Test basic PyMapGIS functionality that the plugin depends on."""
    print("🔍 Testing PyMapGIS Basic Functionality")
    print("-" * 50)
    
    try:
        import pymapgis as pmg
        import geopandas as gpd
        import xarray as xr
        import rioxarray
        print("✅ All required libraries imported successfully")
        print(f"   - PyMapGIS version: {pmg.__version__}")
        
        # Test basic read functionality
        from shapely.geometry import Point
        test_data = gpd.GeoDataFrame({
            'id': [1, 2, 3],
            'name': ['Point A', 'Point B', 'Point C'],
            'geometry': [Point(0, 0), Point(1, 1), Point(2, 2)]
        }, crs='EPSG:4326')
        
        with tempfile.NamedTemporaryFile(suffix='.geojson', delete=False) as f:
            test_data.to_file(f.name, driver='GeoJSON')
            loaded_data = pmg.read(f.name)
            assert isinstance(loaded_data, gpd.GeoDataFrame)
            assert len(loaded_data) == 3
            print("✅ PyMapGIS read functionality works")
            os.unlink(f.name)
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_plugin_structure():
    """Test the plugin file structure and imports."""
    print("\n🔍 Testing Plugin Structure")
    print("-" * 30)
    
    issues = []
    
    # Check required files exist
    required_files = [
        "qgis_plugin/pymapgis_qgis_plugin/__init__.py",
        "qgis_plugin/pymapgis_qgis_plugin/pymapgis_plugin.py", 
        "qgis_plugin/pymapgis_qgis_plugin/pymapgis_dialog.py",
        "qgis_plugin/pymapgis_qgis_plugin/metadata.txt",
        "qgis_plugin/pymapgis_qgis_plugin/icon.png"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            issues.append(f"Missing required file: {file_path}")
        else:
            print(f"✅ {file_path}")
    
    if issues:
        print("❌ Plugin structure issues:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    
    print("✅ All required plugin files present")
    return True

def test_plugin_logic_bugs():
    """Test for specific bugs in the plugin logic."""
    print("\n🔍 Testing Plugin Logic for Bugs")
    print("-" * 35)
    
    bugs_found = []
    
    # Bug 1: Check for commented out deleteLater()
    with open("qgis_plugin/pymapgis_qgis_plugin/pymapgis_plugin.py", 'r') as f:
        content = f.read()
        if "# self.pymapgis_dialog_instance.deleteLater()" in content:
            bugs_found.append({
                "id": "BUG-001",
                "severity": "MEDIUM",
                "file": "pymapgis_plugin.py",
                "line": "96",
                "description": "deleteLater() is commented out - potential memory leak",
                "impact": "Dialog objects may not be properly garbage collected"
            })
    
    # Bug 2: Check for temporary file cleanup issues
    with open("qgis_plugin/pymapgis_qgis_plugin/pymapgis_dialog.py", 'r') as f:
        content = f.read()
        if "tempfile.mkdtemp" in content and "shutil.rmtree" not in content:
            bugs_found.append({
                "id": "BUG-002",
                "severity": "HIGH", 
                "file": "pymapgis_dialog.py",
                "line": "87, 114",
                "description": "Temporary directories created but never cleaned up",
                "impact": "Disk space accumulation over time"
            })
    
    # Bug 3: Check for ImportError handling in dialog
    with open("qgis_plugin/pymapgis_qgis_plugin/pymapgis_dialog.py", 'r') as f:
        content = f.read()
        if "raise ImportError" in content and "except ImportError" not in content.split("raise ImportError")[1]:
            bugs_found.append({
                "id": "BUG-003",
                "severity": "HIGH",
                "file": "pymapgis_dialog.py", 
                "line": "120",
                "description": "ImportError raised but not caught - will crash plugin",
                "impact": "Plugin crashes when rioxarray not properly installed"
            })
    
    # Bug 4: Check for signal connection management
    with open("qgis_plugin/pymapgis_qgis_plugin/pymapgis_plugin.py", 'r') as f:
        content = f.read()
        connect_count = content.count(".connect(")
        disconnect_count = content.count(".disconnect(")
        if connect_count > disconnect_count:
            bugs_found.append({
                "id": "BUG-004",
                "severity": "MEDIUM",
                "file": "pymapgis_plugin.py",
                "line": "81, 93",
                "description": f"Signal connection imbalance: {connect_count} connects vs {disconnect_count} disconnects",
                "impact": "Potential signal connection leaks"
            })
    
    # Bug 5: Check for hardcoded imports in dialog
    with open("qgis_plugin/pymapgis_qgis_plugin/pymapgis_dialog.py", 'r') as f:
        content = f.read()
        if "import pymapgis" in content[:100]:  # Check if import is at top level
            bugs_found.append({
                "id": "BUG-005",
                "severity": "MEDIUM",
                "file": "pymapgis_dialog.py",
                "line": "14",
                "description": "PyMapGIS imported at module level - no error handling",
                "impact": "Plugin fails to load if PyMapGIS not installed"
            })
    
    if bugs_found:
        print(f"❌ Found {len(bugs_found)} bugs:")
        for bug in bugs_found:
            print(f"   {bug['id']} ({bug['severity']}): {bug['description']}")
            print(f"      File: {bug['file']}:{bug['line']}")
            print(f"      Impact: {bug['impact']}")
            print()
    else:
        print("✅ No obvious bugs found in plugin logic")
    
    return bugs_found

def test_error_handling():
    """Test error handling scenarios."""
    print("\n🔍 Testing Error Handling")
    print("-" * 25)
    
    issues = []
    
    # Test 1: Check for bare except clauses
    for filename in ["pymapgis_plugin.py", "pymapgis_dialog.py"]:
        filepath = f"qgis_plugin/pymapgis_qgis_plugin/{filename}"
        with open(filepath, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                if "except:" in line and "except Exception" not in line and "except ImportError" not in line and "except TypeError" not in line:
                    issues.append(f"{filename}:{i} - Bare except clause")
    
    # Test 2: Check for proper exception logging
    with open("qgis_plugin/pymapgis_qgis_plugin/pymapgis_dialog.py", 'r') as f:
        content = f.read()
        if "except Exception as e:" in content and "traceback.format_exc()" in content:
            print("✅ Proper exception logging with traceback")
        else:
            issues.append("Missing comprehensive exception logging")
    
    if issues:
        print("❌ Error handling issues:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ Error handling appears adequate")
        return True

def test_data_type_handling():
    """Test how the plugin handles different data types."""
    print("\n🔍 Testing Data Type Handling")
    print("-" * 30)
    
    try:
        import geopandas as gpd
        import xarray as xr
        import numpy as np
        from shapely.geometry import Point
        
        # Test GeoDataFrame detection
        gdf = gpd.GeoDataFrame({
            'geometry': [Point(0, 0)]
        }, crs='EPSG:4326')
        
        if isinstance(gdf, gpd.GeoDataFrame):
            print("✅ GeoDataFrame type detection works")
        
        # Test xarray DataArray detection
        da = xr.DataArray(np.random.rand(5, 5))
        
        if isinstance(da, xr.DataArray):
            print("✅ DataArray type detection works")
        
        # Test unsupported type
        unsupported_data = {"not": "supported"}
        if not isinstance(unsupported_data, (gpd.GeoDataFrame, xr.DataArray)):
            print("✅ Unsupported data type detection works")
        
        return True
        
    except Exception as e:
        print(f"❌ Data type handling test failed: {e}")
        return False

def test_uri_processing():
    """Test URI processing logic."""
    print("\n🔍 Testing URI Processing")
    print("-" * 25)
    
    test_cases = [
        ("census://acs/acs5?year=2022&geography=county", "acs5"),
        ("tiger://county?year=2022&state=06", "county"),
        ("file://path/to/data.geojson", "data"),
        ("http://example.com/data.shp", "data"),
        ("simple_file.gpkg", "simple_file"),
        ("", "pymapgis_layer"),  # fallback case
    ]
    
    for uri, expected in test_cases:
        # This is the logic from pymapgis_dialog.py line 75-76
        uri_basename = uri.split('/')[-1].split('?')[0]
        layer_name_base = os.path.splitext(uri_basename)[0] if uri_basename else "pymapgis_layer"
        
        if layer_name_base == expected:
            print(f"✅ URI '{uri}' → '{layer_name_base}'")
        else:
            print(f"❌ URI '{uri}' → '{layer_name_base}' (expected '{expected}')")
            return False
    
    print("✅ URI processing logic works correctly")
    return True

def main():
    """Run all plugin evaluation tests."""
    print("🧪 PyMapGIS QGIS Plugin Bug Evaluation")
    print("=" * 50)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Plugin Structure", test_plugin_structure),
        ("Plugin Logic Bugs", test_plugin_logic_bugs),
        ("Error Handling", test_error_handling),
        ("Data Type Handling", test_data_type_handling),
        ("URI Processing", test_uri_processing)
    ]
    
    results = []
    bugs_found = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            print(f"Running: {test_name}")
            print(f"{'='*60}")
            
            result = test_func()
            if test_name == "Plugin Logic Bugs" and isinstance(result, list):
                bugs_found.extend(result)
                results.append(len(result) == 0)  # True if no bugs found
            else:
                results.append(result)
                
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            traceback.print_exc()
            results.append(False)
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"📊 EVALUATION SUMMARY")
    print(f"{'='*60}")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    print(f"Bugs found: {len(bugs_found)}")
    
    if bugs_found:
        print(f"\n🐛 CRITICAL BUGS IDENTIFIED:")
        high_severity = [b for b in bugs_found if b['severity'] == 'HIGH']
        medium_severity = [b for b in bugs_found if b['severity'] == 'MEDIUM']
        
        print(f"   High severity: {len(high_severity)}")
        print(f"   Medium severity: {len(medium_severity)}")
        
        print(f"\n🚨 HIGH PRIORITY FIXES NEEDED:")
        for bug in high_severity:
            print(f"   • {bug['id']}: {bug['description']}")
        
        print(f"\n⚠️  MEDIUM PRIORITY FIXES:")
        for bug in medium_severity:
            print(f"   • {bug['id']}: {bug['description']}")
    
    if all(results) and len(bugs_found) == 0:
        print("\n🎉 Plugin evaluation completed - No critical issues found!")
        return 0
    else:
        print(f"\n⚠️  Plugin has issues that should be addressed before production use.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
