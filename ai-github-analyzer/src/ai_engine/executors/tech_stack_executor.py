"""
技术栈分析执行器。

负责分析项目的技术栈信息，包括编程语言、框架、依赖库等。
"""

from typing import Dict, Any
from loguru import logger

# 使用绝对导入
from src.models import AIContext
from src.ai_engine.executors.base_executor import BaseExecutor


class TechStackExecutor(BaseExecutor):
    """
    技术栈分析执行器。
    
    职责：
    - 识别编程语言及版本
    - 识别核心框架
    - 识别主要依赖库
    - 识别构建工具和部署工具
    - 识别数据库技术
    
    输出要求：
    - 基于配置文件和依赖文件分析
    - 避免猜测，标记不确定性
    - 提供证据来源
    """
    
    def get_task_name(self) -> str:
        """
        获取任务名称。
        
        Returns:
            str: 任务名称 "tech_stack"
        """
        return "tech_stack"
    
    def build_variables(self, context: AIContext) -> Dict[str, Any]:
        """
        构建 Prompt 变量。
        
        从 AIContext 中提取：
        - 仓库名称
        - 项目上下文摘要
        - 文件列表
        - 技术栈初步信息
        
        Args:
            context: AI 分析上下文
            
        Returns:
            Dict[str, Any]: 变量字典
        """
        # 构建文件列表摘要
        file_list = "\n".join([f.file_path for f in context.files[:50]])  # 限制前50个文件
        
        # 提取配置文件内容（如果有）
        config_files_summary = ""
        if context.tech_stack and context.tech_stack.config_files:
            config_files_summary = "\n".join(context.tech_stack.config_files[:20])
        
        # 构建上下文摘要
        context_summary = f"""
仓库名称: {context.repo_name}
仓库路径: {context.repo_path}
主要语言: {', '.join(context.languages[:5]) if context.languages else '未检测到'}
文件数量: {len(context.files)}
目录数量: {len(context.directories)}
"""
        
        variables = {
            "repo_name": context.repo_name,
            "context": context_summary,
            "file_list": file_list,
            "config_files": config_files_summary,
        }
        
        logger.debug(f"TechStackExecutor 构建变量完成: {list(variables.keys())}")
        
        return variables
    
    def validate_output(self, content: str) -> bool:
        """
        校验 LLM 输出是否有效。
        
        校验规则：
        - 内容非空
        - 长度合理（至少 50 字符）
        - 包含关键技术栈关键词（如"语言"、"框架"、"依赖"等）
        
        Args:
            content: LLM 输出的原始内容
            
        Returns:
            bool: 输出是否有效
        """
        if not content or len(content.strip()) < 50:
            logger.warning("TechStackExecutor 输出内容过短")
            return False
        
        # 检查是否包含关键技术栈相关词汇
        keywords = ["语言", "框架", "依赖", "工具", "技术"]
        has_keyword = any(keyword in content for keyword in keywords)
        
        if not has_keyword:
            logger.warning("TechStackExecutor 输出缺少关键技术栈关键词")
            return False
        
        logger.debug("TechStackExecutor 输出校验通过")
        return True
