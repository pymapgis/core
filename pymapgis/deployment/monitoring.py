"""
Monitoring and Observability Infrastructure for PyMapGIS

Comprehensive monitoring with:
- Health check endpoints and probes
- Metrics collection and aggregation
- Logging and log aggregation
- Performance monitoring and alerting
- Service discovery and status tracking
- Dashboard and visualization setup
"""

import os
import json
import time
import logging
import psutil
import requests
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from threading import Thread
import queue

logger = logging.getLogger(__name__)

# Check for optional monitoring dependencies
try:
    import prometheus_client

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    logger.warning("Prometheus client not available")

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available")


@dataclass
class HealthStatus:
    """Health check status."""

    service: str
    status: str  # healthy, unhealthy, degraded
    timestamp: str
    response_time: float
    details: Dict[str, Any]
    error: Optional[str] = None


@dataclass
class MetricPoint:
    """Single metric data point."""

    name: str
    value: float
    timestamp: str
    labels: Dict[str, str]
    unit: str = ""


@dataclass
class LogEntry:
    """Log entry structure."""

    timestamp: str
    level: str
    service: str
    message: str
    metadata: Dict[str, Any]


@dataclass
class MonitoringConfig:
    """Monitoring configuration."""

    health_check_interval: int = 30
    metrics_collection_interval: int = 10
    log_retention_days: int = 30
    alert_thresholds: Dict[str, float] = None
    endpoints: List[str] = None

    def __post_init__(self):
        if self.alert_thresholds is None:
            self.alert_thresholds = {
                "cpu_usage": 80.0,
                "memory_usage": 85.0,
                "disk_usage": 90.0,
                "response_time": 5.0,
                "error_rate": 5.0,
            }

        if self.endpoints is None:
            self.endpoints = [
                "http://localhost:8000/health",
                "http://localhost:8000/ready",
            ]


