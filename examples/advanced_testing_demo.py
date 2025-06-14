#!/usr/bin/env python3
"""
PyMapGIS Advanced Testing Demo

Demonstrates comprehensive testing capabilities including:
- Performance benchmarking for core operations
- Load testing with concurrent user simulation
- Memory and CPU profiling
- Performance regression detection
- Integration and end-to-end testing
"""

import sys
import time
import random
import asyncio
from pathlib import Path
from datetime import datetime

# Add PyMapGIS to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pymapgis as pmg


def demo_performance_benchmarking():
    """Demonstrate performance benchmarking capabilities."""
    print("\n⚡ Performance Benchmarking Demo")
    print("=" * 50)

    try:
        # Get benchmark suite
        benchmark_suite = pmg.testing.get_benchmark_suite()

        # Test function to benchmark
        def sample_geospatial_operation(size=1000):
            """Sample geospatial operation for benchmarking."""
            # Simulate geospatial processing
            points = []
            for i in range(size):
                x = random.uniform(-180, 180)
                y = random.uniform(-90, 90)
                points.append((x, y))

            # Simulate spatial calculations
            distances = []
            for i in range(min(100, len(points) - 1)):
                dx = points[i + 1][0] - points[i][0]
                dy = points[i + 1][1] - points[i][1]
                distance = (dx**2 + dy**2) ** 0.5
                distances.append(distance)

            return len(distances)

        # Run performance benchmark
        print("Running performance benchmark...")
        result = pmg.testing.run_performance_benchmark(
            sample_geospatial_operation, size=500, iterations=50
        )

        print(f"✅ Benchmark completed:")
        print(f"   Function: {result.name}")
        print(f"   Mean time: {result.mean_time*1000:.2f} ms")
        print(f"   Operations/sec: {result.operations_per_second:.2f}")
        print(f"   Memory usage: {result.memory_usage_mb:.2f} MB")
        print(f"   CPU usage: {result.cpu_usage_percent:.2f}%")

        # Run memory benchmark
        print("\nRunning memory benchmark...")
        memory_result = pmg.testing.run_memory_benchmark(
            sample_geospatial_operation, size=1000
        )

        print(f"✅ Memory benchmark completed:")
        print(f"   Peak memory: {memory_result['peak_memory_mb']:.2f} MB")
        print(f"   Memory growth: {memory_result['memory_growth_mb']:.2f} MB")

        return True

    except Exception as e:
        print(f"❌ Benchmarking demo failed: {e}")
        return False


def demo_load_testing():
    """Demonstrate load testing capabilities."""
    print("\n🔄 Load Testing Demo")
    print("=" * 50)

    try:
        # Test function for load testing
        def api_simulation():
            """Simulate API endpoint processing."""
            # Simulate API processing time
            processing_time = random.uniform(0.01, 0.1)
            time.sleep(processing_time)

            # Simulate occasional failures
            if random.random() < 0.05:  # 5% failure rate
                raise Exception("Simulated API error")

            return {"status": "success", "data": "processed"}

        # Run concurrent load test
        print("Running concurrent user simulation...")
        load_result = pmg.testing.run_load_test_simulation(
            api_simulation, concurrent_users=20, duration=10  # 10 seconds
        )

        print(f"✅ Load test completed:")
        print(f"   Total requests: {load_result.total_requests}")
        print(f"   Successful requests: {load_result.successful_requests}")
        print(f"   Failed requests: {load_result.failed_requests}")
        print(f"   Requests/sec: {load_result.requests_per_second:.2f}")
        print(f"   Mean response time: {load_result.mean_response_time*1000:.2f} ms")
        print(f"   Error rate: {load_result.error_rate*100:.2f}%")
        print(f"   P95 response time: {load_result.p95_response_time*1000:.2f} ms")

        return True

    except Exception as e:
        print(f"❌ Load testing demo failed: {e}")
        return False


