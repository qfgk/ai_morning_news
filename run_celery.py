"""
Celery Worker 启动脚本
"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from tasks.celery_app import celery_app

# 导入任务模块以注册任务（重要！）
import tasks.daily_generation

if __name__ == '__main__':
    print("=" * 60)
    print("🔄 Celery Worker")
    print("=" * 60)
    print(f"\n📋 配置:")
    print(f"   Broker: {celery_app.conf.broker_url}")
    print(f"   Backend: {celery_app.conf.result_backend}")
    print(f"\n📝 已注册任务:")
    for task_name in sorted(celery_app.tasks.keys()):
        if not task_name.startswith('celery.'):
            print(f"   - {task_name}")
    print(f"\n⚡ 启动 Worker...")
    print("=" * 60 + "\n")

    # 启动worker（Windows 兼容：使用 solo pool）
    import platform
    if platform.system() == 'Windows':
        print("⚠️  检测到 Windows 环境，使用 solo pool（单进程模式）")
        celery_app.worker_main(['worker', '--loglevel=info', '--pool=solo', '-Q', 'celery,briefing'])
    else:
        celery_app.worker_main(['worker', '--loglevel=info', '-Q', 'celery,briefing'])
