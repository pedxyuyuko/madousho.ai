"""Global flow registry."""
import threading
from typing import Dict, List, Optional, Any
from madousho.flow.base import FlowBase


class FlowRegistry:
    """
    全局 Flow 注册表（单例模式，线程安全）.
    
    Usage:
        registry = FlowRegistry.get_instance()
        registry.register("my_flow", flow_instance)
        flow = registry.get("my_flow")
        all_flows = registry.list_all()
    """
    
    _instance: Optional["FlowRegistry"] = None
    _lock = threading.Lock()
    
    def __init__(self):
        self._flows: Dict[str, FlowBase] = {}
        self._lock = threading.Lock()
    
    @classmethod
    def get_instance(cls) -> "FlowRegistry":
        """获取单例实例."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """重置单例（用于测试）."""
        with cls._lock:
            cls._instance = None
    
    def register(self, flow_name: str, flow_plugin: FlowBase) -> None:
        """
        注册一个 flow。
        
        Args:
            flow_name: Flow 名称
            flow_plugin: FlowBase 实例
        
        Raises:
            ValueError: 如果 flow 名称已存在
        """
        with self._lock:
            if flow_name in self._flows:
                raise ValueError(f"Flow '{flow_name}' is already registered")
            self._flows[flow_name] = flow_plugin
    
    def get(self, flow_name: str) -> FlowBase:
        """
        获取已注册的 flow.
        
        Args:
            flow_name: Flow 名称
            
        Returns:
            FlowBase: 注册的 flow 实例
            
        Raises:
            KeyError: 如果 flow 未找到
        """
        with self._lock:
            if flow_name not in self._flows:
                raise KeyError(f"Flow '{flow_name}' not found. Available: {list(self._flows.keys())}")
            return self._flows[flow_name]
    
    def list_all(self) -> List[str]:
        """
        列出所有已注册的 flow 名称.
        
        Returns:
            List[str]: 所有注册的 flow 名称列表
        """
        with self._lock:
            return list(self._flows.keys())
    
    def clear(self) -> None:
        """清空所有注册（用于测试）"""
        with self._lock:
            self._flows.clear()


# 便捷函数
def get_registry() -> FlowRegistry:
    """获取全局 FlowRegistry 实例."""
    return FlowRegistry.get_instance()