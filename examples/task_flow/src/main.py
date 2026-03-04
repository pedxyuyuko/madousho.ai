"""Example Flow demonstrating the Task system."""
from madousho.flow.base import FlowBase
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


class ExampleFlow(FlowBase):
    """Example flow demonstrating Task system features."""
    
    def run(self):
        print(f"\n🚀 Starting ExampleFlow: {self.name}")
        print(f"   UUID: {self.uuid}")
        
        results = {}
        
        # 1. Sequential execution
        print("\n📝 Step 1: Sequential task execution")
        search_result = self.run_task(SearchTask("AI agents"))
        results["search"] = search_result
        print(f"   ✓ Search completed: {len(search_result['results'])} results")
        
        summarize_result = self.run_task(SummarizeTask(str(search_result)))
        results["summary"] = summarize_result
        print(f"   ✓ Summary completed")
        
        # 2. Parallel execution
        print("\n⚡ Step 2: Parallel task execution")
        fetch_tasks = [
            DataFetchTask("source_1"),
            DataFetchTask("source_2"),
            DataFetchTask("source_3"),
        ]
        fetch_results = self.run_parallel(*fetch_tasks, timeout=30.0)
        results["fetches"] = fetch_results
        print(f"   ✓ Parallel fetch completed: {len(fetch_results)} sources")
        
        # 3. Query tasks by label
        print("\n🔍 Step 3: Query tasks by label")
        print(f"   ✓ Found {len(self.get_tasks('search'))} search tasks")
        print(f"   ✓ Found {len(self.get_tasks('fetch'))} fetch tasks")
        
        # 4. Conditional retry
        print("\n🔄 Step 4: Conditional retry with retry_until")
        DataFetchTask._global_attempt = 0
        
        retry_result = self.retry_until(
            task_factory=lambda: DataFetchTask("flaky_source", fail_count=2),
            condition=lambda r: r.get("attempt", 0) > 2,
            max_retries=5
        )
        results["retry"] = retry_result
        print(f"   ✓ Retry succeeded after {DataFetchTask._global_attempt} attempts")
        
        print("\n✅ ExampleFlow completed successfully!")
        return results


# Required export - framework reads this variable
FlowClass = ExampleFlow
