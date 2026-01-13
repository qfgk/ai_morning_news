"""
Flask API 启动脚本
"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from api.app import create_app
from config.settings import get_settings

# 创建应用实例
app = create_app()
settings = get_settings()

if __name__ == '__main__':
    print("=" * 60)
    print(f"🚀 {settings.APP_NAME} API Server")
    print("=" * 60)
    print(f"\n📋 服务配置:")
    print(f"   环境: {settings.ENVIRONMENT}")
    print(f"   调试模式: {settings.DEBUG}")
    print(f"\n🌐 服务地址:")
    print(f"   http://{settings.FLASK_HOST}:{settings.FLASK_PORT}")
    print(f"\n📌 API端点:")
    print(f"   GET  /health                    - 健康检查")
    print(f"   GET  /api/v1/briefing/latest    - 获取最新早报")
    print(f"   GET  /api/v1/briefing/<date>    - 获取指定日期早报")
    print(f"   POST /api/v1/briefing/generate  - 手动生成早报")
    print(f"   GET  /api/v1/briefing/list      - 早报列表")
    print(f"\n" + "=" * 60)
    print("⚡ 启动服务...")
    print("=" * 60 + "\n")

    app.run(
        host=settings.FLASK_HOST,
        port=settings.FLASK_PORT,
        debug=settings.DEBUG
    )
