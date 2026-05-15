"""
配置分析执行器。

负责分析项目的配置文件和配置项。
"""

from typing import Dict, Any
from loguru import logger

# 使用绝对导入
from src.models import AIContext
from src.ai_engine.executors.base_executor import BaseExecutor


class ConfigAnalysisExecutor(BaseExecutor):
    """
    配置分析执行器。
    
    职责：
    - 分析 YAML/JSON/Properties 配置文件
    - 分析 .env.example 等环境变量模板
    - 分析 Docker 配置
    - 识别关键配置项
    - 说明配置用途
    
    输出要求：
    - 基于实际配置文件分析
    - 分类整理配置项
    - 标记敏感配置
    """
    
    def get_task_name(self) -> str:
        """
        获取任务名称。
        
        Returns:
            str: 任务名称 "config_analysis"
        """
        return "config_analysis"
    
    def build_variables(self, context: AIContext) -> Dict[str, Any]:
        """
        构建 Prompt 变量。
        
        从 AIContext 中提取：
        - 仓库名称
        - 项目上下文摘要
        - 配置文件列表和内容摘要
        
        Args:
            context: AI 分析上下文
            
        Returns:
            Dict[str, Any]: 变量字典
        """
        # 提取配置文件
        config_files_list = []
        for file_ctx in context.files[:50]:
            if any(ext in file_ctx.file_path.lower() for ext in 
                   ['.yaml', '.yml', '.json', '.properties', '.env', '.toml', '.ini', 'dockerfile', 'docker-compose']):
                config_files_list.append(file_ctx.file_path)
        
        config_files_str = "\n".join(config_files_list[:30]) if config_files_list else "未检测到配置文件"
        
        # 构建上下文摘要
        context_summary = f"""
仓库名称: {context.repo_name}
仓库路径: {context.repo_path}
文件总数: {len(context.files)}
检测到的配置文件数: {len(config_files_list)}
"""
        
        variables = {
            "repo_name": context.repo_name,
            "context": context_summary,
            "config_files": config_files_str,
        }
        
        logger.debug(f"ConfigAnalysisExecutor 构建变量完成: {list(variables.keys())}")
        
        return variables
    
    def validate_output(self, content: str) -> bool:
        """
        校验 LLM 输出是否有效。
        
        校验规则：
        - 内容非空
        - 长度合理（至少 80 字符）
        - 包含配置相关关键词
        
        Args:
            content: LLM 输出的原始内容
            
        Returns:
            bool: 输出是否有效
        """
        if not content or len(content.strip()) < 80:
            logger.warning("ConfigAnalysisExecutor 输出内容过短")
            return False
        
        # 检查是否包含配置相关词汇
        keywords = ["配置", "环境变量", "参数", "设置", "选项"]
        has_keyword = any(keyword in content for keyword in keywords)
        
        if not has_keyword:
            logger.warning("ConfigAnalysisExecutor 输出缺少关键配置关键词")
            return False
        
        logger.debug("ConfigAnalysisExecutor 输出校验通过")
        return True
