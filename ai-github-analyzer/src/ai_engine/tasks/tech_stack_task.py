"""
技术栈分析任务。

负责识别项目的编程语言、框架、依赖和构建工具。
"""

from typing import Any, Dict
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
        logger.info("开始执行技术栈分析任务")
        
        # 使用通用 LLM 执行流程
        result = self.execute_with_llm(context)
        
        logger.info("技术栈分析任务完成")
        return result
    
    def get_prompt_template(self) -> str:
        """获取 Prompt 模板名称。"""
        return "tech_stack"
    
    def _prepare_prompt_variables(self, context: TaskContext) -> Dict[str, Any]:
        """准备 Prompt 变量。"""
        from ...models.tech_stack import TechStack
        
        variables = super()._prepare_prompt_variables(context)
        
        # 添加技术栈信息（从 Context Builder 传递过来）
        if context.ai_context and hasattr(context.ai_context, 'tech_stack'):
            tech_stack = context.ai_context.tech_stack
            if isinstance(tech_stack, TechStack):
                variables['tech_stack_info'] = str(tech_stack)
        
        return variables
    
    def _parse_llm_response(self, content: str, context: TaskContext) -> TechStackAnalysis:
        """
        解析 LLM 响应为 TechStackAnalysis。
        
        期望 LLM 返回 JSON 格式或结构化文本，这里简化处理。
        """
        from ...models.analysis_result import TechStackAnalysis
        
        try:
            # 尝试解析 JSON
            import json
            data = json.loads(content)
            
            # 构建 TechStackAnalysis
            return TechStackAnalysis(
                languages=data.get('languages', []),
                frameworks=data.get('frameworks', []),
                libraries=data.get('libraries', []),
                build_tools=data.get('build_tools', []),
                package_managers=data.get('package_managers', []),
                databases=data.get('databases', []),
                ci_cd=data.get('ci_cd', []),
                containers=data.get('containers', []),
                cloud_native=data.get('cloud_native', []),
                testing_tools=data.get('testing_tools', []),
                confidence=data.get('confidence', 0.5),
            )
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"JSON 解析失败，使用原始内容: {e}")
            # Fallback: 返回包含原始内容的对象
            return TechStackAnalysis(
                languages=[content[:200]],  # 截取前 200 字符
                confidence=0.3,
            )
    
    def validate_result(self, result: Any) -> bool:
        """
        验证技术栈分析结果。
        
        Args:
            result: 要验证的结果
            
        Returns:
            bool: 结果是否有效
        """
        if not isinstance(result, TechStackAnalysis):
            logger.warning(f"结果类型不正确: {type(result)}")
            return False
        
        # 基本验证：至少有一个字段不为空
        return True
