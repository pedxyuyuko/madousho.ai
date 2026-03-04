"""Example Flow demonstrating the Task system."""
from madousho.flow.base import FlowBase
from madousho.logger import logger
from .tasks import SearchTask, SummarizeTask, DataFetchTask


class ExampleFlow(FlowBase):
    """Example flow demonstrating Task system features."""
    
    def run(self):
        logger.debug(f"Starting ExampleFlow: {self.name}")
        logger.debug(f"  UUID: {self.uuid}")
        
        results = {}
        
        # 1. Sequential execution
        logger.debug("Step 1: Sequential task execution")
        search_result = self.run_task(SearchTask("AI agents"))
        results["search"] = search_result
        logger.debug(f"  ✓ Search completed: {len(search_result['results'])} results")
        
        summarize_result = self.run_task(SummarizeTask(str(search_result)))
        results["summary"] = summarize_result
        logger.debug("  ✓ Summary completed")
        
        # 2. Parallel execution
        logger.debug("Step 2: Parallel task execution")
        fetch_tasks = [
            DataFetchTask("source_1"),
            DataFetchTask("source_2"),
            DataFetchTask("source_3"),
        ]
        fetch_results = self.run_parallel(*fetch_tasks, timeout=30.0)
        results["fetches"] = fetch_results
        logger.debug(f"  ✓ Parallel fetch completed: {len(fetch_results)} sources")
        
        # 3. Query tasks by label
        logger.debug("Step 3: Query tasks by label")
        logger.debug(f"  ✓ Found {len(self.get_tasks('search'))} search tasks")
        logger.debug(f"  ✓ Found {len(self.get_tasks('fetch'))} fetch tasks")
        
        # 4. Conditional retry
        logger.debug("Step 4: Conditional retry with retry_until")
        DataFetchTask._global_attempt = 0
        
        retry_result = self.retry_until(
            task_factory=lambda: DataFetchTask("flaky_source", fail_count=2),
            condition=lambda r: r.get("attempt", 0) > 2,
            max_retries=5
        )
        results["retry"] = retry_result
        logger.debug(f"  ✓ Retry succeeded after {DataFetchTask._global_attempt} attempts")
        
        logger.debug("ExampleFlow completed successfully!")
        return results


# Required export - framework reads this variable
FlowClass = ExampleFlow