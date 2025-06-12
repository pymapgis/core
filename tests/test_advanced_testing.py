"""
Test suite for PyMapGIS Advanced Testing features.

Tests performance benchmarking, load testing, profiling, regression detection,
and integration testing capabilities.
"""

import pytest
import time
import tempfile
import random
from pathlib import Path
from unittest.mock import Mock, patch

# Import PyMapGIS testing components
try:
    from pymapgis.testing import (
        BenchmarkSuite,
        PerformanceBenchmark,
        LoadTester,
        PerformanceProfiler,
        RegressionTester,
        IntegrationTester,
        run_performance_benchmark,
        run_memory_benchmark,
        run_load_test_simulation,
        detect_regression,
        validate_system_performance,
        get_benchmark_suite,
        get_load_tester,
        get_performance_profiler,
        get_regression_tester,
        get_integration_tester,
    )

    TESTING_AVAILABLE = True
except ImportError:
    TESTING_AVAILABLE = False


@pytest.fixture
def sample_function():
    """Create a sample function for testing."""

    def test_function(size=100, delay=0.01):
        """Sample function that does some work."""
        data = [random.random() for _ in range(size)]
        time.sleep(delay)
        return sum(data)

    return test_function


@pytest.fixture
def temp_baseline_file():
    """Create a temporary baseline file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        baseline_file = f.name
    yield baseline_file
    # Cleanup
    Path(baseline_file).unlink(missing_ok=True)


@pytest.mark.skipif(not TESTING_AVAILABLE, reason="Testing module not available")
class TestPerformanceBenchmarking:
    """Test performance benchmarking functionality."""

    def test_benchmark_suite_creation(self):
        """Test benchmark suite creation."""
        suite = get_benchmark_suite()
        assert suite is not None
        assert hasattr(suite, "run_function_benchmark")

    def test_function_benchmark(self, sample_function):
        """Test function benchmarking."""
        benchmark = PerformanceBenchmark("test_benchmark")
        result = benchmark.run(sample_function, size=50, iterations=5, warmup=2)

        assert result.name == "test_benchmark"
        assert result.iterations == 5
        assert result.mean_time > 0
        assert result.operations_per_second > 0
        assert result.memory_usage_mb >= 0

    def test_run_performance_benchmark(self, sample_function):
        """Test convenience function for performance benchmarking."""
        result = run_performance_benchmark(sample_function, size=50, iterations=5)

        assert result.mean_time > 0
        assert result.operations_per_second > 0
        assert result.metadata["function_name"] == "test_function"

    def test_memory_benchmark(self, sample_function):
        """Test memory benchmarking."""
        result = run_memory_benchmark(sample_function, size=100)

        assert "function_name" in result
        assert "peak_memory_mb" in result
        assert result["function_name"] == "test_function"
        assert result["peak_memory_mb"] >= 0


@pytest.mark.skipif(not TESTING_AVAILABLE, reason="Testing module not available")
class TestLoadTesting:
    """Test load testing functionality."""

    def test_load_tester_creation(self):
        """Test load tester creation."""
        load_tester = get_load_tester()
        assert load_tester is not None
        assert hasattr(load_tester, "simulate_concurrent_load")

    def test_concurrent_load_simulation(self, sample_function):
        """Test concurrent load simulation."""
        load_tester = LoadTester()

        # Use a faster function for testing
        def fast_function():
            time.sleep(0.001)  # 1ms delay
            return "success"

        result = load_tester.simulate_concurrent_load(
            fast_function, concurrent_users=5, duration=2
        )

        assert result.total_requests > 0
        assert result.successful_requests >= 0
        assert result.failed_requests >= 0
        assert result.requests_per_second > 0
        assert result.concurrent_users == 5

    def test_load_test_simulation_convenience(self, sample_function):
        """Test load test simulation convenience function."""

        def fast_function():
            time.sleep(0.001)
            return "success"

        result = run_load_test_simulation(fast_function, concurrent_users=3, duration=1)

        assert result.total_requests > 0
        assert result.concurrent_users == 3


@pytest.mark.skipif(not TESTING_AVAILABLE, reason="Testing module not available")
class TestProfiling:
    """Test profiling functionality."""

    def test_performance_profiler_creation(self):
        """Test performance profiler creation."""
        profiler = get_performance_profiler()
        assert profiler is not None
        assert hasattr(profiler, "profile_function")

    def test_function_profiling(self, sample_function):
        """Test function profiling."""
        profiler = PerformanceProfiler()
        result = profiler.profile_function(sample_function, size=50)

        assert result.function_name == "test_function"
        assert result.execution_time > 0
        assert result.memory_usage_mb >= 0
        assert result.peak_memory_mb >= 0

    def test_memory_profiling(self, sample_function):
        """Test memory profiling."""
        profiler = PerformanceProfiler()
        result = profiler.profile_memory_usage(sample_function, size=100)

        assert "function_name" in result
        assert "peak_memory_mb" in result
        assert result["function_name"] == "test_function"


@pytest.mark.skipif(not TESTING_AVAILABLE, reason="Testing module not available")
class TestRegressionTesting:
    """Test regression testing functionality."""

    def test_regression_tester_creation(self, temp_baseline_file):
        """Test regression tester creation."""
        tester = RegressionTester(temp_baseline_file)
        assert tester is not None
        assert hasattr(tester, "detect_regression")

    def test_baseline_management(self, temp_baseline_file):
        """Test baseline creation and management."""
        tester = RegressionTester(temp_baseline_file)

        # Create baseline
        baseline_values = [0.1, 0.11, 0.09, 0.105, 0.095]
        tester.update_baseline("test_operation", baseline_values)

        # Check baseline exists
        baseline = tester.baseline_manager.get_baseline("test_operation")
        assert baseline is not None
        assert baseline.test_name == "test_operation"
        assert baseline.sample_count == 5

    def test_regression_detection(self, temp_baseline_file):
        """Test regression detection."""
        tester = RegressionTester(temp_baseline_file)

        # Create baseline
        baseline_values = [0.1, 0.11, 0.09, 0.105, 0.095]
        tester.update_baseline("test_operation", baseline_values)

        # Test normal performance (no regression)
        is_regression = tester.detect_regression(
            "test_operation", 0.105, tolerance_percent=10.0
        )
        assert not is_regression

        # Test degraded performance (regression)
        is_regression = tester.detect_regression(
            "test_operation", 0.130, tolerance_percent=10.0
        )
        assert is_regression

    def test_detect_regression_convenience(self, temp_baseline_file):
        """Test regression detection convenience function."""
        # Create baseline first
        tester = RegressionTester(temp_baseline_file)
        baseline_values = [0.1, 0.11, 0.09, 0.105, 0.095]
        tester.update_baseline("test_operation", baseline_values)

        # Test convenience function
        is_regression = detect_regression(
            "test_operation", 0.130, baseline_file=temp_baseline_file, tolerance=10.0
        )
        assert is_regression


@pytest.mark.skipif(not TESTING_AVAILABLE, reason="Testing module not available")
class TestIntegrationTesting:
    """Test integration testing functionality."""

    def test_integration_tester_creation(self):
        """Test integration tester creation."""
        tester = get_integration_tester()
        assert tester is not None
        assert hasattr(tester, "validate_system_performance")

    def test_system_performance_validation(self):
        """Test system performance validation."""
        result = validate_system_performance()

        # Should return either valid metrics or an error message
        assert isinstance(result, dict)
        if "error" not in result:
            assert "status" in result
            assert "performance_score" in result
            assert "metrics" in result

    def test_workflow_testing(self):
        """Test workflow testing."""
        tester = IntegrationTester()

        # Test data pipeline
        result = tester.workflow_tester.test_data_pipeline({"test": "data"})

        assert result.test_name == "data_pipeline"
        assert result.test_type == "workflow"
        assert result.status in ["passed", "failed", "warning"]
        assert result.execution_time > 0

    def test_compatibility_testing(self):
        """Test compatibility testing."""
        tester = IntegrationTester()

        # Test platform compatibility
        result = tester.compatibility_tester.test_platform_compatibility()

        assert result.test_name == "platform_compatibility"
        assert result.test_type == "compatibility"
        assert result.status in ["passed", "failed", "warning"]
        assert "platform_info" in result.details

    def test_dependency_compatibility(self):
        """Test dependency compatibility testing."""
        tester = IntegrationTester()

        # Test with common dependencies
        dependencies = ["sys", "os", "time", "json"]  # Built-in modules
        result = tester.compatibility_tester.test_dependency_compatibility(dependencies)

        assert result.test_name == "dependency_compatibility"
        assert result.test_type == "compatibility"
        assert result.status in ["passed", "failed", "warning"]
        assert result.details["dependencies_tested"] == len(dependencies)


@pytest.mark.skipif(not TESTING_AVAILABLE, reason="Testing module not available")
class TestTestingDecorators:
    """Test testing decorators and utilities."""

    def test_benchmark_decorator(self, sample_function):
        """Test benchmark decorator."""
        from pymapgis.testing import benchmark

        @benchmark(iterations=5, warmup=2)
        def decorated_function(size=50):
            return sample_function(size)

        # Should run without error and log results
        result = decorated_function()
        assert result is not None

    def test_profile_memory_decorator(self, sample_function):
        """Test memory profiling decorator."""
        from pymapgis.testing import profile_memory

        @profile_memory(precision=1)
        def decorated_function(size=50):
            return sample_function(size)

        # Should run without error and log results
        result = decorated_function()
        assert result is not None

    def test_load_test_decorator(self, sample_function):
        """Test load test decorator."""
        from pymapgis.testing import load_test

        @load_test(users=3, duration=1)
        def decorated_function():
            time.sleep(0.001)
            return "success"

        # Should run without error and log results
        result = decorated_function()
        assert result is not None


@pytest.mark.skipif(not TESTING_AVAILABLE, reason="Testing module not available")
class TestTestingUtilities:
    """Test testing utilities and helper functions."""

    def test_global_instances(self):
        """Test global testing instances."""
        # Test that global instances are created and accessible
        benchmark_suite = get_benchmark_suite()
        load_tester = get_load_tester()
        profiler = get_performance_profiler()
        regression_tester = get_regression_tester()
        integration_tester = get_integration_tester()

        assert benchmark_suite is not None
        assert load_tester is not None
        assert profiler is not None
        assert regression_tester is not None
        assert integration_tester is not None

    def test_convenience_functions_availability(self):
        """Test that convenience functions are available."""
        # Test function availability
        assert callable(run_performance_benchmark)
        assert callable(run_memory_benchmark)
        assert callable(run_load_test_simulation)
        assert callable(detect_regression)
        assert callable(validate_system_performance)

    def test_error_handling(self):
        """Test error handling in testing functions."""

        def failing_function():
            raise Exception("Test error")

        # Benchmark should handle errors gracefully
        with pytest.raises(Exception):
            run_performance_benchmark(failing_function, iterations=1)


@pytest.mark.skipif(not TESTING_AVAILABLE, reason="Testing module not available")
class TestTestingConfiguration:
    """Test testing configuration and settings."""

    def test_default_config_availability(self):
        """Test that default configuration is available."""
        from pymapgis.testing import DEFAULT_TESTING_CONFIG

        assert isinstance(DEFAULT_TESTING_CONFIG, dict)
        assert "benchmarks" in DEFAULT_TESTING_CONFIG
        assert "load_testing" in DEFAULT_TESTING_CONFIG
        assert "profiling" in DEFAULT_TESTING_CONFIG
        assert "regression" in DEFAULT_TESTING_CONFIG
        assert "integration" in DEFAULT_TESTING_CONFIG

    def test_config_values(self):
        """Test configuration values are reasonable."""
        from pymapgis.testing import DEFAULT_TESTING_CONFIG

        # Check benchmark config
        benchmark_config = DEFAULT_TESTING_CONFIG["benchmarks"]
        assert benchmark_config["iterations"] > 0
        assert benchmark_config["warmup_iterations"] >= 0
        assert benchmark_config["timeout_seconds"] > 0

        # Check load testing config
        load_config = DEFAULT_TESTING_CONFIG["load_testing"]
        assert load_config["max_users"] > 0
        assert load_config["test_duration"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
