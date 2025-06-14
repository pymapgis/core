"""
Load Testing Module

Provides comprehensive load testing capabilities for PyMapGIS including
concurrent user simulation, stress testing, and scalability validation.
"""

import time
import asyncio
import threading
import statistics
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import logging
import queue
import random

logger = logging.getLogger(__name__)

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests not available - HTTP load testing limited")

try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    logger.warning("aiohttp not available - async HTTP testing limited")


@dataclass
class LoadTestResult:
    """Container for load test results."""

    test_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_duration: float
    requests_per_second: float
    mean_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    min_response_time: float
    max_response_time: float
    error_rate: float
    concurrent_users: int
    timestamp: datetime = field(default_factory=datetime.now)
    errors: List[str] = field(default_factory=list)


@dataclass
class UserSession:
    """Represents a user session for load testing."""

    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    requests_made: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_response_time: float = 0.0


class ConcurrentUserSimulator:
    """Simulates concurrent users for load testing."""

    def __init__(self, max_users: int = 100):
        self.max_users = max_users
        self.active_sessions: Dict[str, UserSession] = {}
        self.results_queue: queue.Queue = queue.Queue()

    def simulate_user_behavior(
        self,
        user_id: str,
        target_function: Callable,
        duration: int,
        think_time_range: tuple = (1, 5),
    ) -> UserSession:
        """
        Simulate individual user behavior.

        Args:
            user_id: Unique user identifier
            target_function: Function to execute
            duration: Test duration in seconds
            think_time_range: Min/max think time between requests

        Returns:
            UserSession with results
        """
        session = UserSession(user_id=user_id, start_time=datetime.now())
        end_time = time.time() + duration

        while time.time() < end_time:
            try:
                start_request = time.time()
                target_function()
                end_request = time.time()

                session.requests_made += 1
                session.successful_requests += 1
                session.total_response_time += end_request - start_request

            except Exception as e:
                session.failed_requests += 1
                logger.debug(f"User {user_id} request failed: {e}")

            # Think time between requests
            think_time = random.uniform(*think_time_range)
            time.sleep(think_time)

        session.end_time = datetime.now()
        return session

    def run_concurrent_simulation(
        self, target_function: Callable, concurrent_users: int, duration: int
    ) -> LoadTestResult:
        """
        Run concurrent user simulation.

        Args:
            target_function: Function to load test
            concurrent_users: Number of concurrent users
            duration: Test duration in seconds

        Returns:
            LoadTestResult
        """
        start_time = time.time()
        sessions = []

        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []

            for i in range(concurrent_users):
                user_id = f"user_{i:04d}"
                future = executor.submit(
                    self.simulate_user_behavior, user_id, target_function, duration
                )
                futures.append(future)

            # Collect results
            for future in as_completed(futures):
                try:
                    session = future.result()
                    sessions.append(session)
                except Exception as e:
                    logger.error(f"User simulation failed: {e}")

        end_time = time.time()
        total_duration = end_time - start_time

        # Calculate aggregate statistics
        total_requests = sum(s.requests_made for s in sessions)
        successful_requests = sum(s.successful_requests for s in sessions)
        failed_requests = sum(s.failed_requests for s in sessions)

        response_times = []
        for session in sessions:
            if session.successful_requests > 0:
                avg_response_time = (
                    session.total_response_time / session.successful_requests
                )
                response_times.extend([avg_response_time] * session.successful_requests)

        if response_times:
            mean_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            response_times.sort()
            p95_response_time = response_times[int(len(response_times) * 0.95)]
            p99_response_time = response_times[int(len(response_times) * 0.99)]
            min_response_time = min(response_times)
            max_response_time = max(response_times)
        else:
            mean_response_time = median_response_time = 0
            p95_response_time = p99_response_time = 0
            min_response_time = max_response_time = 0

        return LoadTestResult(
            test_name=f"ConcurrentUsers_{concurrent_users}",
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            total_duration=total_duration,
            requests_per_second=(
                total_requests / total_duration if total_duration > 0 else 0
            ),
            mean_response_time=mean_response_time,
            median_response_time=median_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            error_rate=failed_requests / total_requests if total_requests > 0 else 0,
            concurrent_users=concurrent_users,
        )


