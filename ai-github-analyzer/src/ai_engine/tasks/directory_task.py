"""
目录结构分析任务。

负责解释项目目录结构和各目录的职责。
"""

from typing import Any
from loguru import logger

from ...models.task_context import TaskContext
from ...models.analysis_result import DirectoryStructureAnalysis
from .base import BaseTask


class DirectoryTask(BaseTask):
    """
    目录结构分析任务。
    
    职责：
    - 分析根目录结构
    - 解释各目录职责
    - 识别关键文件
    - 推断架构模式
    
    输出：
    - DirectoryStructureAnalysis 结构化结果
    """
    
    def __init__(self) -> None:
        """初始化目录结构分析任务。"""
        super().__init__(
            name="directory_structure_analysis",
            description="分析项目目录结构和各目录职责"
        )
    
    def execute(self, context: TaskContext) -> DirectoryStructureAnalysis:
        """
        执行目录结构分析。
        
        Args:
            context: 任务执行上下文
            
        Returns:
            DirectoryStructureAnalysis: 目录结构分析结果
        """
        logger.info("开始执行目录结构分析任务")
        
        # TODO: 实际应该调用 LLM 进行 AI 分析
        # 当前阶段返回空对象，避免 NoneType 错误
        result = DirectoryStructureAnalysis(description="")
        
        logger.info("目录结构分析任务完成")
        return result
    
    def get_prompt_template(self) -> str:
        """获取 Prompt 模板名称。"""
        return "directory_structure"
    
    def validate_result(self, result: Any) -> bool:
        """
        验证目录结构分析结果。
        
        Args:
            result: 要验证的结果
            
        Returns:
            bool: 结果是否有效
        """
        if not isinstance(result, DirectoryStructureAnalysis):
            logger.warning(f"结果类型不正确: {type(result)}")
            return False
        
        return True
