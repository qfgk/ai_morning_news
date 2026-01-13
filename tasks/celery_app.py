"""
Celery 应用实例
"""
from celery import Celery
from config.celery_config import CeleryConfig

# 创建Celery应用
celery_app = Celery('morning_news')

# 加载配置
celery_app.config_from_object(CeleryConfig)

# 如果需要自动发现任务
# celery_app.autodiscover_tasks(['tasks'])
