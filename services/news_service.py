"""
新闻聚合服务
整合爬虫、AI总结、缓存和持久化
"""

from typing import List, Optional
from datetime import datetime
import asyncio

from core.models import Article, DailyBriefing
from adapters.factory import AdapterFactory
from repositories.news_repository import NewsRepository
from cache.cache_repository import CacheRepository


class NewsService:
    """新闻聚合服务（完整版，支持缓存和数据库）"""

    def __init__(self, ai_service, news_repo: NewsRepository = None, cache_repo: CacheRepository = None):
        self.adapter_factory = AdapterFactory()
        self.ai_service = ai_service
        self.news_repo = news_repo
        self.cache_repo = cache_repo

    async def generate_daily_briefing(
        self,
        date: Optional[str] = None,
        sources: Optional[List[str]] = None,
        limit: int = 10,
        use_cache: bool = True,
        save_to_db: bool = False
    ) -> DailyBriefing:
        """生成每日早报"""
        date = date or datetime.now().strftime("%Y-%m-%d")
        sources = sources or ["aibase"]

        print(f"\n📥 开始生成 {date} 的早报...")

        # 1. 检查缓存
        if use_cache and self.cache_repo:
            cached = await self.cache_repo.get_daily_briefing(date)
            if cached:
                print(f"✅ 从缓存获取早报")
                # 从缓存的数据恢复 DailyBriefing 对象
                articles = [Article(**a) for a in cached.get('articles', [])]
                return DailyBriefing(
                    id=cached.get('id'),
                    date=cached['date'],
                    title=cached['title'],
                    articles=articles,
                    total_count=cached['total_count'],
                    ai_summary=cached.get('ai_summary'),
                    created_at=datetime.fromisoformat(cached['created_at']) if cached.get('created_at') else None
                )

        # 2. 从多个消息源抓取文章
        all_articles = []
        for source in sources:
            print(f"\n📍 处理消息源: {source}")
            adapter = self.adapter_factory.get_adapter(source)
            if adapter:
                urls = await adapter.fetch_article_list(limit)
                print(f"    找到 {len(urls)} 篇文章")

                for i, url in enumerate(urls, 1):
                    print(f"    [{i}/{len(urls)}] 正在获取: {url}", end=" ")
                    article = await adapter.fetch_article(url)
                    if article:
                        print(f"✅ {article.title[:30]}...")
                        all_articles.append(article)
                    else:
                        print(f"❌")

        if not all_articles:
            print("⚠️ 未获取到任何文章")
            return DailyBriefing(
                date=date,
                title=f"早报 - {date}",
                articles=[],
                total_count=0
            )

        # 3. 生成AI总结
        print(f"\n🤖 开始生成AI总结...")
        articles_with_summary = await self.ai_service.batch_generate_summaries(all_articles)
        success_count = sum(1 for a in articles_with_summary if a.summary)
        print(f"    ✅ 成功生成 {success_count}/{len(articles_with_summary)} 篇文章总结")

        # 4. 生成整体总结
        daily_summary = await self.ai_service.generate_daily_summary(articles_with_summary)
        if daily_summary:
            print(f"    ✅ 每日汇总: {daily_summary}")

        # 5. 构建早报对象
        briefing = DailyBriefing(
            date=date,
            title=f"早报 - {date}",
            articles=articles_with_summary,
            total_count=len(articles_with_summary),
            ai_summary=daily_summary
        )

        # 6. 持久化到数据库
        if save_to_db and self.news_repo:
            print(f"\n💾 保存到数据库...")
            briefing_id = self.news_repo.save_daily_briefing(briefing)
            briefing.id = briefing_id
            print(f"    ✅ 已保存（ID: {briefing_id}）")

        # 7. 写入缓存
        if use_cache and self.cache_repo:
            await self.cache_repo.set_daily_briefing(date, briefing.to_dict())
            await self.cache_repo.set_latest_briefing(briefing.to_dict())
            print(f"    ✅ 已缓存")

        return briefing

    async def get_briefing_by_date(self, date: str) -> Optional[DailyBriefing]:
        """获取指定日期的早报"""
        # 先查缓存
        if self.cache_repo:
            cached = await self.cache_repo.get_daily_briefing(date)
            if cached:
                articles = [Article(**a) for a in cached.get('articles', [])]
                return DailyBriefing(
                    id=cached.get('id'),
                    date=cached['date'],
                    title=cached['title'],
                    articles=articles,
                    total_count=cached['total_count'],
                    ai_summary=cached.get('ai_summary'),
                    created_at=datetime.fromisoformat(cached['created_at']) if cached.get('created_at') else None
                )

        # 查数据库
        if self.news_repo:
            briefing_data = self.news_repo.get_daily_briefing(date)
            if briefing_data:
                articles = [Article(**a) for a in briefing_data.get('articles', [])]
                return DailyBriefing(
                    id=briefing_data.get('id'),
                    date=briefing_data['date'],
                    title=briefing_data['title'],
                    articles=articles,
                    total_count=briefing_data['total_count'],
                    ai_summary=briefing_data.get('ai_summary'),
                    created_at=datetime.fromisoformat(briefing_data['created_at']) if briefing_data.get('created_at') else None
                )

        return None

    async def get_latest_briefing(self) -> Optional[DailyBriefing]:
        """获取最新早报"""
        # 先查缓存
        if self.cache_repo:
            cached = await self.cache_repo.get_latest_briefing()
            if cached:
                articles = [Article(**a) for a in cached.get('articles', [])]
                return DailyBriefing(
                    id=cached.get('id'),
                    date=cached['date'],
                    title=cached['title'],
                    articles=articles,
                    total_count=cached['total_count'],
                    ai_summary=cached.get('ai_summary'),
                    created_at=datetime.fromisoformat(cached['created_at']) if cached.get('created_at') else None
                )

        # 查数据库
        if self.news_repo:
            briefing_data = self.news_repo.get_latest_briefing()
            if briefing_data:
                articles = [Article(**a) for a in briefing_data.get('articles', [])]
                return DailyBriefing(
                    id=briefing_data.get('id'),
                    date=briefing_data['date'],
                    title=briefing_data['title'],
                    articles=articles,
                    total_count=briefing_data['total_count'],
                    ai_summary=briefing_data.get('ai_summary'),
                    created_at=datetime.fromisoformat(briefing_data['created_at']) if briefing_data.get('created_at') else None
                )

        return None

    def save_briefing_to_json(self, briefing: DailyBriefing, filename: str = "articles_data.json"):
        """保存早报到JSON文件"""
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(briefing.to_dict(), f, ensure_ascii=False, indent=2)
        print(f"\n💾 已保存到: {filename}")
