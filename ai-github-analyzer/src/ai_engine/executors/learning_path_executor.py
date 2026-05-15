"""
学习路线生成执行器。

负责生成项目的学习路线和阅读建议。
"""

from typing import Dict, Any
from loguru import logger

# 使用绝对导入
from src.models import AIContext
from src.ai_engine.executors.base_executor import BaseExecutor


class LearningPathExecutor(BaseExecutor):
    """
    学习路线生成执行器。
    
    职责：
    - 生成建议阅读顺序
    - 识别优先学习的模块
    - 规划学习路径
    - 提供学习建议
    
    输出要求：
    - 基于项目结构和复杂度分析
    - 分阶段规划学习路线
    - 标注每个阶段的学习目标
    - 提供实践建议
    """
    
    def get_task_name(self) -> str:
        """
        获取任务名称。
        
        Returns:
            str: 任务名称 "learning_path"
        """
        return "learning_path"
    
    def build_variables(self, context: AIContext) -> Dict[str, Any]:
        """
        构建 Prompt 变量。
        
        从 AIContext 中提取：
        - 仓库名称
        - 项目上下文摘要
        - 目录结构
        - 技术栈信息
        - 核心模块列表
        
        Args:
            context: AI 分析上下文
            
        Returns:
            Dict[str, Any]: 变量字典
        """
        # 提取目录结构
        directory_structure = ""
        for dir_ctx in context.directories[:20]:
            directory_structure += f"{dir_ctx.path} (深度: {dir_ctx.depth})\n"
        
        # 提取技术栈信息
        tech_stack_info = ""
        if context.tech_stack:
            if context.tech_stack.languages:
                tech_stack_info += f"编程语言: {', '.join(context.tech_stack.languages)}\n"
            if context.tech_stack.frameworks:
                tech_stack_info += f"框架: {', '.join(context.tech_stack.frameworks)}\n"
            if context.tech_stack.dependencies:
                tech_stack_info += f"核心依赖: {', '.join(context.tech_stack.dependencies[:10])}\n"
        
        # 构建上下文摘要
        context_summary = f"""
仓库名称: {context.repo_name}
仓库路径: {context.repo_path}
文件总数: {len(context.files)}
目录数量: {len(context.directories)}
"""
        
        variables = {
            "repo_name": context.repo_name,
            "context": context_summary,
            "directory_structure": directory_structure,
            "tech_stack": tech_stack_info,
        }
        
        logger.debug(f"LearningPathExecutor 构建变量完成: {list(variables.keys())}")
        
        return variables
    
    def validate_output(self, content: str) -> bool:
        """
        校验 LLM 输出是否有效。
        
        校验规则：
        - 内容非空
        - 长度合理（至少 100 字符）
        - 包含学习相关关键词
        
        Args:
            content: LLM 输出的原始内容
            
        Returns:
            bool: 输出是否有效
        """
        if not content or len(content.strip()) < 100:
            logger.warning("LearningPathExecutor 输出内容过短")
            return False
        
        # 检查是否包含学习相关词汇
        keywords = ["学习", "阅读", "理解", "掌握", "建议", "路线", "阶段"]
        has_keyword = any(keyword in content for keyword in keywords)
        
        if not has_keyword:
            logger.warning("LearningPathExecutor 输出缺少关键学习关键词")
            return False
        
        logger.debug("LearningPathExecutor 输出校验通过")
        return True
