"""
早报系统测试脚本
使用新架构测试基本功能
"""

import asyncio
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from services.news_service import NewsService
from services.ai_summary_service import AISummaryService
from config.settings import get_settings


async def main():
    """主函数"""
    settings = get_settings()

    print("=" * 60)
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION}")
    print("=" * 60)

    # 检查API密钥
    if not settings.ZHIPUAI_API_KEY or settings.ZHIPUAI_API_KEY == "your_api_key_here":
        print("❌ 错误: 请在 .env 文件中设置 ZHIPUAI_API_KEY")
        print("   可以复制 .env.example 为 .env 并填入你的API密钥")
        return

    # 初始化服务
    ai_service = AISummaryService(
        api_key=settings.ZHIPUAI_API_KEY,
        base_url=settings.ZHIPUAI_BASE_URL,
        model=settings.ZHIPUAI_MODEL
    )
    news_service = NewsService(ai_service)

    # 生成早报
    briefing = await news_service.generate_daily_briefing(
        sources=["aibase"],
        limit=settings.CRAWLER_MAX_ARTICLES
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


if __name__ == "__main__":
    asyncio.run(main())
