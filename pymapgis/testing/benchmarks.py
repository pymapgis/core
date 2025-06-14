"""
Performance Benchmarking Module

Provides comprehensive performance benchmarking capabilities for PyMapGIS
operations including geospatial processing, I/O operations, and memory usage.
"""

import time
import gc
import statistics
import tracemalloc
import psutil
import threading
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

try:
    import numpy as np
    import pandas as pd

    NUMPY_PANDAS_AVAILABLE = True
except ImportError:
    NUMPY_PANDAS_AVAILABLE = False

try:
    import geopandas as gpd
    from shapely.geometry import Point, Polygon

    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False


@dataclass
class BenchmarkResult:
    """Container for benchmark results."""

    name: str
    iterations: int
    total_time: float
    mean_time: float
    median_time: float
    std_dev: float
    min_time: float
    max_time: float
    operations_per_second: float
    memory_usage_mb: float
    cpu_usage_percent: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """System performance metrics."""

    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_io_sent_mb: float
    network_io_recv_mb: float


class PerformanceBenchmark:
    """Base class for performance benchmarks."""

    def __init__(self, name: str):
        self.name = name
        self.results: List[BenchmarkResult] = []

    def run(
        self,
        function: Callable,
        *args,
        iterations: int = 100,
        warmup: int = 10,
        **kwargs,
    ) -> BenchmarkResult:
        """
        Run a performance benchmark.

        Args:
            function: Function to benchmark
            *args: Function arguments
            iterations: Number of iterations
            warmup: Number of warmup iterations
            **kwargs: Function keyword arguments

        Returns:
            BenchmarkResult
        """
        # Warmup runs
        for _ in range(warmup):
            try:
                function(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Warmup iteration failed: {e}")

        # Force garbage collection
        gc.collect()

        # Start memory tracking
        tracemalloc.start()
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Benchmark runs
        execution_times = []
        cpu_times = []

        for i in range(iterations):
            # Monitor CPU before execution
            cpu_before = process.cpu_percent()

            start_time = time.perf_counter()
            try:
                function(*args, **kwargs)
            except Exception as e:
                logger.error(f"Benchmark iteration {i} failed: {e}")
                continue
            end_time = time.perf_counter()

            execution_time = end_time - start_time
            execution_times.append(execution_time)

            # Monitor CPU after execution
            cpu_after = process.cpu_percent()
            cpu_times.append(max(cpu_after - cpu_before, 0))

        # Stop memory tracking
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_usage = max(final_memory - initial_memory, peak / 1024 / 1024)

        # Calculate statistics
        if not execution_times:
            raise RuntimeError("No successful benchmark iterations")

        total_time = sum(execution_times)
        mean_time = statistics.mean(execution_times)
        median_time = statistics.median(execution_times)
        std_dev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0
        min_time = min(execution_times)
        max_time = max(execution_times)
        ops_per_second = 1.0 / mean_time if mean_time > 0 else 0
        avg_cpu = statistics.mean(cpu_times) if cpu_times else 0

        result = BenchmarkResult(
            name=self.name,
            iterations=len(execution_times),
            total_time=total_time,
            mean_time=mean_time,
            median_time=median_time,
            std_dev=std_dev,
            min_time=min_time,
            max_time=max_time,
            operations_per_second=ops_per_second,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=avg_cpu,
            metadata={
                "function_name": function.__name__,
                "args_count": len(args),
                "kwargs_count": len(kwargs),
                "warmup_iterations": warmup,
            },
        )

        self.results.append(result)
        return result


class GeospatialBenchmark(PerformanceBenchmark):
    """Benchmark for geospatial operations."""

    def __init__(self):
        super().__init__("GeospatialBenchmark")

    def benchmark_point_creation(self, count: int = 1000) -> BenchmarkResult:
        """Benchmark point geometry creation."""
        if not GEOPANDAS_AVAILABLE:
            raise ImportError("GeoPandas required for geospatial benchmarks")

        def create_points():
            points = [Point(i, i) for i in range(count)]
            return points

        return self.run(create_points, iterations=50)

    def benchmark_polygon_intersection(
        self, polygon_count: int = 100
    ) -> BenchmarkResult:
        """Benchmark polygon intersection operations."""
        if not GEOPANDAS_AVAILABLE:
            raise ImportError("GeoPandas required for geospatial benchmarks")

        # Create test polygons
        polygons = []
        for i in range(polygon_count):
            coords = [(i, i), (i + 1, i), (i + 1, i + 1), (i, i + 1), (i, i)]
            polygons.append(Polygon(coords))

        def intersect_polygons():
            intersections = []
            for i in range(len(polygons) - 1):
                intersection = polygons[i].intersection(polygons[i + 1])
                intersections.append(intersection)
            return intersections

        return self.run(intersect_polygons, iterations=20)

    def benchmark_spatial_join(
        self, points_count: int = 1000, polygons_count: int = 10
    ) -> BenchmarkResult:
        """Benchmark spatial join operations."""
        if not GEOPANDAS_AVAILABLE:
            raise ImportError("GeoPandas required for geospatial benchmarks")

        # Create test data
        points = gpd.GeoDataFrame(
            {
                "geometry": [
                    Point(np.random.random(), np.random.random())
                    for _ in range(points_count)
                ]
            }
        )

        polygons = gpd.GeoDataFrame(
            {
                "geometry": [
                    Polygon([(i, i), (i + 0.5, i), (i + 0.5, i + 0.5), (i, i + 0.5)])
                    for i in range(polygons_count)
                ]
            }
        )

        def spatial_join():
            return gpd.sjoin(points, polygons, how="inner", predicate="within")

        return self.run(spatial_join, iterations=10)


class IOBenchmark(PerformanceBenchmark):
    """Benchmark for I/O operations."""

    def __init__(self):
        super().__init__("IOBenchmark")

    def benchmark_file_read(
        self, file_path: Path, chunk_size: int = 8192
    ) -> BenchmarkResult:
        """Benchmark file reading operations."""

        def read_file():
            with open(file_path, "rb") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break

        return self.run(read_file, iterations=20)

    def benchmark_file_write(
        self, file_path: Path, data_size_mb: int = 10
    ) -> BenchmarkResult:
        """Benchmark file writing operations."""
        data = b"x" * (data_size_mb * 1024 * 1024)

        def write_file():
            with open(file_path, "wb") as f:
                f.write(data)

        return self.run(write_file, iterations=10)

    def benchmark_csv_processing(self, row_count: int = 10000) -> BenchmarkResult:
        """Benchmark CSV processing operations."""
        if not NUMPY_PANDAS_AVAILABLE:
            raise ImportError("Pandas required for CSV benchmarks")

        # Create test data
        data = {
            "id": range(row_count),
            "x": np.random.random(row_count),
            "y": np.random.random(row_count),
            "value": np.random.random(row_count) * 100,
        }
        df = pd.DataFrame(data)

        def process_csv():
            # Simulate common operations
            filtered = df[df["value"] > 50]
            grouped = filtered.groupby("id").mean()
            return grouped

        return self.run(process_csv, iterations=50)


class MemoryBenchmark(PerformanceBenchmark):
    """Benchmark for memory usage patterns."""

    def __init__(self):
        super().__init__("MemoryBenchmark")

    def benchmark_memory_allocation(self, size_mb: int = 100) -> BenchmarkResult:
        """Benchmark memory allocation patterns."""

        def allocate_memory():
            # Allocate large array
            size = size_mb * 1024 * 1024 // 8  # 8 bytes per float64
            data = (
                np.zeros(size, dtype=np.float64)
                if NUMPY_PANDAS_AVAILABLE
                else [0.0] * size
            )

            # Perform some operations
            if NUMPY_PANDAS_AVAILABLE and isinstance(data, np.ndarray):
                data += 1
                result = np.sum(data)
            else:
                data = [x + 1 for x in data]
                result = sum(data)

            del data
            return result

        return self.run(allocate_memory, iterations=10)

    def benchmark_memory_fragmentation(self, iterations: int = 1000) -> BenchmarkResult:
        """Benchmark memory fragmentation patterns."""

        def fragment_memory():
            allocations = []

            # Allocate many small objects
            for i in range(iterations):
                if NUMPY_PANDAS_AVAILABLE:
                    data = np.random.random(100)
                else:
                    data = [np.random.random() for _ in range(100)]
                allocations.append(data)

            # Free every other allocation
            for i in range(0, len(allocations), 2):
                del allocations[i]

            # Force garbage collection
            gc.collect()

            return len(allocations)

        return self.run(fragment_memory, iterations=5)


class BenchmarkSuite:
    """Suite for running multiple benchmarks."""

    def __init__(self):
        self.benchmarks: Dict[str, PerformanceBenchmark] = {}
        self.results: List[BenchmarkResult] = []

    def add_benchmark(self, benchmark: PerformanceBenchmark):
        """Add a benchmark to the suite."""
        self.benchmarks[benchmark.name] = benchmark

    def run_function_benchmark(
        self,
        function: Callable,
        *args,
        iterations: int = 100,
        warmup: int = 10,
        **kwargs,
    ) -> BenchmarkResult:
        """Run a benchmark on a specific function."""
        benchmark = PerformanceBenchmark(f"Function_{function.__name__}")
        result = benchmark.run(
            function, *args, iterations=iterations, warmup=warmup, **kwargs
        )
        self.results.append(result)
        return result

    def run_all_benchmarks(self) -> List[BenchmarkResult]:
        """Run all benchmarks in the suite."""
        results = []
        for name, benchmark in self.benchmarks.items():
            try:
                # Run default benchmarks for each type
                if isinstance(benchmark, GeospatialBenchmark):
                    results.extend(
                        [
                            benchmark.benchmark_point_creation(),
                            benchmark.benchmark_polygon_intersection(),
                        ]
                    )
                elif isinstance(benchmark, IOBenchmark):
                    # Create temporary file for testing
                    temp_file = Path("/tmp/benchmark_test.dat")
                    results.extend(
                        [
                            benchmark.benchmark_csv_processing(),
                        ]
                    )
                elif isinstance(benchmark, MemoryBenchmark):
                    results.extend(
                        [
                            benchmark.benchmark_memory_allocation(),
                            benchmark.benchmark_memory_fragmentation(),
                        ]
                    )
            except Exception as e:
                logger.error(f"Benchmark {name} failed: {e}")

        self.results.extend(results)
        return results

    def get_system_metrics(self) -> SystemMetrics:
        """Get current system performance metrics."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk_io = psutil.disk_io_counters()
        network_io = psutil.net_io_counters()

        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_available_mb=memory.available / 1024 / 1024,
            disk_io_read_mb=disk_io.read_bytes / 1024 / 1024 if disk_io else 0,
            disk_io_write_mb=disk_io.write_bytes / 1024 / 1024 if disk_io else 0,
            network_io_sent_mb=network_io.bytes_sent / 1024 / 1024 if network_io else 0,
            network_io_recv_mb=network_io.bytes_recv / 1024 / 1024 if network_io else 0,
        )


def run_benchmark_suite() -> List[BenchmarkResult]:
    """Run a comprehensive benchmark suite."""
    suite = BenchmarkSuite()

    # Add standard benchmarks
    if GEOPANDAS_AVAILABLE:
        suite.add_benchmark(GeospatialBenchmark())

    suite.add_benchmark(IOBenchmark())
    suite.add_benchmark(MemoryBenchmark())

    return suite.run_all_benchmarks()


def create_benchmark_report(results: List[BenchmarkResult]) -> Dict[str, Any]:
    """Create a comprehensive benchmark report."""
    if not results:
        return {"error": "No benchmark results available"}

    report: Dict[str, Any] = {
        "summary": {
            "total_benchmarks": len(results),
            "timestamp": datetime.now().isoformat(),
            "fastest_operation": min(results, key=lambda r: r.mean_time).name,
            "slowest_operation": max(results, key=lambda r: r.mean_time).name,
            "highest_memory_usage": max(results, key=lambda r: r.memory_usage_mb).name,
        },
        "results": [],
        "system_info": {
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
            "platform": psutil.os.name,
        },
    }

    for result in results:
        report["results"].append(
            {
                "name": result.name,
                "mean_time_ms": result.mean_time * 1000,
                "operations_per_second": result.operations_per_second,
                "memory_usage_mb": result.memory_usage_mb,
                "cpu_usage_percent": result.cpu_usage_percent,
                "iterations": result.iterations,
                "std_dev_ms": result.std_dev * 1000,
            }
        )

    return report
