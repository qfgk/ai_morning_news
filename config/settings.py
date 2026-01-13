"""
配置管理
使用 pydantic-settings 管理环境变量
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    APP_NAME: str = "Morning News System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development/staging/production

    # Flask 配置
    FLASK_HOST: str = "0.0.0.0"
    FLASK_PORT: int = 5000

    # API 密钥（留空则不需要验证）
    API_KEY: Optional[str] = None

    # 数据库配置
    DATABASE_URL: Optional[str] = None

    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    # 智谱AI配置
    ZHIPUAI_API_KEY: str
    ZHIPUAI_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4"
    ZHIPUAI_MODEL: str = "glm-4.7"

    # Celery 配置
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # 爬虫配置
    CRAWLER_TIMEOUT: int = 30
    CRAWLER_MAX_ARTICLES: int = 10
    CRAWLER_DELAY: float = 1.0

    # AI 总结并发数
    AI_SUMMARY_CONCURRENT: int = 10  # 同时请求AI的数量

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 全局配置实例
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """获取配置单例"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
