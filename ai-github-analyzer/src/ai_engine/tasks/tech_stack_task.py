"""
技术栈分析任务。

负责识别项目的编程语言、框架、依赖和构建工具。
"""

from typing import Any
from loguru import logger

from ...models.task_context import TaskContext
from ...models.analysis_result import TechStackAnalysis
from .base import BaseTask


class TechStackTask(BaseTask):
    """
    技术栈分析任务。
    
    职责：
    - 识别编程语言
    - 检测框架和库
    - 分析依赖关系
    - 识别构建和部署工具
    
    输出：
    - TechStackAnalysis 结构化结果
    """
    
    def __init__(self) -> None:
        """初始化技术栈分析任务。"""
        super().__init__(
            name="tech_stack_analysis",
            description="分析项目技术栈，包括语言、框架、依赖等"
        )
    
    def execute(self, context: TaskContext) -> TechStackAnalysis:
        """
        执行技术栈分析。
        
        Args:
            context: 任务执行上下文
            
        Returns:
            TechStackAnalysis: 技术栈分析结果
        """
        pass
    
    def get_prompt_template(self) -> str:
        """获取 Prompt 模板名称。"""
        return "tech_stack"
    
    def validate_result(self, result: Any) -> bool:
        """
        验证技术栈分析结果。
        
        Args:
            result: 要验证的结果
            
        Returns:
            bool: 结果是否有效
        """
        pass
