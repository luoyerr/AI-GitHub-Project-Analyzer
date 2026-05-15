"""
配置分析任务。

负责分析项目的配置文件和环境变量。
"""

from typing import Any
from loguru import logger

from ...models.task_context import TaskContext
from ...models.analysis_result import ConfigAnalysis
from .base import BaseTask


class ConfigTask(BaseTask):
    """
    配置分析任务。
    
    职责：
    - 识别配置文件
    - 分析环境变量
    - 提取关键配置项
    - 说明配置用途
    
    输出：
    - ConfigAnalysis 结构化结果
    """
    
    def __init__(self) -> None:
        """初始化配置分析任务。"""
        super().__init__(
            name="config_analysis",
            description="分析项目配置和环境变量"
        )
    
    def execute(self, context: TaskContext) -> ConfigAnalysis:
        """
        执行配置分析。
        
        Args:
            context: 任务执行上下文
            
        Returns:
            ConfigAnalysis: 配置分析结果
        """
        logger.info("开始执行配置分析任务")
        
        # 使用通用 LLM 执行流程
        result = self.execute_with_llm(context)
        
        logger.info("配置分析任务完成")
        return result
    
    def get_prompt_template(self) -> str:
        """获取 Prompt 模板名称。"""
        return "config_analysis"
    
    def validate_result(self, result: Any) -> bool:
        """
        验证配置分析结果。
        
        Args:
            result: 要验证的结果
            
        Returns:
            bool: 结果是否有效
        """
        if not isinstance(result, ConfigAnalysis):
            logger.warning(f"结果类型不正确: {type(result)}")
            return False
        
        return True
