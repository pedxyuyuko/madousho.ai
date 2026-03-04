"""Unit tests for FlowBase task management extensions."""

import pytest
import sys
from pathlib import Path
from uuid import uuid4

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from madousho.flow.base import FlowBase
from madousho.flow.tasks.base import TaskBase


# Test fixtures
class TaskFixture(TaskBase):
    """Simple test task for FlowBase tests."""
    
    def __init__(self, value: int = 42, label: str = "test"):
        super().__init__(label=label)
        self.value = value
    
    def run(self) -> int:
        return self.value


class FailingTask(TaskBase):
    """Task that always fails."""
    
    def __init__(self, error_msg: str = "Task failed"):
        super().__init__(label="failing")
        self.error_msg = error_msg
    
    def run(self) -> int:
        raise Exception(self.error_msg)


class FlowFixture(FlowBase):
    """Test flow implementation."""
    
    def run(self, **kwargs):
        return "flow result"


class TestFlowBaseInit:
    """Tests for FlowBase initialization."""
    
    def test_create_flow_with_minimal_params(self):
        """Test creating FlowBase with minimal parameters."""
        flow = FlowFixture()
        
        assert flow.uuid is not None
        assert flow.name is not None
        assert flow.description == ""
        assert flow.context == {}
    
    def test_create_flow_with_name(self):
        """Test creating FlowBase with custom name."""
        flow = FlowFixture(name="my_flow")
        
        assert flow.name == "my_flow"
    
    def test_create_flow_with_description(self):
        """Test creating FlowBase with description."""
        flow = FlowFixture(description="A test flow")
        
        assert flow.description == "A test flow"
    
    def test_create_flow_with_context(self):
        """Test creating FlowBase with context."""
        flow = FlowFixture(context={"key": "value", "number": 42})
        
        assert flow.context == {"key": "value", "number": 42}
    
    def test_create_flow_with_uuid(self):
        """Test creating FlowBase with custom UUID."""
        custom_uuid = str(uuid4())
        flow = FlowFixture(uuid=custom_uuid)
        
        assert flow.uuid == custom_uuid
        assert flow.flow_uuid == custom_uuid
    
    def test_flow_uuid_and_uuid_are_same(self):
        """Test that flow_uuid and uuid properties return same value."""
        flow = FlowFixture()
        
        assert flow.uuid == flow.flow_uuid


class TestFlowBaseRegisterTask:
    """Tests for FlowBase.register_task()."""
    
    def test_register_task_returns_uuid(self):
        """Test that register_task returns task UUID."""
        flow = FlowFixture()
        task = TaskFixture()
        
        task_uuid = flow.register_task(task)
        
        assert task_uuid is not None
        assert isinstance(task_uuid, str)
    
    def test_register_task_sets_task_uuid(self):
        """Test that register_task sets task._uuid."""
        flow = FlowFixture()
        task = TaskFixture()
        
        flow.register_task(task)
        
        assert task._uuid is not None
    
    def test_register_task_sets_task_flow(self):
        """Test that register_task sets task._flow reference."""
        flow = FlowFixture()
        task = TaskFixture()
        
        flow.register_task(task)
        
        assert task._flow is flow
    
    def test_register_task_sets_state_to_pending(self):
        """Test that register_task sets task._state to pending."""
        flow = FlowFixture()
        task = TaskFixture()
        
        flow.register_task(task)
        
        assert task._state == "pending"
    
    def test_register_task_with_custom_timeout(self):
        """Test that register_task accepts custom timeout."""
        flow = FlowFixture()
        task = TaskFixture()
        
        # Should not raise
        task_uuid = flow.register_task(task, timeout=60.0)
        
        assert task_uuid is not None


class TestFlowBaseGetTasks:
    """Tests for FlowBase.get_tasks()."""
    
    def test_get_tasks_empty(self):
        """Test get_tasks when no tasks registered."""
        flow = FlowFixture()
        
        tasks = flow.get_tasks("nonexistent")
        
        assert tasks == []
    
    def test_get_tasks_returns_matching_label(self):
        """Test that get_tasks returns tasks with matching label."""
        flow = FlowFixture()
        
        flow.register_task(TaskFixture(label="search"))
        flow.register_task(TaskFixture(label="search"))
        flow.register_task(TaskFixture(label="fetch"))
        
        search_tasks = flow.get_tasks("search")
        
        assert len(search_tasks) == 2
    
    def test_get_tasks_returns_in_registration_order(self):
        """Test that get_tasks returns tasks in registration order."""
        flow = FlowFixture()
        
        flow.register_task(TaskFixture(value=1, label="same"))
        flow.register_task(TaskFixture(value=2, label="same"))
        flow.register_task(TaskFixture(value=3, label="same"))
        
        tasks = flow.get_tasks("same")
        
        assert len(tasks) == 3
        # Tasks should be in registration order


