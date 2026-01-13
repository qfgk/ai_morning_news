"""
适配器工厂
根据消息源类型创建对应的适配器实例
"""

from typing import Optional, Dict, Type
from adapters.base import BaseAdapter
from adapters.aibase_adapter import AIBaseAdapter
from core.models import SourceType


class AdapterFactory:
    """适配器工厂类"""

    _adapters: Dict[SourceType, Type[BaseAdapter]] = {
        SourceType.AIBASE: AIBaseAdapter,
    }

    @classmethod
    def register_adapter(cls, source_type: SourceType, adapter_class: Type[BaseAdapter]):
        """注册新的适配器"""
        cls._adapters[source_type] = adapter_class

    @classmethod
    def get_adapter(cls, source_type: str) -> Optional[BaseAdapter]:
        """根据消息源类型获取适配器实例"""
        try:
            source_enum = SourceType(source_type)
            adapter_class = cls._adapters.get(source_enum)
            if adapter_class:
                return adapter_class()
        except ValueError:
            pass
        return None

    @classmethod
    def get_all_adapters(cls) -> Dict[str, BaseAdapter]:
        """获取所有已注册的适配器实例"""
        return {source_type.value: adapter_class()
                for source_type, adapter_class in cls._adapters.items()}
