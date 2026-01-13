"""
Celery Beat 启动脚本（定时任务调度器）
"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from celery import Celery
from celery.beat import Beat
from config.celery_config import CeleryConfig

# 创建Celery应用
app = Celery('morning_news')
app.config_from_object(CeleryConfig)

if __name__ == '__main__':
    print("=" * 60)
    print("⏰ Celery Beat - 定时任务调度器")
    print("=" * 60)
    print(f"\n📋 配置:")
    print(f"   Broker: {CeleryConfig.broker_url}")
    print(f"   Backend: {CeleryConfig.result_backend}")
    print(f"\n⚡ 启动调度器...")
    print("=" * 60 + "\n")

    # 启动beat
    beat = Beat(app=app, loglevel='info')
    beat.run()
