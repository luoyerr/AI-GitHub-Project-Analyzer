"""
学习路径分析任务。

负责生成项目的学习路线和建议阅读顺序。
"""

from typing import Any
from loguru import logger

from ...models import TaskContext, LearningPath
from .base import BaseTask


class LearningPathTask(BaseTask):
    """
    学习路径分析任务。
    
    职责：
    - 建议阅读顺序
    - 识别优先模块
    - 制定学习步骤
    - 估算学习时间
    
    输出：
    - LearningPath 结构化结果
    """
    
    def __init__(self) -> None:
        """初始化学习路径分析任务。"""
        super().__init__(
            name="learning_path",
            description="生成项目学习路径和建议阅读顺序"
        )
    
    def execute(self, context: TaskContext) -> LearningPath:
        """
        执行学习路径分析。
        
        Args:
            context: 任务执行上下文
            
        Returns:
            LearningPath: 学习路径结果
        """
        pass
    
    def get_prompt_template(self) -> str:
        """获取 Prompt 模板名称。"""
        return "learning_path"
    
    def validate_result(self, result: Any) -> bool:
        """
        验证学习路径结果。
        
        Args:
            result: 要验证的结果
            
        Returns:
            bool: 结果是否有效
        """
        pass
