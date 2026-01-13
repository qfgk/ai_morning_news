"""
缓存仓储层
提供业务级别的缓存操作
"""

from typing import Optional, List, Dict, Any
from cache.redis_client import RedisClient
from cache.cache_keys import CacheKeys
from core.constants import (
    CACHE_TTL_DAILY_BRIEFING,
    CACHE_TTL_ARTICLE,
    CACHE_TTL_LATEST,
    CACHE_TTL_TASK_LOCK
)


class CacheRepository:
    """缓存仓储层"""

    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client

    async def get_daily_briefing(self, date: str) -> Optional[dict]:
        """获取早报缓存"""
        key = CacheKeys.daily_briefing(date)
        return await self.redis.get_json(key)

    async def set_daily_briefing(self, date: str, data: dict):
        """设置早报缓存"""
        key = CacheKeys.daily_briefing(date)
        await self.redis.set_json(key, data, ex=CACHE_TTL_DAILY_BRIEFING)

    async def get_article(self, article_id: str) -> Optional[dict]:
        """获取文章缓存"""
        key = CacheKeys.article(article_id)
        return await self.redis.get_json(key)

    async def set_article(self, article_id: str, data: dict):
        """设置文章缓存"""
        key = CacheKeys.article(article_id)
        await self.redis.set_json(key, data, ex=CACHE_TTL_ARTICLE)

    async def get_article_list(self, date: str) -> Optional[List[dict]]:
        """获取文章列表缓存"""
        key = CacheKeys.article_list(date)
        return await self.redis.get_json(key)

    async def set_article_list(self, date: str, data: List[dict]):
        """设置文章列表缓存"""
        key = CacheKeys.article_list(date)
        await self.redis.set_json(key, data, ex=3600)  # 1小时

    async def get_latest_briefing(self) -> Optional[dict]:
        """获取最新早报缓存"""
        return await self.redis.get_json(CacheKeys.LATEST_BRIEFING)

    async def set_latest_briefing(self, data: dict):
        """设置最新早报缓存"""
        await self.redis.set_json(CacheKeys.LATEST_BRIEFING, data, ex=CACHE_TTL_LATEST)

    async def acquire_task_lock(self, task_name: str, date: str) -> bool:
        """获取任务锁"""
        key = CacheKeys.task_lock(task_name, date)
        return await self.redis.acquire_lock(key, timeout=CACHE_TTL_TASK_LOCK)

    async def release_task_lock(self, task_name: str, date: str):
        """释放任务锁"""
        key = CacheKeys.task_lock(task_name, date)
        await self.redis.release_lock(key)

    async def delete_daily_briefing(self, date: str):
        """删除早报缓存"""
        key = CacheKeys.daily_briefing(date)
        await self.redis.delete(key)

    async def clear_all_briefings(self):
        """清空所有早报缓存（慎用）"""
        # 使用 SCAN 命令遍历所有早报缓存键
        pattern = CacheKeys.DAILY_BRIEFING.replace("{date}", "*")
        keys = []
        async for key in self.redis.client.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await self.redis.delete(*keys)

    async def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        info = await self.redis.client.info("stats")
        return {
            "total_keys": info.get("keyspace", 0),
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
        }
