"""
Celery Worker 启动脚本
"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from celery import Celery
from config.celery_config import CeleryConfig

# 创建Celery应用
app = Celery('morning_news')
app.config_from_object(CeleryConfig)

if __name__ == '__main__':
    print("=" * 60)
    print("🔄 Celery Worker")
    print("=" * 60)
    print(f"\n📋 配置:")
    print(f"   Broker: {CeleryConfig.broker_url}")
    print(f"   Backend: {CeleryConfig.result_backend}")
    print(f"\n⚡ 启动 Worker...")
    print("=" * 60 + "\n")

    # 启动worker（Windows 兼容：使用 solo pool）
    import platform
    if platform.system() == 'Windows':
        print("⚠️  检测到 Windows 环境，使用 solo pool（单进程模式）")
        app.worker_main(['worker', '--loglevel=info', '--pool=solo'])
    else:
        app.worker_main(['worker', '--loglevel=info'])
