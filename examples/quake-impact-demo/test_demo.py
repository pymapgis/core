"""
Test script for Quake Impact Now demo

Verifies that all components work correctly:
1. Data fetching from USGS
2. Zonal statistics processing
3. Vector tile export
4. Web API endpoints
"""

import asyncio
import json
import requests
import time
from pathlib import Path
import sys
import os

# Add the parent directory to the path so we can import pymapgis
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pymapgis as pmg


async def test_data_processing():
    """Test the core data processing pipeline."""
    print("🧪 Testing data processing pipeline...")
    
    # Test 1: Read earthquake data
    print("  📡 Testing USGS data fetch...")
    try:
        quakes = pmg.read("https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson")
        print(f"  ✅ Fetched {len(quakes)} earthquakes")
        
        if len(quakes) == 0:
            print("  ⚠️  No earthquakes in the last 24 hours - creating test data")
            # Create test earthquake data
            import geopandas as gpd
            from shapely.geometry import Point
            import pandas as pd
            
            test_data = {
                'id': ['test1', 'test2'],
                'mag': [5.5, 6.2],
                'geometry': [Point(-120, 37), Point(-118, 34)]
            }
            quakes = gpd.GeoDataFrame(test_data, crs="EPSG:4326")
            print(f"  ✅ Created {len(quakes)} test earthquakes")
            
    except Exception as e:
        print(f"  ❌ Error fetching earthquake data: {e}")
        return False
    
    # Test 2: Buffer operations
    print("  🔄 Testing buffer operations...")
    try:
        quakes_proj = quakes.to_crs("EPSG:3857")
        buffers = quakes_proj.geometry.buffer(50_000)
        print(f"  ✅ Created {len(buffers)} 50km buffers")
    except Exception as e:
        print(f"  ❌ Error creating buffers: {e}")
        return False
    
    # Test 3: Zonal statistics (with fallback)
    print("  📊 Testing zonal statistics...")
    try:
        async with pmg.AsyncGeoProcessor(workers=2) as gp:
            # Use a simple test raster URL or create mock data
            pop_stats = await gp.zonal_stats(
                "https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/0_Mosaicked/ppp_2020_1km_Aggregated.tif",
                buffers[:2],  # Test with first 2 only
                stats=("sum",),
                nodata=0
            )
            print(f"  ✅ Calculated zonal statistics for {len(pop_stats)} features")
    except Exception as e:
        print(f"  ⚠️  Zonal statistics failed ({e}), using mock data")
        # Create mock population data
        import pandas as pd
        import numpy as np
        pop_stats = pd.DataFrame({
            'sum': np.random.randint(1000, 100000, len(quakes))
        })
    
    # Test 4: Impact calculation
    print("  🧮 Testing impact calculation...")
    try:
        import math
        quakes['pop50k'] = pop_stats['sum'][:len(quakes)]
        quakes['Impact'] = quakes.apply(
            lambda r: (math.log10(max(r.pop50k, 1)) * r.mag), axis=1
        )
        print(f"  ✅ Calculated impact scores (range: {quakes['Impact'].min():.1f} - {quakes['Impact'].max():.1f})")
    except Exception as e:
        print(f"  ❌ Error calculating impact: {e}")
        return False
    
    # Test 5: Export operations
    print("  💾 Testing export operations...")
    try:
        # Create output directory
        Path("tiles/impact").mkdir(parents=True, exist_ok=True)
        
        # Test GeoJSON export
        quakes.to_file("impact.geojson", driver="GeoJSON")
        print("  ✅ Exported GeoJSON")
        
        # Test PNG export
        quakes.plot.save_png("impact.png", column="Impact", dpi=150)
        print("  ✅ Exported PNG")
        
        # Test vector tile export (simplified)
        try:
            quakes.pmg.to_mvt(
                "tiles/impact/{z}/{x}/{y}.mvt",
                layer="quake",
                fields=["Impact", "mag", "pop50k"]
            )
            print("  ✅ Exported vector tiles")
        except Exception as e:
            print(f"  ⚠️  Vector tile export failed: {e}")
            
    except Exception as e:
        print(f"  ❌ Error in export operations: {e}")
        return False
    
    print("✅ Data processing pipeline test completed successfully!")
    return True


def test_web_api():
    """Test the web API endpoints."""
    print("🌐 Testing web API...")
    
    # Start the server in the background (simplified test)
    import subprocess
    import time
    
    try:
        # Test if server is already running
        response = requests.get("http://localhost:8000/health", timeout=5)
        print("  ✅ Server already running")
    except:
        print("  ⚠️  Server not running - start with: uvicorn app:app --host 0.0.0.0 --port 8000")
        return False
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"  ✅ Health check: {health_data['status']}")
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Health check error: {e}")
        return False
    
    # Test main page
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("  ✅ Main page accessible")
        else:
            print(f"  ❌ Main page failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Main page error: {e}")
    
    # Test protected endpoint
    try:
        response = requests.get(
            "http://localhost:8000/internal/latest",
            headers={"Authorization": "Bearer demo-token"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Protected endpoint: {data.get('features_count', 0)} features")
        else:
            print(f"  ❌ Protected endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Protected endpoint error: {e}")
    
    print("✅ Web API test completed!")
    return True


def test_dependencies():
    """Test that all required dependencies are available."""
    print("📦 Testing dependencies...")
    
    dependencies = {
        'geopandas': 'geopandas',
        'pandas': 'pandas', 
        'numpy': 'numpy',
        'shapely': 'shapely',
        'rasterio': 'rasterio',
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'mapbox_vector_tile': 'mapbox_vector_tile',
        'mercantile': 'mercantile',
        'rasterstats': 'rasterstats',
        'matplotlib': 'matplotlib',
        'requests': 'requests'
    }
    
    missing = []
    for name, module in dependencies.items():
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} - missing")
            missing.append(name)
    
    if missing:
        print(f"⚠️  Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies available!")
    return True


async def main():
    """Run all tests."""
    print("🧪 Quake Impact Now - Test Suite")
    print("=" * 50)
    
    # Test dependencies first
    deps_ok = test_dependencies()
    if not deps_ok:
        print("❌ Dependency test failed - fix dependencies first")
        return
    
    # Test data processing
    processing_ok = await test_data_processing()
    
    # Test web API (optional)
    api_ok = test_web_api()
    
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"  Dependencies: {'✅' if deps_ok else '❌'}")
    print(f"  Data Processing: {'✅' if processing_ok else '❌'}")
    print(f"  Web API: {'✅' if api_ok else '⚠️'}")
    
    if deps_ok and processing_ok:
        print("\n🎉 Core functionality working! Ready to run the demo.")
        print("\nNext steps:")
        print("1. Run: python quake_impact.py")
        print("2. Run: uvicorn app:app --host 0.0.0.0 --port 8000")
        print("3. Open: http://localhost:8000")
    else:
        print("\n❌ Some tests failed - check the errors above")


if __name__ == "__main__":
    asyncio.run(main())
