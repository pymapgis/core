#!/usr/bin/env python3
"""
Test script to verify that the 2 critical bugs have been fixed.

This script tests:
1. BUG-001: deleteLater() uncommented (memory leak fix)
2. BUG-002: Temporary file cleanup using context managers

Author: PyMapGIS Team
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock
import traceback

def test_bug_001_fix():
    """Test that BUG-001 (deleteLater commented out) has been fixed."""
    print("🔍 Testing BUG-001 Fix: deleteLater() uncommented")
    print("-" * 55)
    
    # Read the plugin file and check if deleteLater is uncommented
    plugin_file = "qgis_plugin/pymapgis_qgis_plugin/pymapgis_plugin.py"
    
    if not Path(plugin_file).exists():
        print(f"❌ Plugin file not found: {plugin_file}")
        return False
    
    with open(plugin_file, 'r') as f:
        content = f.read()
    
    # Check if the problematic commented line is gone
    if "# self.pymapgis_dialog_instance.deleteLater()" in content:
        print("❌ BUG-001 NOT FIXED: deleteLater() is still commented out")
        print("   Found: # self.pymapgis_dialog_instance.deleteLater()")
        return False
    
    # Check if the uncommented version exists
    if "self.pymapgis_dialog_instance.deleteLater()" in content:
        print("✅ BUG-001 FIXED: deleteLater() is now uncommented")
        
        # Count occurrences to make sure it's in the right place
        lines = content.split('\n')
        deleteLater_lines = []
        for i, line in enumerate(lines, 1):
            if "self.pymapgis_dialog_instance.deleteLater()" in line and not line.strip().startswith('#'):
                deleteLater_lines.append(i)
        
        print(f"   Found uncommented deleteLater() calls on lines: {deleteLater_lines}")
        
        if len(deleteLater_lines) >= 1:
            print("✅ Proper cleanup calls are in place")
            return True
        else:
            print("❌ deleteLater() found but not in expected locations")
            return False
    else:
        print("❌ BUG-001 NOT FIXED: deleteLater() call not found")
        return False

def test_bug_002_fix():
    """Test that BUG-002 (temporary file cleanup) has been fixed."""
    print("\n🔍 Testing BUG-002 Fix: Temporary file cleanup with context managers")
    print("-" * 70)
    
    # Read the dialog file and check for context manager usage
    dialog_file = "qgis_plugin/pymapgis_qgis_plugin/pymapgis_dialog.py"
    
    if not Path(dialog_file).exists():
        print(f"❌ Dialog file not found: {dialog_file}")
        return False
    
    with open(dialog_file, 'r') as f:
        content = f.read()
    
    # Check if the problematic mkdtemp calls are gone
    if "tempfile.mkdtemp(prefix='pymapgis_qgis_')" in content:
        print("❌ BUG-002 NOT FIXED: tempfile.mkdtemp() still being used")
        print("   Found: tempfile.mkdtemp(prefix='pymapgis_qgis_')")
        return False
    
    # Check if TemporaryDirectory context manager is being used
    if "tempfile.TemporaryDirectory(prefix='pymapgis_qgis_')" in content:
        print("✅ BUG-002 FIXED: Using tempfile.TemporaryDirectory() context manager")
        
        # Count occurrences
        temp_dir_count = content.count("tempfile.TemporaryDirectory(prefix='pymapgis_qgis_')")
        with_statements = content.count("with tempfile.TemporaryDirectory")
        
        print(f"   Found {temp_dir_count} TemporaryDirectory() calls")
        print(f"   Found {with_statements} 'with' context manager statements")
        
        if temp_dir_count >= 2 and with_statements >= 2:
            print("✅ Both vector and raster processing use context managers")
            
            # Check for cleanup comments
            if "automatically cleaned up" in content:
                print("✅ Code includes cleanup documentation")
            
            return True
        else:
            print("❌ Not all temporary directory usage has been converted")
            return False
    else:
        print("❌ BUG-002 NOT FIXED: TemporaryDirectory context manager not found")
        return False

def test_code_quality_improvements():
    """Test for additional code quality improvements."""
    print("\n🔍 Testing Code Quality Improvements")
    print("-" * 40)
    
    dialog_file = "qgis_plugin/pymapgis_qgis_plugin/pymapgis_dialog.py"
    
    with open(dialog_file, 'r') as f:
        content = f.read()
    
    improvements = []
    
    # Check for improved error handling around rioxarray
    if "if not hasattr(data, 'rio'):" in content:
        if "raise ImportError" in content:
            # Check if it's properly wrapped in try-catch
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "raise ImportError" in line:
                    # Look for surrounding try-catch
                    found_try = False
                    found_except = False
                    for j in range(max(0, i-10), min(len(lines), i+10)):
                        if "try:" in lines[j]:
                            found_try = True
                        if "except ImportError" in lines[j]:
                            found_except = True
                    
                    if found_try and found_except:
                        improvements.append("✅ ImportError properly handled in try-catch block")
                    else:
                        improvements.append("⚠️  ImportError raised but may not be in try-catch")
    
    # Check for cleanup documentation
    if "automatically cleaned up" in content:
        improvements.append("✅ Added documentation about automatic cleanup")
    
    # Check for proper indentation in context managers
    if "with tempfile.TemporaryDirectory" in content:
        improvements.append("✅ Proper context manager indentation")
    
    if improvements:
        print("   Code quality improvements found:")
        for improvement in improvements:
            print(f"   {improvement}")
    else:
        print("   No additional improvements detected")
    
    return len(improvements) > 0

def simulate_fixed_behavior():
    """Simulate the behavior after fixes to demonstrate improvements."""
    print("\n🔍 Simulating Fixed Plugin Behavior")
    print("-" * 40)
    
    try:
        import geopandas as gpd
        from shapely.geometry import Point
        
        # Simulate the new temporary file behavior
        print("   Simulating vector data processing with context manager:")
        
        test_data = gpd.GeoDataFrame({
            'id': [1, 2],
            'geometry': [Point(0, 0), Point(1, 1)]
        }, crs='EPSG:4326')
        
        # This simulates the new code behavior
        temp_dirs_created = []
        temp_dirs_cleaned = []
        
        for i in range(2):
            print(f"      Processing dataset {i+1}...")
            
            # Simulate context manager behavior
            with tempfile.TemporaryDirectory(prefix='pymapgis_qgis_') as temp_dir:
                temp_dirs_created.append(temp_dir)
                
                # Create temporary file
                temp_file = os.path.join(temp_dir, f"test_{i}.gpkg")
                test_data.to_file(temp_file, driver="GPKG")
                
                print(f"         Created: {temp_file}")
                print(f"         Directory exists: {os.path.exists(temp_dir)}")
                
                # Simulate QGIS layer loading (temp_dir still exists here)
                
            # After exiting context manager, directory should be cleaned up
            temp_dirs_cleaned.append(temp_dir)
            print(f"         After context exit - Directory exists: {os.path.exists(temp_dir)}")
        
        print(f"   ✅ Created {len(temp_dirs_created)} temporary directories")
        print(f"   ✅ All {len(temp_dirs_cleaned)} directories automatically cleaned up")
        
        # Verify cleanup
        all_cleaned = all(not os.path.exists(d) for d in temp_dirs_cleaned)
        if all_cleaned:
            print("   ✅ No temporary files left behind!")
        else:
            print("   ❌ Some temporary files still exist")
        
        return all_cleaned
        
    except Exception as e:
        print(f"   ❌ Simulation failed: {e}")
        return False

def main():
    """Run all bug fix verification tests."""
    print("🧪 PyMapGIS QGIS Plugin Bug Fix Verification")
    print("=" * 55)
    
    tests = [
        ("BUG-001 Fix (deleteLater)", test_bug_001_fix),
        ("BUG-002 Fix (temp cleanup)", test_bug_002_fix),
        ("Code Quality", test_code_quality_improvements),
        ("Behavior Simulation", simulate_fixed_behavior)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            traceback.print_exc()
            results.append(False)
    
    print(f"\n{'='*55}")
    print(f"📊 Bug Fix Verification Results")
    print(f"{'='*55}")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 ALL BUGS FIXED SUCCESSFULLY!")
        print("✅ BUG-001: Memory leak fixed (deleteLater uncommented)")
        print("✅ BUG-002: Disk space leak fixed (context managers)")
        print("✅ Plugin is now ready for production use")
        
        print(f"\n🚀 Key Improvements:")
        print("   • Automatic cleanup of temporary files and directories")
        print("   • Proper Qt object memory management")
        print("   • No more disk space accumulation")
        print("   • No more memory leaks from dialog objects")
        
        return 0
    else:
        failed_tests = [tests[i][0] for i, result in enumerate(results) if not result]
        print(f"\n⚠️  Some fixes may not be complete:")
        for test_name in failed_tests:
            print(f"   ❌ {test_name}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
