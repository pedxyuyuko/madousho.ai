"""Search task implementation."""
from madousho.flow.tasks.base import TaskBase


class SearchTask(TaskBase):
    """Simulated search task."""
    
    def __init__(self, query: str):
        super().__init__(label="search")
        self.query = query
    
    def run(self):
        return {
            "query": self.query,
            "results": [f"Result {i} for '{self.query}'" for i in range(1, 4)],
        }