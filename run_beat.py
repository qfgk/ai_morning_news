"""
Celery Beat 启动脚本（定时任务调度器）
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from tasks.celery_app import celery_app

if __name__ == '__main__':
    print("=" * 60)
    print("Celery Beat - 定时任务调度器")
    print("=" * 60)
    print(f"\n配置:")
    print(f"   Broker: {celery_app.conf.broker_url}")
    print(f"   Backend: {celery_app.conf.result_backend}")
    print(f"   Schedule: {os.getenv('SCHEDULE_CRONTAB', '未配置')}")
    print(f"\n启动调度器...")
    print("=" * 60 + "\n")

    # 使用 celery.apps.beat.Beat 启动调度器
    from celery.apps.beat import Beat
    beat = Beat(app=celery_app, loglevel='info')
    beat.run()
