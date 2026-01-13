"""
API 数据模式
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class ArticleSchema(BaseModel):
    """文章数据模式"""
    id: Optional[str] = None
    title: str
    content: Optional[str] = None
    author: Optional[str] = None
    publication_date: Optional[str] = None
    source_url: str
    source_type: str
    summary: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "title": "AI技术突破",
                "content": "文章内容...",
                "source_url": "https://example.com/news/123",
                "source_type": "aibase",
                "summary": "AI总结..."
            }
        }


class DailyBriefingSchema(BaseModel):
    """每日早报数据模式"""
    id: Optional[int] = None
    date: str = Field(..., description="日期 YYYY-MM-DD")
    title: str
    articles: List[ArticleSchema]
    total_count: int
    ai_summary: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-01-13",
                "title": "早报 - 2025-01-13",
                "articles": [],
                "total_count": 0,
                "ai_summary": "今日要闻..."
            }
        }


class GenerateBriefingRequest(BaseModel):
    """生成早报请求模式"""
    date: Optional[str] = Field(None, description="日期 YYYY-MM-DD，默认为今天")
    sources: Optional[List[str]] = Field(["aibase"], description="消息源列表")
    limit: Optional[int] = Field(10, ge=1, le=50, description="每个消息源最大文章数")
    use_cache: Optional[bool] = Field(True, description="是否使用缓存")
    save_to_db: Optional[bool] = Field(False, description="是否保存到数据库")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-01-13",
                "sources": ["aibase"],
                "limit": 10
            }
        }


class ApiResponse(BaseModel):
    """API响应基类"""
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="消息")
    data: Optional[dict] = Field(None, description="数据")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": {}
            }
        }


class HealthResponse(BaseModel):
    """健康检查响应"""
    service: str = Field("ok", description="服务状态")
    database: str = Field("unknown", description="数据库状态")
    redis: str = Field("unknown", description="Redis状态")

    class Config:
        json_schema_extra = {
            "example": {
                "service": "ok",
                "database": "ok",
                "redis": "ok"
            }
        }
