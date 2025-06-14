#!/usr/bin/env python3
"""
Test script for PyMapGIS async processing functionality.
"""

import asyncio
import tempfile
import pandas as pd
import numpy as np
from pathlib import Path
import time

def create_test_data():
    """Create test CSV data for async processing."""
    print("Creating test data...")
    
    # Create a moderately large dataset
    n_rows = 100000
    data = {
        'id': range(n_rows),
        'x': np.random.uniform(-180, 180, n_rows),
        'y': np.random.uniform(-90, 90, n_rows),
        'population': np.random.randint(100, 100000, n_rows),
        'area_km2': np.random.uniform(1, 1000, n_rows),
        'category': np.random.choice(['urban', 'suburban', 'rural'], n_rows)
    }
    
    df = pd.DataFrame(data)
    
    # Save to temporary file
    temp_file = Path(tempfile.gettempdir()) / "test_async_data.csv"
    df.to_csv(temp_file, index=False)
    
    print(f"Created test data: {len(df)} rows at {temp_file}")
    return temp_file

async def test_async_processing():
    """Test async processing functionality."""
    print("Testing PyMapGIS async processing...")
    
    try:
        # Import async processing
        from pymapgis.async_processing import (
            AsyncGeoProcessor,
            async_process_in_chunks,
            PerformanceMonitor
        )
        print("✅ Async processing module imported successfully")
        
        # Create test data
        test_file = create_test_data()
        
        # Define a simple processing function
        def calculate_density(chunk):
            """Calculate population density."""
            chunk['density'] = chunk['population'] / chunk['area_km2']
            return chunk[chunk['density'] > 50]  # Filter high-density areas
        
        # Test 1: Basic async processing
        print("\n--- Test 1: Basic Async Processing ---")
        start_time = time.time()
        
        result = await async_process_in_chunks(
            filepath=test_file,
            operation=calculate_density,
            chunk_size=10000,
            show_progress=True
        )
        
        duration = time.time() - start_time
        print(f"✅ Processed {len(result)} high-density areas in {duration:.2f}s")
        
        # Test 2: Performance monitoring
        print("\n--- Test 2: Performance Monitoring ---")
        monitor = PerformanceMonitor("Density Calculation")
        monitor.start()
        
        # Simulate some processing
        for i in range(5):
            monitor.update(items=1000, bytes_count=50000)
            await asyncio.sleep(0.1)  # Simulate work
        
        stats = monitor.finish()
        print(f"✅ Performance monitoring: {stats['items_per_second']:.1f} items/s")
        
        # Test 3: Parallel operations
        print("\n--- Test 3: Parallel Operations ---")
        
        # Create multiple small datasets
        test_items = [f"item_{i}" for i in range(10)]
        
        def simple_operation(item):
            """Simple operation for parallel testing."""
            time.sleep(0.1)  # Simulate work
            return f"processed_{item}"
        
        from pymapgis.async_processing import parallel_geo_operations
        
        start_time = time.time()
        results = await parallel_geo_operations(
            data_items=test_items,
            operation=simple_operation,
            max_workers=4
        )
        duration = time.time() - start_time
        
        print(f"✅ Parallel processing: {len(results)} items in {duration:.2f}s")
        
        # Clean up
        test_file.unlink()
        
        print("\n🎉 All async processing tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_basic_import():
    """Test basic PyMapGIS import with async functions."""
    print("Testing basic PyMapGIS import...")
    
    try:
        import pymapgis as pmg
        print(f"✅ PyMapGIS imported, version: {pmg.__version__}")
        
        # Test if async functions are available
        async_functions = [
            'AsyncGeoProcessor',
            'async_read_large_file', 
            'async_process_in_chunks',
            'parallel_geo_operations'
        ]
        
        for func_name in async_functions:
            if hasattr(pmg, func_name):
                print(f"✅ {func_name} available")
            else:
                print(f"❌ {func_name} not available")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("PyMapGIS Async Processing Test Suite")
    print("=" * 50)
    
    # Test basic imports
    import_ok = await test_basic_import()
    
    if import_ok:
        # Test async processing functionality
        async_ok = await test_async_processing()
        
        print("\n" + "=" * 50)
        print("Test Summary:")
        print(f"Basic imports: {'✅ PASSED' if import_ok else '❌ FAILED'}")
        print(f"Async processing: {'✅ PASSED' if async_ok else '❌ FAILED'}")
        
        if import_ok and async_ok:
            print("\n🎉 All tests passed! Async processing is ready for use.")
            return 0
        else:
            print("\n❌ Some tests failed.")
            return 1
    else:
        print("\n❌ Basic import test failed.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
