"""
配置管理
使用 pydantic-settings 管理环境变量
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


def get_ai_config(settings: 'Settings') -> tuple[str, str, str]:
    """
    获取 AI 配置

    Returns:
        (api_key, base_url, model)
    """
    if not settings.AI_API_KEY:
        raise ValueError("未配置 AI_API_KEY，请在 .env 文件中设置")

    return (
        settings.AI_API_KEY,
        settings.AI_BASE_URL,
        settings.AI_MODEL
    )


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

    # AI 大模型配置（支持 OpenAI 格式）
    AI_API_KEY: str  # API 密钥（必填）
    AI_BASE_URL: str = "https://api.openai.com/v1"  # API 基础 URL
    AI_MODEL: str = "gpt-3.5-turbo"  # 模型名称

    # Celery 配置
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # 爬虫配置
    CRAWLER_TIMEOUT: int = 30
    CRAWLER_MAX_ARTICLES: int = 10
    CRAWLER_DELAY: float = 1.0

    # AI 总结并发数
    AI_SUMMARY_CONCURRENT: int = 10  # 同时请求AI的数量

    # 定时任务配置（crontab 表达式）
    SCHEDULE_CRONTAB: str = "0 8 * * *"  # 每天 8:00 (分 时 日 月 周)

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


def get_ai_settings() -> tuple[str, str, str]:
    """
    获取 AI 配置的便捷函数

    Returns:
        (api_key, base_url, model)

    Raises:
        ValueError: 如果未配置 AI 密钥
    """
    settings = get_settings()
    return get_ai_config(settings)
