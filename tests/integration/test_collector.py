import pytest
from main import CryptoMetricsCollector

@pytest.mark.asyncio
async def test_collect_all_metrics():
    """Test the complete metrics collection process"""
    collector = CryptoMetricsCollector()
    
    try:
        async with collector:
            metrics = await collector.collect_all_metrics('bitcoin')
            
            # Verify structure
            assert 'market' in metrics
            assert 'volume' in metrics
            assert 'social' in metrics
            assert 'development' in metrics
            
            # Verify market metrics
            market_data = metrics['market']
            assert 'current_metrics' in market_data
            assert 'trend_metrics' in market_data
            
            # Verify volume metrics
            volume_data = metrics['volume']
            assert 'current_metrics' in volume_data
            assert 'exchange_metrics' in volume_data
            
            # Verify social metrics
            social_data = metrics['social']
            assert 'sentiment_metrics' in social_data
            assert 'engagement_metrics' in social_data
            
            # Verify development metrics
            dev_data = metrics['development']
            assert 'basic_metrics' in dev_data
            assert 'velocity_metrics' in dev_data
            
    except Exception as e:
        pytest.fail(f'Test failed with error: {str(e)}')

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in the collection process"""
    collector = CryptoMetricsCollector()
    
    try:
        async with collector:
            # Test with invalid coin ID
            metrics = await collector.collect_all_metrics('invalid_coin_id')
            
            # Verify error handling
            for category in ['market', 'volume', 'social', 'development']:
                assert category in metrics
                if 'error' in metrics[category]:
                    assert isinstance(metrics[category]['error'], str)
                    
    except Exception as e:
        pytest.fail(f'Test failed with error: {str(e)}')

@pytest.mark.asyncio
async def test_concurrent_collection():
    """Test concurrent collection of multiple coins"""
    collector = CryptoMetricsCollector()
    coins = ['bitcoin', 'ethereum', 'cardano']
    
    try:
        async with collector:
            # Create tasks for each coin
            tasks = [collector.collect_all_metrics(coin) for coin in coins]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify results
            assert len(results) == len(coins)
            for result in results:
                if not isinstance(result, Exception):
                    assert 'market' in result
                    assert 'volume' in result
                    assert 'social' in result
                    assert 'development' in result
                    
    except Exception as e:
        pytest.fail(f'Test failed with error: {str(e)}')