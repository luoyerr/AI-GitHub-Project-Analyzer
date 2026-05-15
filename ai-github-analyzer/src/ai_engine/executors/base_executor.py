"""
基础执行器抽象类。

定义所有 Task Executor 的统一接口和执行流程。
提供高复用性，减少重复代码。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from loguru import logger

# 使用绝对导入
from src.models import AIContext, PromptResult, TokenUsage
from src.ai_engine.prompt_manager import PromptManager
from src.ai_engine.llm_client import LLMClient


class BaseExecutor(ABC):
    """
    基础执行器抽象类。
    
    职责：
    - 定义统一的 execute 接口
    - 提供标准的执行流程（获取 Prompt -> 构建 -> 调用 LLM -> 校验 -> 返回）
    - 封装公共逻辑（PromptManager、LLMClient 初始化）
    - 支持后续扩展（retry、parallel、DAG）
    
    子类需要实现：
    - get_task_name(): 返回任务名称
    - build_variables(): 构建 Prompt 变量
    - validate_output(): 校验 LLM 输出
    
    使用示例：
        >>> class MyExecutor(BaseExecutor):
        ...     def get_task_name(self) -> str:
        ...         return "my_task"
        ...     
        ...     def build_variables(self, context: AIContext) -> Dict[str, Any]:
        ...         return {"repo_name": context.repo_name}
        ...     
        ...     def validate_output(self, content: str) -> bool:
        ...         return len(content) > 0
        >>> 
        >>> executor = MyExecutor()
        >>> result = executor.execute(context)
    """
    
    def __init__(
        self,
        prompt_manager: Optional[PromptManager] = None,
        llm_client: Optional[LLMClient] = None
    ) -> None:
        """
        初始化执行器。
        
        Args:
            prompt_manager: Prompt 管理器实例，如果未提供则自动创建
            llm_client: LLM 客户端实例，如果未提供则自动创建
        """
        self.prompt_manager: PromptManager = prompt_manager or PromptManager()
        self.llm_client: LLMClient = llm_client or LLMClient()
        
        logger.debug(f"执行器初始化完成: {self.get_task_name()}")
    
    def execute(self, context: AIContext) -> PromptResult:
        """
        执行分析任务（统一接口）。
        
        标准执行流程：
        1. 获取任务名称和 Prompt 模板
        2. 构建 Prompt 变量
        3. 渲染最终 Prompt
        4. 调用 LLM 生成响应
        5. 校验输出内容
        6. 返回 PromptResult
        
        Args:
            context: AI 分析上下文
            
        Returns:
            PromptResult: 任务执行结果
            
        Raises:
            Exception: 当执行过程中出现未预期的错误时
        """
        task_name = self.get_task_name()
        logger.info(f"开始执行任务: {task_name}")
        
        try:
            # 步骤 1: 构建 Prompt 变量
            variables = self.build_variables(context)
            logger.debug(f"任务 {task_name} 构建变量: {list(variables.keys())}")
            
            # 步骤 2: 渲染 Prompt
            prompt = self.prompt_manager.build_prompt(
                task_name=task_name,
                variables=variables
            )
            logger.debug(f"任务 {task_name} Prompt 长度: {len(prompt)} 字符")
            
            # 步骤 3: 获取系统 Prompt
            system_prompt = self.prompt_manager.get_system_prompt()
            
            # 步骤 4: 调用 LLM
            llm_response = self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt
            )
            
            # 步骤 5: 校验输出
            is_valid = False
            if llm_response.success and llm_response.content:
                is_valid = self.validate_output(llm_response.content)
                logger.debug(f"任务 {task_name} 输出校验结果: {is_valid}")
            
            # 步骤 6: 构建并返回结果
            # 转换 token_usage 为 TokenUsage 对象
            token_usage_obj = None
            if llm_response.token_usage:
                token_usage_obj = TokenUsage(
                    prompt_tokens=llm_response.token_usage.get("prompt_tokens", 0),
                    completion_tokens=llm_response.token_usage.get("completion_tokens", 0),
                    total_tokens=llm_response.token_usage.get("total_tokens", 0)
                )
            
            result = PromptResult(
                task_name=task_name,
                success=llm_response.success and is_valid,
                prompt=prompt,
                content=llm_response.content,
                model_name=llm_response.model,
                token_usage=token_usage_obj,
                elapsed_time=llm_response.elapsed_time,
                error_message=llm_response.error_message if not llm_response.success else None,
                metadata={
                    "is_valid": is_valid,
                    "variables_count": len(variables),
                }
            )
            
            if result.success:
                logger.info(f"任务 {task_name} 执行成功")
            else:
                logger.warning(f"任务 {task_name} 执行失败或校验不通过")
            
            return result
            
        except Exception as e:
            # 捕获未预期的异常
            error_msg = f"任务 {task_name} 执行异常: {str(e)}"
            logger.error(error_msg)
            
            return PromptResult(
                task_name=task_name,
                success=False,
                prompt=None,
                content=None,
                model_name=None,
                token_usage=None,
                elapsed_time=0.0,
                error_message=error_msg
            )
    
    @abstractmethod
    def get_task_name(self) -> str:
        """
        获取任务名称（对应 Prompt 模板文件名）。
        
        Returns:
            str: 任务名称，例如 "tech_stack"、"risks" 等
        """
        pass
    
    @abstractmethod
    def build_variables(self, context: AIContext) -> Dict[str, Any]:
        """
        构建 Prompt 变量字典。
        
        从 AIContext 中提取需要的信息，转换为 Prompt 模板所需的变量。
        
        Args:
            context: AI 分析上下文
            
        Returns:
            Dict[str, Any]: 变量字典，键为变量名，值为变量值
        """
        pass
    
    @abstractmethod
    def validate_output(self, content: str) -> bool:
        """
        校验 LLM 输出是否有效。
        
        根据任务特点定义校验规则，例如：
        - 内容非空
        - 包含关键段落
        - 格式符合要求
        
        Args:
            content: LLM 输出的原始内容
            
        Returns:
            bool: 输出是否有效
        """
        pass
