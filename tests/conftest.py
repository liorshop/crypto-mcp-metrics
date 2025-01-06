import pytest
import asyncio
from typing import Dict, Any

@pytest.fixture
def event_loop():
    """Create and provide event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_market_data() -> Dict[str, Any]:
    """Provide sample market data for testing"""
    return {
        'market_cap': 1000000000,
        'current_price': 50000,
        'total_volume': 5000000,
        'high_24h': 51000,
        'low_24h': 49000
    }

@pytest.fixture
def sample_volume_data() -> Dict[str, Any]:
    """Provide sample volume data for testing"""
    return {
        'total_volume': 5000000,
        'tickers': [
            {
                'market': {'name': 'Binance'},
                'converted_volume': {'usd': 2000000}
            },
            {
                'market': {'name': 'Coinbase'},
                'converted_volume': {'usd': 1500000}
            }
        ]
    }

@pytest.fixture
def sample_social_data() -> Dict[str, Any]:
    """Provide sample social data for testing"""
    return {
        'twitter_followers': 100000,
        'reddit_subscribers': 50000,
        'telegram_channel_user_count': 25000,
        'reddit_average_posts_48h': 100,
        'reddit_average_comments_48h': 500
    }

@pytest.fixture
def sample_dev_data() -> Dict[str, Any]:
    """Provide sample development data for testing"""
    return {
        'forks': 1000,
        'stars': 5000,
        'subscribers': 300,
        'total_issues': 1500,
        'closed_issues': 1200,
        'pull_requests_merged': 800,
        'pull_request_contributors': 150,
        'commit_count_4_weeks': 200
    }