from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from .base import BaseMetricCollector
from ..utils.error_handler import ValidationError

class VolumeMetrics(BaseMetricCollector):
    """Collector for volume-related metrics"""
    
    REQUIRED_FIELDS = [
        'total_volume',
        'tickers'
    ]
    
    def __init__(self):
        super().__init__()
        self.service = 'coingecko'
    
    def validate(self, data: Dict[str, Any]) -> None:
        """Validate volume metrics data"""
        self.data_processor.validate_required_fields(data, self.REQUIRED_FIELDS)
        
        if not isinstance(data['tickers'], list):
            raise ValidationError('Tickers must be a list')
        
        try:
            self.data_processor.clean_numeric_data(data['total_volume'])
        except (ValueError, TypeError) as e:
            raise ValidationError(f'Invalid total volume value: {str(e)}')
    
    async def get_historical_data(self, 
                                coin_id: str, 
                                days: int = 30) -> List[Dict[str, Any]]:
        """Get historical volume data"""
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
        
        volumes = response.get('total_volumes', [])
        
        historical_data = []
        for timestamp_ms, volume in volumes:
            timestamp = datetime.fromtimestamp(timestamp_ms / 1000)
            historical_data.append({
                'timestamp': timestamp,
                'volume': volume
            })
        
        return historical_data
    
    def analyze_exchange_distribution(self, tickers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze volume distribution across exchanges"""
        exchange_volumes = defaultdict(float)
        total_volume = 0
        
        for ticker in tickers:
            volume = ticker.get('converted_volume', {}).get('usd', 0)
            exchange = ticker.get('market', {}).get('name', 'Unknown')
            
            exchange_volumes[exchange] += volume
            total_volume += volume
        
        # Calculate percentage distribution
        distribution = {}
        for exchange, volume in exchange_volumes.items():
            percentage = (volume / total_volume * 100) if total_volume > 0 else 0
            distribution[exchange] = round(percentage, 2)
        
        # Sort exchanges by volume
        sorted_distribution = dict(sorted(
            distribution.items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        return {
            'distribution': sorted_distribution,
            'concentration': self.calculate_concentration(list(distribution.values()))
        }
    
    def calculate_concentration(self, percentages: List[float]) -> Dict[str, float]:
        """Calculate volume concentration metrics"""
        sorted_percentages = sorted(percentages, reverse=True)
        
        return {
            'top_exchange': sorted_percentages[0] if percentages else 0,
            'top_3_exchanges': sum(sorted_percentages[:3]) if len(percentages) >= 3 else sum(sorted_percentages),
            'top_5_exchanges': sum(sorted_percentages[:5]) if len(percentages) >= 5 else sum(sorted_percentages)
        }
    
    def calculate_metrics(self,
                         current_data: Dict[str, Any],
                         historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate volume metrics"""
        volumes = [d['volume'] for d in historical_data]
        
        # Calculate basic metrics
        current_volume = current_data['total_volume']
        avg_volume = sum(volumes) / len(volumes) if volumes else 0
        max_volume = max(volumes) if volumes else 0
        min_volume = min(volumes) if volumes else 0
        
        # Calculate trends
        volume_ma = self.data_processor.moving_average(volumes)
        volume_trend = self.data_processor.calculate_percentage_change(
            volumes[0], volumes[-1]
        ) if volumes else 0
        
        # Detect anomalies
        volume_anomalies = self.data_processor.detect_anomalies(volumes)
        
        # Analyze exchange distribution
        exchange_analysis = self.analyze_exchange_distribution(current_data['tickers'])
        
        return {
            'current_metrics': {
                'current_volume': current_volume,
                'vs_average': self.data_processor.calculate_percentage_change(
                    avg_volume, current_volume
                )
            },
            'historical_metrics': {
                'average_volume': avg_volume,
                'max_volume': max_volume,
                'min_volume': min_volume,
                'volume_trend': volume_trend
            },
            'moving_averages': {
                'volume_ma': volume_ma[-1] if volume_ma else 0
            },
            'anomaly_indicators': {
                'volume_anomalies_detected': any(volume_anomalies[-7:]) if volume_anomalies else False
            },
            'exchange_metrics': exchange_analysis
        }
    
    async def collect(self, coin_id: str) -> Dict[str, Any]:
        """Collect volume metrics for a specific coin"""
        # Get current data
        endpoint = f'coins/{coin_id}/tickers'
        current_data = await self.api_handler.get(
            service=self.service,
            endpoint=endpoint
        )
        
        # Get total volume from market data
        market_endpoint = f'coins/{coin_id}'
        market_data = await self.api_handler.get(
            service=self.service,
            endpoint=market_endpoint,
            params={'localization': 'false', 'tickers': 'false'}
        )
        
        # Combine data
        volume_data = {
            'total_volume': market_data.get('market_data', {}).get('total_volume', {}).get('usd', 0),
            'tickers': current_data.get('tickers', [])
        }
        
        # Validate data
        self.validate(volume_data)
        
        # Get historical data
        historical_data = await self.get_historical_data(coin_id)
        
        # Calculate metrics
        metrics = self.calculate_metrics(volume_data, historical_data)
        
        return metrics