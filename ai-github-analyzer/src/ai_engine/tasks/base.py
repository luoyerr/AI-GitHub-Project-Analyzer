"""
统一任务协议基类。

定义所有分析任务必须实现的接口和标准行为。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from loguru import logger

# 使用绝对导入避免相对导入问题
try:
    from models.task_context import TaskContext
    from models.prompt_result import PromptResult
except ImportError:
    # 如果作为包的一部分运行，使用相对导入
    from ...models.task_context import TaskContext
    from ...models.prompt_result import PromptResult

# 延迟导入 LLMClient 和 PromptManager，避免循环依赖
def _get_llm_client():
    """获取 LLM 客户端实例（延迟加载）。"""
    try:
        from ..llm_client import LLMClient
        return LLMClient()
    except Exception as e:
        logger.error(f"无法创建 LLM 客户端: {e}")
        raise

def _get_prompt_manager():
    """获取 Prompt 管理器实例（延迟加载）。"""
    try:
        from ..prompt_manager import PromptManager
        return PromptManager()
    except Exception as e:
        logger.error(f"无法创建 Prompt 管理器: {e}")
        raise


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
    
    def execute_with_llm(self, context: TaskContext) -> Any:
        """
        通用 LLM 执行流程（模板方法）。
        
        标准流程：
        1. 构建 Prompt
        2. 调用 LLM
        3. 解析响应
        4. 返回结构化结果
        
        Args:
            context: 任务执行上下文
            
        Returns:
            Any: 任务执行结果
            
        Raises:
            Exception: 当任务执行失败时
        """
        task_name = self.get_prompt_template()
        
        # Step 1: 构建 Prompt
        logger.info(f"[{self.name}] Step 1: 构建 Prompt")
        prompt_manager = _get_prompt_manager()
        
        # 准备变量
        variables = self._prepare_prompt_variables(context)
        
        # 构建最终 Prompt
        prompt = prompt_manager.build_prompt(task_name, variables)
        
        # DEBUG: 打印 Prompt
        print("=" * 80)
        print(f"[PROMPT] {self.name}")
        print(f"Prompt length: {len(prompt)} characters")
        print(f"Prompt preview: {prompt[:500]}...")
        print("=" * 80)
        
        if not prompt or len(prompt.strip()) == 0:
            raise ValueError(f"Prompt 为空: {task_name}")
        
        # Step 2: 调用 LLM
        logger.info(f"[{self.name}] Step 2: 调用 LLM")
        llm_client = _get_llm_client()
        
        system_prompt = prompt_manager.get_system_prompt()
        llm_response = llm_client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=4000
        )
        
        # DEBUG: 打印 LLM 原始响应
        print("=" * 80)
        print(f"[LLM RESPONSE] {self.name}")
        print(f"Success: {llm_response.success}")
        print(f"Model: {llm_response.model}")
        print(f"Token usage: {llm_response.token_usage}")
        print(f"Elapsed time: {llm_response.elapsed_time:.2f}s")
        if llm_response.error_message:
            print(f"Error: {llm_response.error_message}")
        print(f"Content preview: {str(llm_response.content)[:500]}..." if llm_response.content else "Content: None")
        print("=" * 80)
        
        if not llm_response.success:
            raise Exception(f"LLM 调用失败: {llm_response.error_message}")
        
        if not llm_response.content:
            raise Exception("LLM 返回内容为空")
        
        # Step 3: 解析响应
        logger.info(f"[{self.name}] Step 3: 解析 LLM 响应")
        parsed_result = self._parse_llm_response(llm_response.content, context)
        
        # DEBUG: 打印解析结果
        print("=" * 80)
        print(f"[PARSED RESULT] {self.name}")
        print(f"Result type: {type(parsed_result)}")
        print(f"Result: {parsed_result}")
        print("=" * 80)
        
        # Step 4: 验证结果
        if not self.validate_result(parsed_result):
            logger.warning(f"[{self.name}] 结果验证失败，但仍返回")
        
        logger.info(f"[{self.name}] 任务执行完成")
        return parsed_result
    
    def _prepare_prompt_variables(self, context: TaskContext) -> Dict[str, Any]:
        """
        准备 Prompt 所需的变量。
        
        子类可以重写此方法以提供自定义变量。
        
        Args:
            context: 任务执行上下文
            
        Returns:
            Dict[str, Any]: 变量字典
        """
        # 默认变量
        variables = {
            "repo_name": context.ai_context.repo_name if context.ai_context else "未知仓库",
            "context": str(context.ai_context) if context.ai_context else "无上下文",
        }
        return variables
    
    def _parse_llm_response(self, content: str, context: TaskContext) -> Any:
        """
        解析 LLM 响应为结构化结果。
        
        子类必须实现此方法以解析特定格式的响应。
        
        Args:
            content: LLM 返回的文本内容
            context: 任务执行上下文
            
        Returns:
            Any: 结构化结果
            
        Raises:
            Exception: 当解析失败时
        """
        # 默认实现：直接返回原始内容
        # 子类应该重写此方法
        return content
    
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
