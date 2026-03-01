# 这是我给的伪代码 你按照这个思路实现
class FlowBase(ABC):
    # 不要去验证配置 那是框架的事情

    @abstractmethod
    def run(self, **kwargs) -> Any:
        """
        执行 flow 逻辑。
        
        Args:
            **kwargs: 运行时参数
        
        Returns:
            flow 执行结果
        """
        pass
    
    def on_start(self) -> None:
        """
        flow 启动前的钩子（可选覆盖）。
        """
        pass
    
    def on_complete(self, result: Any) -> None:
        """
        flow 完成后的钩子（可选覆盖）。
        
        Args:
            result: flow 执行结果
        """
        pass
    
    def on_error(self, error: Exception) -> None:
        """
        flow 出错时的钩子（可选覆盖）。
        
        Args:
            error: 抛出的异常
        """
        pass
