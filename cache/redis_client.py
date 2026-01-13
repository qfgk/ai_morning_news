"""
Redis 客户端封装
提供异步Redis操作接口
"""

import json
import redis.asyncio as aioredis
from typing import Optional, Any


class RedisClient:
    """Redis 客户端封装"""

    def __init__(self, host: str = "localhost", port: int = 6379,
                 password: Optional[str] = None, db: int = 0):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.client: Optional[aioredis.Redis] = None

    async def connect(self):
        """建立连接"""
        self.client = await aioredis.from_url(
            f"redis://{self.host}:{self.port}",
            password=self.password,
            db=self.db,
            encoding="utf-8",
            decode_responses=True
        )

    async def disconnect(self):
        """断开连接"""
        if self.client:
            await self.client.close()

    async def ping(self) -> bool:
        """测试连接"""
        if self.client:
            return await self.client.ping()
        return False

    async def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        if not self.client:
            return None
        return await self.client.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None):
        """设置缓存"""
        if not self.client:
            return
        await self.client.set(key, value, ex=ex)

    async def get_json(self, key: str) -> Optional[dict]:
        """获取JSON缓存"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None

    async def set_json(self, key: str, value: Any, ex: Optional[int] = None):
        """设置JSON缓存"""
        await self.set(key, json.dumps(value, ensure_ascii=False), ex=ex)

    async def delete(self, key: str):
        """删除缓存"""
        if not self.client:
            return
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not self.client:
            return False
        return await self.client.exists(key) > 0

    async def acquire_lock(self, key: str, timeout: int = 3600) -> bool:
        """获取分布式锁"""
        if not self.client:
            return False
        return await self.client.set(key, "1", nx=True, ex=timeout)

    async def release_lock(self, key: str):
        """释放分布式锁"""
        await self.delete(key)

    async def expire(self, key: str, seconds: int):
        """设置过期时间"""
        if not self.client:
            return
        await self.client.expire(key, seconds)

    async def ttl(self, key: str) -> int:
        """获取剩余过期时间"""
        if not self.client:
            return -1
        return await self.client.ttl(key)
