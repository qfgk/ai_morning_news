"""
新闻数据访问层
"""
import hashlib
from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import desc

from database.models import ArticleDB, DailyBriefingDB, TaskLog, SourceTypeEnum, ArticleStatusEnum
from database.base import session_scope
from core.models import Article, DailyBriefing, SourceType, ArticleStatus


class NewsRepository:
    """新闻数据访问层"""

    @staticmethod
    def _generate_article_id(url: str) -> str:
        """生成文章ID（MD5）"""
        return hashlib.md5(url.encode()).hexdigest()

    def save_article(self, article: Article) -> str:
        """保存单篇文章"""
        article_id = self._generate_article_id(article.source_url)

        with session_scope() as session:
            # 检查是否已存在
            existing = session.query(ArticleDB).filter_by(id=article_id).first()
            if existing:
                # 更新
                existing.title = article.title
                existing.content = article.content
                existing.author = article.author
                existing.publication_date = article.publication_date
                existing.summary = article.summary
                existing.status = ArticleStatusEnum(article.status.value)
                existing.updated_at = datetime.now()
            else:
                # 新增
                article_db = ArticleDB(
                    id=article_id,
                    title=article.title,
                    content=article.content,
                    author=article.author,
                    publication_date=article.publication_date,
                    source_url=article.source_url,
                    source_type=SourceTypeEnum(article.source_type.value),
                    summary=article.summary,
                    status=ArticleStatusEnum(article.status.value),
                )
                session.add(article_db)

        return article_id

    def save_articles(self, articles: List[Article]) -> List[str]:
        """批量保存文章"""
        article_ids = []
        for article in articles:
            article_id = self.save_article(article)
            article_ids.append(article_id)
        return article_ids

    def get_article_by_url(self, url: str) -> Optional[dict]:
        """根据URL获取文章"""
        article_id = self._generate_article_id(url)
        with session_scope() as session:
            article = session.query(ArticleDB).filter_by(id=article_id).first()
            if article:
                return article.to_dict()
        return None

    def get_article_by_id(self, article_id: str) -> Optional[dict]:
        """根据ID获取文章"""
        with session_scope() as session:
            article = session.query(ArticleDB).filter_by(id=article_id).first()
            if article:
                return article.to_dict()
        return None

    def save_daily_briefing(self, briefing: DailyBriefing) -> int:
        """保存每日早报"""
        # 先保存所有文章
        article_ids = self.save_articles(briefing.articles)

        with session_scope() as session:
            # 检查是否已存在
            existing = session.query(DailyBriefingDB).filter_by(date=briefing.date).first()
            if existing:
                # 更新
                existing.title = briefing.title
                existing.article_ids = article_ids
                existing.total_count = briefing.total_count
                existing.ai_summary = briefing.ai_summary
                briefing_id = existing.id
            else:
                # 新增
                briefing_db = DailyBriefingDB(
                    date=briefing.date,
                    title=briefing.title,
                    article_ids=article_ids,
                    total_count=briefing.total_count,
                    ai_summary=briefing.ai_summary
                )
                session.add(briefing_db)
                session.flush()
                briefing_id = briefing_db.id

        return briefing_id

    def get_daily_briefing(self, date: str) -> Optional[dict]:
        """获取指定日期的早报"""
        with session_scope() as session:
            briefing = session.query(DailyBriefingDB).filter_by(date=date).first()
            if briefing:
                result = briefing.to_dict()
                # 获取文章详情
                if briefing.article_ids:
                    articles = []
                    for article_id in briefing.article_ids:
                        article = session.query(ArticleDB).filter_by(id=article_id).first()
                        if article:
                            articles.append(article.to_dict())
                    result['articles'] = articles
                return result
        return None

    def get_latest_briefing(self) -> Optional[dict]:
        """获取最新早报"""
        with session_scope() as session:
            briefing = session.query(DailyBriefingDB).order_by(
                desc(DailyBriefingDB.date)
            ).first()
            if briefing:
                result = briefing.to_dict()
                # 获取文章详情
                if briefing.article_ids:
                    articles = []
                    for article_id in briefing.article_ids:
                        article = session.query(ArticleDB).filter_by(id=article_id).first()
                        if article:
                            articles.append(article.to_dict())
                    result['articles'] = articles
                return result
        return None

    def list_briefings(self, limit: int = 10, offset: int = 0) -> List[dict]:
        """列出早报"""
        with session_scope() as session:
            briefings = session.query(DailyBriefingDB).order_by(
                desc(DailyBriefingDB.date)
            ).limit(limit).offset(offset).all()
            return [b.to_dict() for b in briefings]

    def log_task(self, task_name: str, status: str, start_time: datetime,
                 end_time: Optional[datetime] = None, duration: Optional[int] = None,
                 result: Optional[str] = None, error_message: Optional[str] = None):
        """记录任务日志"""
        with session_scope() as session:
            log = TaskLog(
                task_name=task_name,
                status=status,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                result=result,
                error_message=error_message
            )
            session.add(log)

    def get_task_logs(self, task_name: Optional[str] = None, limit: int = 50) -> List[dict]:
        """获取任务日志"""
        with session_scope() as session:
            query = session.query(TaskLog)
            if task_name:
                query = query.filter_by(task_name=task_name)
            logs = query.order_by(desc(TaskLog.created_at)).limit(limit).all()
            return [log.to_dict() for log in logs]
