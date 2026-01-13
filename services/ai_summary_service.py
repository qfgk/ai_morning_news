"""
AI 总结服务
封装智谱AI API调用
"""

from typing import Optional, List
import asyncio
from zhipuai import ZhipuAI
from core.models import Article, ArticleStatus
from core.constants import AI_SUMMARY_SYSTEM_PROMPT


class AISummaryService:
    """AI 总结服务"""

    def __init__(self, api_key: str, base_url: str = "https://open.bigmodel.cn/api/paas/v4",
                 model: str = "glm-4.7", max_concurrent: int = 10):
        self.client = ZhipuAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.system_prompt = AI_SUMMARY_SYSTEM_PROMPT
        self.max_concurrent = max_concurrent

    def _generate_summary_sync(self, content: str) -> Optional[str]:
        """同步生成单篇文章总结"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"文章内容：{content}"}
                ],
                top_p=0.7,
                temperature=0.1,
                stream=False
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"    ❌ AI总结失败: {e}")
            return None

    async def generate_summary(self, content: str) -> Optional[str]:
        """异步生成单篇文章总结"""
        return await asyncio.to_thread(self._generate_summary_sync, content)

    async def batch_generate_summaries(self, articles: List[Article]) -> List[Article]:
        """批量生成文章总结（并发执行）"""
        # 创建任务列表
        tasks = []
        for article in articles:
            if not article.summary:
                tasks.append(self.generate_summary(article.content))
            else:
                tasks.append(None)  # 已有总结的占位

        if not tasks:
            return articles

        # 过滤出需要执行的任务
        pending_tasks = [t for t in tasks if t is not None]

        if not pending_tasks:
            return articles

        print(f"    🔄 并发生成 {len(pending_tasks)} 篇文章总结（最大并发: {self.max_concurrent}）...")

        # 使用 Semaphore 限制并发数
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def limited_task(task):
            async with semaphore:
                return await task

        # 并发执行所有任务
        results = await asyncio.gather(*[limited_task(t) for t in pending_tasks])

        # 将结果赋值回文章
        result_index = 0
        for i, article in enumerate(articles):
            if tasks[i] is not None:  # 需要生成总结的
                article.summary = results[result_index]
                # 生成成功后更新状态为 completed
                if article.summary:
                    article.status = ArticleStatus.COMPLETED
                result_index += 1

        return articles

    def _generate_daily_summary_sync(self, titles_and_summaries: str) -> Optional[str]:
        """同步生成每日早报整体总结"""
        prompt = f"""
                请基于以下文章列表，生成一份简短的早报汇总（3-5句话）：
                
                {titles_and_summaries}
                
                要求：
                1. 总结今日最重要的3-5条资讯
                2. 每条一句话概括
                3. 总字数不超过100字
                """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的新闻编辑，擅长提炼资讯要点。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"    ❌ 生成每日总结失败: {e}")
            return None

    async def generate_daily_summary(self, articles: List[Article]) -> Optional[str]:
        """生成每日早报整体总结"""
        if not articles:
            print(f"    ⚠️ 文章列表为空，无法生成每日总结")
            return None

        print(f"    📝 正在生成每日总结（共 {len(articles)} 篇文章）...")

        titles_and_summaries = "\n".join([
            f"{i+1}. {article.title}\n{article.summary}"
            for i, article in enumerate(articles)
        ])

        result = await asyncio.to_thread(self._generate_daily_summary_sync, titles_and_summaries)

        if result:
            print(f"    ✅ 每日总结生成成功")
        else:
            print(f"    ⚠️ 每日总结生成失败（返回为空）")

        return result
