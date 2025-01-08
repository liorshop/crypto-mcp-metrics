from typing import Dict, Any, List
from ..utils.error_handler import ValidationError
from ..utils.logging import logger

class ContextManager:
    """Manages context preparation and optimization for Claude"""
    
    def __init__(self, config: Dict[str, Any]):
        self.max_tokens = config.get('MAX_TOKENS', 4096)
        self.token_estimator = TokenEstimator()
        self.metrics = MetricsCollector()

    async def prepare_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare and optimize context for Claude"""
        try:
            # 1. Validate data
            self._validate_data(data)

            # 2. Structure context
            context = self._structure_context(data)

            # 3. Check token count
            token_count = await self.token_estimator.estimate(context)
            if token_count > self.max_tokens:
                context = await self._optimize_context(context)

            # 4. Add metadata
            context['metadata'] = self._add_metadata(context)

            return context

        except Exception as e:
            logger.error(f'Context preparation failed: {str(e)}')
            raise

    def _validate_data(self, data: Dict[str, Any]) -> None:
        """Validate input data"""
        required_fields = ['metrics', 'timeframe']
        for field in required_fields:
            if field not in data:
                raise ValidationError(f'Missing required field: {field}')

    def _structure_context(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure data into Claude-friendly context"""
        return {
            'metrics': {
                'market': data.get('market_metrics'),
                'volume': data.get('volume_metrics'),
                'social': data.get('social_metrics'),
                'development': data.get('dev_metrics')
            },
            'timeframe': data.get('timeframe'),
            'analysis_type': data.get('analysis_type', 'general')
        }

    async def _optimize_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize context to fit within token limits"""
        # Implement context optimization strategies
        optimized = context.copy()

        # Strategy 1: Summarize historical data
        if 'historical_data' in optimized['metrics']:
            optimized['metrics']['historical_data'] = \
                self._summarize_historical_data(optimized['metrics']['historical_data'])

        # Strategy 2: Remove less important metrics
        priority_metrics = ['market', 'volume']
        optimized['metrics'] = {k: v for k, v in optimized['metrics'].items()
                               if k in priority_metrics}

        return optimized

    def _summarize_historical_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Summarize historical data to reduce context size"""
        if not data:
            return []

        # Keep only key points (e.g., start, middle, end, and significant changes)
        summary_size = min(len(data), 10)  # Max 10 points
        step = max(1, len(data) // summary_size)

        return data[::step]