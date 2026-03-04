"""Data fetch task implementation."""
from madousho.flow.tasks.base import TaskBase


class DataFetchTask(TaskBase):
    """Simulated data fetch task with retry support."""
    
    _global_attempt = 0
    
    def __init__(self, source: str, fail_count: int = 0):
        super().__init__(label="fetch")
        self.source = source
        self._fail_count = fail_count
    
    def run(self):
        DataFetchTask._global_attempt += 1
        
        if DataFetchTask._global_attempt <= self._fail_count:
            raise Exception(f"Simulated failure {DataFetchTask._global_attempt}")
        
        return {
            "source": self.source,
            "data": f"Data from {self.source}",
            "attempt": DataFetchTask._global_attempt,
        }