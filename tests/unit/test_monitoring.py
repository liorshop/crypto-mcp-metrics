import pytest
import time
from utils.monitoring import (
    PerformanceMonitor,
    ResourceMonitor,
    PerformanceAnalyzer,
    MetricPoint
)

class TestPerformanceMonitor:
    @pytest.fixture
    def monitor(self):
        return PerformanceMonitor()

    def test_record_metric(self, monitor):
        """Test basic metric recording"""
        monitor.record_metric('test_metric', 100, {'tag': 'value'})
        metrics = monitor.get_metrics('test_metric')
        
        assert len(metrics) == 1
        assert metrics[0].value == 100
        assert metrics[0].tags == {'tag': 'value'}

    def test_measure_context(self, monitor):
        """Test duration measurement context manager"""
        with monitor.measure('test_operation'):
            time.sleep(0.1)

        metrics = monitor.get_metrics('test_operation_duration')
        assert len(metrics) == 1
        assert 0.1 <= metrics[0].value <= 0.2

    def test_get_summary(self, monitor):
        """Test metric summary calculation"""
        values = [1, 2, 3, 4, 5]
        for v in values:
            monitor.record_metric('test_metric', v)

        summary = monitor.get_summary('test_metric')
        assert summary['min'] == 1
        assert summary['max'] == 5
        assert summary['avg'] == 3
        assert summary['count'] == 5

class TestResourceMonitor:
    @pytest.fixture
    def resource_monitor(self):
        monitor = ResourceMonitor()
        monitor.start_monitoring(interval=0.1)
        yield monitor
        monitor.stop_monitoring()

    def test_resource_monitoring(self, resource_monitor):
        """Test resource usage monitoring"""
        # Let it collect some data
        time.sleep(0.3)

        # Check CPU metrics
        cpu_metrics = resource_monitor.performance_monitor.get_metrics('cpu_usage')
        assert len(cpu_metrics) >= 2

        # Check memory metrics
        memory_metrics = resource_monitor.performance_monitor.get_metrics('memory_rss')
        assert len(memory_metrics) >= 2

        # Check IO metrics
        io_metrics = resource_monitor.performance_monitor.get_metrics('io_read_bytes')
        assert len(io_metrics) >= 2

class TestPerformanceAnalyzer:
    @pytest.fixture
    def analyzer(self):
        monitor = PerformanceMonitor()
        return PerformanceAnalyzer(monitor)

    def test_response_time_analysis(self, analyzer):
        """Test response time analysis"""
        # Record some test response times
        for value in [0.1, 0.2, 0.3, 0.4, 0.5]:
            analyzer.monitor.record_metric('request_duration', value)

        analysis = analyzer.analyze_response_times(time_window=1)
        
        assert 'avg_response_time' in analysis
        assert 'p95_response_time' in analysis
        assert 'p99_response_time' in analysis
        assert abs(analysis['avg_response_time'] - 0.3) < 0.001

    def test_error_rate_analysis(self, analyzer):
        """Test error rate analysis"""
        # Record some test errors and requests
        for _ in range(10):
            analyzer.monitor.record_metric('request_count', 1)
        
        for _ in range(2):
            analyzer.monitor.record_metric('request_error', 1)

        analysis = analyzer.analyze_error_rates(time_window=1)
        
        assert 'error_rate' in analysis
        assert abs(analysis['error_rate'] - 20.0) < 0.001  # 20% error rate

    def test_percentile_calculation(self, analyzer):
        """Test percentile calculation"""
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        p95 = analyzer._percentile(values, 95)
        p50 = analyzer._percentile(values, 50)
        
        assert p95 == 10  # 95th percentile of 1-10
        assert p50 == 5   # Median of 1-10