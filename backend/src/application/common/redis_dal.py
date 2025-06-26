import asyncio
import redis.asyncio as redis
from redis.asyncio.client import Lock

import os

redis_pool: redis.ConnectionPool = None
redis_pool_event_loop: asyncio.AbstractEventLoop = None


def get_redis_pool() -> redis.ConnectionPool:
    global redis_pool, redis_pool_event_loop
    if (
            redis_pool is None
            or redis_pool_event_loop is None
            or redis_pool_event_loop.is_closed()
            or redis_pool_event_loop is not asyncio.get_event_loop()
    ):
        redis_url = os.environ.get("REDIS_URL") or 'redis://'
        redis_pool = redis.ConnectionPool.from_url(
            url=redis_url,
            decode_responses=True,
        )
        redis_pool_event_loop = asyncio.get_event_loop()
    return redis_pool


class RedisDAL:
    def __init__(self):
        self._db = None
        self._pool = None

    @property
    def db(self):
        pool = get_redis_pool()
        if self._db is None or self._pool is not pool:
            self._pool = pool
            self._db = redis.Redis(connection_pool=pool, decode_responses=True)

        return self._db

    @staticmethod
    async def release():
        if redis_pool:
            await redis_pool.disconnect()

    async def get_val(self, pref: str) -> dict | None:
        return await self.db.get(f"nest_{pref}")

    async def set_val(self, pref: str, value: str):
        await self.db.set(
            f"nest_{pref}", value
        )

    async def del_val(self, pref: str):
        await self.db.delete(f"nest_{pref}")

    # lock = await RedisDAL().acquire_lock(f'key_{param_id}', blocking=False, timeout=10)
    async def acquire_lock(self, lock_name: str, blocking: bool = True, **kwargs) -> Lock | None:
        lock = self.db.lock(lock_name, **kwargs)
        result = await lock.acquire(blocking=blocking)

        if result:
            return lock
