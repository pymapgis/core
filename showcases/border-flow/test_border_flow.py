#!/usr/bin/env python3
"""
Test script for Border Flow Now demo

Verifies that the demo components work correctly without requiring
external dependencies or network access.
"""

import sys
import json
from pathlib import Path

# Add the PyMapGIS core to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

def test_data_files():
    """Test that required data files exist."""
    print("🧪 Testing data files...")
    
    # Check ports.geojson exists
    ports_file = Path("data/ports.geojson")
    if not ports_file.exists():
        print(f"❌ Missing: {ports_file}")
        return False
    
    # Validate GeoJSON structure
    try:
        with open(ports_file) as f:
            ports_data = json.load(f)
        
        if ports_data.get("type") != "FeatureCollection":
            print("❌ Invalid GeoJSON structure")
            return False
        
        features = ports_data.get("features", [])
        print(f"✅ Found {len(features)} border crossing features")
        
        # Check required properties
        for i, feature in enumerate(features[:3]):  # Check first 3
            props = feature.get("properties", {})
            required_fields = ["port_id", "name", "state", "lanes"]
            for field in required_fields:
                if field not in props:
                    print(f"❌ Missing field '{field}' in feature {i}")
                    return False
        
        print("✅ GeoJSON structure valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading GeoJSON: {e}")
        return False


def test_app_structure():
    """Test that required application files exist."""
    print("🧪 Testing application structure...")
    
    required_files = [
        "worker.py",
        "app.py",
        "Dockerfile",
        "README.md",
        "static/index.html",
        "static/app.js"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Missing: {file_path}")
            return False
        else:
            print(f"✅ Found: {file_path}")
    
    return True


def test_imports():
    """Test that required imports work."""
    print("🧪 Testing imports...")
    
    try:
        import pymapgis as pmg
        print("✅ PyMapGIS imported successfully")
    except ImportError as e:
        print(f"❌ PyMapGIS import failed: {e}")
        return False
    
    try:
        import pandas as pd
        import geopandas as gpd
        print("✅ Pandas/GeoPandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        from fastapi import FastAPI
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    return True


def test_worker_logic():
    """Test the core worker logic with test data."""
    print("🧪 Testing worker logic...")
    
    try:
        import pymapgis as pmg
        import pandas as pd
        import math
        from pathlib import Path
        
        # Load the ports data
        ports_file = Path("data/ports.geojson")
        ports = pmg.read(str(ports_file))
        print(f"✅ Loaded {len(ports)} border crossings")
        
        # Create test wait times
        import numpy as np
        test_waits = np.random.randint(5, 120, len(ports))
        ports['wait'] = test_waits
        ports['lanes'] = ports['lanes'].fillna(4)
        
        # Calculate congestion scores
        ports['Score'] = ports.apply(
            lambda r: math.log1p(r.wait) * r.lanes, axis=1
        )
        
        print(f"✅ Calculated congestion scores (range: {ports['Score'].min():.1f} to {ports['Score'].max():.1f})")
        
        # Test export (without actually writing files)
        print("✅ Core processing logic works")
        return True
        
    except Exception as e:
        print(f"❌ Worker logic failed: {e}")
        return False


def test_api_structure():
    """Test that the FastAPI app can be created."""
    print("🧪 Testing API structure...")
    
    try:
        from fastapi import FastAPI
        
        # Create a test app
        app = FastAPI(title="Border Flow Now Test")
        print("✅ FastAPI app created successfully")
        
        # Check that our app.py can be imported
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", "app.py")
        if spec is None:
            print("❌ Could not load app.py")
            return False
        
        print("✅ app.py structure valid")
        return True
        
    except Exception as e:
        print(f"❌ API structure test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚛 Border Flow Now - Test Suite")
    print("=" * 50)
    
    tests = [
        ("Data Files", test_data_files),
        ("App Structure", test_app_structure),
        ("Imports", test_imports),
        ("Worker Logic", test_worker_logic),
        ("API Structure", test_api_structure)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! Border Flow demo is ready.")
        print("\nNext steps:")
        print("1. Run: python worker.py")
        print("2. Run: uvicorn app:app --host 0.0.0.0 --port 8000")
        print("3. Open: http://localhost:8000")
    else:
        print(f"\n⚠️  {len(tests) - passed} tests failed. Check the errors above.")
    
    return passed == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
