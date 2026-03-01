"""Example flow implementation."""
from typing import Any
from madousho.flow.base import FlowBase


class ExampleFlow(FlowBase):
    """
    Example flow demonstrating FlowBase inheritance.
    
    This is a skeleton example showing the required structure:
    - Inherits from FlowBase
    - Implements only run() method (the only abstract method)
    - Exports FlowClass variable
    """
    
    def run(self, **kwargs) -> Any:
        """
        Execute the flow logic.
        
        Args:
            **kwargs: Runtime parameters
        
        Returns:
            Flow execution result
        """
        # This is a skeleton example - replace with real flow logic
        return "example_flow_completed"


# Required export - framework reads this variable
FlowClass = ExampleFlow
