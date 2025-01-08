import pytest
import asyncio
import time
from typing import List, Dict, Any
from core.mcp import MCPCore
from utils.monitoring import PerformanceMonitor

class TestLoad:
    @pytest.fixture
    async def mcp_core(self, config):
        core = MCPCore(config)
        await core.initialize()
        yield core
        await core.cleanup()

    @pytest.fixture
    def performance_monitor(self):
        return PerformanceMonitor()

    async def _make_request(self, mcp_core: MCPCore, errors: List[Exception]) -> None:
        """Make a single request and track errors"""
        try:
            await mcp_core.process_request({
                'metrics': {
                    'price': 50000,
                    'volume': 1000000,
                    'market_cap': 1000000000
                }
            })
        except Exception as e:
            errors.append(e)

    @pytest.mark.asyncio
    async def test_sustained_load(self, mcp_core: MCPCore, performance_monitor: PerformanceMonitor):
        """Test system under sustained load"""
        with performance_monitor.measure('sustained_load'):
            duration = 60  # Test duration in seconds
            request_rate = 10  # Requests per second
            
            start_time = time.time()
            request_count = 0
            errors = []

            while time.time() - start_time < duration:
                tasks = [
                    self._make_request(mcp_core, errors)
                    for _ in range(request_rate)
                ]
                await asyncio.gather(*tasks)
                request_count += request_rate
                await asyncio.sleep(1)  # Wait 1 second
                
                # Log current metrics
                performance_monitor.record_metric('requests_per_second', request_rate)
                performance_monitor.record_metric('error_count', len(errors))

        # Calculate final metrics
        elapsed_time = time.time() - start_time
        requests_per_second = request_count / elapsed_time
        error_rate = len(errors) / request_count if request_count > 0 else 0

        # Log final metrics
        performance_monitor.record_metric('final_rps', requests_per_second)
        performance_monitor.record_metric('final_error_rate', error_rate)

        # Assertions
        assert requests_per_second >= request_rate * 0.9  # Allow 10% variance
        assert error_rate <= 0.01  # Maximum 1% error rate

    @pytest.mark.asyncio
    async def test_burst_load(self, mcp_core: MCPCore, performance_monitor: PerformanceMonitor):
        """Test system under burst load"""
        with performance_monitor.measure('burst_load'):
            burst_size = 100  # Number of simultaneous requests
            
            start_time = time.time()
            tasks = [self._make_request(mcp_core, []) for _ in range(burst_size)]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            elapsed_time = time.time() - start_time

            # Calculate metrics
            success_count = sum(1 for r in results if not isinstance(r, Exception))
            error_count = len(results) - success_count
            requests_per_second = burst_size / elapsed_time

            # Log metrics
            performance_monitor.record_metric('burst_success_count', success_count)
            performance_monitor.record_metric('burst_error_count', error_count)
            performance_monitor.record_metric('burst_rps', requests_per_second)

            # Assertions
            assert success_count >= burst_size * 0.95  # 95% success rate
            assert requests_per_second >= 10  # Minimum throughput

    @pytest.mark.asyncio
    async def test_claude_performance(self, mcp_core: MCPCore, performance_monitor: PerformanceMonitor):
        """Test Claude.ai processing performance"""
        with performance_monitor.measure('claude_processing'):
            test_cases = [
                {'context_size': 'small', 'data': {'text': 'x' * 100}},
                {'context_size': 'medium', 'data': {'text': 'x' * 1000}},
                {'context_size': 'large', 'data': {'text': 'x' * 5000}}
            ]

            for case in test_cases:
                start_time = time.time()
                await mcp_core.claude_manager.process_request(case['data'])
                elapsed_time = time.time() - start_time

                # Log metrics
                performance_monitor.record_metric(
                    f'claude_processing_time_{case["context_size"]}',
                    elapsed_time
                )

    @pytest.mark.asyncio
    async def test_memory_usage(self, mcp_core: MCPCore, performance_monitor: PerformanceMonitor):
        """Test memory usage under load"""
        import psutil
        import os

        with performance_monitor.measure('memory_usage'):
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss

            # Process multiple large requests
            large_data = {'text': 'x' * 10000}
            request_count = 100

            for i in range(request_count):
                await mcp_core.process_request(large_data)
                current_memory = process.memory_info().rss
                memory_increase = current_memory - initial_memory

                # Log memory metrics
                performance_monitor.record_metric(
                    'memory_usage',
                    current_memory,
                    {'request_number': i}
                )

            final_memory = process.memory_info().rss
            total_increase = final_memory - initial_memory

            # Log final metrics
            performance_monitor.record_metric('total_memory_increase', total_increase)

            # Assert reasonable memory usage
            assert total_increase < 100 * 1024 * 1024  # Less than 100MB increase