from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .base import BaseMetricCollector
from ..utils.error_handler import ValidationError

class SocialMetrics(BaseMetricCollector):
    """Collector for social media-related metrics"""
    
    REQUIRED_FIELDS = [
        'twitter_followers',
        'reddit_subscribers',
        'telegram_channel_user_count',
        'reddit_average_posts_48h',
        'reddit_average_comments_48h'
    ]
    
    SENTIMENT_WEIGHTS = {
        'positive': 1,
        'neutral': 0,
        'negative': -1
    }
    
    def __init__(self):
        super().__init__()
        self.coingecko_service = 'coingecko'
        self.social_service = 'social_searcher'
    
    def validate(self, data: Dict[str, Any]) -> None:
        """Validate social metrics data"""
        self.data_processor.validate_required_fields(data, self.REQUIRED_FIELDS)
        
        # Validate numeric values
        for field in self.REQUIRED_FIELDS:
            try:
                value = data.get(field, 0)
                if not isinstance(value, (int, float)) or value < 0:
                    raise ValidationError(f'Invalid value for {field}: must be a non-negative number')
            except (ValueError, TypeError) as e:
                raise ValidationError(f'Invalid value for {field}: {str(e)}')
    
    async def get_social_mentions(self, coin_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get social media mentions and sentiment"""
        endpoint = 'search'
        params = {
            'q': coin_id,
            'network': 'twitter,reddit',
            'from': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
            'to': datetime.now().strftime('%Y-%m-%d'),
            'type': 'tweets,posts'
        }
        
        response = await self.api_handler.get(
            service=self.social_service,
            endpoint=endpoint,
            params=params
        )
        
        return response.get('posts', [])
    
    def calculate_sentiment_score(self, mentions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate sentiment metrics from social mentions"""
        if not mentions:
            return {
                'average_sentiment': 0,
                'sentiment_distribution': {
                    'positive': 0,
                    'neutral': 0,
                    'negative': 0
                }
            }
        
        sentiment_counts = {
            'positive': 0,
            'neutral': 0,
            'negative': 0
        }
        
        total_score = 0
        
        for mention in mentions:
            sentiment = mention.get('sentiment', 'neutral')
            sentiment_counts[sentiment] += 1
            total_score += self.SENTIMENT_WEIGHTS.get(sentiment, 0)
        
        total_mentions = len(mentions)
        average_sentiment = total_score / total_mentions
        
        sentiment_distribution = {
            sentiment: count / total_mentions * 100
            for sentiment, count in sentiment_counts.items()
        }
        
        return {
            'average_sentiment': average_sentiment,
            'sentiment_distribution': sentiment_distribution
        }
    
    def analyze_engagement_trends(self, 
                                current_data: Dict[str, Any],
                                historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze social engagement trends"""
        reddit_metrics = {
            'subscribers': current_data['reddit_subscribers'],
            'active_accounts': current_data.get('reddit_accounts_active_48h', 0),
            'posts_per_day': current_data['reddit_average_posts_48h'] / 2,
            'comments_per_day': current_data['reddit_average_comments_48h'] / 2
        }
        
        twitter_metrics = {
            'followers': current_data['twitter_followers'],
            'status_updates': current_data.get('twitter_status_updates', 0)
        }
        
        telegram_metrics = {
            'users': current_data['telegram_channel_user_count']
        }
        
        # Calculate engagement rates
        reddit_engagement = (reddit_metrics['active_accounts'] / reddit_metrics['subscribers'] * 100) \
            if reddit_metrics['subscribers'] > 0 else 0
            
        return {
            'reddit': {
                **reddit_metrics,
                'engagement_rate': reddit_engagement
            },
            'twitter': twitter_metrics,
            'telegram': telegram_metrics
        }
    
    async def collect(self, coin_id: str) -> Dict[str, Any]:
        """Collect social metrics for a specific coin"""
        # Get community data from CoinGecko
        endpoint = f'coins/{coin_id}'
        params = {
            'localization': 'false',
            'tickers': 'false',
            'market_data': 'false',
            'developer_data': 'false'
        }
        
        response = await self.api_handler.get(
            service=self.coingecko_service,
            endpoint=endpoint,
            params=params
        )
        
        community_data = response.get('community_data', {})
        
        # Validate data
        self.validate(community_data)
        
        # Get social mentions and sentiment
        mentions = await self.get_social_mentions(coin_id)
        sentiment_metrics = self.calculate_sentiment_score(mentions)
        
        # Analyze engagement trends
        engagement_metrics = self.analyze_engagement_trends(community_data, [])
        
        return {
            'sentiment_metrics': sentiment_metrics,
            'engagement_metrics': engagement_metrics,
            'mentions_count': len(mentions),
            'platform_metrics': {
                'reddit': {
                    'subscribers': community_data['reddit_subscribers'],
                    'active_users': community_data.get('reddit_accounts_active_48h', 0)
                },
                'twitter': {
                    'followers': community_data['twitter_followers']
                },
                'telegram': {
                    'users': community_data['telegram_channel_user_count']
                }
            }
        }