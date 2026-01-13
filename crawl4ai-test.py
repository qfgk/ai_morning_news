import json
import asyncio
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from bs4 import BeautifulSoup
import re
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

from zhipuai import ZhipuAI

# 获取前10篇文章的编号（使用 crawl4ai 等待 JS 渲染）
async def extract_snumber_from_url(base_url, top_n=10):
    try:
        async with AsyncWebCrawler(verbose=True) as crawler:
            result = await crawler.arun(
                url=base_url,
                wait_for="css:a[href*='/news/']",  # 等待文章链接出现
                bypass_cache=True,
            )

            if not result.success:
                print(f"❌ 请求失败: {result.status_code}")
                return None

            soup = BeautifulSoup(result.html, 'html.parser')
            links = soup.find_all('a', href=True)

            # 使用集合去重
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
                # 降序排列（编号越大越新），取前N个
                sorted_numbers = sorted(snumbers, reverse=True)[:top_n]
                print(f"✅ 找到 {len(sorted_numbers)} 个文章编号: {sorted_numbers}")
                return sorted_numbers

            print("⚠️ 未找到文章链接")
            return None

    except Exception as e:
        print(f"❌ error: {e}")
        return None


async def extract_news_article(news_url):
    """使用 CSS 选择器提取文章内容"""

    schema = {
        "name": "AIbase News Article",
        "baseSelector": "article",  # 保持 article 作为基础范围
        "fields": [
            {
                "name": "title",
                "selector": "h1",  # 简单有效
                "type": "text",
            },
            {
                "name": "publication_date",
                "selector": "div.text-surface-500 > span:last-child",
                "type": "text",
            },
            {
                "name": "author",
                "selector": "h4 > .text-surface-600",
                "type": "text",
            },
            {
                "name": "content",
                "selector": "div.leading-8.post-content.overflow-hidden",
                "type": "text",
            }
        ],
    }

    extraction_strategy = JsonCssExtractionStrategy(schema)

    async with AsyncWebCrawler(verbose=False) as crawler:
        result = await crawler.arun(
            url=news_url,
            config=CrawlerRunConfig(
                extraction_strategy=extraction_strategy,
                wait_for="css:.post-content",  # 等待内容加载
                page_timeout=30000,
            ),
            page_timeout=30000,
        )

        if not result.success:
            print("请求失败")
            return None

        if result.extracted_content is None:
            print(f"    提取失败")
            print(f"    已保存HTML到: debug_article.html")
            with open("debug_article.html", "w", encoding="utf-8") as f:
                f.write(result.html if result.html else result.cleaned_html)
            return None

        try:
            extracted_data = json.loads(result.extracted_content)
            # 如果返回的是列表，取出第一个元素
            if isinstance(extracted_data, list):
                if len(extracted_data) > 0:
                    return extracted_data[0]
                else:
                    return None
            return extracted_data
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return None

def get_news_summary(data):
    """同步函数：调用AI生成文章总结"""
    API_KEY = "61f915e05dd949e98a94267103c0d9ec.FtcjGX1KzJfIaZZj"
    BASE_URL = "https://open.bigmodel.cn/api/paas/v4"

    client = ZhipuAI(api_key=API_KEY, base_url=BASE_URL)

    system_prompt = """
    ## Goals
    读取并解析 JSON 格式的文章，提炼出文章的主旨，形成最多3句，推荐2句的简洁的概述。

    ## Constrains:
    概述长度不超过 80 字，保持文章的原意和重点。

    ## Skills
    JSON 解析能力，文章内容理解和总结能力。

    ## Output Format
    最多3句，推荐2句概述，简洁明了，不超过 80 字。

    ## Workflow:
    1. 读取并解析 JSON 格式的文章
    2. 理解文章内容，提取关键信息
    3. 生成简洁的概述，最多3句，推荐2句，不超过 80 字
    """

    try:
        response = client.chat.completions.create(
            model="glm-4.7",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"文章内容：{data}"}
            ],
            top_p=0.7,
            temperature=0.1,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"    ❌ AI总结失败: {e}")
        return None


async def get_news_summary_async(data):
    """异步包装器：在线程池中执行同步的AI调用"""
    return await asyncio.to_thread(get_news_summary, data)


def save_articles_to_json(articles, filename="articles_data.json"):
    """保存文章列表到JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
async def main():
    # 1. 获取文章编号
    numbers = await extract_snumber_from_url("https://www.aibase.com/zh/news/", 10)

    if not numbers:
        print("❌ 未获取到文章编号")
        return

    # 2. 拼接成完整URL
    urls = [f"https://www.aibase.com/zh/news/{num}" for num in numbers]
    print(f"\n📝 文章URL列表:")
    for i, url in enumerate(urls, 1):
        print(f"  {i}. {url}")

    # 3. 流水线处理：获取文章 -> AI总结 -> 保存
    print(f"\n📥 开始处理文章...")
    articles = []
    news_summary = ""

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] 正在处理: {url}")

        # 步骤1: 获取文章内容
        article = await extract_news_article(url)
        if not article or not article.get('title'):
            print(f"    ❌ 获取失败")
            await asyncio.sleep(1)
            continue

        print(f"    ✅ 标题: {article.get('title', '')}")

        # 步骤2: 立即调用AI总结
        print(f"    🤖 正在生成总结...", end=" ", flush=True)
        summary = await get_news_summary_async(article.get('content', ''))
        article['summary'] = summary

        if summary:
            print(f"✅")
            # 累积早报格式
            news_summary += f"{i}.{article.get('title', '')}\n{summary}\n\n"
        else:
            print(f"❌")

        # 步骤3: 添加到列表并立即保存
        articles.append(article)
        save_articles_to_json(articles)
        print(f"    💾 已保存到 articles_data.json")

        await asyncio.sleep(1)  # 避免请求过快

    # 4. 输出汇总
    print(f"\n{'='*60}")
    print(f"✅ 成功处理 {len(articles)} 篇文章")
    print(f"{'='*60}")

    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article.get('title', '无标题')}")
        if article.get('publication_date'):
            print(f"   📅 {article.get('publication_date')}")
        if article.get('summary'):
            print(f"   📝 总结: {article.get('summary')}")

    # 5. 输出早报格式
    print(f"\n{'='*60}")
    print("📰 早报汇总")
    print(f"{'='*60}\n")
    print(news_summary)
    print(f"💾 最终数据已保存到: articles_data.json")



if __name__ == "__main__":
    asyncio.run(main())