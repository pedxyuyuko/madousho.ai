"""Unit tests for TaskBase abstract class."""

import pytest
import inspect
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from madousho.flow.tasks.base import TaskBase


class TestTaskBase:
    """Tests for TaskBase abstract class."""
    
    def test_import_successful(self):
        """Test that TaskBase can be imported."""
        from madousho.flow.tasks.base import TaskBase
        assert TaskBase is not None
    
    def test_is_abstract_class(self):
        """Test that TaskBase is an abstract class."""
        assert inspect.isabstract(TaskBase)
    
    def test_cannot_instantiate_abstract_class(self):
        """Test that TaskBase cannot be instantiated directly."""
        with pytest.raises(TypeError) as exc_info:
            TaskBase()
        
        assert "abstract" in str(exc_info.value).lower()
    
    def test_run_is_abstract(self):
        """Test that run() is an abstract method."""
        assert hasattr(TaskBase, "run")
        assert TaskBase.run.__isabstractmethod__
    
    def test_run_is_synchronous(self):
        """Test that run() is a synchronous method (not async)."""
        import asyncio
        # Check using inspect module
        assert not inspect.iscoroutinefunction(TaskBase.run)
    
    def test_has_required_methods(self):
        """Test that TaskBase has all required methods."""
        assert hasattr(TaskBase, "run")
        assert hasattr(TaskBase, "get_flow")
        assert hasattr(TaskBase, "_save_state")
        assert hasattr(TaskBase, "uuid")
        assert hasattr(TaskBase, "flow_uuid")
    
    def test_concrete_task_can_be_created(self):
        """Test that a concrete implementation of TaskBase can be created."""
        
        class ConcreteTask(TaskBase):
            def run(self) -> int:
                return 42
        
        task = ConcreteTask()
        assert task is not None
        assert task.run() == 42
    
    def test_task_with_label(self):
        """Test that TaskBase accepts label parameter."""
        
        class LabeledTask(TaskBase):
            def run(self) -> str:
                return "result"
        
        task = LabeledTask(label="test_label")
        assert task.label == "test_label"
    
    def test_task_without_label(self):
        """Test that TaskBase works without label parameter."""
        
        class UnlabeledTask(TaskBase):
            def run(self) -> str:
                return "result"
        
        task = UnlabeledTask()
        assert task.label is None
    
    def test_task_with_kwargs(self):
        """Test that TaskBase accepts arbitrary kwargs."""
        
        class KwargsTask(TaskBase):
            def run(self) -> dict:
                return self.kwargs
        
        task = KwargsTask(key1="value1", key2=42)
        assert task.kwargs["key1"] == "value1"
        assert task.kwargs["key2"] == 42
    
    def test_uuid_property_raises_when_not_set(self):
        """Test that uuid property raises RuntimeError when not set."""
        
        class TestTask(TaskBase):
            def run(self) -> int:
                return 1
        
        task = TestTask()
        with pytest.raises(RuntimeError) as exc_info:
            _ = task.uuid
        
        assert "not set" in str(exc_info.value).lower()
    
    def test_flow_uuid_property_raises_when_not_registered(self):
        """Test that flow_uuid property raises RuntimeError when not registered."""
        
        class TestTask(TaskBase):
            def run(self) -> int:
                return 1
        
        task = TestTask()
        with pytest.raises(RuntimeError) as exc_info:
            _ = task.flow_uuid
        
        assert "not registered" in str(exc_info.value).lower()
    
    def test_get_flow_raises_when_not_registered(self):
        """Test that get_flow() raises RuntimeError when not registered."""
        
        class TestTask(TaskBase):
            def run(self) -> int:
                return 1
        
        task = TestTask()
        with pytest.raises(RuntimeError) as exc_info:
            task.get_flow()
        
        assert "not registered" in str(exc_info.value).lower()
    
    def test_save_state_does_not_raise(self):
        """Test that _save_state() doesn't raise when called (no-op implementation)."""
        
        class TestTask(TaskBase):
            def run(self) -> int:
                return 1
        
        task = TestTask()
        # Should not raise
        task._save_state()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
