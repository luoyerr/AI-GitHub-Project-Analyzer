"""
核心模块分析任务。

负责识别和解释项目的核心模块及其职责。
"""

from typing import Any
from loguru import logger

from ...models.task_context import TaskContext
from ...models.analysis_result import CoreModuleAnalysis
from .base import BaseTask


class CoreModulesTask(BaseTask):
    """
    核心模块分析任务。
    
    职责：
    - 识别核心模块
    - 分析模块职责
    - 发现模块间关系
    - 定位入口点
    
    输出：
    - CoreModuleAnalysis 结构化结果
    """
    
    def __init__(self) -> None:
        """初始化核心模块分析任务。"""
        super().__init__(
            name="core_modules_analysis",
            description="分析项目核心模块及其职责"
        )
    
    def execute(self, context: TaskContext) -> CoreModuleAnalysis:
        """
        执行核心模块分析。
        
        Args:
            context: 任务执行上下文
            
        Returns:
            CoreModuleAnalysis: 核心模块分析结果
        """
        pass
    
    def get_prompt_template(self) -> str:
        """获取 Prompt 模板名称。"""
        return "core_modules"
    
    def validate_result(self, result: Any) -> bool:
        """
        验证核心模块分析结果。
        
        Args:
            result: 要验证的结果
            
        Returns:
            bool: 结果是否有效
        """
        pass
