from dotenv import load_dotenv
import os
from typing import Dict

load_dotenv()

class Config:
    # API Keys
    COINGECKO_API_KEY = os.getenv('COINGECKO_API_KEY')
    COINMARKETCAP_API_KEY = os.getenv('COINMARKETCAP_API_KEY')
    SOCIAL_SEARCHER_API_KEY = os.getenv('SOCIAL_SEARCHER_API_KEY')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    
    # API Rate Limits
    RATE_LIMIT_WINDOW = 60  # seconds
    MAX_REQUESTS_PER_WINDOW: Dict[str, int] = {
        'coingecko': 50,
        'coinmarketcap': 30,
        'social_searcher': 100,
        'github': 5000
    }
    
    # API Endpoints
    COINGECKO_BASE_URL = 'https://api.coingecko.com/api/v3'
    COINMARKETCAP_BASE_URL = 'https://pro-api.coinmarketcap.com/v1'
    SOCIAL_SEARCHER_BASE_URL = 'https://api.social-searcher.com/v2'
    GITHUB_API_URL = 'https://api.github.com'
    
    # Cache Configuration
    CACHE_EXPIRY = 300  # 5 minutes
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def get_api_key(cls, service: str) -> str:
        keys = {
            'coingecko': cls.COINGECKO_API_KEY,
            'coinmarketcap': cls.COINMARKETCAP_API_KEY,
            'social_searcher': cls.SOCIAL_SEARCHER_API_KEY,
            'github': cls.GITHUB_TOKEN
        }
        return keys.get(service, '')
    
    @classmethod
    def get_base_url(cls, service: str) -> str:
        urls = {
            'coingecko': cls.COINGECKO_BASE_URL,
            'coinmarketcap': cls.COINMARKETCAP_BASE_URL,
            'social_searcher': cls.SOCIAL_SEARCHER_BASE_URL,
            'github': cls.GITHUB_API_URL
        }
        return urls.get(service, '')