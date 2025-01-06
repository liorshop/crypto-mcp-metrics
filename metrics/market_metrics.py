from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .base import BaseMetricCollector
from ..utils.error_handler import ValidationError

class MarketMetrics(BaseMetricCollector):
    """Collector for market-related metrics"""
    
    REQUIRED_FIELDS = [
        'market_cap',
        'current_price',
        'total_volume',
        'high_24h',
        'low_24h',
    ]
    
    def __init__(self):
        super().__init__()
        self.service = 'coingecko'
    
    def validate(self, data: Dict[str, Any]) -> None:
        """Validate market metrics data"""
        self.data_processor.validate_required_fields(data, self.REQUIRED_FIELDS)
        
        # Validate numeric values
        for field in self.REQUIRED_FIELDS:
            try:
                self.data_processor.clean_numeric_data(data[field])
            except (ValueError, TypeError) as e:
                raise ValidationError(f'Invalid value for {field}: {str(e)}')
    
    async def get_historical_data(self, 
                                coin_id: str, 
                                days: int = 30) -> List[Dict[str, Any]]:
        """Get historical market data"""
        endpoint = f'coins/{coin_id}/market_chart'
        params = {
            'vs_currency': 'usd',
            'days': days,
            'interval': 'daily'
        }
        
        response = await self.api_handler.get(
            service=self.service,
            endpoint=endpoint,
            params=params
        )
        
        # Process historical data
        prices = response.get('prices', [])
        market_caps = response.get('market_caps', [])
        volumes = response.get('total_volumes', [])
        
        historical_data = []
        for i in range(len(prices)):
            timestamp = datetime.fromtimestamp(prices[i][0] / 1000)
            data_point = {
                'timestamp': timestamp,
                'price': prices[i][1],
                'market_cap': market_caps[i][1] if i < len(market_caps) else None,
                'volume': volumes[i][1] if i < len(volumes) else None
            }
            historical_data.append(data_point)
        
        return historical_data
    
    def calculate_metrics(self,
                         current_data: Dict[str, Any],
                         historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate market metrics"""
        # Extract time series data
        prices = [d['price'] for d in historical_data]
        volumes = [d['volume'] for d in historical_data]
        market_caps = [d['market_cap'] for d in historical_data]
        
        # Calculate price metrics
        price_ma = self.data_processor.moving_average(prices)
        price_volatility = float(pd.Series(prices).std())
        price_trend = self.data_processor.calculate_percentage_change(
            prices[0], prices[-1]
        )
        
        # Calculate volume metrics
        volume_ma = self.data_processor.moving_average(volumes)
        volume_trend = self.data_processor.calculate_percentage_change(
            volumes[0], volumes[-1]
        )
        
        # Detect anomalies
        price_anomalies = self.data_processor.detect_anomalies(prices)
        volume_anomalies = self.data_processor.detect_anomalies(volumes)
        
        return {
            'current_metrics': {
                'price': current_data['current_price'],
                'market_cap': current_data['market_cap'],
                'volume_24h': current_data['total_volume'],
                'high_24h': current_data['high_24h'],
                'low_24h': current_data['low_24h']
            },
            'trend_metrics': {
                'price_trend': price_trend,
                'volume_trend': volume_trend,
                'price_volatility': price_volatility
            },
            'moving_averages': {
                'price_ma': price_ma[-1],
                'volume_ma': volume_ma[-1]
            },
            'anomaly_indicators': {
                'price_anomalies_detected': any(price_anomalies[-7:]),
                'volume_anomalies_detected': any(volume_anomalies[-7:])
            }
        }
    
    async def collect(self, coin_id: str) -> Dict[str, Any]:
        """Collect market metrics for a specific coin"""
        # Get current market data
        endpoint = f'coins/{coin_id}'
        params = {
            'localization': 'false',
            'tickers': 'false',
            'community_data': 'false',
            'developer_data': 'false'
        }
        
        current_data = await self.api_handler.get(
            service=self.service,
            endpoint=endpoint,
            params=params
        )
        
        # Validate current data
        market_data = current_data.get('market_data', {})
        self.validate(market_data)
        
        # Get historical data
        historical_data = await self.get_historical_data(coin_id)
        
        # Calculate metrics
        metrics = self.calculate_metrics(market_data, historical_data)
        
        return metrics