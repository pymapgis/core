#!/usr/bin/env python3
"""
Test script for the Arkansas Counties QGIS example.
This validates that the example works correctly and produces expected outputs.
"""

import sys
import os
from pathlib import Path
import geopandas as gpd

# Add PyMapGIS to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_data_files():
    """Test that all expected data files were created."""
    print("🧪 Testing data files...")
    
    data_dir = Path(__file__).parent / "data"
    
    expected_files = [
        "arkansas_counties.gpkg",
        "arkansas_counties_analysis.png", 
        "arkansas_counties_interactive.html",
        "tl_2023_us_county.shp",
        "tl_2023_us_county.dbf",
        "tl_2023_us_county.shx",
        "tl_2023_us_county.prj"
    ]
    
    missing_files = []
    for filename in expected_files:
        filepath = data_dir / filename
        if not filepath.exists():
            missing_files.append(filename)
        else:
            print(f"   ✅ {filename}")
    
    if missing_files:
        print(f"   ❌ Missing files: {missing_files}")
        return False
    
    print("   ✅ All expected files present")
    return True

def test_arkansas_counties_data():
    """Test the Arkansas counties GeoPackage."""
    print("\n🧪 Testing Arkansas counties data...")
    
    data_dir = Path(__file__).parent / "data"
    gpkg_path = data_dir / "arkansas_counties.gpkg"
    
    if not gpkg_path.exists():
        print("   ❌ Arkansas counties GeoPackage not found")
        return False
    
    try:
        # Load the data
        gdf = gpd.read_file(gpkg_path)
        
        # Test basic properties
        print(f"   📊 Counties loaded: {len(gdf)}")
        print(f"   📊 CRS: {gdf.crs}")
        print(f"   📊 Columns: {list(gdf.columns)}")
        
        # Validate Arkansas data
        if len(gdf) != 75:
            print(f"   ⚠️  Expected 75 counties, got {len(gdf)}")
        else:
            print("   ✅ Correct number of Arkansas counties (75)")
        
        # Check for required columns
        required_columns = ['NAME', 'STATEFP', 'geometry']
        missing_columns = [col for col in required_columns if col not in gdf.columns]
        
        if missing_columns:
            print(f"   ❌ Missing columns: {missing_columns}")
            return False
        else:
            print("   ✅ All required columns present")
        
        # Check that all counties are in Arkansas (STATEFP = '05')
        non_arkansas = gdf[gdf['STATEFP'] != '05']
        if len(non_arkansas) > 0:
            print(f"   ❌ Found {len(non_arkansas)} non-Arkansas counties")
            return False
        else:
            print("   ✅ All counties are in Arkansas")
        
        # Check geometry validity
        invalid_geom = gdf[~gdf.geometry.is_valid]
        if len(invalid_geom) > 0:
            print(f"   ⚠️  Found {len(invalid_geom)} invalid geometries")
        else:
            print("   ✅ All geometries are valid")
        
        # Sample some county names
        sample_counties = gdf['NAME'].head(5).tolist()
        print(f"   📍 Sample counties: {', '.join(sample_counties)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error loading Arkansas counties data: {e}")
        return False

def test_visualization_files():
    """Test that visualization files are valid."""
    print("\n🧪 Testing visualization files...")
    
    data_dir = Path(__file__).parent / "data"
    
    # Test PNG file
    png_path = data_dir / "arkansas_counties_analysis.png"
    if png_path.exists():
        file_size = png_path.stat().st_size
        if file_size > 1000:  # Should be at least 1KB for a real plot
            print(f"   ✅ Analysis plot created ({file_size:,} bytes)")
        else:
            print(f"   ⚠️  Analysis plot seems too small ({file_size} bytes)")
    else:
        print("   ❌ Analysis plot not found")
        return False
    
    # Test HTML file
    html_path = data_dir / "arkansas_counties_interactive.html"
    if html_path.exists():
        file_size = html_path.stat().st_size
        if file_size > 1000:  # Should be at least 1KB for a real map
            print(f"   ✅ Interactive map created ({file_size:,} bytes)")
            
            # Check if it contains expected HTML content
            with open(html_path, 'r') as f:
                content = f.read()
                if 'folium' in content.lower() or 'leaflet' in content.lower():
                    print("   ✅ Interactive map contains mapping library")
                else:
                    print("   ⚠️  Interactive map may not contain expected mapping content")
        else:
            print(f"   ⚠️  Interactive map seems too small ({file_size} bytes)")
    else:
        print("   ❌ Interactive map not found")
        return False
    
    return True

def test_pymapgis_integration():
    """Test PyMapGIS integration."""
    print("\n🧪 Testing PyMapGIS integration...")
    
    try:
        import pymapgis as pmg
        print("   ✅ PyMapGIS imported successfully")
        
        # Test reading the Arkansas counties with PyMapGIS
        data_dir = Path(__file__).parent / "data"
        gpkg_path = data_dir / "arkansas_counties.gpkg"
        
        arkansas_data = pmg.read(str(gpkg_path))
        print(f"   ✅ PyMapGIS can read Arkansas counties ({len(arkansas_data)} features)")
        
        # Test that it's a GeoDataFrame
        if isinstance(arkansas_data, gpd.GeoDataFrame):
            print("   ✅ Data is a GeoDataFrame")
        else:
            print(f"   ❌ Expected GeoDataFrame, got {type(arkansas_data)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ PyMapGIS integration test failed: {e}")
        return False

def test_qgis_script_structure():
    """Test that the QGIS script has proper structure."""
    print("\n🧪 Testing QGIS script structure...")
    
    qgis_script = Path(__file__).parent / "create_qgis_project.py"
    
    if not qgis_script.exists():
        print("   ❌ QGIS script not found")
        return False
    
    # Read the script and check for key components
    with open(qgis_script, 'r') as f:
        content = f.read()
    
    required_components = [
        'QgsApplication',
        'QgsVectorLayer', 
        'QgsProject',
        'arkansas_counties.gpkg',
        'def main(',
        'if __name__ == "__main__"'
    ]
    
    missing_components = []
    for component in required_components:
        if component not in content:
            missing_components.append(component)
    
    if missing_components:
        print(f"   ❌ Missing components: {missing_components}")
        return False
    else:
        print("   ✅ QGIS script has all required components")
    
    return True

def main():
    """Run all tests."""
    print("🧪 Arkansas Counties QGIS Example - Test Suite")
    print("=" * 55)
    
    tests = [
        test_data_files,
        test_arkansas_counties_data,
        test_visualization_files,
        test_pymapgis_integration,
        test_qgis_script_structure
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    print(f"\n📊 Test Results")
    print("=" * 20)
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tests passed! The Arkansas Counties example is working correctly.")
        print("\n✅ The example demonstrates:")
        print("   • PyMapGIS data loading and processing")
        print("   • Geospatial analysis and visualization")
        print("   • QGIS integration preparation")
        print("   • Interactive mapping capabilities")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
