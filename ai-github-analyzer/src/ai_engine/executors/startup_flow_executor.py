"""
启动流程分析执行器。

负责分析项目的启动流程和运行方式。
"""

from typing import Dict, Any
from loguru import logger

# 使用绝对导入
from src.models import AIContext
from src.ai_engine.executors.base_executor import BaseExecutor


class StartupFlowExecutor(BaseExecutor):
    """
    启动流程分析执行器。
    
    职责：
    - 分析环境准备步骤
    - 分析依赖安装方式
    - 识别启动命令
    - 识别构建命令
    - 分析数据库初始化流程
    
    输出要求：
    - 基于配置文件和脚本分析
    - 提供清晰的步骤说明
    - 标记可选步骤
    """
    
    def get_task_name(self) -> str:
        """
        获取任务名称。
        
        Returns:
            str: 任务名称 "startup_flow"
        """
        return "startup_flow"
    
    def build_variables(self, context: AIContext) -> Dict[str, Any]:
        """
        构建 Prompt 变量。
        
        从 AIContext 中提取：
        - 仓库名称
        - 项目上下文摘要
        - 配置文件内容
        - 脚本文件列表
        
        Args:
            context: AI 分析上下文
            
        Returns:
            Dict[str, Any]: 变量字典
        """
        # 提取配置文件和脚本文件
        config_and_scripts = []
        for file_ctx in context.files[:50]:
            if any(keyword in file_ctx.file_path.lower() for keyword in 
                   ['docker', 'makefile', 'package.json', 'requirements', 'setup', 'start', 'run', '.env']):
                config_and_scripts.append(file_ctx.file_path)
        
        config_files_str = "\n".join(config_and_scripts[:30]) if config_and_scripts else "未检测到配置或脚本文件"
        
        # 构建上下文摘要
        context_summary = f"""
仓库名称: {context.repo_name}
仓库路径: {context.repo_path}
文件总数: {len(context.files)}
主要语言: {', '.join(context.languages[:5]) if context.languages else '未检测到'}
"""
        
        variables = {
            "repo_name": context.repo_name,
            "context": context_summary,
            "config_files": config_files_str,
        }
        
        logger.debug(f"StartupFlowExecutor 构建变量完成: {list(variables.keys())}")
        
        return variables
    
    def validate_output(self, content: str) -> bool:
        """
        校验 LLM 输出是否有效。
        
        校验规则：
        - 内容非空
        - 长度合理（至少 80 字符）
        - 包含启动相关关键词
        
        Args:
            content: LLM 输出的原始内容
            
        Returns:
            bool: 输出是否有效
        """
        if not content or len(content.strip()) < 80:
            logger.warning("StartupFlowExecutor 输出内容过短")
            return False
        
        # 检查是否包含启动相关词汇
        keywords = ["启动", "运行", "安装", "依赖", "命令", "环境"]
        has_keyword = any(keyword in content for keyword in keywords)
        
        if not has_keyword:
            logger.warning("StartupFlowExecutor 输出缺少关键启动关键词")
            return False
        
        logger.debug("StartupFlowExecutor 输出校验通过")
        return True
