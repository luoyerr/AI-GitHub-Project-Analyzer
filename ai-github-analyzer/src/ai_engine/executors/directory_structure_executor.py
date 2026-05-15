"""
目录结构分析执行器。

负责分析项目的目录结构和各目录职责。
"""

from typing import Dict, Any
from loguru import logger

# 使用绝对导入
from src.models import AIContext
from src.ai_engine.executors.base_executor import BaseExecutor


class DirectoryStructureExecutor(BaseExecutor):
    """
    目录结构分析执行器。
    
    职责：
    - 解释 src/ 或源代码目录职责
    - 解释 config/ 或配置目录职责
    - 解释 tests/ 或测试目录职责
    - 解释 docs/ 或文档目录职责
    - 识别架构模式（MVC、分层等）
    
    输出要求：
    - 基于实际目录结构分析
    - 说明每个目录的作用
    - 标记不明确的目录
    """
    
    def get_task_name(self) -> str:
        """
        获取任务名称。
        
        Returns:
            str: 任务名称 "directory_structure"
        """
        return "directory_structure"
    
    def build_variables(self, context: AIContext) -> Dict[str, Any]:
        """
        构建 Prompt 变量。
        
        从 AIContext 中提取：
        - 仓库名称
        - 项目上下文摘要
        - 目录树结构
        - 关键文件列表
        
        Args:
            context: AI 分析上下文
            
        Returns:
            Dict[str, Any]: 变量字典
        """
        # 构建目录树结构
        directory_tree = ""
        for dir_ctx in context.directories[:30]:  # 限制前30个目录
            children_str = ", ".join(dir_ctx.children[:10])  # 每个目录最多显示10个子项
            directory_tree += f"{dir_ctx.path} (深度: {dir_ctx.depth}): {children_str}\n"
        
        # 提取关键文件列表
        key_files = "\n".join([f.file_path for f in context.files[:30]])
        
        # 构建上下文摘要
        context_summary = f"""
仓库名称: {context.repo_name}
仓库路径: {context.repo_path}
目录数量: {len(context.directories)}
文件总数: {len(context.files)}
"""
        
        variables = {
            "repo_name": context.repo_name,
            "context": context_summary,
            "directory_tree": directory_tree,
            "key_files": key_files,
        }
        
        logger.debug(f"DirectoryStructureExecutor 构建变量完成: {list(variables.keys())}")
        
        return variables
    
    def validate_output(self, content: str) -> bool:
        """
        校验 LLM 输出是否有效。
        
        校验规则：
        - 内容非空
        - 长度合理（至少 100 字符）
        - 包含目录相关关键词
        
        Args:
            content: LLM 输出的原始内容
            
        Returns:
            bool: 输出是否有效
        """
        if not content or len(content.strip()) < 100:
            logger.warning("DirectoryStructureExecutor 输出内容过短")
            return False
        
        # 检查是否包含目录相关词汇
        keywords = ["目录", "文件夹", "结构", "职责", "作用"]
        has_keyword = any(keyword in content for keyword in keywords)
        
        if not has_keyword:
            logger.warning("DirectoryStructureExecutor 输出缺少关键目录关键词")
            return False
        
        logger.debug("DirectoryStructureExecutor 输出校验通过")
        return True
