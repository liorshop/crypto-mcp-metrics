import aiohttp
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from ..config import Config
from ..utils.error_handler import APIError
import backoff

class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.window = Config.RATE_LIMIT_WINDOW
    
    def _cleanup_old_requests(self, service: str) -> None:
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window)
        self.requests[service] = [
            timestamp for timestamp in self.requests.get(service, [])
            if timestamp > window_start
        ]
    
    async def check_limit(self, service: str) -> None:
        self._cleanup_old_requests(service)
        current_requests = len(self.requests.get(service, []))
        max_requests = Config.MAX_REQUESTS_PER_WINDOW.get(service, 0)
        
        if current_requests >= max_requests:
            raise APIError(f'Rate limit exceeded for {service}')
        
        if service not in self.requests:
            self.requests[service] = []
        self.requests[service].append(datetime.now())

class APIHandler:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiter = RateLimiter()
    
    async def initialize(self) -> None:
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None
    
    @backoff.on_exception(backoff.expo,
                         (aiohttp.ClientError, asyncio.TimeoutError),
                         max_tries=3)
    async def request(self,
                      method: str,
                      service: str,
                      endpoint: str,
                      params: Optional[Dict[str, Any]] = None,
                      headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        await self.initialize()
        await self.rate_limiter.check_limit(service)
        
        base_url = Config.get_base_url(service)
        api_key = Config.get_api_key(service)
        
        headers = headers or {}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        url = f'{base_url}/{endpoint.lstrip("/")}'
        
        try:
            async with self.session.request(method,
                                          url,
                                          params=params,
                                          headers=headers) as response:
                if response.status >= 400:
                    raise APIError(
                        f'API request failed: {response.status} {await response.text()}')
                return await response.json()
        except aiohttp.ClientError as e:
            raise APIError(f'API request failed: {str(e)}')
    
    async def get(self,
                  service: str,
                  endpoint: str,
                  params: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        return await self.request('GET', service, endpoint, params, headers)
    
    async def post(self,
                   service: str,
                   endpoint: str,
                   params: Optional[Dict[str, Any]] = None,
                   headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        return await self.request('POST', service, endpoint, params, headers)