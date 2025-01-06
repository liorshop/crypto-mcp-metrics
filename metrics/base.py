from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..core.api_handler import APIHandler
from ..core.data_processor import DataProcessor
from ..utils.logging import logger
from ..utils.error_handler import ValidationError

class BaseMetricCollector(ABC):
    """Base class for all metric collectors"""
    
    def __init__(self):
        self.api_handler = APIHandler()
        self.data_processor = DataProcessor()
        self.logger = logger
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()
    
    async def cleanup(self) -> None:
        """Cleanup resources"""
        await self.api_handler.close()
    
    @abstractmethod
    async def collect(self, coin_id: str) -> Dict[str, Any]:
        """Collect metrics for a specific coin
        
        Args:
            coin_id: Identifier for the cryptocurrency
            
        Returns:
            Dictionary containing collected metrics
        """
        pass
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> None:
        """Validate collected data
        
        Args:
            data: Data to validate
            
        Raises:
            ValidationError: If data validation fails
        """
        pass
    
    async def get_historical_data(self, 
                                coin_id: str, 
                                days: int = 30) -> List[Dict[str, Any]]:
        """Get historical data for analysis
        
        Args:
            coin_id: Identifier for the cryptocurrency
            days: Number of days of historical data to retrieve
            
        Returns:
            List of historical data points
        """
        pass
    
    def calculate_metrics(self, 
                         current_data: Dict[str, Any],
                         historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate derived metrics from raw data
        
        Args:
            current_data: Current point-in-time data
            historical_data: Historical data points
            
        Returns:
            Dictionary containing calculated metrics
        """
        pass