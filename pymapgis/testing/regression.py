"""
Performance Regression Testing Module

Provides capabilities for detecting performance regressions by comparing
current performance metrics against historical baselines.
"""

import json
import statistics
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceBaseline:
    """Container for performance baseline data."""

    test_name: str
    metric_name: str
    baseline_value: float
    baseline_std_dev: float
    sample_count: int
    created_date: datetime
    last_updated: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RegressionResult:
    """Container for regression test results."""

    test_name: str
    current_value: float
    baseline_value: float
    deviation_percent: float
    is_regression: bool
    severity: str  # 'low', 'medium', 'high', 'critical'
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)


class BaselineManager:
    """Manages performance baselines storage and retrieval."""

    def __init__(self, baseline_file: str = "performance_baselines.json"):
        self.baseline_file = Path(baseline_file)
        self.baselines: Dict[str, PerformanceBaseline] = {}
        self.load_baselines()

    def load_baselines(self):
        """Load baselines from file."""
        if self.baseline_file.exists():
            try:
                with open(self.baseline_file, "r") as f:
                    data = json.load(f)

                for key, baseline_data in data.items():
                    # Convert datetime strings back to datetime objects
                    baseline_data["created_date"] = datetime.fromisoformat(
                        baseline_data["created_date"]
                    )
                    baseline_data["last_updated"] = datetime.fromisoformat(
                        baseline_data["last_updated"]
                    )

                    self.baselines[key] = PerformanceBaseline(**baseline_data)

                logger.info(f"Loaded {len(self.baselines)} performance baselines")
            except Exception as e:
                logger.error(f"Failed to load baselines: {e}")
                self.baselines = {}

    def save_baselines(self):
        """Save baselines to file."""
        try:
            # Convert baselines to serializable format
            data = {}
            for key, baseline in self.baselines.items():
                baseline_dict = asdict(baseline)
                # Convert datetime objects to strings
                baseline_dict["created_date"] = baseline.created_date.isoformat()
                baseline_dict["last_updated"] = baseline.last_updated.isoformat()
                data[key] = baseline_dict

            with open(self.baseline_file, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Saved {len(self.baselines)} performance baselines")
        except Exception as e:
            logger.error(f"Failed to save baselines: {e}")

    def get_baseline(
        self, test_name: str, metric_name: str = "execution_time"
    ) -> Optional[PerformanceBaseline]:
        """Get baseline for a specific test."""
        key = f"{test_name}_{metric_name}"
        return self.baselines.get(key)

    def set_baseline(
        self,
        test_name: str,
        values: List[float],
        metric_name: str = "execution_time",
        metadata: Dict[str, Any] = None,
    ):
        """Set or update baseline for a test."""
        if not values:
            raise ValueError("Cannot create baseline from empty values list")

        key = f"{test_name}_{metric_name}"
        baseline_value = statistics.mean(values)
        baseline_std_dev = statistics.stdev(values) if len(values) > 1 else 0.0

        now = datetime.now()

        if key in self.baselines:
            # Update existing baseline
            baseline = self.baselines[key]
            baseline.baseline_value = baseline_value
            baseline.baseline_std_dev = baseline_std_dev
            baseline.sample_count = len(values)
            baseline.last_updated = now
            if metadata:
                baseline.metadata.update(metadata)
        else:
            # Create new baseline
            baseline = PerformanceBaseline(
                test_name=test_name,
                metric_name=metric_name,
                baseline_value=baseline_value,
                baseline_std_dev=baseline_std_dev,
                sample_count=len(values),
                created_date=now,
                last_updated=now,
                metadata=metadata or {},
            )
            self.baselines[key] = baseline

        self.save_baselines()
        logger.info(
            f"Updated baseline for {test_name}: {baseline_value:.4f} ± {baseline_std_dev:.4f}"
        )

    def cleanup_old_baselines(self, retention_days: int = 30):
        """Remove baselines older than retention period."""
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        keys_to_remove = []
        for key, baseline in self.baselines.items():
            if baseline.last_updated < cutoff_date:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self.baselines[key]

        if keys_to_remove:
            self.save_baselines()
            logger.info(f"Cleaned up {len(keys_to_remove)} old baselines")


class RegressionDetector:
    """Detects performance regressions against baselines."""

    def __init__(self, baseline_manager: BaselineManager):
        self.baseline_manager = baseline_manager

    def detect_regression(
        self,
        test_name: str,
        current_value: float,
        metric_name: str = "execution_time",
        tolerance_percent: float = 10.0,
    ) -> RegressionResult:
        """
        Detect if current performance represents a regression.

        Args:
            test_name: Name of the test
            current_value: Current performance value
            metric_name: Name of the metric being tested
            tolerance_percent: Acceptable deviation percentage

        Returns:
            RegressionResult
        """
        baseline = self.baseline_manager.get_baseline(test_name, metric_name)

        if not baseline:
            return RegressionResult(
                test_name=test_name,
                current_value=current_value,
                baseline_value=0.0,
                deviation_percent=0.0,
                is_regression=False,
                severity="unknown",
                confidence=0.0,
                details={"error": "No baseline available"},
            )

        # Calculate deviation
        deviation_percent = (
            (current_value - baseline.baseline_value) / baseline.baseline_value
        ) * 100

        # Determine if this is a regression (performance got worse)
        # For execution time, higher values are worse
        # For throughput metrics, lower values are worse
        is_worse = deviation_percent > tolerance_percent

        # Calculate confidence based on standard deviation
        if baseline.baseline_std_dev > 0:
            z_score = (
                abs(current_value - baseline.baseline_value) / baseline.baseline_std_dev
            )
            confidence = min(z_score / 3.0, 1.0)  # Normalize to 0-1 range
        else:
            confidence = 1.0 if abs(deviation_percent) > tolerance_percent else 0.0

        # Determine severity
        severity = self._calculate_severity(abs(deviation_percent), tolerance_percent)

        return RegressionResult(
            test_name=test_name,
            current_value=current_value,
            baseline_value=baseline.baseline_value,
            deviation_percent=deviation_percent,
            is_regression=is_worse,
            severity=severity,
            confidence=confidence,
            details={
                "baseline_std_dev": baseline.baseline_std_dev,
                "baseline_sample_count": baseline.sample_count,
                "baseline_age_days": (datetime.now() - baseline.last_updated).days,
                "tolerance_percent": tolerance_percent,
                "z_score": z_score if baseline.baseline_std_dev > 0 else None,
            },
        )

    def _calculate_severity(
        self, deviation_percent: float, tolerance_percent: float
    ) -> str:
        """Calculate regression severity based on deviation."""
        if deviation_percent <= tolerance_percent:
            return "none"
        elif deviation_percent <= tolerance_percent * 2:
            return "low"
        elif deviation_percent <= tolerance_percent * 4:
            return "medium"
        elif deviation_percent <= tolerance_percent * 8:
            return "high"
        else:
            return "critical"

    def batch_regression_check(
        self, test_results: Dict[str, float], tolerance_percent: float = 10.0
    ) -> List[RegressionResult]:
        """
        Check multiple test results for regressions.

        Args:
            test_results: Dictionary of test_name -> performance_value
            tolerance_percent: Acceptable deviation percentage

        Returns:
            List of RegressionResult
        """
        results = []

        for test_name, current_value in test_results.items():
            regression_result = self.detect_regression(
                test_name, current_value, tolerance_percent=tolerance_percent
            )
            results.append(regression_result)

        return results


class RegressionTester:
    """Main regression testing orchestrator."""

    def __init__(self, baseline_file: str = "performance_baselines.json"):
        self.baseline_manager = BaselineManager(baseline_file)
        self.detector = RegressionDetector(self.baseline_manager)
        self.test_history: List[RegressionResult] = []

    def update_baseline(
        self,
        test_name: str,
        values: List[float],
        metric_name: str = "execution_time",
        metadata: Dict[str, Any] = None,
    ):
        """Update performance baseline for a test."""
        self.baseline_manager.set_baseline(test_name, values, metric_name, metadata)

    def detect_regression(
        self,
        test_name: str,
        current_value: float,
        baseline_file: str = None,
        tolerance_percent: float = 10.0,
    ) -> bool:
        """
        Detect if current performance represents a regression.

        Args:
            test_name: Name of the test
            current_value: Current performance value
            baseline_file: Optional specific baseline file
            tolerance_percent: Acceptable deviation percentage

        Returns:
            True if regression detected, False otherwise
        """
        if baseline_file and baseline_file != self.baseline_manager.baseline_file:
            # Use different baseline manager for this check
            temp_manager = BaselineManager(baseline_file)
            temp_detector = RegressionDetector(temp_manager)
            result = temp_detector.detect_regression(
                test_name, current_value, tolerance_percent=tolerance_percent
            )
        else:
            result = self.detector.detect_regression(
                test_name, current_value, tolerance_percent=tolerance_percent
            )

        self.test_history.append(result)

        if result.is_regression:
            logger.warning(
                f"Performance regression detected in {test_name}: "
                f"{result.deviation_percent:.2f}% deviation (severity: {result.severity})"
            )

        return result.is_regression

    def generate_regression_report(
        self, include_history: bool = True
    ) -> Dict[str, Any]:
        """Generate comprehensive regression test report."""
        recent_results = self.test_history[-50:] if include_history else []
        regressions = [r for r in recent_results if r.is_regression]

        report: Dict[str, Any] = {
            "summary": {
                "total_tests": len(recent_results),
                "regressions_detected": len(regressions),
                "regression_rate": (
                    len(regressions) / len(recent_results) if recent_results else 0
                ),
                "timestamp": datetime.now().isoformat(),
            },
            "baselines": {
                "total_baselines": len(self.baseline_manager.baselines),
                "baseline_file": str(self.baseline_manager.baseline_file),
            },
            "regressions": [],
        }

        # Add regression details
        for regression in regressions:
            report["regressions"].append(
                {
                    "test_name": regression.test_name,
                    "deviation_percent": regression.deviation_percent,
                    "severity": regression.severity,
                    "confidence": regression.confidence,
                    "current_value": regression.current_value,
                    "baseline_value": regression.baseline_value,
                    "timestamp": regression.timestamp.isoformat(),
                }
            )

        # Add severity breakdown
        severity_counts: Dict[str, int] = {}
        for regression in regressions:
            severity_counts[regression.severity] = (
                severity_counts.get(regression.severity, 0) + 1
            )

        report["severity_breakdown"] = severity_counts

        return report

    def cleanup_old_data(self, retention_days: int = 30):
        """Clean up old baseline and test data."""
        self.baseline_manager.cleanup_old_baselines(retention_days)

        # Clean up old test history
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        self.test_history = [r for r in self.test_history if r.timestamp > cutoff_date]


# Convenience functions
def detect_performance_regression(
    test_name: str,
    current_result: float,
    baseline_file: str = None,
    tolerance: float = 10.0,
) -> bool:
    """
    Convenience function to detect performance regression.

    Args:
        test_name: Name of the test
        current_result: Current performance result
        baseline_file: Optional baseline file path
        tolerance: Regression tolerance percentage

    Returns:
        True if regression detected, False otherwise
    """
    tester = RegressionTester(baseline_file or "performance_baselines.json")
    return tester.detect_regression(
        test_name, current_result, tolerance_percent=tolerance
    )


def update_performance_baseline(
    test_name: str,
    values: List[float],
    baseline_file: str = None,
    metadata: Dict[str, Any] = None,
):
    """
    Convenience function to update performance baseline.

    Args:
        test_name: Name of the test
        values: List of performance values
        baseline_file: Optional baseline file path
        metadata: Optional metadata
    """
    tester = RegressionTester(baseline_file or "performance_baselines.json")
    tester.update_baseline(test_name, values, metadata=metadata)
