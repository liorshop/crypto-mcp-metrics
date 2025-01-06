import pytest
from metrics.volume_metrics import VolumeMetrics
from utils.error_handler import ValidationError

@pytest.mark.asyncio
async def test_volume_metrics_validation(sample_volume_data):
    """Test volume metrics validation"""
    metrics = VolumeMetrics()
    
    # Test valid data
    metrics.validate(sample_volume_data)
    
    # Test invalid data
    invalid_data = sample_volume_data.copy()
    invalid_data['tickers'] = 'invalid'
    
    with pytest.raises(ValidationError):
        metrics.validate(invalid_data)

@pytest.mark.asyncio
async def test_exchange_distribution_analysis(sample_volume_data):
    """Test exchange distribution analysis"""
    metrics = VolumeMetrics()
    
    result = metrics.analyze_exchange_distribution(sample_volume_data['tickers'])
    
    assert 'distribution' in result
    assert 'concentration' in result
    assert len(result['distribution']) == 2  # Two exchanges in sample data
    assert 'Binance' in result['distribution']
    assert 'Coinbase' in result['distribution']

@pytest.mark.asyncio
async def test_volume_metrics_calculation(sample_volume_data):
    """Test volume metrics calculation"""
    metrics = VolumeMetrics()
    
    historical_data = [
        {'timestamp': '2024-01-01', 'volume': 4800000},
        {'timestamp': '2024-01-02', 'volume': 5000000},
        {'timestamp': '2024-01-03', 'volume': 5200000}
    ]
    
    result = metrics.calculate_metrics(sample_volume_data, historical_data)
    
    assert 'current_metrics' in result
    assert 'historical_metrics' in result
    assert 'moving_averages' in result
    assert 'anomaly_indicators' in result
    assert 'exchange_metrics' in result