class DataVolumeStressTester:
    """Tests system behavior under high data volume stress."""

    def __init__(self):
        self.test_results: List[LoadTestResult] = []

    def test_data_processing_volume(
        self, processing_function: Callable, data_sizes: List[int], iterations: int = 10
    ) -> List[LoadTestResult]:
        """
        Test data processing under increasing volume stress.

        Args:
            processing_function: Function that processes data
            data_sizes: List of data sizes to test
            iterations: Number of iterations per size

        Returns:
            List of LoadTestResult
        """
        results = []

        for size in data_sizes:
            response_times = []
            successful_operations = 0
            failed_operations = 0

            start_time = time.time()

            for i in range(iterations):
                try:
                    operation_start = time.time()
                    processing_function(size)
                    operation_end = time.time()

                    response_times.append(operation_end - operation_start)
                    successful_operations += 1

                except Exception as e:
                    failed_operations += 1
                    logger.debug(f"Data processing failed for size {size}: {e}")

            end_time = time.time()
            total_duration = end_time - start_time

            if response_times:
                mean_response_time = statistics.mean(response_times)
                median_response_time = statistics.median(response_times)
                response_times.sort()
                p95_response_time = response_times[int(len(response_times) * 0.95)]
                p99_response_time = response_times[int(len(response_times) * 0.99)]
                min_response_time = min(response_times)
                max_response_time = max(response_times)
            else:
                mean_response_time = median_response_time = 0
                p95_response_time = p99_response_time = 0
                min_response_time = max_response_time = 0

            result = LoadTestResult(
                test_name=f"DataVolume_{size}",
                total_requests=iterations,
                successful_requests=successful_operations,
                failed_requests=failed_operations,
                total_duration=total_duration,
                requests_per_second=(
                    iterations / total_duration if total_duration > 0 else 0
                ),
                mean_response_time=mean_response_time,
                median_response_time=median_response_time,
                p95_response_time=p95_response_time,
                p99_response_time=p99_response_time,
                min_response_time=min_response_time,
                max_response_time=max_response_time,
                error_rate=failed_operations / iterations if iterations > 0 else 0,
                concurrent_users=1,
            )

            results.append(result)
            self.test_results.append(result)

        return results


class StreamingLoadTester:
    """Load tester for streaming operations."""

    def __init__(self):
        self.active_streams: List[threading.Thread] = []

    def test_streaming_throughput(
        self, stream_function: Callable, concurrent_streams: int, duration: int
    ) -> LoadTestResult:
        """
        Test streaming throughput under load.

        Args:
            stream_function: Streaming function to test
            concurrent_streams: Number of concurrent streams
            duration: Test duration in seconds

        Returns:
            LoadTestResult
        """
        results_queue: queue.Queue = queue.Queue()

        def stream_worker(stream_id: int):
            """Worker function for individual stream."""
            start_time = time.time()
            end_time = start_time + duration
            operations = 0
            errors = 0

            while time.time() < end_time:
                try:
                    stream_function()
                    operations += 1
                except Exception as e:
                    errors += 1
                    logger.debug(f"Stream {stream_id} error: {e}")

            results_queue.put(
                {
                    "stream_id": stream_id,
                    "operations": operations,
                    "errors": errors,
                    "duration": time.time() - start_time,
                }
            )

        # Start concurrent streams
        threads = []
        start_time = time.time()

        for i in range(concurrent_streams):
            thread = threading.Thread(target=stream_worker, args=(i,))
            thread.start()
            threads.append(thread)

        # Wait for all streams to complete
        for thread in threads:
            thread.join()

        end_time = time.time()
        total_duration = end_time - start_time

        # Collect results
        total_operations = 0
        total_errors = 0

        while not results_queue.empty():
            result = results_queue.get()
            total_operations += result["operations"]
            total_errors += result["errors"]

        return LoadTestResult(
            test_name=f"StreamingLoad_{concurrent_streams}",
            total_requests=total_operations,
            successful_requests=total_operations - total_errors,
            failed_requests=total_errors,
            total_duration=total_duration,
            requests_per_second=(
                total_operations / total_duration if total_duration > 0 else 0
            ),
            mean_response_time=0,  # Not applicable for streaming
            median_response_time=0,
            p95_response_time=0,
            p99_response_time=0,
            min_response_time=0,
            max_response_time=0,
            error_rate=total_errors / total_operations if total_operations > 0 else 0,
            concurrent_users=concurrent_streams,
        )


