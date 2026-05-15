"""
架构图生成任务。

负责生成项目的 Mermaid 架构图。
"""

from typing import Any
from loguru import logger

from ...models.task_context import TaskContext
from ...models.analysis_result import ArchitectureDiagram
from .base import BaseTask


class ArchitectureTask(BaseTask):
    """
    架构图生成任务。
    
    职责：
    - 分析系统组件
    - 识别组件关系
    - 生成 Mermaid 代码
    - 提供架构说明
    
    依赖：
    - core_modules_analysis
    - directory_structure_analysis
    
    输出：
    - ArchitectureDiagram 结构化结果
    """
    
    def __init__(self) -> None:
        """初始化架构图生成任务。"""
        super().__init__(
            name="architecture_diagram",
            description="生成项目 Mermaid 架构图"
        )
    
    def execute(self, context: TaskContext) -> ArchitectureDiagram:
        """
        执行架构图生成。
        
        Args:
            context: 任务执行上下文
            
        Returns:
            ArchitectureDiagram: 架构图结果
        """
        logger.info("开始执行架构图生成任务")
        
        # TODO: 实际应该调用 LLM 进行 AI 分析
        # 当前阶段返回空对象，避免 NoneType 错误
        result = ArchitectureDiagram(mermaid_code="", description="")
        
        logger.info("架构图生成任务完成")
        return result
    
    def get_prompt_template(self) -> str:
        """获取 Prompt 模板名称。"""
        return "architecture_diagram"
    
    def get_dependencies(self) -> list:
        """获取依赖任务列表。"""
        return ["core_modules_analysis", "directory_structure_analysis"]
    
    def validate_result(self, result: Any) -> bool:
        """
        验证架构图结果。
        
        Args:
            result: 要验证的结果
            
        Returns:
            bool: 结果是否有效
        """
        if not isinstance(result, ArchitectureDiagram):
            logger.warning(f"结果类型不正确: {type(result)}")
            return False
        
        return True
