import pytest
from metrics.social_metrics import SocialMetrics
from utils.error_handler import ValidationError

@pytest.mark.asyncio
async def test_social_metrics_validation(sample_social_data):
    """Test social metrics validation"""
    metrics = SocialMetrics()
    
    # Test valid data
    metrics.validate(sample_social_data)
    
    # Test invalid data
    invalid_data = sample_social_data.copy()
    invalid_data['twitter_followers'] = -1
    
    with pytest.raises(ValidationError):
        metrics.validate(invalid_data)

@pytest.mark.asyncio
async def test_sentiment_calculation():
    """Test sentiment score calculation"""
    metrics = SocialMetrics()
    
    mentions = [
        {'sentiment': 'positive'},
        {'sentiment': 'positive'},
        {'sentiment': 'neutral'},
        {'sentiment': 'negative'}
    ]
    
    result = metrics.calculate_sentiment_score(mentions)
    
    assert 'average_sentiment' in result
    assert 'sentiment_distribution' in result
    assert result['sentiment_distribution']['positive'] == 50.0
    assert result['sentiment_distribution']['neutral'] == 25.0
    assert result['sentiment_distribution']['negative'] == 25.0

@pytest.mark.asyncio
async def test_engagement_analysis(sample_social_data):
    """Test engagement metrics analysis"""
    metrics = SocialMetrics()
    
    result = metrics.analyze_engagement_trends(sample_social_data, [])
    
    assert 'reddit' in result
    assert 'twitter' in result
    assert 'telegram' in result
    assert 'engagement_rate' in result['reddit']
    assert result['twitter']['followers'] == sample_social_data['twitter_followers']