class DatabaseLoadTester:
    """Load tester for database operations."""

    def __init__(self):
        self.connection_pool_size = 10

    def test_database_connections(
        self, db_function: Callable, concurrent_connections: int, duration: int
    ) -> LoadTestResult:
        """
        Test database under concurrent connection load.

        Args:
            db_function: Database operation function
            concurrent_connections: Number of concurrent connections
            duration: Test duration in seconds

        Returns:
            LoadTestResult
        """
        # This is a placeholder for database load testing
        # In a real implementation, this would use actual database connections

        def simulate_db_operation():
            # Simulate database operation with random delay
            time.sleep(random.uniform(0.01, 0.1))
            if random.random() < 0.05:  # 5% failure rate
                raise Exception("Simulated database error")

        simulator = ConcurrentUserSimulator()
        return simulator.run_concurrent_simulation(
            simulate_db_operation, concurrent_connections, duration
        )


class LoadTester:
    """Main load testing orchestrator."""

    def __init__(self):
        self.user_simulator = ConcurrentUserSimulator()
        self.data_stress_tester = DataVolumeStressTester()
        self.streaming_tester = StreamingLoadTester()
        self.database_tester = DatabaseLoadTester()
        self.results: List[LoadTestResult] = []

    def simulate_concurrent_load(
        self, target_function: Callable, concurrent_users: int, duration: int
    ) -> LoadTestResult:
        """Simulate concurrent user load."""
        result = self.user_simulator.run_concurrent_simulation(
            target_function, concurrent_users, duration
        )
        self.results.append(result)
        return result

    def test_data_volume_stress(
        self, processing_function: Callable, data_sizes: List[int]
    ) -> List[LoadTestResult]:
        """Test data volume stress."""
        results = self.data_stress_tester.test_data_processing_volume(
            processing_function, data_sizes
        )
        self.results.extend(results)
        return results

    def test_streaming_load(
        self, stream_function: Callable, concurrent_streams: int, duration: int
    ) -> LoadTestResult:
        """Test streaming load."""
        result = self.streaming_tester.test_streaming_throughput(
            stream_function, concurrent_streams, duration
        )
        self.results.append(result)
        return result


def run_load_test(
    target_function: Callable, test_config: Dict[str, Any]
) -> List[LoadTestResult]:
    """
    Run a comprehensive load test.

    Args:
        target_function: Function to load test
        test_config: Load test configuration

    Returns:
        List of LoadTestResult
    """
    load_tester = LoadTester()
    results = []

    # Concurrent user tests
    if "concurrent_users" in test_config:
        for user_count in test_config["concurrent_users"]:
            result = load_tester.simulate_concurrent_load(
                target_function, user_count, test_config.get("duration", 60)
            )
            results.append(result)

    return results


def generate_load_report(results: List[LoadTestResult]) -> Dict[str, Any]:
    """Generate a comprehensive load test report."""
    if not results:
        return {"error": "No load test results available"}

    report: Dict[str, Any] = {
        "summary": {
            "total_tests": len(results),
            "timestamp": datetime.now().isoformat(),
            "highest_rps": max(
                results, key=lambda r: r.requests_per_second
            ).requests_per_second,
            "lowest_error_rate": min(results, key=lambda r: r.error_rate).error_rate,
            "fastest_response": min(
                results, key=lambda r: r.mean_response_time
            ).mean_response_time,
        },
        "results": [],
    }

    for result in results:
        report["results"].append(
            {
                "test_name": result.test_name,
                "requests_per_second": result.requests_per_second,
                "error_rate": result.error_rate * 100,  # Convert to percentage
                "mean_response_time_ms": result.mean_response_time * 1000,
                "p95_response_time_ms": result.p95_response_time * 1000,
                "concurrent_users": result.concurrent_users,
                "total_requests": result.total_requests,
                "successful_requests": result.successful_requests,
            }
        )

    return report
