"""
Performance Profiling Module

Provides comprehensive profiling capabilities for memory usage, CPU performance,
and I/O operations analysis.
"""

import time
import gc
import tracemalloc
import psutil
import threading
import functools
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

try:
    import cProfile
    import pstats
    import io

    CPROFILE_AVAILABLE = True
except ImportError:
    CPROFILE_AVAILABLE = False
    logger.warning("cProfile not available - CPU profiling limited")

try:
    import memory_profiler

    MEMORY_PROFILER_AVAILABLE = True
except ImportError:
    MEMORY_PROFILER_AVAILABLE = False
    logger.warning("memory_profiler not available - detailed memory analysis limited")


@dataclass
class ProfileResult:
    """Container for profiling results."""

    function_name: str
    execution_time: float
    memory_usage_mb: float
    peak_memory_mb: float
    cpu_time: float
    cpu_percent: float
    memory_allocations: int
    memory_deallocations: int
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemorySnapshot:
    """Memory usage snapshot."""

    timestamp: datetime
    current_memory_mb: float
    peak_memory_mb: float
    allocated_blocks: int
    total_size_mb: float


@dataclass
class CPUSnapshot:
    """CPU usage snapshot."""

    timestamp: datetime
    cpu_percent: float
    cpu_times: Dict[str, float]
    load_average: List[float]


class PerformanceProfiler:
    """Main performance profiler."""

    def __init__(self):
        self.profiling_active = False
        self.memory_snapshots: List[MemorySnapshot] = []
        self.cpu_snapshots: List[CPUSnapshot] = []

    def profile_function(self, func: Callable, *args, **kwargs) -> ProfileResult:
        """
        Profile a function's performance.

        Args:
            func: Function to profile
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            ProfileResult
        """
        # Start memory tracking
        tracemalloc.start()
        gc.collect()

        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # CPU profiling setup
        if CPROFILE_AVAILABLE:
            profiler = cProfile.Profile()
            profiler.enable()

        cpu_before = process.cpu_percent()
        start_time = time.perf_counter()

        try:
            # Execute function
            result = func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Function execution failed during profiling: {e}")
            raise
        finally:
            end_time = time.perf_counter()
            cpu_after = process.cpu_percent()

            # Stop CPU profiling
            if CPROFILE_AVAILABLE:
                profiler.disable()

            # Get memory statistics
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            final_memory = process.memory_info().rss / 1024 / 1024  # MB

        execution_time = end_time - start_time
        memory_usage = max(final_memory - initial_memory, 0)
        peak_memory = peak / 1024 / 1024  # Convert to MB
        cpu_time = max(cpu_after - cpu_before, 0)

        # Get CPU profiling stats
        cpu_stats: Dict[str, Any] = {}
        if CPROFILE_AVAILABLE:
            stats_stream = io.StringIO()
            stats = pstats.Stats(profiler, stream=stats_stream)
            stats.sort_stats("cumulative")
            # Access stats attributes safely
            cpu_stats = {
                "total_calls": getattr(stats, "total_calls", 0),
                "primitive_calls": getattr(stats, "prim_calls", 0),
                "total_time": getattr(stats, "total_tt", 0.0),
            }

        return ProfileResult(
            function_name=func.__name__,
            execution_time=execution_time,
            memory_usage_mb=memory_usage,
            peak_memory_mb=peak_memory,
            cpu_time=execution_time,  # Wall clock time
            cpu_percent=cpu_time,
            memory_allocations=0,  # Would need more detailed tracking
            memory_deallocations=0,
            metadata={
                "args_count": len(args),
                "kwargs_count": len(kwargs),
                "cpu_stats": cpu_stats,
            },
        )

    def profile_memory_usage(
        self, func: Callable, *args, precision: int = 1, **kwargs
    ) -> Dict[str, Any]:
        """
        Profile memory usage of a function.

        Args:
            func: Function to profile
            *args: Function arguments
            precision: Memory measurement precision
            **kwargs: Function keyword arguments

        Returns:
            Memory profiling results
        """
        if MEMORY_PROFILER_AVAILABLE:
            # Use memory_profiler for detailed analysis
            mem_usage = memory_profiler.memory_usage(
                (func, args, kwargs), precision=precision
            )

            return {
                "function_name": func.__name__,
                "memory_usage_mb": mem_usage,
                "peak_memory_mb": max(mem_usage),
                "min_memory_mb": min(mem_usage),
                "memory_growth_mb": mem_usage[-1] - mem_usage[0],
                "samples": len(mem_usage),
            }
        else:
            # Fallback to basic memory tracking
            result = self.profile_function(func, *args, **kwargs)
            return {
                "function_name": result.function_name,
                "memory_usage_mb": result.memory_usage_mb,
                "peak_memory_mb": result.peak_memory_mb,
                "min_memory_mb": 0,
                "memory_growth_mb": result.memory_usage_mb,
                "samples": 1,
            }


