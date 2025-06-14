"""
PyMapGIS Advanced Testing Module

Provides comprehensive testing infrastructure for performance benchmarks,
load testing, and enterprise-grade quality assurance.

Features:
- Performance Benchmarking: Micro-benchmarks for core operations
- Load Testing: High-volume data processing and concurrent user simulation
- Memory Profiling: Memory usage analysis and leak detection
- Stress Testing: System limits and breaking point analysis
- Regression Testing: Performance regression detection
- Integration Testing: End-to-end workflow validation

Enterprise Features:
- Automated performance monitoring
- Continuous integration testing
- Performance regression alerts
- Scalability validation
- Resource utilization analysis
- Cross-platform compatibility testing
"""

import time
import psutil
import threading
import asyncio
import logging
import statistics
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from contextlib import contextmanager
import gc
import tracemalloc
from pathlib import Path

logger = logging.getLogger(__name__)

# Optional imports for advanced testing
try:
    import pytest

    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False
    logger.warning("pytest not available - some testing features limited")

try:
    import locust
    from locust import HttpUser, task, between

    LOCUST_AVAILABLE = True
except ImportError:
    LOCUST_AVAILABLE = False
    logger.warning("locust not available - load testing limited")

try:
    import memory_profiler

    MEMORY_PROFILER_AVAILABLE = True
except ImportError:
    MEMORY_PROFILER_AVAILABLE = False
    logger.warning("memory_profiler not available - memory analysis limited")

try:
    import numpy as np
    import pandas as pd

    NUMPY_PANDAS_AVAILABLE = True
except ImportError:
    NUMPY_PANDAS_AVAILABLE = False
    logger.warning("NumPy/Pandas not available - data analysis limited")

# Core testing components
from .benchmarks import (
    BenchmarkSuite,
    PerformanceBenchmark,
    GeospatialBenchmark,
    IOBenchmark,
    MemoryBenchmark,
    BenchmarkResult,
    run_benchmark_suite,
    create_benchmark_report,
)

from .load_testing import (
    LoadTester,
    ConcurrentUserSimulator,
    DataVolumeStressTester,
    StreamingLoadTester,
    DatabaseLoadTester,
    LoadTestResult,
    run_load_test,
    generate_load_report,
)

from .profiling import (
    PerformanceProfiler,
    MemoryProfiler,
    CPUProfiler,
    IOProfiler,
    ResourceMonitor,
    profile_function,
    monitor_resources,
)

from .regression import (
    RegressionTester,
    PerformanceBaseline,
    RegressionDetector,
    BaselineManager,
    detect_performance_regression,
    update_performance_baseline,
)

from .integration import (
    IntegrationTester,
    WorkflowTester,
    EndToEndTester,
    CompatibilityTester,
    run_integration_tests,
    validate_system_health,
)

# Version and metadata
__version__ = "0.3.2"
__author__ = "PyMapGIS Team"

# Default testing configuration
DEFAULT_TESTING_CONFIG = {
    "benchmarks": {
        "iterations": 100,
        "warmup_iterations": 10,
        "timeout_seconds": 300,
        "memory_threshold_mb": 1000,
        "cpu_threshold_percent": 80,
    },
    "load_testing": {
        "max_users": 100,
        "spawn_rate": 10,
        "test_duration": 300,  # seconds
        "ramp_up_time": 60,
        "think_time_min": 1,
        "think_time_max": 5,
    },
    "profiling": {
        "sample_interval": 0.1,
        "memory_precision": 1,
        "enable_line_profiling": False,
        "enable_memory_tracking": True,
        "enable_cpu_profiling": True,
    },
    "regression": {
        "tolerance_percent": 10,
        "baseline_retention_days": 30,
        "alert_threshold_percent": 20,
        "min_samples": 5,
    },
    "integration": {
        "test_timeout": 600,
        "retry_attempts": 3,
        "parallel_execution": True,
        "cleanup_after_test": True,
    },
}

# Global testing instances
_benchmark_suite = None
_load_tester = None
_performance_profiler = None
_regression_tester = None
_integration_tester = None


def get_benchmark_suite() -> Optional["BenchmarkSuite"]:
    """Get the global benchmark suite instance."""
    global _benchmark_suite
    if _benchmark_suite is None:
        _benchmark_suite = BenchmarkSuite()
    return _benchmark_suite


def get_load_tester() -> Optional["LoadTester"]:
    """Get the global load tester instance."""
    global _load_tester
    if _load_tester is None:
        _load_tester = LoadTester()
    return _load_tester


def get_performance_profiler() -> Optional["PerformanceProfiler"]:
    """Get the global performance profiler instance."""
    global _performance_profiler
    if _performance_profiler is None:
        _performance_profiler = PerformanceProfiler()
    return _performance_profiler


def get_regression_tester() -> Optional["RegressionTester"]:
    """Get the global regression tester instance."""
    global _regression_tester
    if _regression_tester is None:
        _regression_tester = RegressionTester()
    return _regression_tester


def get_integration_tester() -> Optional["IntegrationTester"]:
    """Get the global integration tester instance."""
    global _integration_tester
    if _integration_tester is None:
        _integration_tester = IntegrationTester()
    return _integration_tester


