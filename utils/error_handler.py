class APIError(Exception):
    """Custom exception for API-related errors"""
    pass

class ValidationError(Exception):
    """Custom exception for data validation errors"""
    pass

class RateLimitError(Exception):
    """Custom exception for rate limit violations"""
    pass

class ConfigurationError(Exception):
    """Custom exception for configuration-related errors"""
    pass