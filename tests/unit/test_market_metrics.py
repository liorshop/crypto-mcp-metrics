import pytest
from metrics.market_metrics import MarketMetrics
from utils.error_handler import ValidationError

@pytest.mark.asyncio
async def test_market_metrics_validation(sample_market_data):
    """Test market metrics validation"""
    metrics = MarketMetrics()
    
    # Test valid data
    metrics.validate(sample_market_data)
    
    # Test invalid data
    invalid_data = sample_market_data.copy()
    invalid_data['market_cap'] = 'invalid'
    
    with pytest.raises(ValidationError):
        metrics.validate(invalid_data)

@pytest.mark.asyncio
async def test_market_metrics_calculation(sample_market_data):
    """Test market metrics calculation"""
    metrics = MarketMetrics()
    
    historical_data = [
        {'price': 49000, 'volume': 4800000, 'market_cap': 980000000},
        {'price': 50000, 'volume': 5000000, 'market_cap': 1000000000},
        {'price': 51000, 'volume': 5200000, 'market_cap': 1020000000}
    ]
    
    result = metrics.calculate_metrics(sample_market_data, historical_data)
    
    assert 'current_metrics' in result
    assert 'trend_metrics' in result
    assert 'moving_averages' in result
    assert 'anomaly_indicators' in result