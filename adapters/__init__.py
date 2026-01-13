"""
消息源适配器模块
采用适配器模式，支持多种消息源
"""

from .base import BaseAdapter
from .factory import AdapterFactory

__all__ = [
    "BaseAdapter",
    "AdapterFactory",
]
