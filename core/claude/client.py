import asyncio
from typing import Dict, Any, Optional
from anthropic import AsyncAnthropic
from ..utils.error_handler import ClaudeError, TokenLimitError
from ..utils.logging import logger

class ClaudeClient:
    """Client for interacting with Claude.ai API"""
    
    def __init__(self, config: Dict[str, Any]):
        self.client = AsyncAnthropic(api_key=config['CLAUDE_API_KEY'])
        self.model = config.get('CLAUDE_MODEL', 'claude-3-sonnet-20240229')
        self.max_tokens = config.get('MAX_TOKENS', 4096)
        self.temperature = config.get('TEMPERATURE', 0.7)
        self.metrics = MetricsCollector()

    async def process_request(self, prompt: str) -> Dict[str, Any]:
        """Process a request through Claude.ai"""
        try:
            async with self.metrics.measure('claude_request'):
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                return self._process_response(response)
                
        except Exception as e:
            logger.error(f'Claude request failed: {str(e)}')
            raise ClaudeError(f'Failed to process request: {str(e)}')

    def _process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Process Claude's response"""
        try:
            return {
                'content': response.content[0].text,
                'tokens': response.usage.total_tokens,
                'model': response.model,
                'role': response.role
            }
        except Exception as e:
            logger.error(f'Failed to process Claude response: {str(e)}')
            raise ClaudeError(f'Failed to process response: {str(e)}')
