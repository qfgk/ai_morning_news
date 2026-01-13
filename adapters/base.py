"""
消息源适配器抽象基类
所有消息源适配器必须继承此类并实现抽象方法
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from core.models import Article, SourceType


class BaseAdapter(ABC):
    """消息源适配器抽象基类"""

    def __init__(self, source_type: SourceType):
        self.source_type = source_type

    @abstractmethod
    async def fetch_article_list(self, limit: int = 10) -> List[str]:
        """
        获取文章列表URL

        Args:
            limit: 获取文章数量

        Returns:
            List[str]: 文章URL列表
        """
        pass

    @abstractmethod
    async def fetch_article(self, url: str) -> Optional[Article]:
        """
        抓取单篇文章内容

        Args:
            url: 文章URL

        Returns:
            Article: 文章数据，失败返回None
        """
        pass

    @abstractmethod
    async def validate_url(self, url: str) -> bool:
        """
        验证URL是否属于当前消息源

        Args:
            url: 待验证URL

        Returns:
            bool: 是否有效
        """
        pass
