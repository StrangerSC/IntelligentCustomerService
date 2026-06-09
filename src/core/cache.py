"""缓存工具。

开发模式（REDIS_URL 为空）使用本地内存，生产模式使用 Redis。
"""

import asyncio
import time

from src.config.settings import settings


class LoginAttemptCache:
    """登录失败计数器缓存。

    有 REDIS_URL → Redis 后端，否则 → 本地 dict 后端。
    接口一致，调用方无需关心后端。
    """

    _redis: "redis.asyncio.Redis | None" = None
    _local: dict[str, tuple[int, float]] = {}      # {key: (count, expire_at)}
    _lock: asyncio.Lock | None = None

    def _use_redis(self) -> bool:
        return bool(settings.REDIS_URL)

    async def _get_redis(self) -> "redis.asyncio.Redis":
        if self._redis is None:
            import redis.asyncio as aioredis

            self._redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding='utf-8',
                decode_responses=True,
            )
        return self._redis

    async def incr(self, key: str, ttl: int) -> int:
        """自增计数器，返回当前值。每次调用重置 key 的 TTL。"""
        if self._use_redis():
            client = await self._get_redis()
            async with client.pipeline(transaction=True) as pipe:
                pipe.incr(key)
                pipe.expire(key, ttl)
                results = await pipe.execute()
            return results[0]

        # 本地模式
        if self._lock is None:
            self._lock = asyncio.Lock()
        async with self._lock:
            now = time.monotonic()
            # 清理过期 key
            expired = [k for k, (_, exp) in self._local.items() if now >= exp]
            for k in expired:
                del self._local[k]
            # 自增
            if key in self._local:
                value, _ = self._local[key]
                value += 1
            else:
                value = 1
            self._local[key] = (value, now + ttl)
            return value

    async def delete(self, key: str) -> None:
        """删除计数。"""
        if self._use_redis():
            client = await self._get_redis()
            await client.delete(key)
            return

        if self._lock is None:
            self._lock = asyncio.Lock()
        async with self._lock:
            self._local.pop(key, None)


# 单例
cache = LoginAttemptCache()
