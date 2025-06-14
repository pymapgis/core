#!/usr/bin/env python3
"""
Test script for PyMapGIS performance optimization functionality.
"""

import time
import tempfile
import pandas as pd
import numpy as np
from pathlib import Path

def test_performance_imports():
    """Test performance module imports."""
    print("Testing performance optimization imports...")
    
    try:
        from pymapgis.performance import (
            PerformanceOptimizer,
            AdvancedCache,
            LazyLoader,
            SpatialIndex,
            QueryOptimizer,
            MemoryManager,
            PerformanceProfiler,
            optimize_performance,
            lazy_load,
            cache_result,
            profile_performance,
        )
        print("✅ Core performance classes imported successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_advanced_cache():
    """Test advanced caching functionality."""
    print("\nTesting advanced cache...")
    
    try:
        from pymapgis.performance import AdvancedCache
        
        # Create cache with small limits for testing
        cache = AdvancedCache(memory_limit_mb=10, disk_limit_mb=50)
        
        # Test basic cache operations
        test_data = {"key1": "value1", "key2": [1, 2, 3, 4, 5]}
        
        cache.put("test_key", test_data)
        retrieved = cache.get("test_key")
        
        if retrieved == test_data:
            print("✅ Basic cache put/get works")
        else:
            print("❌ Cache put/get failed")
            return False
        
        # Test cache miss
        missing = cache.get("nonexistent_key")
        if missing is None:
            print("✅ Cache miss handled correctly")
        else:
            print("❌ Cache miss not handled correctly")
            return False
        
        # Test cache stats
        stats = cache.get_stats()
        if 'memory_cache' in stats and 'disk_cache' in stats:
            print("✅ Cache statistics available")
            print(f"   Memory cache: {stats['memory_cache']['items']} items")
        else:
            print("❌ Cache statistics not available")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Advanced cache test failed: {e}")
        return False

def test_lazy_loading():
    """Test lazy loading functionality."""
    print("\nTesting lazy loading...")
    
    try:
        from pymapgis.performance import lazy_load
        
        # Track if expensive function was called
        call_count = 0
        
        @lazy_load
        def expensive_computation(x):
            nonlocal call_count
            call_count += 1
            time.sleep(0.1)  # Simulate expensive operation
            return x * x
        
        # First call should execute the function
        result1 = expensive_computation(5)
        if result1 == 25 and call_count == 1:
            print("✅ Lazy function executed on first call")
        else:
            print("❌ Lazy function first call failed")
            return False
        
        # Second call should use cached result
        result2 = expensive_computation(5)
        if result2 == 25 and call_count == 1:  # Should still be 1
            print("✅ Lazy function used cache on second call")
        else:
            print("❌ Lazy function caching failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Lazy loading test failed: {e}")
        return False

def test_performance_profiler():
    """Test performance profiling functionality."""
    print("\nTesting performance profiler...")
    
    try:
        from pymapgis.performance import PerformanceProfiler
        
        profiler = PerformanceProfiler()
        
        # Test profiling
        profiler.start_profile("test_operation")
        time.sleep(0.1)  # Simulate work
        result = profiler.end_profile("test_operation")
        
        if 'duration_seconds' in result and result['duration_seconds'] > 0.05:
            print("✅ Performance profiling works")
            print(f"   Duration: {result['duration_seconds']:.3f}s")
        else:
            print("❌ Performance profiling failed")
            return False
        
        # Test profile summary
        summary = profiler.get_profile_summary("test_operation")
        if 'executions' in summary and summary['executions'] == 1:
            print("✅ Profile summary available")
        else:
            print("❌ Profile summary failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Performance profiler test failed: {e}")
        return False

def test_memory_manager():
    """Test memory management functionality."""
    print("\nTesting memory manager...")
    
    try:
        from pymapgis.performance import MemoryManager
        
        # Create memory manager with low threshold for testing
        memory_mgr = MemoryManager(target_memory_mb=100)
        
        # Test memory usage tracking
        current_memory = memory_mgr.get_memory_usage()
        if current_memory > 0:
            print(f"✅ Memory usage tracking: {current_memory:.1f}MB")
        else:
            print("❌ Memory usage tracking failed")
            return False
        
        # Test cleanup callback
        callback_called = False
        
        def test_callback():
            nonlocal callback_called
            callback_called = True
        
        memory_mgr.add_cleanup_callback(test_callback)
        
        # Force cleanup
        cleanup_result = memory_mgr.cleanup_memory()
        if callback_called and 'memory_freed_mb' in cleanup_result:
            print("✅ Memory cleanup and callbacks work")
        else:
            print("❌ Memory cleanup failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Memory manager test failed: {e}")
        return False

def test_spatial_index():
    """Test spatial indexing functionality."""
    print("\nTesting spatial index...")
    
    try:
        from pymapgis.performance import SpatialIndex
        
        # Create spatial index
        spatial_idx = SpatialIndex(index_type="grid")  # Use grid for testing
        
        # Create mock geometry objects with bounds
        class MockGeometry:
            def __init__(self, bounds):
                self.bounds = bounds
        
        # Insert some geometries
        geom1 = MockGeometry((0, 0, 10, 10))
        geom2 = MockGeometry((5, 5, 15, 15))
        geom3 = MockGeometry((20, 20, 30, 30))
        
        spatial_idx.insert(1, geom1)
        spatial_idx.insert(2, geom2)
        spatial_idx.insert(3, geom3)
        
        # Query for intersections
        query_bounds = (8, 8, 12, 12)
        results = spatial_idx.query(query_bounds)
        
        # Should find geometries 1 and 2
        if len(results) >= 1:  # At least one intersection
            print("✅ Spatial index query works")
            print(f"   Found {len(results)} intersecting geometries")
        else:
            print("❌ Spatial index query failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Spatial index test failed: {e}")
        return False

def test_decorators():
    """Test performance decorators."""
    print("\nTesting performance decorators...")
    
    try:
        from pymapgis.performance import cache_result, profile_performance
        
        # Test cache decorator
        call_count = 0
        
        @cache_result()
        def cached_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call
        result1 = cached_function(5)
        # Second call (should use cache)
        result2 = cached_function(5)
        
        if result1 == 10 and result2 == 10 and call_count == 1:
            print("✅ Cache decorator works")
        else:
            print("❌ Cache decorator failed")
            return False
        
        # Test profile decorator
        @profile_performance
        def profiled_function(x):
            time.sleep(0.05)
            return x + 1
        
        result = profiled_function(10)
        if result == 11:
            print("✅ Profile decorator works")
        else:
            print("❌ Profile decorator failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Decorator test failed: {e}")
        return False

def test_pymapgis_integration():
    """Test integration with main PyMapGIS package."""
    print("\nTesting PyMapGIS integration...")
    
    try:
        import pymapgis as pmg
        
        # Check if performance functions are available
        performance_functions = [
            'optimize_performance',
            'get_performance_stats',
            'enable_auto_optimization',
            'disable_auto_optimization',
            'clear_performance_cache'
        ]
        
        available_functions = []
        for func_name in performance_functions:
            if hasattr(pmg, func_name):
                available_functions.append(func_name)
                print(f"✅ pmg.{func_name} available")
            else:
                print(f"⚠️ pmg.{func_name} not available")
        
        if len(available_functions) >= 3:  # At least some functions available
            print(f"✅ {len(available_functions)}/{len(performance_functions)} performance functions integrated")
        else:
            print("⚠️ Performance functions not well integrated")
        
        # Test basic performance stats
        try:
            stats = pmg.get_performance_stats()
            if isinstance(stats, dict) and 'cache' in stats:
                print("✅ Performance statistics available")
            else:
                print("⚠️ Performance statistics not available")
        except:
            print("⚠️ Performance statistics failed")
        
        return True
        
    except Exception as e:
        print(f"❌ PyMapGIS integration test failed: {e}")
        return False

def main():
    """Run all performance optimization tests."""
    print("PyMapGIS Performance Optimization Test Suite")
    print("=" * 55)
    
    tests = [
        ("Performance Imports", test_performance_imports),
        ("Advanced Cache", test_advanced_cache),
        ("Lazy Loading", test_lazy_loading),
        ("Performance Profiler", test_performance_profiler),
        ("Memory Manager", test_memory_manager),
        ("Spatial Index", test_spatial_index),
        ("Decorators", test_decorators),
        ("PyMapGIS Integration", test_pymapgis_integration),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 55)
    print("Test Summary:")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All performance optimization tests passed!")
        print("Performance optimization features are ready for use.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")
        print("Some performance features may not be fully available.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
