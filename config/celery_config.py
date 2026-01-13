"""
Celery 配置
"""
from celery import Celery
from config.settings import get_settings

settings = get_settings()

# Celery 配置
class CeleryConfig:
    """Celery配置类"""

    # Broker配置
    broker_url = settings.CELERY_BROKER_URL or "redis://localhost:6379/1"
    result_backend = settings.CELERY_RESULT_BACKEND or "redis://localhost:6379/2"

    # 任务配置
    task_serializer = 'json'
    result_serializer = 'json'
    accept_content = ['json']
    timezone = 'Asia/Shanghai'
    enable_utc = True

    # 结果过期时间（1天）
    result_expires = 86400

    # 任务执行时间限制
    task_time_limit = 3600  # 1小时
    task_soft_time_limit = 3000  # 50分钟

    # Worker配置
    worker_prefetch_multiplier = 1
    worker_max_tasks_per_child = 1000

    # 任务路由
    task_routes = {
        'tasks.daily_generation.generate_daily_briefing_task': {'queue': 'briefing'},
    }

    # 定时任务配置
    beat_schedule = {
        'generate-daily-briefing': {
            'task': 'tasks.daily_generation.generate_daily_briefing_task',
            'schedule': 60 * 60 * 24,  # 每天（通过crontab更精确）
            # 'schedule': crontab(hour=8, minute=0),  # 每天8:00执行
            'options': {
                'expires': 3600  # 任务1小时后过期
            }
        },
    }


def create_celery(app=None):
    """创建Celery实例"""
    celery = Celery(
        'morning_news',
        broker=CeleryConfig.broker_url,
        backend=CeleryConfig.result_backend
    )

    # 加载配置
    celery.config_from_object(CeleryConfig)

    return celery
