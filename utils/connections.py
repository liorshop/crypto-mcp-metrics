import os
import redis
import asyncpg
from typing import Optional
from contextlib import asynccontextmanager

class ConnectionManager:
    def __init__(self):
        self.redis_pool: Optional[redis.ConnectionPool] = None
        self.pg_pool: Optional[asyncpg.Pool] = None

    async def init_connections(self):
        """Initialize all connections"""
        await self._init_redis()
        await self._init_postgres()

    async def _init_redis(self):
        """Initialize Redis connection pool"""
        self.redis_pool = redis.ConnectionPool.from_url(
            os.getenv('REDIS_URL', 'redis://redis:6379'),
            decode_responses=True
        )

    async def _init_postgres(self):
        """Initialize PostgreSQL connection pool"""
        self.pg_pool = await asyncpg.create_pool(
            os.getenv('POSTGRES_URL'),
            min_size=5,
            max_size=20
        )

    @asynccontextmanager
    async def get_redis(self):
        """Get Redis connection from pool"""
        if not self.redis_pool:
            await self._init_redis()
        conn = redis.Redis(connection_pool=self.redis_pool)
        try:
            yield conn
        finally:
            await conn.close()

    @asynccontextmanager
    async def get_postgres(self):
        """Get PostgreSQL connection from pool"""
        if not self.pg_pool:
            await self._init_postgres()
        async with self.pg_pool.acquire() as conn:
            yield conn

    async def cleanup(self):
        """Clean up all connections"""
        if self.redis_pool:
            self.redis_pool.disconnect()
        if self.pg_pool:
            await self.pg_pool.close()