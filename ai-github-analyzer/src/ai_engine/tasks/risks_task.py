"""
风险分析任务。

负责识别项目的潜在风险点。
"""

from typing import Any
from loguru import logger

from ...models.task_context import TaskContext
from ...models.analysis_result import RiskAnalysis
from .base import BaseTask


class RisksTask(BaseTask):
    """
    风险分析任务。
    
    职责：
    - 识别安全风险
    - 分析性能问题
    - 评估可维护性
    - 检查扩展性问题
    - 发现技术债
    
    输出：
    - RiskAnalysis 结构化结果
    """
    
    def __init__(self) -> None:
        """初始化风险分析任务。"""
        super().__init__(
            name="risks_analysis",
            description="分析项目潜在风险点"
        )
    
    def execute(self, context: TaskContext) -> RiskAnalysis:
        """
        执行风险分析。
        
        Args:
            context: 任务执行上下文
            
        Returns:
            RiskAnalysis: 风险分析结果
        """
        logger.info("开始执行风险分析任务")
        
        # 使用通用 LLM 执行流程
        result = self.execute_with_llm(context)
        
        logger.info("风险分析任务完成")
        return result
    
    def get_prompt_template(self) -> str:
        """获取 Prompt 模板名称。"""
        return "risks"
    
    def validate_result(self, result: Any) -> bool:
        """
        验证风险分析结果。
        
        Args:
            result: 要验证的结果
            
        Returns:
            bool: 结果是否有效
        """
        if not isinstance(result, RiskAnalysis):
            logger.warning(f"结果类型不正确: {type(result)}")
            return False
        
        return True
