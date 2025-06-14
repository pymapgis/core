#!/usr/bin/env python3
"""
Debug script to identify import issues in PyMapGIS.
"""

import sys
import time

def test_import(module_name, description=""):
    """Test importing a module with timeout."""
    print(f"Testing {module_name}... {description}")
    start_time = time.time()
    try:
        if module_name == "pymapgis":
            import pymapgis
            print(f"✅ {module_name} imported successfully in {time.time() - start_time:.2f}s")
            return True
        elif module_name == "pymapgis.cache":
            from pymapgis.cache import stats
            print(f"✅ {module_name} imported successfully in {time.time() - start_time:.2f}s")
            return True
        elif module_name == "pymapgis.io":
            from pymapgis.io import read
            print(f"✅ {module_name} imported successfully in {time.time() - start_time:.2f}s")
            return True
        elif module_name == "pymapgis.serve":
            from pymapgis.serve import serve
            print(f"✅ {module_name} imported successfully in {time.time() - start_time:.2f}s")
            return True
        elif module_name == "pymapgis.vector":
            from pymapgis.vector import buffer
            print(f"✅ {module_name} imported successfully in {time.time() - start_time:.2f}s")
            return True
        elif module_name == "pymapgis.raster":
            from pymapgis.raster import reproject
            print(f"✅ {module_name} imported successfully in {time.time() - start_time:.2f}s")
            return True
        elif module_name == "pymapgis.viz":
            from pymapgis.viz import explore
            print(f"✅ {module_name} imported successfully in {time.time() - start_time:.2f}s")
            return True
        elif module_name == "pymapgis.cli":
            from pymapgis.cli import app
            print(f"✅ {module_name} imported successfully in {time.time() - start_time:.2f}s")
            return True
        else:
            exec(f"import {module_name}")
            print(f"✅ {module_name} imported successfully in {time.time() - start_time:.2f}s")
            return True
    except Exception as e:
        print(f"❌ {module_name} failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("PyMapGIS Import Debug Test")
    print("=" * 50)
    
    # Test basic dependencies first
    modules_to_test = [
        ("geopandas", "Core geospatial library"),
        ("xarray", "Array processing library"),
        ("rioxarray", "Raster I/O library"),
        ("fastapi", "Web framework"),
        ("typer", "CLI framework"),
        ("requests_cache", "HTTP caching"),
        ("fsspec", "File system abstraction"),
        ("pymapgis.settings", "Settings module"),
        ("pymapgis.cache", "Cache module"),
        ("pymapgis.io", "IO module"),
        ("pymapgis.vector", "Vector module"),
        ("pymapgis.raster", "Raster module"),
        ("pymapgis.viz", "Visualization module"),
        ("pymapgis.serve", "Serve module"),
        ("pymapgis.cli", "CLI module"),
        ("pymapgis", "Main package"),
    ]
    
    results = {}
    for module, desc in modules_to_test:
        results[module] = test_import(module, desc)
        print()
    
    print("Summary:")
    print("=" * 50)
    for module, success in results.items():
        status = "✅ OK" if success else "❌ FAILED"
        print(f"{module:25} {status}")

if __name__ == "__main__":
    main()