def demo_profiling():
    """Demonstrate profiling capabilities."""
    print("\n📊 Profiling Demo")
    print("=" * 50)

    try:
        # Get performance profiler
        profiler = pmg.testing.get_performance_profiler()

        # Function to profile
        def data_processing_task():
            """Simulate data processing task."""
            # Simulate memory allocation
            data = []
            for i in range(10000):
                data.append(random.random() * 100)

            # Simulate processing
            processed = []
            for value in data:
                if value > 50:
                    processed.append(value * 2)

            # Simulate cleanup
            del data

            return len(processed)

        # Profile the function
        print("Profiling data processing task...")
        profile_result = profiler.profile_function(data_processing_task)

        print(f"✅ Profiling completed:")
        print(f"   Function: {profile_result.function_name}")
        print(f"   Execution time: {profile_result.execution_time*1000:.2f} ms")
        print(f"   Memory usage: {profile_result.memory_usage_mb:.2f} MB")
        print(f"   Peak memory: {profile_result.peak_memory_mb:.2f} MB")
        print(f"   CPU time: {profile_result.cpu_time*1000:.2f} ms")

        # Test memory profiling with context manager
        print("\nTesting resource monitoring...")
        with pmg.testing.monitor_resources(interval=0.5) as monitor:
            # Simulate some work
            time.sleep(2)
            data_processing_task()

        resource_summary = monitor.get_resource_summary()
        print(f"✅ Resource monitoring completed:")
        print(f"   Average CPU: {resource_summary['cpu_summary']['average']:.2f}%")
        print(f"   Peak CPU: {resource_summary['cpu_summary']['peak']:.2f}%")
        print(
            f"   Average Memory: {resource_summary['memory_summary']['average']:.2f}%"
        )

        return True

    except Exception as e:
        print(f"❌ Profiling demo failed: {e}")
        return False


def demo_regression_testing():
    """Demonstrate regression testing capabilities."""
    print("\n🔍 Regression Testing Demo")
    print("=" * 50)

    try:
        # Get regression tester
        regression_tester = pmg.testing.get_regression_tester()

        # Simulate establishing a baseline
        print("Establishing performance baseline...")
        baseline_values = []
        for i in range(10):
            # Simulate consistent performance
            execution_time = 0.1 + random.uniform(-0.01, 0.01)
            baseline_values.append(execution_time)

        regression_tester.update_baseline(
            "sample_operation",
            baseline_values,
            metadata={"version": "1.0.0", "environment": "test"},
        )
        print(f"✅ Baseline established with {len(baseline_values)} samples")

        # Test normal performance (should not trigger regression)
        print("\nTesting normal performance...")
        normal_performance = 0.105  # Within tolerance
        is_regression = regression_tester.detect_regression(
            "sample_operation", normal_performance, tolerance_percent=10.0
        )
        print(f"   Performance: {normal_performance:.3f}s")
        print(f"   Regression detected: {'❌ YES' if is_regression else '✅ NO'}")

        # Test degraded performance (should trigger regression)
        print("\nTesting degraded performance...")
        degraded_performance = 0.130  # 30% slower
        is_regression = regression_tester.detect_regression(
            "sample_operation", degraded_performance, tolerance_percent=10.0
        )
        print(f"   Performance: {degraded_performance:.3f}s")
        print(f"   Regression detected: {'❌ YES' if is_regression else '✅ NO'}")

        # Generate regression report
        print("\nGenerating regression report...")
        report = regression_tester.generate_regression_report()
        print(f"✅ Regression report generated:")
        print(f"   Total tests: {report['summary']['total_tests']}")
        print(f"   Regressions detected: {report['summary']['regressions_detected']}")
        print(f"   Regression rate: {report['summary']['regression_rate']*100:.1f}%")

        return True

    except Exception as e:
        print(f"❌ Regression testing demo failed: {e}")
        return False


def demo_integration_testing():
    """Demonstrate integration testing capabilities."""
    print("\n🔗 Integration Testing Demo")
    print("=" * 50)

    try:
        # Get integration tester
        integration_tester = pmg.testing.get_integration_tester()

        # Validate system health
        print("Validating system health...")
        health_result = integration_tester.validate_system_performance()

        if "error" not in health_result:
            print(f"✅ System health validation:")
            print(f"   Status: {health_result['status']}")
            print(f"   Performance score: {health_result['performance_score']:.1f}/100")
            print(f"   CPU usage: {health_result['metrics']['cpu_usage']:.1f}%")
            print(f"   Memory usage: {health_result['metrics']['memory_usage']:.1f}%")
            print(
                f"   Available memory: {health_result['metrics']['available_memory_gb']:.1f} GB"
            )
        else:
            print(f"ℹ️ System health check limited: {health_result['error']}")

        # Run comprehensive integration tests
        print("\nRunning integration tests...")
        test_results = integration_tester.run_comprehensive_tests()

        print(f"✅ Integration tests completed:")
        print(f"   Total tests: {len(test_results)}")

        # Summarize results by status
        status_counts = {}
        for result in test_results:
            status_counts[result.status] = status_counts.get(result.status, 0) + 1

        for status, count in status_counts.items():
            print(f"   {status.capitalize()}: {count}")

        # Show details for any failed tests
        failed_tests = [r for r in test_results if r.status == "failed"]
        if failed_tests:
            print("\n❌ Failed tests:")
            for test in failed_tests:
                print(f"   - {test.test_name}: {test.errors}")

        return True

    except Exception as e:
        print(f"❌ Integration testing demo failed: {e}")
        return False


