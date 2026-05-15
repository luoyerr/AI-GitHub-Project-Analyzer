"""
启动流程分析任务。

负责分析项目的启动流程和运行方式。
"""

from typing import Any
from loguru import logger

from ...models.task_context import TaskContext
from ...models.analysis_result import StartupFlowAnalysis
from .base import BaseTask


class StartupTask(BaseTask):
    """
    启动流程分析任务。
    
    职责：
    - 分析环境准备步骤
    - 识别安装命令
    - 提取启动命令
    - 分析构建流程
    - 数据库初始化说明
    
    输出：
    - StartupFlowAnalysis 结构化结果
    """
    
    def __init__(self) -> None:
        """初始化启动流程分析任务。"""
        super().__init__(
            name="startup_flow_analysis",
            description="分析项目启动流程和运行方式"
        )
    
    def execute(self, context: TaskContext) -> StartupFlowAnalysis:
        """
        执行启动流程分析。
        
        Args:
            context: 任务执行上下文
            
        Returns:
            StartupFlowAnalysis: 启动流程分析结果
        """
        pass
    
    def get_prompt_template(self) -> str:
        """获取 Prompt 模板名称。"""
        return "startup_flow"
    
    def validate_result(self, result: Any) -> bool:
        """
        验证启动流程分析结果。
        
        Args:
            result: 要验证的结果
            
        Returns:
            bool: 结果是否有效
        """
        pass
