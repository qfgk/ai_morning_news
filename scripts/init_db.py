"""
数据库初始化脚本
创建数据库表
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from database import init_db, get_db_manager
from config.settings import get_settings


def main():
    """主函数"""
    settings = get_settings()

    print("=" * 60)
    print("🗄️  数据库初始化")
    print("=" * 60)

    # 检查数据库配置
    if not settings.DATABASE_URL:
        print("❌ 错误: DATABASE_URL 环境变量未设置")
        print("   请在 .env 文件中配置数据库连接")
        print("   例如: DATABASE_URL=mysql+pymysql://root:password@localhost/morning_news")
        return

    print(f"\n📋 数据库配置:")
    print(f"   URL: {settings.DATABASE_URL}")

    # 确认操作
    response = input("\n⚠️  此操作将创建数据库表，是否继续？(y/n): ")
    if response.lower() != 'y':
        print("❌ 操作已取消")
        return

    try:
        print("\n🔧 开始初始化数据库...")
        init_db()
        print("✅ 数据库初始化成功！")

        print("\n📊 已创建以下表:")
        print("   - articles         文章表")
        print("   - daily_briefings  每日早报表")
        print("   - task_logs        任务日志表")

        print("\n" + "=" * 60)
        print("✅ 初始化完成！")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        print("\n请检查:")
        print("   1. 数据库服务是否已启动")
        print("   2. 数据库连接配置是否正确")
        print("   3. 数据库用户是否有创建表的权限")


if __name__ == "__main__":
    main()