def demo_comprehensive_testing():
    """Demonstrate comprehensive testing workflow."""
    print("\n🎯 Comprehensive Testing Workflow Demo")
    print("=" * 50)

    try:
        # Function to test comprehensively
        def geospatial_workflow(data_size=1000):
            """Sample geospatial workflow for comprehensive testing."""
            # Step 1: Data generation
            points = [
                (random.uniform(-180, 180), random.uniform(-90, 90))
                for _ in range(data_size)
            ]

            # Step 2: Spatial processing
            processed_points = []
            for x, y in points:
                # Simple transformation
                new_x = x + random.uniform(-0.1, 0.1)
                new_y = y + random.uniform(-0.1, 0.1)
                processed_points.append((new_x, new_y))

            # Step 3: Analysis
            distances = []
            for i in range(min(100, len(processed_points) - 1)):
                dx = processed_points[i + 1][0] - processed_points[i][0]
                dy = processed_points[i + 1][1] - processed_points[i][1]
                distance = (dx**2 + dy**2) ** 0.5
                distances.append(distance)

            return {
                "input_points": len(points),
                "processed_points": len(processed_points),
                "calculated_distances": len(distances),
                "avg_distance": sum(distances) / len(distances) if distances else 0,
            }

        print("Running comprehensive testing workflow...")

        # 1. Performance benchmark
        print("1. Performance benchmarking...")
        benchmark_result = pmg.testing.run_performance_benchmark(
            geospatial_workflow, data_size=500, iterations=20
        )

        # 2. Load testing
        print("2. Load testing...")
        load_result = pmg.testing.run_load_test_simulation(
            lambda: geospatial_workflow(100), concurrent_users=10, duration=5
        )

        # 3. Regression check
        print("3. Regression testing...")
        is_regression = pmg.testing.detect_regression(
            "geospatial_workflow", benchmark_result.mean_time, tolerance=15.0
        )

        print(f"\n✅ Comprehensive testing completed:")
        print(f"   Benchmark mean time: {benchmark_result.mean_time*1000:.2f} ms")
        print(f"   Load test RPS: {load_result.requests_per_second:.2f}")
        print(f"   Load test error rate: {load_result.error_rate*100:.2f}%")
        print(f"   Regression detected: {'❌ YES' if is_regression else '✅ NO'}")

        return True

    except Exception as e:
        print(f"❌ Comprehensive testing demo failed: {e}")
        return False


def main():
    """Run the complete advanced testing demo."""
    print("🧪 PyMapGIS Advanced Testing Demo")
    print("=" * 60)
    print("Demonstrating comprehensive testing capabilities")

    try:
        # Run all testing demos
        demos = [
            ("Performance Benchmarking", demo_performance_benchmarking),
            ("Load Testing", demo_load_testing),
            ("Profiling", demo_profiling),
            ("Regression Testing", demo_regression_testing),
            ("Integration Testing", demo_integration_testing),
            ("Comprehensive Testing", demo_comprehensive_testing),
        ]

        results = []
        for demo_name, demo_func in demos:
            print(f"\n🚀 Running {demo_name} demo...")
            success = demo_func()
            results.append((demo_name, success))

        print("\n🎉 Advanced Testing Demo Complete!")
        print("=" * 60)

        # Summary
        successful = sum(1 for _, success in results if success)
        total = len(results)

        print(f"✅ Successfully demonstrated {successful}/{total} testing components")

        print("\n📊 Demo Results:")
        for demo_name, success in results:
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"   {demo_name}: {status}")

        print("\n🚀 PyMapGIS Advanced Testing is ready for enterprise deployment!")
        print(
            "🧪 Features: Benchmarking, Load testing, Profiling, Regression detection"
        )
        print("📈 Ready for performance validation and quality assurance")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
