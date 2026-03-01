"""Unit tests for FlowBase abstract base class."""
import pytest
from typing import Any, Dict
from madousho.flow.base import FlowBase, get_flow_class


class MockFlow(FlowBase):
    """Mock flow for testing purposes."""
    
    def run(self, **kwargs) -> Any:
        """Execute mock flow logic."""
        return "mock_result"


class TestFlowBaseInstantiation:
    """Tests for FlowBase instantiation and initialization."""
    
    def test_flow_initialization_with_flow_config(self):
        """Test flow instance creation with flow_config."""
        config = {"example_field": "value", "nested": {"key": "value"}}
        flow = MockFlow(flow_config=config)
        
        assert flow.flow_config == config
        assert flow.global_config == {}
    
    def test_flow_initialization_with_global_config(self):
        """Test flow instance creation with both flow_config and global_config."""
        flow_config = {"flow_field": "flow_value"}
        global_config = {"api": {"port": 8000}, "default_model_group": "gpt-4"}
        
        flow = MockFlow(flow_config=flow_config, global_config=global_config)
        
        assert flow.flow_config == flow_config
        assert flow.global_config == global_config
    
    def test_flow_initialization_with_none_global_config(self):
        """Test that None global_config defaults to empty dict."""
        flow = MockFlow(flow_config={"test": "value"}, global_config=None)
        assert flow.global_config == {}
    
    def test_flow_initialization_empty_configs(self):
        """Test flow instance creation with empty configs."""
        flow = MockFlow(flow_config={}, global_config={})
        
        assert flow.flow_config == {}
        assert flow.global_config == {}


class TestFlowBaseRun:
    """Tests for FlowBase run() method."""
    
    def test_flow_run_returns_result(self):
        """Test that run() returns expected result."""
        flow = MockFlow(flow_config={})
        result = flow.run()
        assert result == "mock_result"
    
    def test_flow_run_with_kwargs(self):
        """Test that run() can accept keyword arguments."""
        flow = MockFlow(flow_config={})
        # MockFlow ignores kwargs, but should accept them
        result = flow.run(param1="value1", param2=42)
        assert result == "mock_result"
    
    def test_flow_run_access_to_configs(self):
        """Test that run() can access flow_config and global_config."""
        class ConfigAccessFlow(FlowBase):
            def run(self, **kwargs) -> Any:
                return {
                    "flow_config": self.flow_config,
                    "global_config": self.global_config
                }
        
        flow_config = {"flow_key": "flow_value"}
        global_config = {"global_key": "global_value"}
        
        flow = ConfigAccessFlow(flow_config=flow_config, global_config=global_config)
        result = flow.run()
        
        assert result["flow_config"] == flow_config
        assert result["global_config"] == global_config


class TestFlowBaseLifecycleHooks:
    """Tests for optional lifecycle hook methods."""
    
    def test_on_start_default_implementation(self):
        """Test that on_start() has default no-op implementation."""
        flow = MockFlow(flow_config={})
        # Should not raise any exception
        flow.on_start()
    
    def test_on_complete_default_implementation(self):
        """Test that on_complete() has default no-op implementation."""
        flow = MockFlow(flow_config={})
        # Should not raise any exception
        flow.on_complete(result="test_result")
    
    def test_on_error_default_implementation(self):
        """Test that on_error() has default no-op implementation."""
        flow = MockFlow(flow_config={})
        test_error = Exception("test error")
        # Should not raise any exception
        flow.on_error(test_error)
    
    def test_lifecycle_hooks_can_be_overridden(self):
        """Test that lifecycle hooks can be overridden."""
        class HookFlow(FlowBase):
            def __init__(self, flow_config: Dict[str, Any], global_config: Dict[str, Any] = None):
                super().__init__(flow_config, global_config)
                self.hook_calls = []
            
            def run(self, **kwargs) -> Any:
                return "result"
            
            def on_start(self) -> None:
                self.hook_calls.append("on_start")
            
            def on_complete(self, result: Any) -> None:
                self.hook_calls.append(f"on_complete:{result}")
            
            def on_error(self, error: Exception) -> None:
                self.hook_calls.append(f"on_error:{error}")
        
        flow = HookFlow(flow_config={})
        
        flow.on_start()
        assert "on_start" in flow.hook_calls
        
        flow.on_complete("test_result")
        assert "on_complete:test_result" in flow.hook_calls
        
        flow.on_error(ValueError("test"))
        assert "on_error:test" in flow.hook_calls


