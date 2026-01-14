"""
SQLAlchemy 数据库模型
"""
import enum
import json
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SQLEnum, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SourceTypeEnum(str, enum.Enum):
    """消息源类型枚举"""
    AIBASE = "aibase"
    RSS = "rss"
    API = "api"
    CUSTOM = "custom"


class ArticleStatusEnum(str, enum.Enum):
    """文章状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ArticleDB(Base):
    """文章表"""
    __tablename__ = 'articles'

    id = Column(String(64), primary_key=True, comment="文章ID（MD5）")
    title = Column(String(500), nullable=False, comment="标题")
    content = Column(Text, nullable=False, comment="内容")
    author = Column(String(100), comment="作者")
    publication_date = Column(String(50), comment="发布日期")
    source_url = Column(String(500), unique=True, nullable=False, comment="来源URL")
    source_type = Column(SQLEnum(SourceTypeEnum), nullable=False, comment="来源类型")
    summary = Column(Text, comment="AI生成的总结")
    status = Column(SQLEnum(ArticleStatusEnum), default=ArticleStatusEnum.PENDING, comment="状态")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, onupdate=datetime.now, comment="更新时间")

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "publication_date": self.publication_date,
            "source_url": self.source_url,
            "source_type": self.source_type.value if self.source_type else None,
            "summary": self.summary,
            "status": self.status.value if self.status else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<ArticleDB(id={self.id}, title={self.title[:20]}...)>"


class DailyBriefingDB(Base):
    """每日早报表"""
    __tablename__ = 'daily_briefings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String(10), unique=True, nullable=False, index=True, comment="日期 YYYY-MM-DD")
    title = Column(String(200), nullable=False, comment="早报标题")
    article_ids = Column(JSON, comment="文章ID列表")
    total_count = Column(Integer, default=0, comment="文章总数")
    ai_summary = Column(Text, comment="AI生成的整体总结")
    full_text = Column(Text, comment="完整的格式化早报文本（可直接发送）")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "date": self.date,
            "title": self.title,
            "article_ids": self.article_ids,
            "total_count": self.total_count,
            "ai_summary": self.ai_summary,
            "full_text": self.full_text,  # 完整格式化文本
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<DailyBriefingDB(id={self.id}, date={self.date})>"


class TaskLog(Base):
    """任务执行日志"""
    __tablename__ = 'task_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_name = Column(String(100), nullable=False, comment="任务名称")
    status = Column(String(20), nullable=False, comment="执行状态 success/failed/running")
    start_time = Column(DateTime, comment="开始时间")
    end_time = Column(DateTime, comment="结束时间")
    duration = Column(Integer, comment="执行时长（秒）")
    result = Column(Text, comment="执行结果")
    error_message = Column(Text, comment="错误信息")
    created_at = Column(DateTime, default=datetime.now, comment="记录时间")

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "task_name": self.task_name,
            "status": self.status,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "result": self.result,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<TaskLog(id={self.id}, task_name={self.task_name}, status={self.status})>"