class MemoryProfiler:
    """Specialized memory profiler."""

    def __init__(self):
        self.snapshots: List[MemorySnapshot] = []
        self.monitoring = False
        self.monitor_thread = None

    def take_snapshot(self) -> MemorySnapshot:
        """Take a memory usage snapshot."""
        if not tracemalloc.is_tracing():
            tracemalloc.start()

        current, peak = tracemalloc.get_traced_memory()
        stats = tracemalloc.take_snapshot().statistics("lineno")

        snapshot = MemorySnapshot(
            timestamp=datetime.now(),
            current_memory_mb=current / 1024 / 1024,
            peak_memory_mb=peak / 1024 / 1024,
            allocated_blocks=len(stats),
            total_size_mb=sum(stat.size for stat in stats) / 1024 / 1024,
        )

        self.snapshots.append(snapshot)
        return snapshot

    def start_monitoring(self, interval: float = 1.0):
        """Start continuous memory monitoring."""
        if self.monitoring:
            return

        self.monitoring = True

        def monitor_loop():
            while self.monitoring:
                self.take_snapshot()
                time.sleep(interval)

        self.monitor_thread = threading.Thread(target=monitor_loop)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop continuous memory monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()

    def get_memory_trend(self) -> Dict[str, Any]:
        """Analyze memory usage trends."""
        if len(self.snapshots) < 2:
            return {"error": "Insufficient snapshots for trend analysis"}

        memory_values = [s.current_memory_mb for s in self.snapshots]
        peak_values = [s.peak_memory_mb for s in self.snapshots]

        return {
            "total_snapshots": len(self.snapshots),
            "memory_trend": {
                "initial_mb": memory_values[0],
                "final_mb": memory_values[-1],
                "peak_mb": max(peak_values),
                "growth_mb": memory_values[-1] - memory_values[0],
                "average_mb": sum(memory_values) / len(memory_values),
            },
            "potential_leak": memory_values[-1] > memory_values[0] * 1.5,
        }


class CPUProfiler:
    """Specialized CPU profiler."""

    def __init__(self):
        self.snapshots: List[CPUSnapshot] = []
        self.monitoring = False
        self.monitor_thread = None

    def take_snapshot(self) -> CPUSnapshot:
        """Take a CPU usage snapshot."""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_times = psutil.cpu_times()._asdict()

        try:
            load_avg = list(psutil.getloadavg())
        except AttributeError:
            # getloadavg not available on Windows
            load_avg = [0.0, 0.0, 0.0]

        snapshot = CPUSnapshot(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            cpu_times=cpu_times,
            load_average=load_avg,
        )

        self.snapshots.append(snapshot)
        return snapshot

    def start_monitoring(self, interval: float = 1.0):
        """Start continuous CPU monitoring."""
        if self.monitoring:
            return

        self.monitoring = True

        def monitor_loop():
            while self.monitoring:
                self.take_snapshot()
                time.sleep(interval)

        self.monitor_thread = threading.Thread(target=monitor_loop)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop continuous CPU monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()

    def get_cpu_analysis(self) -> Dict[str, Any]:
        """Analyze CPU usage patterns."""
        if not self.snapshots:
            return {"error": "No CPU snapshots available"}

        cpu_values = [s.cpu_percent for s in self.snapshots]

        return {
            "total_snapshots": len(self.snapshots),
            "cpu_analysis": {
                "average_cpu_percent": sum(cpu_values) / len(cpu_values),
                "peak_cpu_percent": max(cpu_values),
                "min_cpu_percent": min(cpu_values),
                "high_cpu_periods": len([v for v in cpu_values if v > 80]),
                "load_averages": (
                    {
                        "1min": self.snapshots[-1].load_average[0],
                        "5min": self.snapshots[-1].load_average[1],
                        "15min": self.snapshots[-1].load_average[2],
                    }
                    if self.snapshots
                    else {}
                ),
            },
        }


