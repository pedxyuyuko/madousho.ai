"""TaskBase abstract class for Madousho.ai Task system."""

from abc import ABC, abstractmethod
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from madousho.flow.base import FlowBase


class TaskBase(ABC):
    """Abstract base class for all Tasks in Madousho.ai.
    
    Tasks are the basic unit of work in a Flow. Each task:
    - Does ONE thing only (single responsibility)
    - Cannot spawn other tasks
    - Has a synchronous run() method
    - Can be labeled for grouping (labels are not unique)
    
    Example:
        class SearchTask(TaskBase):
            def __init__(self, query: str):
                super().__init__(label="search")
                self.query = query
            
            def run(self) -> dict:
                # Your implementation here
                return {"results": [...]}
    """
    
    def __init__(self, label: Optional[str] = None, **kwargs):
        """Initialize a Task.
        
        Args:
            label: Optional label for grouping tasks (not unique within Flow)
            **kwargs: Additional task-specific parameters
        """
        self.label = label
        self._flow: Optional["FlowBase"] = None
        self._uuid: Optional[str] = None
        self._state = "pending"
        self._result: Any = None
        self._error: Optional[str] = None
        self.kwargs = kwargs
    
    @abstractmethod
    def run(self) -> Any:
        """Execute the task. SYNCHRONOUS method.
        
        Returns:
            Task execution result
            
        Raises:
            Exception: Task execution fails
        """
        pass
    
    def _save_state(self) -> None:
        """Save task state to JSON file (internal method).
        
        Called by FlowBase after task execution.
        Subclasses should not override this.
        """
        # Implementation provided by FlowBase
        pass
    
    def get_flow(self) -> "FlowBase":
        """Get the Flow instance this task belongs to.
        
        Returns:
            The Flow instance
            
        Raises:
            RuntimeError: If task is not registered with a Flow
        """
        if self._flow is None:
            raise RuntimeError("Task is not registered with any Flow")
        return self._flow
    
    @property
    def flow_uuid(self) -> str:
        """Get the flow UUID via get_flow().flow_uuid."""
        return self.get_flow().flow_uuid  # type: ignore[attr-defined]
    
    @property
    def uuid(self) -> str:
        """Get the task UUID.
        
        Returns:
            The task UUID
            
        Raises:
            RuntimeError: If task UUID not set (task not registered)
        """
        if self._uuid is None:
            raise RuntimeError("Task UUID not set - task not registered")
        return self._uuid
