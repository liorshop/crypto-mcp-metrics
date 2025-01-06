import pytest
from metrics.dev_metrics import DevelopmentMetrics
from utils.error_handler import ValidationError

@pytest.mark.asyncio
async def test_dev_metrics_validation(sample_dev_data):
    """Test development metrics validation"""
    metrics = DevelopmentMetrics()
    
    # Test valid data
    metrics.validate(sample_dev_data)
    
    # Test invalid data
    invalid_data = sample_dev_data.copy()
    invalid_data['forks'] = -1
    
    with pytest.raises(ValidationError):
        metrics.validate(invalid_data)

@pytest.mark.asyncio
async def test_velocity_metrics_calculation():
    """Test development velocity metrics calculation"""
    metrics = DevelopmentMetrics()
    
    commit_activity = [
        {'total': 50, 'days': [5, 8, 10, 0, 15, 7, 5]},
        {'total': 45, 'days': [4, 6, 8, 12, 5, 5, 5]},
        {'total': 55, 'days': [7, 8, 9, 10, 11, 5, 5]},
        {'total': 60, 'days': [8, 9, 10, 11, 12, 5, 5]}
    ]
    
    result = metrics.calculate_velocity_metrics(commit_activity)
    
    assert 'weekly_commit_average' in result
    assert 'commit_trend' in result
    assert 'active_days_per_week' in result
    assert result['weekly_commit_average'] == 52.5  # (50 + 45 + 55 + 60) / 4

@pytest.mark.asyncio
async def test_code_impact_metrics_calculation():
    """Test code impact metrics calculation"""
    metrics = DevelopmentMetrics()
    
    code_frequency = [
        [1640995200, 1000, -500],  # Added 1000, removed 500
        [1641600000, 800, -400],   # Added 800, removed 400
        [1642204800, 1200, -600],  # Added 1200, removed 600
        [1642809600, 900, -450]    # Added 900, removed 450
    ]
    
    result = metrics.calculate_code_impact_metrics(code_frequency)
    
    assert 'net_code_change' in result
    assert 'code_churn' in result
    assert 'change_impact' in result

@pytest.mark.asyncio
async def test_activity_score_calculation(sample_dev_data):
    """Test development activity score calculation"""
    metrics = DevelopmentMetrics()
    
    score = metrics.calculate_activity_score(sample_dev_data)
    
    assert isinstance(score, float)
    assert 0 <= score <= 100  # Score should be a percentage