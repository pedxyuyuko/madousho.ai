"""Tests for FlowRegistry class."""
import pytest
from madousho.flow.registry import FlowRegistry, get_registry
from madousho.flow.base import FlowBase


class MockFlow(FlowBase):
    """测试用的 mock flow."""
    
    def run(self, **kwargs):
        return "mock_result"


def test_singleton_instance():
    """测试单例模式."""
    registry1 = FlowRegistry.get_instance()
    registry2 = FlowRegistry.get_instance()
    assert registry1 is registry2


def test_register_and_get_flow():
    """测试注册和获取 flow."""
    registry = FlowRegistry.get_instance()
    registry.clear()  # 清空以便测试
    
    flow = MockFlow(flow_config={})
    registry.register("test_flow", flow)
    
    retrieved_flow = registry.get("test_flow")
    assert retrieved_flow is flow


def test_get_nonexistent_flow():
    """测试获取不存在的 flow."""
    registry = FlowRegistry.get_instance()
    registry.clear()  # 清空以便测试
    
    with pytest.raises(KeyError, match="Flow 'nonexistent' not found"):
        registry.get("nonexistent")


def test_register_duplicate_flow():
    """测试注册重复的 flow."""
    registry = FlowRegistry.get_instance()
    registry.clear()  # 清空以便测试
    
    flow1 = MockFlow(flow_config={})
    flow2 = MockFlow(flow_config={})
    
    registry.register("test_flow", flow1)
    
    with pytest.raises(ValueError, match="Flow 'test_flow' is already registered"):
        registry.register("test_flow", flow2)


def test_list_all_flows():
    """测试列出所有 flows."""
    registry = FlowRegistry.get_instance()
    registry.clear()  # 清空以便测试
    
    flow1 = MockFlow(flow_config={})
    flow2 = MockFlow(flow_config={})
    
    registry.register("flow1", flow1)
    registry.register("flow2", flow2)
    
    flows = registry.list_all()
    assert set(flows) == {"flow1", "flow2"}


def test_clear_registry():
    """测试清空注册表."""
    registry = FlowRegistry.get_instance()
    registry.clear()  # 清空以便测试
    
    flow = MockFlow(flow_config={})
    registry.register("test_flow", flow)
    
    assert len(registry.list_all()) == 1
    
    registry.clear()
    assert len(registry.list_all()) == 0


def test_get_registry_helper():
    """测试便捷函数."""
    registry1 = get_registry()
    registry2 = FlowRegistry.get_instance()
    
    assert registry1 is registry2


def test_thread_safety():
    """测试线程安全性（基本验证）."""
    registry = FlowRegistry.get_instance()
    registry.clear()  # 清空以便测试
    
    # 注册几个 flows
    for i in range(5):
        flow = MockFlow(flow_config={})
        registry.register(f"flow_{i}", flow)
    
    # 验证所有 flows 都能正确访问
    for i in range(5):
        retrieved_flow = registry.get(f"flow_{i}")
        assert isinstance(retrieved_flow, MockFlow)
    
    # 验证数量
    flows = registry.list_all()
    assert len(flows) == 5
    assert set(flows) == {f"flow_{i}" for i in range(5)}