class IOProfiler:
    """I/O operations profiler."""

    def __init__(self):
        self.io_stats = []

    def profile_io_operation(
        self, operation: Callable, *args, **kwargs
    ) -> Dict[str, Any]:
        """Profile I/O operation performance."""
        process = psutil.Process()

        # Get initial I/O stats
        try:
            initial_io = process.io_counters()
        except psutil.AccessDenied:
            initial_io = None

        start_time = time.perf_counter()

        try:
            result = operation(*args, **kwargs)
        except Exception as e:
            logger.error(f"I/O operation failed during profiling: {e}")
            raise
        finally:
            end_time = time.perf_counter()

            # Get final I/O stats
            try:
                final_io = process.io_counters()
            except psutil.AccessDenied:
                final_io = None

        execution_time = end_time - start_time

        io_stats = {}
        if initial_io and final_io:
            io_stats = {
                "read_bytes": final_io.read_bytes - initial_io.read_bytes,
                "write_bytes": final_io.write_bytes - initial_io.write_bytes,
                "read_count": final_io.read_count - initial_io.read_count,
                "write_count": final_io.write_count - initial_io.write_count,
                "read_mb_per_sec": (
                    (final_io.read_bytes - initial_io.read_bytes)
                    / 1024
                    / 1024
                    / execution_time
                    if execution_time > 0
                    else 0
                ),
                "write_mb_per_sec": (
                    (final_io.write_bytes - initial_io.write_bytes)
                    / 1024
                    / 1024
                    / execution_time
                    if execution_time > 0
                    else 0
                ),
            }

        return {
            "operation_name": operation.__name__,
            "execution_time": execution_time,
            "io_stats": io_stats,
        }


class ResourceMonitor:
    """System resource monitor."""

    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.resource_history = []

    def get_current_resources(self) -> Dict[str, Any]:
        """Get current system resource usage."""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        try:
            network = psutil.net_io_counters()
            network_stats = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
            }
        except (AttributeError, OSError):
            network_stats = {}

        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": cpu_percent,
            "memory": {
                "total_gb": memory.total / 1024 / 1024 / 1024,
                "available_gb": memory.available / 1024 / 1024 / 1024,
                "percent": memory.percent,
                "used_gb": memory.used / 1024 / 1024 / 1024,
            },
            "disk": {
                "total_gb": disk.total / 1024 / 1024 / 1024,
                "free_gb": disk.free / 1024 / 1024 / 1024,
                "used_gb": disk.used / 1024 / 1024 / 1024,
                "percent": (disk.used / disk.total) * 100,
            },
            "network": network_stats,
        }

    def start_monitoring(self, interval: float = 5.0):
        """Start continuous resource monitoring."""
        if self.monitoring:
            return

        self.monitoring = True

        def monitor_loop():
            while self.monitoring:
                resources = self.get_current_resources()
                self.resource_history.append(resources)
                time.sleep(interval)

        self.monitor_thread = threading.Thread(target=monitor_loop)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop continuous resource monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()

    def get_resource_summary(self) -> Dict[str, Any]:
        """Get resource usage summary."""
        if not self.resource_history:
            return self.get_current_resources()

        cpu_values = [r["cpu_percent"] for r in self.resource_history]
        memory_values = [r["memory"]["percent"] for r in self.resource_history]

        return {
            "monitoring_duration": len(self.resource_history),
            "cpu_summary": {
                "average": sum(cpu_values) / len(cpu_values),
                "peak": max(cpu_values),
                "min": min(cpu_values),
            },
            "memory_summary": {
                "average": sum(memory_values) / len(memory_values),
                "peak": max(memory_values),
                "min": min(memory_values),
            },
            "current": self.get_current_resources(),
        }


# Convenience functions
def profile_function(func: Callable) -> Callable:
    """Decorator to profile a function."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        profiler = PerformanceProfiler()
        result_data = profiler.profile_function(func, *args, **kwargs)
        logger.info(f"Profile results for {func.__name__}: {result_data}")
        return func(*args, **kwargs)

    return wrapper


@contextmanager
def monitor_resources(interval: float = 1.0):
    """Context manager for resource monitoring."""
    monitor = ResourceMonitor()
    monitor.start_monitoring(interval)
    try:
        yield monitor
    finally:
        monitor.stop_monitoring()
