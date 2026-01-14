"""
Celery 应用实例
"""
from celery import Celery
from config.celery_config import CeleryConfig, get_beat_schedule

# 创建Celery应用
celery_app = Celery('morning_news')

# 加载配置
celery_app.config_from_object(CeleryConfig)

# 设置定时任务调度
celery_app.conf.beat_schedule = get_beat_schedule()

# 如果需要自动发现任务
# celery_app.autodiscover_tasks(['tasks'])
