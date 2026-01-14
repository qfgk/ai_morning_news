"""
Celery 配置
"""
from celery import Celery
from celery.schedules import crontab
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


def get_beat_schedule():
    """根据配置生成定时任务调度表"""
    settings = get_settings()

    if not settings.SCHEDULE_CRONTAB:
        return {}  # 未配置定时任务

    # 解析 crontab 表达式: "分 时 日 月 周"
    # 例如: "0 8 * * *" = 每天 8:00
    parts = settings.SCHEDULE_CRONTAB.strip().split()

    if len(parts) != 5:
        print(f"警告: SCHEDULE_CRONTAB 格式错误: {settings.SCHEDULE_CRONTAB}")
        print("正确格式: \"分 时 日 月 周\"，例如: \"0 8 * * *\"")
        return {}

    minute, hour, day, month, day_of_week = parts

    return {
        'generate-daily-briefing': {
            'task': 'tasks.daily_generation.generate_daily_briefing_task',
            'schedule': crontab(
                minute=minute,
                hour=hour,
                day_of_month=day,
                month_of_year=month,
                day_of_week=day_of_week
            ),
            'options': {
                'expires': 3600  # 任务1小时后过期
            }
        }
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

    # 设置定时任务调度
    celery.conf.beat_schedule = get_beat_schedule()

    return celery
