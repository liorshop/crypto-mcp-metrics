import pytest
import asyncio
from typing import Dict, Any
from core.claude.client import ClaudeClient
from core.claude.context import ContextManager
from utils.monitoring import PerformanceMonitor

class TestClaudePerformance:
    @pytest.fixture
    def monitor(self):
        return PerformanceMonitor()

    @pytest.fixture
    async def claude_client(self, config):
        client = ClaudeClient(config)
        yield client
        await client.cleanup()

    @pytest.fixture
    def context_manager(self, config):
        return ContextManager(config)

    @pytest.mark.asyncio
    async def test_claude_response_times(self, claude_client, monitor):
        """Test Claude.ai response times with different payloads"""
        test_cases = [
            {
                'name': 'small_context',
                'data': {'text': 'x' * 100},
                'max_time': 2.0
            },
            {
                'name': 'medium_context',
                'data': {'text': 'x' * 1000},
                'max_time': 3.0
            },
            {
                'name': 'large_context',
                'data': {'text': 'x' * 5000},
                'max_time': 5.0
            }
        ]

        for case in test_cases:
            with monitor.measure(f'claude_response_{case["name"]}'):
                response = await claude_client.process_request(case['data'])
                assert response is not None

            metrics = monitor.get_metrics(f'claude_response_{case["name"]}_duration')
            assert len(metrics) == 1
            assert metrics[0].value <= case['max_time']

    @pytest.mark.asyncio
    async def test_context_optimization(self, context_manager, monitor):
        """Test context optimization performance"""
        test_cases = [
            {
                'name': 'small_optimization',
                'data': self._generate_test_data(1000)
            },
            {
                'name': 'medium_optimization',
                'data': self._generate_test_data(5000)
            },
            {
                'name': 'large_optimization',
                'data': self._generate_test_data(10000)
            }
        ]

        for case in test_cases:
            with monitor.measure(f'context_optimization_{case["name"]}'):
                optimized = await context_manager.prepare_context(case['data'])
                assert optimized is not None

            # Verify optimization results
            metrics = monitor.get_metrics(
                f'context_optimization_{case["name"]}_duration'
            )
            assert len(metrics) == 1
            
            # Check optimization ratio
            original_size = len(str(case['data']))
            optimized_size = len(str(optimized))
            optimization_ratio = optimized_size / original_size
            
            assert optimization_ratio <= 0.8  # At least 20% reduction

    @pytest.mark.asyncio
    async def test_concurrent_claude_requests(self, claude_client, monitor):
        """Test concurrent Claude.ai request handling"""
        concurrent_requests = 5
        test_data = {'text': 'Test request'}

        with monitor.measure('concurrent_claude_requests'):
            tasks = [
                claude_client.process_request(test_data)
                for _ in range(concurrent_requests)
            ]
            results = await asyncio.gather(*tasks)

        assert len(results) == concurrent_requests
        assert all(r is not None for r in results)

        metrics = monitor.get_metrics('concurrent_claude_requests_duration')
        assert len(metrics) == 1
        # Average time per request should be reasonable
        avg_time_per_request = metrics[0].value / concurrent_requests
        assert avg_time_per_request <= 2.0

    def _generate_test_data(self, size: int) -> Dict[str, Any]:
        """Generate test data of specified size"""
        return {
            'metrics': {
                'market': {'data': 'x' * (size // 4)},
                'volume': {'data': 'x' * (size // 4)},
                'social': {'data': 'x' * (size // 4)},
                'development': {'data': 'x' * (size // 4)}
            }
        }

class TestClaudeErrorHandling:
    @pytest.fixture
    def monitor(self):
        return PerformanceMonitor()

    @pytest.fixture
    async def claude_client(self, config):
        client = ClaudeClient(config)
        yield client
        await client.cleanup()

    @pytest.mark.asyncio
    async def test_error_recovery_time(self, claude_client, monitor):
        """Test error recovery performance"""
        # Force an error by sending invalid data
        invalid_data = {'invalid': None}

        with monitor.measure('error_recovery'):
            try:
                await claude_client.process_request(invalid_data)
            except Exception:
                pass

        metrics = monitor.get_metrics('error_recovery_duration')
        assert len(metrics) == 1
        assert metrics[0].value <= 1.0  # Error handling should be quick

    @pytest.mark.asyncio
    async def test_token_limit_handling(self, claude_client, monitor):
        """Test token limit handling performance"""
        # Create data that exceeds token limit
        large_data = {'text': 'x' * 100000}

        with monitor.measure('token_limit_handling'):
            try:
                await claude_client.process_request(large_data)
            except Exception as e:
                assert 'token limit' in str(e).lower()

        metrics = monitor.get_metrics('token_limit_handling_duration')
        assert len(metrics) == 1
        assert metrics[0].value <= 0.5  # Token limit check should be fast