# Convenience functions for quick testing
def run_performance_benchmark(
    function: Callable, *args, iterations: int = 100, **kwargs
) -> BenchmarkResult:
    """
    Run a performance benchmark on a function.

    Args:
        function: Function to benchmark
        *args: Function arguments
        iterations: Number of iterations to run
        **kwargs: Function keyword arguments

    Returns:
        BenchmarkResult object
    """
    benchmark_suite = get_benchmark_suite()
    return benchmark_suite.run_function_benchmark(
        function, *args, iterations=iterations, **kwargs
    )


def run_memory_benchmark(function: Callable, *args, **kwargs) -> Dict[str, Any]:
    """
    Run a memory usage benchmark on a function.

    Args:
        function: Function to benchmark
        *args: Function arguments
        **kwargs: Function keyword arguments

    Returns:
        Memory benchmark results
    """
    profiler = get_performance_profiler()
    return profiler.profile_memory_usage(function, *args, **kwargs)


def run_load_test_simulation(
    target_function: Callable, concurrent_users: int = 10, duration: int = 60
) -> LoadTestResult:
    """
    Run a load test simulation.

    Args:
        target_function: Function to load test
        concurrent_users: Number of concurrent users to simulate
        duration: Test duration in seconds

    Returns:
        LoadTestResult object
    """
    load_tester = get_load_tester()
    return load_tester.simulate_concurrent_load(
        target_function, concurrent_users, duration
    )


def detect_regression(
    test_name: str, current_result: float, baseline_file: str = None, tolerance: float = 10.0
) -> bool:
    """
    Detect performance regression.

    Args:
        test_name: Name of the test
        current_result: Current performance result
        baseline_file: Optional baseline file path
        tolerance: Regression tolerance percentage

    Returns:
        True if regression detected, False otherwise
    """
    regression_tester = get_regression_tester()
    return regression_tester.detect_regression(test_name, current_result, baseline_file, tolerance_percent=tolerance)


def validate_system_performance() -> Dict[str, Any]:
    """
    Validate overall system performance.

    Returns:
        System performance validation results
    """
    integration_tester = get_integration_tester()
    return integration_tester.validate_system_performance()


# Testing decorators for easy integration
def benchmark(iterations: int = 100, warmup: int = 10):
    """
    Decorator to benchmark a function.

    Args:
        iterations: Number of iterations to run
        warmup: Number of warmup iterations
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            benchmark_suite = get_benchmark_suite()
            results = benchmark_suite.run_function_benchmark(
                func, *args, iterations=iterations, warmup=warmup, **kwargs
            )
            logger.info(f"Benchmark results for {func.__name__}: {results}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def profile_memory(precision: int = 1):
    """
    Decorator to profile memory usage of a function.

    Args:
        precision: Memory measurement precision
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            profiler = get_performance_profiler()
            results = profiler.profile_memory_usage(
                func, *args, precision=precision, **kwargs
            )
            logger.info(f"Memory profile for {func.__name__}: {results}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def load_test(users: int = 10, duration: int = 60):
    """
    Decorator to load test a function.

    Args:
        users: Number of concurrent users
        duration: Test duration in seconds
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            load_tester = get_load_tester()
            results = load_tester.simulate_concurrent_load(func, users, duration)
            logger.info(f"Load test results for {func.__name__}: {results}")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def regression_check(baseline_file: str = None, tolerance: float = 10.0):
    """
    Decorator to check for performance regression.

    Args:
        baseline_file: Baseline file path
        tolerance: Regression tolerance percentage
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time

            regression_tester = get_regression_tester()
            is_regression = regression_tester.detect_regression(
                func.__name__, execution_time, baseline_file, tolerance
            )

            if is_regression:
                logger.warning(f"Performance regression detected in {func.__name__}")

            return result

        return wrapper

    return decorator


# Export all public components
__all__ = [
    # Core testing components
    "BenchmarkSuite",
    "PerformanceBenchmark",
    "GeospatialBenchmark",
    "IOBenchmark",
    "MemoryBenchmark",
    "run_benchmark_suite",
    "create_benchmark_report",
    # Load testing
    "LoadTester",
    "ConcurrentUserSimulator",
    "DataVolumeStressTester",
    "StreamingLoadTester",
    "DatabaseLoadTester",
    "run_load_test",
    "generate_load_report",
    # Profiling
    "PerformanceProfiler",
    "MemoryProfiler",
    "CPUProfiler",
    "IOProfiler",
    "ResourceMonitor",
    "profile_function",
    "monitor_resources",
    # Regression testing
    "RegressionTester",
    "PerformanceBaseline",
    "RegressionDetector",
    "BaselineManager",
    "detect_performance_regression",
    "update_performance_baseline",
    # Integration testing
    "IntegrationTester",
    "WorkflowTester",
    "EndToEndTester",
    "CompatibilityTester",
    "run_integration_tests",
    "validate_system_health",
    # Manager instances
    "get_benchmark_suite",
    "get_load_tester",
    "get_performance_profiler",
    "get_regression_tester",
    "get_integration_tester",
    # Convenience functions
    "run_performance_benchmark",
    "run_memory_benchmark",
    "run_load_test_simulation",
    "detect_regression",
    "validate_system_performance",
    # Decorators
    "benchmark",
    "profile_memory",
    "load_test",
    "regression_check",
    # Configuration
    "DEFAULT_TESTING_CONFIG",
]
