"""
早报系统运行脚本
支持缓存和数据库功能
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from services.news_service import NewsService
from services.ai_summary_service import AISummaryService
from repositories.news_repository import NewsRepository
from cache.cache_repository import CacheRepository
from cache.redis_client import RedisClient
from config.settings import get_settings, get_ai_settings


async def main():
    """主函数"""
    settings = get_settings()

    print("=" * 60)
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION}")
    print("=" * 60)

    # 获取 AI 配置
    try:
        api_key, base_url, model = get_ai_settings()
        print(f"\n🤖 AI 配置:")
        print(f"   API: {base_url}")
        print(f"   模型: {model}")
    except ValueError as e:
        print(f"❌ 错误: {e}")
        print("   请在 .env 文件中设置 AI_API_KEY")
        print("   可以复制 .env.example 为 .env 并填入你的API密钥")
        return

    # 解析命令行参数
    use_cache = "--no-cache" not in sys.argv
    use_db = "--db" in sys.argv
    use_redis = "--redis" in sys.argv

    print(f"\n📋 运行模式:")
    print(f"   缓存: {'✅' if use_cache else '❌'}")
    print(f"   数据库: {'✅' if use_db else '❌'}")
    print(f"   Redis: {'✅' if use_redis else '❌'}")

    # 初始化 AI 服务
    ai_service = AISummaryService(
        api_key=api_key,
        base_url=base_url,
        model=model,
        max_concurrent=settings.AI_SUMMARY_CONCURRENT
    )

    news_repo = None
    if use_db:
        print(f"\n💾 初始化数据库...")
        try:
            news_repo = NewsRepository()
            print(f"   ✅ 数据库已连接")
        except Exception as e:
            print(f"   ❌ 数据库连接失败: {e}")
            print(f"   提示: 请先运行 'python scripts/init_db.py' 初始化数据库")
            use_db = False

    cache_repo = None
    if use_redis:
        print(f"\n🔄 初始化Redis...")
        try:
            redis_client = RedisClient(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB
            )
            await redis_client.connect()
            if await redis_client.ping():
                cache_repo = CacheRepository(redis_client)
                print(f"   ✅ Redis已连接")
            else:
                print(f"   ❌ Redis连接失败")
                await redis_client.disconnect()
        except Exception as e:
            print(f"   ❌ Redis连接失败: {e}")
            print(f"   提示: 请确保Redis服务已启动")

    # 创建新闻服务
    news_service = NewsService(
        ai_service=ai_service,
        news_repo=news_repo,
        cache_repo=cache_repo
    )

    # 生成早报
    briefing = await news_service.generate_daily_briefing(
        sources=["aibase"],
        limit=settings.CRAWLER_MAX_ARTICLES,
        use_cache=use_cache,
        save_to_db=use_db
    )

    # 输出结果
    print("\n" + "=" * 60)
    print(f"📰 {briefing.title}")
    print("=" * 60)

    if briefing.articles:
        print(f"\n✅ 共获取 {briefing.total_count} 篇文章\n")

        for i, article in enumerate(briefing.articles, 1):
            print(f"{i}. {article.title}")
            if article.summary:
                print(f"   {article.summary}")
            print()

        if briefing.ai_summary:
            print("📝 每日汇总:")
            print(f"   {briefing.ai_summary}\n")

        # 保存到JSON
        news_service.save_briefing_to_json(briefing)

        print("=" * 60)
        print("✅ 早报生成完成！")
        print("=" * 60)
    else:
        print("⚠️ 未获取到任何文章")

    # 关闭Redis连接
    if cache_repo and cache_repo.redis:
        await cache_repo.redis.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
