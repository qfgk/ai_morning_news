"""
核心数据模型
使用 Pydantic 进行数据验证
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class SourceType(str, Enum):
    """消息源类型"""
    AIBASE = "aibase"
    RSS = "rss"
    API = "api"
    CUSTOM = "custom"


class ArticleStatus(str, Enum):
    """文章状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Article(BaseModel):
    """文章数据模型"""
    id: Optional[str] = None
    title: str
    content: str
    author: Optional[str] = None
    publication_date: Optional[str] = None
    source_url: str
    source_type: SourceType
    summary: Optional[str] = None
    status: ArticleStatus = ArticleStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "publication_date": self.publication_date,
            "source_url": self.source_url,
            "source_type": self.source_type.value if isinstance(self.source_type, SourceType) else self.source_type,
            "summary": self.summary,
            "status": self.status.value if isinstance(self.status, ArticleStatus) else self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DailyBriefing(BaseModel):
    """每日早报模型"""
    id: Optional[int] = None
    date: str  # YYYY-MM-DD
    title: str
    articles: List[Article]
    total_count: int
    ai_summary: Optional[str] = None  # AI 生成的整体总结
    created_at: datetime = Field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "date": self.date,
            "title": self.title,
            "articles": [article.to_dict() for article in self.articles],
            "total_count": self.total_count,
            "ai_summary": self.ai_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def to_brief_format(self) -> str:
        """生成早报文本格式"""
        lines = []
        for i, article in enumerate(self.articles, 1):
            lines.append(f"{i}. {article.title}")
            if article.summary:
                lines.append(f"{article.summary}")
            lines.append("")
        return "\n".join(lines)
