"""Summarize task implementation."""
from madousho.flow.tasks.base import TaskBase


class SummarizeTask(TaskBase):
    """Simulated summarization task."""
    
    def __init__(self, text: str):
        super().__init__(label="summarize")
        self.text = text
    
    def run(self):
        return {
            "original_length": len(self.text),
            "summary": f"Summary: {self.text[:50]}...",
            "key_points": ["Point 1", "Point 2", "Point 3"],
        }