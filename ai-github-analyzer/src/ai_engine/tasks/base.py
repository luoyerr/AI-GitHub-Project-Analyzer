"""
统一任务协议基类。

定义所有分析任务必须实现的接口和标准行为。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from loguru import logger

from ...models import TaskContext, PromptResult


class BaseTask(ABC):
    """
    任务基类。
    
    职责：
    - 定义任务的标准接口
    - 提供通用的任务执行逻辑
    - 管理任务状态和元数据
    
    所有具体任务必须继承此类并实现抽象方法。
    
    设计原则：
    - 单一职责：每个任务只负责一个分析维度
    - 独立测试：任务可以独立于其他任务进行测试
    - 可替换 Prompt：任务的 Prompt 可以独立更换
    - 结构化输出：任务必须输出结构化的结果
    """
    
    def __init__(self, name: str, description: str = "") -> None:
        """
        初始化任务。
        
        Args:
            name: 任务名称
            description: 任务描述
        """
        self.name: str = name
        self.description: str = description
        self.status: str = "pending"  # pending, running, success, failed, retrying, skipped
        self.retry_count: int = 0
        self.max_retries: int = 2
        self.timeout_seconds: int = 60
        self.result: Optional[Any] = None
        self.error_message: Optional[str] = None
    
    @abstractmethod
    def execute(self, context: TaskContext) -> Any:
        """
        执行任务的主要逻辑。
        
        Args:
            context: 任务执行上下文
            
        Returns:
            Any: 任务执行结果
            
        Raises:
            Exception: 当任务执行失败时
        """
        pass
    
    @abstractmethod
    def get_prompt_template(self) -> str:
        """
        获取任务使用的 Prompt 模板名称。
        
        Returns:
            str: Prompt 模板名称
        """
        pass
    
    @abstractmethod
    def validate_result(self, result: Any) -> bool:
        """
        验证任务结果的有效性。
        
        Args:
            result: 要验证的结果
            
        Returns:
            bool: 结果是否有效
        """
        pass
    
    def prepare_context(self, context: TaskContext) -> TaskContext:
        """
        准备任务执行所需的上下文。
        
        Args:
            context: 原始上下文
            
        Returns:
            TaskContext: 处理后的上下文
        """
        pass
    
    def handle_error(self, error: Exception) -> None:
        """
        处理任务执行过程中的错误。
        
        Args:
            error: 发生的错误
        """
        pass
    
    def should_retry(self) -> bool:
        """
        判断是否应该重试任务。
        
        Returns:
            bool: 是否应该重试
        """
        pass
    
    def get_dependencies(self) -> List[str]:
        """
        获取任务依赖的其他任务名称。
        
        Returns:
            List[str]: 依赖任务名称列表
        """
        return []
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取任务元数据。
        
        Returns:
            Dict[str, Any]: 任务元数据
        """
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
        }
    
    def reset(self) -> None:
        """
        重置任务状态，准备重新执行。
        """
        self.status = "pending"
        self.retry_count = 0
        self.result = None
        self.error_message = None
    
    def __repr__(self) -> str:
        """返回任务的字符串表示。"""
        return f"{self.__class__.__name__}(name='{self.name}', status='{self.status}')"
