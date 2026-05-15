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
        
        # 使用通用 LLM 执行流程
        result = self.execute_with_llm(context)
        
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
    
    def _parse_llm_response(self, content: str, context: TaskContext) -> ArchitectureDiagram:
        """
        解析 LLM 响应为 ArchitectureDiagram。
        
        期望 LLM 返回 Mermaid 代码或包含 Mermaid 代码块的文本。
        关键修复：只提取纯 Mermaid 代码，不包含 Markdown fence。
        """
        from ...models.analysis_result import ArchitectureDiagram
        from ...report.formatter import MarkdownFormatter
        import re
        
        try:
            # 关键修复：使用 clean_mermaid() 清洗内容，去除所有 Markdown fence
            mermaid_code = MarkdownFormatter.clean_mermaid(content)
            
            # 验证是否为合法的 Mermaid 语法
            valid_keywords = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 'stateDiagram', 'gantt', 'pie']
            is_valid_mermaid = any(keyword in mermaid_code for keyword in valid_keywords)
            
            if not is_valid_mermaid:
                # 如果清洗后仍不是合法 Mermaid，尝试从原始内容中提取
                mermaid_pattern = r'```mermaid\s*\n(.*?)\n```'
                match = re.search(mermaid_pattern, content, re.DOTALL | re.IGNORECASE)
                
                if match:
                    mermaid_code = MarkdownFormatter.clean_mermaid(match.group(1))
                else:
                    logger.warning(f"LLM 返回的内容不是合法的 Mermaid 语法")
                    mermaid_code = ""
            
            # 提取描述（如果有）
            description = "AI 生成的架构图"
            
            return ArchitectureDiagram(
                mermaid_code=mermaid_code,
                description=description
            )
        except Exception as e:
            logger.error(f"解析架构图失败: {e}")
            return ArchitectureDiagram(mermaid_code="", description="")
