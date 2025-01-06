from typing import Dict, Any, List, Optional, Union
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ..utils.logging import logger
from ..utils.error_handler import ValidationError

class DataProcessor:
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
        """Validate that all required fields are present in the data"""
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValidationError(f'Missing required fields: {missing_fields}')
    
    @staticmethod
    def clean_numeric_data(value: Union[str, int, float]) -> float:
        """Clean and convert numeric data to float"""
        if isinstance(value, str):
            # Remove currency symbols and commas
            value = value.replace('$', '').replace(',', '').strip()
            try:
                return float(value)
            except ValueError:
                logger.warning(f'Could not convert {value} to float')
                return 0.0
        return float(value)
    
    @staticmethod
    def calculate_percentage_change(old_value: float, new_value: float) -> float:
        """Calculate percentage change between two values"""
        if old_value == 0:
            return 0.0
        return ((new_value - old_value) / abs(old_value)) * 100
    
    @staticmethod
    def moving_average(data: List[float], window: int = 7) -> List[float]:
        """Calculate moving average for a list of values"""
        if not data:
            return []
        return list(pd.Series(data).rolling(window=window, min_periods=1).mean())
    
    @staticmethod
    def detect_anomalies(data: List[float], threshold: float = 2.0) -> List[bool]:
        """Detect anomalies using z-score method"""
        if not data:
            return []
        series = pd.Series(data)
        z_scores = np.abs((series - series.mean()) / series.std())
        return list(z_scores > threshold)
    
    @staticmethod
    def interpolate_missing_values(data: List[Optional[float]]) -> List[float]:
        """Interpolate missing values in time series data"""
        if not data:
            return []
        series = pd.Series(data)
        return list(series.interpolate(method='linear', limit_direction='both'))
    
    @staticmethod
    def normalize_data(data: List[float]) -> List[float]:
        """Normalize data to range [0, 1]"""
        if not data:
            return []
        min_val = min(data)
        max_val = max(data)
        if min_val == max_val:
            return [0.5] * len(data)
        return [(x - min_val) / (max_val - min_val) for x in data]
    
    @staticmethod
    def aggregate_time_series(timestamps: List[datetime], 
                            values: List[float], 
                            interval: str = '1D') -> tuple[List[datetime], List[float]]:
        """Aggregate time series data by interval"""
        if not timestamps or not values:
            return [], []
        
        df = pd.DataFrame({
            'timestamp': timestamps,
            'value': values
        })
        
        df.set_index('timestamp', inplace=True)
        resampled = df.resample(interval).mean()
        
        return list(resampled.index), list(resampled['value'])