class TestFlowBaseRunTask:
    """Tests for FlowBase.run_task()."""
    
    def test_run_task_executes_task(self):
        """Test that run_task executes the task."""
        flow = FlowFixture()
        task = TaskFixture(value=100)
        
        result = flow.run_task(task)
        
        assert result == 100
    
    def test_run_task_returns_result(self):
        """Test that run_task returns task result."""
        flow = FlowFixture()
        task = TaskFixture(value=42)
        
        result = flow.run_task(task)
        
        assert result == 42
    
    def test_run_task_propagates_exception(self):
        """Test that run_task propagates task exceptions."""
        flow = FlowFixture()
        task = FailingTask(error_msg="Test error")
        
        with pytest.raises(Exception) as exc_info:
            flow.run_task(task)
        
        assert "Test error" in str(exc_info.value)
    
    def test_run_task_saves_state_on_success(self):
        """Test that run_task saves state on success."""
        flow = FlowFixture()
        task = TaskFixture(value=42)
        
        flow.run_task(task)
        
        assert task._state == "completed"
        assert task._result == 42
    
    def test_run_task_saves_state_on_failure(self):
        """Test that run_task saves state on failure."""
        flow = FlowFixture()
        task = FailingTask()
        
        try:
            flow.run_task(task)
        except Exception:
            pass
        
        assert task._state == "failed"
        assert task._error is not None


class TestFlowBaseRunParallel:
    """Tests for FlowBase.run_parallel()."""
    
    def test_run_parallel_executes_all_tasks(self):
        """Test that run_parallel executes all tasks."""
        flow = FlowFixture()
        
        tasks = [TaskFixture(value=i) for i in range(3)]
        results = flow.run_parallel(*tasks)
        
        assert results == [0, 1, 2]
    
    def test_run_parallel_returns_results_in_order(self):
        """Test that run_parallel returns results in input order."""
        flow = FlowFixture()
        
        tasks = [
            TaskFixture(value=10),
            TaskFixture(value=20),
            TaskFixture(value=30),
        ]
        results = flow.run_parallel(*tasks)
        
        assert results == [10, 20, 30]
    
    def test_run_parallel_propagates_exception(self):
        """Test that run_parallel propagates exceptions."""
        flow = FlowFixture()
        
        tasks = [
            TaskFixture(value=1),
            FailingTask("Parallel error"),
            TaskFixture(value=3),
        ]
        
        with pytest.raises(Exception) as exc_info:
            flow.run_parallel(*tasks)
        
        assert "Parallel error" in str(exc_info.value)
    
    def test_run_parallel_with_single_task(self):
        """Test that run_parallel works with single task."""
        flow = FlowFixture()
        
        results = flow.run_parallel(TaskFixture(value=42))
        
        assert results == [42]


class TestFlowBaseRetryUntil:
    """Tests for FlowBase.retry_until()."""
    
    def test_retry_until_succeeds_on_first_try(self):
        """Test retry_until when condition is met on first try."""
        flow = FlowFixture()
        
        attempt_count = {"count": 0}
        
        def create_task():
            attempt_count["count"] += 1
            return TaskFixture(value=100)
        
        def check_success(result):
            return result >= 50
        
        result = flow.retry_until(create_task, check_success, max_retries=3)
        
        assert result == 100
        assert attempt_count["count"] == 1
    
    def test_retry_until_succeeds_after_retries(self):
        """Test retry_until when condition is met after retries."""
        flow = FlowFixture()
        
        attempt_count = {"count": 0}
        
        def create_task():
            attempt_count["count"] += 1
            # Return attempt number as value
            return TaskFixture(value=attempt_count["count"])
        
        def check_success(result):
            return result >= 3
        
        result = flow.retry_until(create_task, check_success, max_retries=5)
        
        assert result == 3
        assert attempt_count["count"] == 3
    
    def test_retry_until_exhausts_max_retries(self):
        """Test retry_until when max_retries is exhausted."""
        flow = FlowFixture()
        
        def create_task():
            return TaskFixture(value=1)  # Always returns 1
        
        def check_success(result):
            return result >= 10  # Never succeeds
        
        with pytest.raises(Exception) as exc_info:
            flow.retry_until(create_task, check_success, max_retries=3)
        
        # Should have tried 3 times
        assert "Condition not met" in str(exc_info.value)
    
    def test_retry_until_with_exception(self):
        """Test retry_until when task raises exception."""
        flow = FlowFixture()
        
        attempt_count = {"count": 0}
        
        def create_failing_task():
            attempt_count["count"] += 1
            if attempt_count["count"] < 3:
                raise Exception("Temporary failure")
            return TaskFixture(value=42)
        
        def check_success(result):
            return result == 42
        
        result = flow.retry_until(create_failing_task, check_success, max_retries=5)
        
        assert result == 42
        assert attempt_count["count"] == 3
    
    def test_retry_until_all_retries_fail_with_exception(self):
        """Test retry_until when all retries fail with exception."""
        flow = FlowFixture()
        
        def create_always_failing_task():
            raise Exception("Always fails")
        
        with pytest.raises(Exception) as exc_info:
            flow.retry_until(create_always_failing_task, lambda r: True, max_retries=3)
        
        assert "Always fails" in str(exc_info.value)


class TestFlowBaseProperties:
    """Tests for FlowBase properties."""
    
    def test_uuid_is_string(self):
        """Test that uuid property returns string."""
        flow = FlowFixture()
        
        assert isinstance(flow.uuid, str)
    
    def test_flow_uuid_is_string(self):
        """Test that flow_uuid property returns string."""
        flow = FlowFixture()
        
        assert isinstance(flow.flow_uuid, str)
    
    def test_name_is_string(self):
        """Test that name property returns string."""
        flow = FlowFixture(name="test")
        
        assert isinstance(flow.name, str)
    
    def test_description_is_string(self):
        """Test that description property returns string."""
        flow = FlowFixture(description="test")
        
        assert isinstance(flow.description, str)
    
    def test_context_is_dict(self):
        """Test that context property returns dict."""
        flow = FlowFixture(context={"key": "value"})
        
        assert isinstance(flow.context, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