class TestFlowBaseAbstract:
    """Tests to verify FlowBase is properly abstract."""
    
    def test_cannot_instantiate_flowbase_directly(self):
        """Test that FlowBase cannot be instantiated directly."""
        with pytest.raises(TypeError) as exc_info:
            FlowBase(flow_config={})
        
        assert "abstract" in str(exc_info.value).lower() or "instantiate" in str(exc_info.value).lower()
    
    def test_must_implement_run_method(self):
        """Test that subclasses must implement run() method."""
        class IncompleteFlow(FlowBase):
            pass
        
        with pytest.raises(TypeError):
            IncompleteFlow(flow_config={})


class TestGetFlowClass:
    """Tests for get_flow_class() function."""
    
    def test_get_flow_class_valid(self):
        """Test get_flow_class() with valid module."""
        class TestModule:
            FlowClass = MockFlow
        
        module = TestModule()
        flow_class = get_flow_class(module)
        
        assert flow_class is MockFlow
        assert issubclass(flow_class, FlowBase)
    
    def test_get_flow_class_missing_flowclass(self):
        """Test get_flow_class() raises error when FlowClass is missing."""
        class TestModule:
            pass
        
        module = TestModule()
        
        with pytest.raises(ValueError) as exc_info:
            get_flow_class(module)
        
        assert "FlowClass" in str(exc_info.value)
        assert "does not export" in str(exc_info.value)
    
    def test_get_flow_class_not_subclass(self):
        """Test get_flow_class() raises error when FlowClass is not FlowBase subclass."""
        class NotAFlow:
            pass
        
        class TestModule:
            FlowClass = NotAFlow
        
        module = TestModule()
        
        with pytest.raises(ValueError) as exc_info:
            get_flow_class(module)
        
        assert "FlowClass" in str(exc_info.value)
        assert "subclass of FlowBase" in str(exc_info.value)
    
    def test_get_flow_class_with_instance(self):
        """Test get_flow_class() rejects FlowClass instance instead of class."""
        class TestModule:
            FlowClass = MockFlow(flow_config={})
        
        module = TestModule()
        
        with pytest.raises(ValueError) as exc_info:
            get_flow_class(module)
        
        assert "subclass of FlowBase" in str(exc_info.value)
    
    def test_get_flow_class_real_module(self):
        """Test get_flow_class() with real Python module."""
        import types
        
        # Create a mock module
        module = types.ModuleType("test_flow_module")
        module.FlowClass = MockFlow
        
        flow_class = get_flow_class(module)
        assert flow_class is MockFlow


class TestFlowBaseIntegration:
    """Integration tests for FlowBase usage patterns."""
    
    def test_complete_flow_lifecycle(self):
        """Test complete flow lifecycle with all hooks."""
        class LifecycleFlow(FlowBase):
            def __init__(self, flow_config: Dict[str, Any], global_config: Dict[str, Any] = None):
                super().__init__(flow_config, global_config)
                self.lifecycle = []
            
            def run(self, **kwargs) -> Any:
                self.lifecycle.append("run")
                return "success"
            
            def on_start(self) -> None:
                self.lifecycle.append("start")
            
            def on_complete(self, result: Any) -> None:
                self.lifecycle.append(f"complete:{result}")
            
            def on_error(self, error: Exception) -> None:
                self.lifecycle.append(f"error:{error}")
        
        flow = LifecycleFlow(flow_config={"test": "config"})
        
        # Simulate flow execution
        flow.on_start()
        result = flow.run()
        flow.on_complete(result)
        
        assert flow.lifecycle == ["start", "run", "complete:success"]
    
    def test_flow_error_handling(self):
        """Test flow error handling with on_error hook."""
        class ErrorFlow(FlowBase):
            def __init__(self, flow_config: Dict[str, Any], global_config: Dict[str, Any] = None):
                super().__init__(flow_config, global_config)
                self.error_handled = None
            
            def run(self, **kwargs) -> Any:
                raise ValueError("intentional error")
            
            def on_error(self, error: Exception) -> None:
                self.error_handled = error
        
        flow = ErrorFlow(flow_config={})
        
        try:
            flow.run()
        except ValueError as e:
            flow.on_error(e)
        
        assert flow.error_handled is not None
        assert isinstance(flow.error_handled, ValueError)
        assert str(flow.error_handled) == "intentional error"
