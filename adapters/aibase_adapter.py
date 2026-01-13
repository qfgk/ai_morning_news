"""
AIbase 消息源适配器
基于现有 crawl4ai-test.py 重构
"""

import json
import re
from typing import List, Optional
from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

from adapters.base import BaseAdapter
from core.models import Article, SourceType, ArticleStatus


class AIBaseAdapter(BaseAdapter):
    """AIbase 消息源适配器"""

    BASE_URL = "https://www.aibase.com/zh/news/"

    def __init__(self):
        super().__init__(source_type=SourceType.AIBASE)
        self.extraction_schema = {
            "name": "AIbase News Article",
            "baseSelector": "article",
            "fields": [
                {
                    "name": "title",
                    "selector": "h1",
                    "type": "text",
                },
                {
                    "name": "publication_date",
                    "selector": "div.text-surface-500 > span:last-child",
                    "type": "text",
                },
                {
                    "name": "author",
                    "selector": "h4.text-surface-600",
                    "type": "text",
                },
                {
                    "name": "content",
                    "selector": "div.leading-8.post-content.overflow-hidden",
                    "type": "text",
                }
            ],
        }

    async def fetch_article_list(self, limit: int = 10) -> List[str]:
        """获取文章编号列表"""
        try:
            async with AsyncWebCrawler(verbose=True) as crawler:
                result = await crawler.arun(
                    url=self.BASE_URL,
                    wait_for="css:a[href*='/news/']",
                    bypass_cache=True,
                )

                if not result.success:
                    print(f"❌ 请求失败: {result.status_code}")
                    return []

                soup = BeautifulSoup(result.html, 'html.parser')
                links = soup.find_all('a', href=True)

                snumbers = set()
                for link in links:
                    href = link.get('href')
                    if href and '/news/' in href:
                        pattern = r'/zh/news/(\d+)'
                        match = re.search(pattern, href)
                        if match:
                            snumber = int(match.group(1))
                            snumbers.add(snumber)

                if snumbers:
                    sorted_numbers = sorted(snumbers, reverse=True)[:limit]
                    print(f"✅ 找到 {len(sorted_numbers)} 个文章编号: {sorted_numbers}")
                    return [f"{self.BASE_URL}{num}" for num in sorted_numbers]

                print("⚠️ 未找到文章链接")
                return []
        except Exception as e:
            print(f"❌ 获取文章列表失败: {e}")
            return []

    async def fetch_article(self, url: str) -> Optional[Article]:
        """提取文章内容"""
        extraction_strategy = JsonCssExtractionStrategy(self.extraction_schema)

        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(
                url=url,
                config=CrawlerRunConfig(
                    extraction_strategy=extraction_strategy,
                    wait_for="css:.post-content",
                    page_timeout=30000,
                ),
                page_timeout=30000,
            )

            if not result.success:
                print(f"    ❌ 请求失败: {url}")
                return None

            if result.extracted_content is None:
                print(f"    ❌ 提取失败: {url}")
                return None

            try:
                extracted_data = json.loads(result.extracted_content)
                if isinstance(extracted_data, list) and len(extracted_data) > 0:
                    extracted_data = extracted_data[0]
                elif isinstance(extracted_data, list):
                    return None

                return Article(
                    title=extracted_data.get('title', ''),
                    content=extracted_data.get('content', ''),
                    author=extracted_data.get('author'),
                    publication_date=extracted_data.get('publication_date'),
                    source_url=url,
                    source_type=self.source_type,
                    status=ArticleStatus.PROCESSING  # 抓取成功，等待AI总结
                )
            except (json.JSONDecodeError, KeyError) as e:
                print(f"    ❌ JSON解析失败: {e}")
                return None

    async def validate_url(self, url: str) -> bool:
        """验证URL是否为AIbase链接"""
        return "aibase.com/zh/news/" in url