class HealthCheckManager:
    """Health check management and monitoring."""

    def __init__(self, config: Optional[MonitoringConfig] = None):
        self.config = config or MonitoringConfig()
        self.health_history: List[HealthStatus] = []
        self.running = False
        self.check_thread: Optional[Thread] = None

    def check_endpoint_health(self, endpoint: str, timeout: int = 10) -> HealthStatus:
        """Check health of a single endpoint."""
        start_time = time.time()

        try:
            response = requests.get(endpoint, timeout=timeout)
            response_time = time.time() - start_time

            if response.status_code == 200:
                status = "healthy"
                details = {
                    "status_code": response.status_code,
                    "content_length": len(response.content),
                }

                # Try to parse JSON response for additional details
                try:
                    json_data = response.json()
                    details.update(json_data)
                except (ValueError, json.JSONDecodeError):
                    pass

                error = None
            else:
                status = "unhealthy"
                details = {"status_code": response.status_code}
                error = f"HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            response_time = timeout
            status = "unhealthy"
            details = {"timeout": timeout}
            error = "Request timeout"

        except requests.exceptions.ConnectionError:
            response_time = time.time() - start_time
            status = "unhealthy"
            details = {}
            error = "Connection error"

        except Exception as e:
            response_time = time.time() - start_time
            status = "unhealthy"
            details = {}
            error = str(e)

        return HealthStatus(
            service=endpoint,
            status=status,
            timestamp=datetime.now().isoformat(),
            response_time=response_time,
            details=details,
            error=error,
        )

    def check_system_health(self) -> HealthStatus:
        """Check system health metrics."""
        if not PSUTIL_AVAILABLE:
            return HealthStatus(
                service="system",
                status="unknown",
                timestamp=datetime.now().isoformat(),
                response_time=0.0,
                details={},
                error="psutil not available",
            )

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Determine overall health status
            status = "healthy"
            if (
                cpu_percent > self.config.alert_thresholds["cpu_usage"]
                or memory.percent > self.config.alert_thresholds["memory_usage"]
                or (disk.used / disk.total * 100)
                > self.config.alert_thresholds["disk_usage"]
            ):
                status = "degraded"

            details = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / 1024 / 1024 / 1024,
                "disk_usage_percent": disk.used / disk.total * 100,
                "disk_free_gb": disk.free / 1024 / 1024 / 1024,
                "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
            }

            return HealthStatus(
                service="system",
                status=status,
                timestamp=datetime.now().isoformat(),
                response_time=1.0,  # CPU check interval
                details=details,
            )

        except Exception as e:
            return HealthStatus(
                service="system",
                status="unhealthy",
                timestamp=datetime.now().isoformat(),
                response_time=0.0,
                details={},
                error=str(e),
            )

    def run_health_checks(self) -> List[HealthStatus]:
        """Run all configured health checks."""
        results = []

        # Check system health
        system_health = self.check_system_health()
        results.append(system_health)

        # Check endpoint health
        for endpoint in self.config.endpoints:
            endpoint_health = self.check_endpoint_health(endpoint)
            results.append(endpoint_health)

        # Store in history
        self.health_history.extend(results)

        # Cleanup old history
        cutoff_time = datetime.now() - timedelta(days=1)
        self.health_history = [
            h
            for h in self.health_history
            if datetime.fromisoformat(h.timestamp) > cutoff_time
        ]

        return results

    def start_monitoring(self):
        """Start continuous health monitoring."""
        if self.running:
            return

        self.running = True

        def monitor_loop():
            while self.running:
                try:
                    self.run_health_checks()
                    time.sleep(self.config.health_check_interval)
                except Exception as e:
                    logger.error(f"Health check monitoring error: {e}")
                    time.sleep(self.config.health_check_interval)

        self.check_thread = Thread(target=monitor_loop, daemon=True)
        self.check_thread.start()
        logger.info("Health check monitoring started")

    def stop_monitoring(self):
        """Stop health monitoring."""
        self.running = False
        if self.check_thread:
            self.check_thread.join(timeout=5)
        logger.info("Health check monitoring stopped")

    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary."""
        if not self.health_history:
            return {"status": "unknown", "services": 0}

        recent_checks = [
            h
            for h in self.health_history
            if datetime.fromisoformat(h.timestamp)
            > datetime.now() - timedelta(minutes=5)
        ]

        if not recent_checks:
            return {"status": "stale", "services": 0}

        # Group by service
        services: Dict[str, List[HealthStatus]] = {}
        for check in recent_checks:
            if check.service not in services:
                services[check.service] = []
            services[check.service].append(check)

        # Get latest status for each service
        service_statuses = {}
        for service, checks in services.items():
            latest_check = max(checks, key=lambda c: c.timestamp)
            service_statuses[service] = latest_check.status

        # Determine overall status
        if all(status == "healthy" for status in service_statuses.values()):
            overall_status = "healthy"
        elif any(status == "unhealthy" for status in service_statuses.values()):
            overall_status = "unhealthy"
        else:
            overall_status = "degraded"

        return {
            "status": overall_status,
            "services": len(service_statuses),
            "service_statuses": service_statuses,
            "last_check": max(recent_checks, key=lambda c: c.timestamp).timestamp,
        }


class MetricsCollector:
    """Metrics collection and aggregation."""

    def __init__(self, config: Optional[MonitoringConfig] = None):
        self.config = config or MonitoringConfig()
        self.metrics: List[MetricPoint] = []
        self.running = False
        self.collection_thread: Optional[Thread] = None

    def collect_system_metrics(self) -> List[MetricPoint]:
        """Collect system metrics."""
        if not PSUTIL_AVAILABLE:
            return []

        timestamp = datetime.now().isoformat()
        metrics = []

        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            metrics.append(
                MetricPoint(
                    name="cpu_usage_percent",
                    value=cpu_percent,
                    timestamp=timestamp,
                    labels={"host": "localhost"},
                    unit="percent",
                )
            )

            # Memory metrics
            memory = psutil.virtual_memory()
            metrics.append(
                MetricPoint(
                    name="memory_usage_percent",
                    value=memory.percent,
                    timestamp=timestamp,
                    labels={"host": "localhost"},
                    unit="percent",
                )
            )

            metrics.append(
                MetricPoint(
                    name="memory_available_bytes",
                    value=memory.available,
                    timestamp=timestamp,
                    labels={"host": "localhost"},
                    unit="bytes",
                )
            )

            # Disk metrics
            disk = psutil.disk_usage("/")
            metrics.append(
                MetricPoint(
                    name="disk_usage_percent",
                    value=(disk.used / disk.total) * 100,
                    timestamp=timestamp,
                    labels={"host": "localhost", "mount": "/"},
                    unit="percent",
                )
            )

            # Network metrics
            try:
                network = psutil.net_io_counters()
                metrics.append(
                    MetricPoint(
                        name="network_bytes_sent",
                        value=network.bytes_sent,
                        timestamp=timestamp,
                        labels={"host": "localhost"},
                        unit="bytes",
                    )
                )

                metrics.append(
                    MetricPoint(
                        name="network_bytes_recv",
                        value=network.bytes_recv,
                        timestamp=timestamp,
                        labels={"host": "localhost"},
                        unit="bytes",
                    )
                )
            except (AttributeError, OSError):
                pass

        except Exception as e:
            logger.error(f"System metrics collection error: {e}")

        return metrics

    def collect_application_metrics(self) -> List[MetricPoint]:
        """Collect application-specific metrics."""
        timestamp = datetime.now().isoformat()
        metrics = []

        # Example application metrics
        # In a real application, these would be collected from the application
        metrics.append(
            MetricPoint(
                name="requests_total",
                value=1000,  # Example value
                timestamp=timestamp,
                labels={"service": "pymapgis", "method": "GET"},
                unit="count",
            )
        )

        metrics.append(
            MetricPoint(
                name="request_duration_seconds",
                value=0.25,  # Example value
                timestamp=timestamp,
                labels={"service": "pymapgis", "endpoint": "/api/data"},
                unit="seconds",
            )
        )

        return metrics

    def start_collection(self):
        """Start metrics collection."""
        if self.running:
            return

        self.running = True

        def collection_loop():
            while self.running:
                try:
                    # Collect system metrics
                    system_metrics = self.collect_system_metrics()
                    self.metrics.extend(system_metrics)

                    # Collect application metrics
                    app_metrics = self.collect_application_metrics()
                    self.metrics.extend(app_metrics)

                    # Cleanup old metrics
                    cutoff_time = datetime.now() - timedelta(hours=24)
                    self.metrics = [
                        m
                        for m in self.metrics
                        if datetime.fromisoformat(m.timestamp) > cutoff_time
                    ]

                    time.sleep(self.config.metrics_collection_interval)

                except Exception as e:
                    logger.error(f"Metrics collection error: {e}")
                    time.sleep(self.config.metrics_collection_interval)

        self.collection_thread = Thread(target=collection_loop, daemon=True)
        self.collection_thread.start()
        logger.info("Metrics collection started")

    def stop_collection(self):
        """Stop metrics collection."""
        self.running = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        logger.info("Metrics collection stopped")

    def get_metrics_summary(self, time_range: int = 300) -> Dict[str, Any]:
        """Get metrics summary for the last N seconds."""
        cutoff_time = datetime.now() - timedelta(seconds=time_range)
        recent_metrics = [
            m for m in self.metrics if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]

        if not recent_metrics:
            return {"metrics": 0, "time_range": time_range}

        # Group by metric name
        metric_groups: Dict[str, List[float]] = {}
        for metric in recent_metrics:
            if metric.name not in metric_groups:
                metric_groups[metric.name] = []
            metric_groups[metric.name].append(metric.value)

        # Calculate statistics
        summary = {}
        for name, values in metric_groups.items():
            summary[name] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "latest": values[-1] if values else 0,
            }

        return {
            "metrics": len(recent_metrics),
            "time_range": time_range,
            "summary": summary,
        }


class LoggingManager:
    """Centralized logging management."""

    def __init__(self, config: Optional[MonitoringConfig] = None):
        self.config = config or MonitoringConfig()
        self.log_entries: List[LogEntry] = []
        self.log_queue: queue.Queue = queue.Queue()
        self.running = False
        self.processing_thread: Optional[Thread] = None

    def setup_logging(self, log_level: str = "INFO") -> bool:
        """Setup centralized logging configuration."""
        try:
            # Configure root logger
            logging.basicConfig(
                level=getattr(logging, log_level.upper()),
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler("pymapgis.log"),
                ],
            )

            # Add custom handler to capture logs
            class QueueHandler(logging.Handler):
                def __init__(self, log_queue):
                    super().__init__()
                    self.log_queue = log_queue

                def emit(self, record):
                    log_entry = LogEntry(
                        timestamp=datetime.fromtimestamp(record.created).isoformat(),
                        level=record.levelname,
                        service=record.name,
                        message=record.getMessage(),
                        metadata={
                            "module": record.module,
                            "function": record.funcName,
                            "line": record.lineno,
                        },
                    )
                    self.log_queue.put(log_entry)

            # Add queue handler to root logger
            queue_handler = QueueHandler(self.log_queue)
            logging.getLogger().addHandler(queue_handler)

            logger.info("Centralized logging configured")
            return True

        except Exception as e:
            logger.error(f"Failed to setup logging: {e}")
            return False

    def start_log_processing(self):
        """Start log processing."""
        if self.running:
            return

        self.running = True

        def process_logs():
            while self.running:
                try:
                    # Process log entries from queue
                    while not self.log_queue.empty():
                        log_entry = self.log_queue.get_nowait()
                        self.log_entries.append(log_entry)

                    # Cleanup old logs
                    cutoff_time = datetime.now() - timedelta(
                        days=self.config.log_retention_days
                    )
                    self.log_entries = [
                        entry
                        for entry in self.log_entries
                        if datetime.fromisoformat(entry.timestamp) > cutoff_time
                    ]

                    time.sleep(1)

                except Exception as e:
                    logger.error(f"Log processing error: {e}")
                    time.sleep(1)

        self.processing_thread = Thread(target=process_logs, daemon=True)
        self.processing_thread.start()
        logger.info("Log processing started")

    def stop_log_processing(self):
        """Stop log processing."""
        self.running = False
        if self.processing_thread:
            self.processing_thread.join(timeout=5)
        logger.info("Log processing stopped")

    def get_recent_logs(self, count: int = 100, level: str = None) -> List[LogEntry]:
        """Get recent log entries."""
        logs = self.log_entries[-count:] if count else self.log_entries

        if level:
            logs = [log for log in logs if log.level == level.upper()]

        return logs


class MonitoringManager:
    """Main monitoring orchestrator."""

    def __init__(self, config: Optional[MonitoringConfig] = None):
        self.config = config or MonitoringConfig()
        self.health_manager = HealthCheckManager(self.config)
        self.metrics_collector = MetricsCollector(self.config)
        self.logging_manager = LoggingManager(self.config)

    def setup_monitoring(self, monitoring_config: Dict[str, Any]) -> Dict[str, Any]:
        """Setup complete monitoring infrastructure."""
        try:
            results = {}

            # Setup logging
            log_level = monitoring_config.get("logging_level", "INFO")
            results["logging"] = self.logging_manager.setup_logging(log_level)

            # Start health monitoring
            if monitoring_config.get("health_checks", True):
                self.health_manager.start_monitoring()
                results["health_checks"] = True

            # Start metrics collection
            if monitoring_config.get("metrics_collection", True):
                self.metrics_collector.start_collection()
                results["metrics_collection"] = True

            # Start log processing
            self.logging_manager.start_log_processing()
            results["log_processing"] = True

            logger.info("Monitoring infrastructure setup completed")

            return {
                "success": True,
                "components": results,
                "config": asdict(self.config),
            }

        except Exception as e:
            logger.error(f"Monitoring setup failed: {e}")
            return {"success": False, "error": str(e)}

    def get_monitoring_dashboard(self) -> Dict[str, Any]:
        """Get monitoring dashboard data."""
        return {
            "health": self.health_manager.get_health_summary(),
            "metrics": self.metrics_collector.get_metrics_summary(),
            "logs": {
                "total_entries": len(self.logging_manager.log_entries),
                "recent_errors": len(
                    [
                        log
                        for log in self.logging_manager.get_recent_logs(100)
                        if log.level == "ERROR"
                    ]
                ),
            },
            "timestamp": datetime.now().isoformat(),
        }

    def shutdown(self):
        """Shutdown all monitoring components."""
        self.health_manager.stop_monitoring()
        self.metrics_collector.stop_collection()
        self.logging_manager.stop_log_processing()
        logger.info("Monitoring infrastructure shutdown completed")


# Convenience functions
def setup_monitoring(config: Dict[str, Any]) -> Dict[str, Any]:
    """Setup monitoring infrastructure."""
    manager = MonitoringManager()
    return manager.setup_monitoring(config)


def create_health_checks(endpoints: List[str]) -> List[HealthStatus]:
    """Create health checks for endpoints."""
    config = MonitoringConfig(endpoints=endpoints)
    manager = HealthCheckManager(config)
    return manager.run_health_checks()


def collect_metrics() -> List[MetricPoint]:
    """Collect current metrics."""
    collector = MetricsCollector()
    return collector.collect_system_metrics() + collector.collect_application_metrics()


def configure_logging(level: str = "INFO") -> bool:
    """Configure centralized logging."""
    manager = LoggingManager()
    return manager.setup_logging(level)
