"""
缓存键定义
统一管理所有Redis缓存键
"""

class CacheKeys:
    """Redis 缓存键定义"""

    # 早报缓存（24小时）
    DAILY_BRIEFING = "morning_news:daily_briefing:{date}"  # TTL: 86400

    # 文章缓存（7天）
    ARTICLE = "morning_news:article:{id}"  # TTL: 604800

    # 文章列表缓存（1小时）
    ARTICLE_LIST = "morning_news:articles:list:{date}"  # TTL: 3600

    # 最新早报缓存（15分钟）
    LATEST_BRIEFING = "morning_news:latest"  # TTL: 900

    # 任务锁（防止重复执行）
    TASK_LOCK = "morning_news:lock:task:{task_name}:{date}"  # TTL: 3600

    # API限流
    RATE_LIMIT = "morning_news:rate_limit:{user_id}:{endpoint}"  # TTL: 60

    @staticmethod
    def daily_briefing(date: str) -> str:
        """获取早报缓存键"""
        return CacheKeys.DAILY_BRIEFING.format(date=date)

    @staticmethod
    def article(article_id: str) -> str:
        """获取文章缓存键"""
        return CacheKeys.ARTICLE.format(id=article_id)

    @staticmethod
    def article_list(date: str) -> str:
        """获取文章列表缓存键"""
        return CacheKeys.ARTICLE_LIST.format(date=date)

    @staticmethod
    def task_lock(task_name: str, date: str) -> str:
        """获取任务锁缓存键"""
        return CacheKeys.TASK_LOCK.format(task_name=task_name, date=date)

    @staticmethod
    def rate_limit(user_id: str, endpoint: str) -> str:
        """获取限流缓存键"""
        return CacheKeys.RATE_LIMIT.format(user_id=user_id, endpoint=endpoint)
