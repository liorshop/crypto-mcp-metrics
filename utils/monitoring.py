import time
from typing import Dict, Any, Optional, List, ContextManager
from contextlib import contextmanager
import psutil
import logging
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class MetricPoint:
    """Represents a single metric measurement"""
    value: float
    timestamp: float
    tags: Dict[str, str]

class PerformanceMonitor:
    """Monitors and tracks performance metrics"""

    def __init__(self):
        self.metrics: Dict[str, List[MetricPoint]] = defaultdict(list)
        self.logger = logging.getLogger('performance_monitor')

    def record_metric(self, 
                      name: str, 
                      value: float, 
                      tags: Optional[Dict[str, str]] = None) -> None:
        """Record a metric measurement"""
        self.metrics[name].append(
            MetricPoint(
                value=value,
                timestamp=time.time(),
                tags=tags or {}
            )
        )
        self._log_metric(name, value, tags)

    @contextmanager
    def measure(self, name: str, tags: Optional[Dict[str, str]] = None) -> ContextManager:
        """Context manager to measure execution time"""
        start_time = time.time()
        try:
            yield
        finally:
            end_time = time.time()
            duration = end_time - start_time
            self.record_metric(f'{name}_duration', duration, tags)

    def get_metrics(self, name: str) -> List[MetricPoint]:
        """Get all measurements for a metric"""
        return self.metrics.get(name, [])

    def get_latest(self, name: str) -> Optional[MetricPoint]:
        """Get the latest measurement for a metric"""
        metrics = self.metrics.get(name, [])
        return metrics[-1] if metrics else None

    def get_average(self, name: str) -> Optional[float]:
        """Get the average value for a metric"""
        metrics = self.metrics.get(name, [])
        if not metrics:
            return None
        return sum(m.value for m in metrics) / len(metrics)

    def get_summary(self, name: str) -> Dict[str, float]:
        """Get statistical summary for a metric"""
        metrics = self.metrics.get(name, [])
        if not metrics:
            return {}

        values = [m.value for m in metrics]
        return {
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'count': len(values)
        }

    def _log_metric(self, 
                    name: str, 
                    value: float, 
                    tags: Optional[Dict[str, str]]) -> None:
        """Log metric measurement"""
        tag_str = ' '.join(f'{k}={v}' for k, v in (tags or {}).items())
        self.logger.info(f'Metric: {name}={value} {tag_str}'.strip())

class ResourceMonitor:
    """Monitors system resource usage"""

    def __init__(self):
        self.process = psutil.Process()
        self.performance_monitor = PerformanceMonitor()

    def start_monitoring(self, interval: float = 1.0) -> None:
        """Start monitoring resource usage"""
        import threading
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Stop monitoring resource usage"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()

    def _monitor_loop(self, interval: float) -> None:
        """Monitor loop to collect resource metrics"""
        while self.monitoring:
            try:
                # CPU Usage
                cpu_percent = self.process.cpu_percent()
                self.performance_monitor.record_metric('cpu_usage', cpu_percent)

                # Memory Usage
                memory_info = self.process.memory_info()
                self.performance_monitor.record_metric('memory_rss', memory_info.rss)
                self.performance_monitor.record_metric('memory_vms', memory_info.vms)

                # IO Counters
                io_counters = self.process.io_counters()
                self.performance_monitor.record_metric('io_read_bytes', io_counters.read_bytes)
                self.performance_monitor.record_metric('io_write_bytes', io_counters.write_bytes)

                # Thread Count
                thread_count = len(self.process.threads())
                self.performance_monitor.record_metric('thread_count', thread_count)

                time.sleep(interval)

            except Exception as e:
                logging.error(f'Error in resource monitoring: {str(e)}')

class PerformanceAnalyzer:
    """Analyzes performance metrics"""

    def __init__(self, performance_monitor: PerformanceMonitor):
        self.monitor = performance_monitor

    def analyze_response_times(self, time_window: float = 300) -> Dict[str, Any]:
        """Analyze response times over a time window"""
        current_time = time.time()
        metrics = self.monitor.get_metrics('request_duration')
        recent_metrics = [
            m for m in metrics 
            if current_time - m.timestamp <= time_window
        ]

        if not recent_metrics:
            return {}

        response_times = [m.value for m in recent_metrics]
        return {
            'avg_response_time': sum(response_times) / len(response_times),
            'p95_response_time': self._percentile(response_times, 95),
            'p99_response_time': self._percentile(response_times, 99),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times)
        }

    def analyze_error_rates(self, time_window: float = 300) -> Dict[str, float]:
        """Analyze error rates over a time window"""
        current_time = time.time()
        error_metrics = self.monitor.get_metrics('request_error')
        total_metrics = self.monitor.get_metrics('request_count')

        recent_errors = len([
            m for m in error_metrics 
            if current_time - m.timestamp <= time_window
        ])
        recent_total = len([
            m for m in total_metrics 
            if current_time - m.timestamp <= time_window
        ])

        if recent_total == 0:
            return {'error_rate': 0.0}

        return {'error_rate': recent_errors / recent_total * 100}

    @staticmethod
    def _percentile(values: List[float], percentile: float) -> float:
        """Calculate percentile value"""
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[index]