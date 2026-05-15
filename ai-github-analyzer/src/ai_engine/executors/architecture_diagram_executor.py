"""
架构图生成执行器。

负责生成项目的 Mermaid 格式架构图。
禁止输出解释文字，仅输出 Mermaid 代码。
"""

from typing import Dict, Any
from loguru import logger

# 使用绝对导入
from src.models import AIContext
from src.ai_engine.executors.base_executor import BaseExecutor


class ArchitectureDiagramExecutor(BaseExecutor):
    """
    架构图生成执行器。
    
    职责：
    - 生成系统整体架构图
    - 展示模块间调用关系
    - 展示数据流向
    - 标注外部依赖
    - 展示部署拓扑（如适用）
    
    输出要求：
    - 仅使用 Mermaid 语法
    - 保持图表简洁清晰
    - 标注关键组件
    - 避免过度复杂
    
    重要约束：
    - 禁止输出解释文字
    - 仅输出 Mermaid 代码块
    """
    
    def get_task_name(self) -> str:
        """
        获取任务名称。
        
        Returns:
            str: 任务名称 "architecture_diagram"
        """
        return "architecture_diagram"
    
    def build_variables(self, context: AIContext) -> Dict[str, Any]:
        """
        构建 Prompt 变量。
        
        从 AIContext 中提取：
        - 仓库名称
        - 项目上下文摘要
        - 模块结构信息
        - 依赖关系图（简化版）
        
        Args:
            context: AI 分析上下文
            
        Returns:
            Dict[str, Any]: 变量字典
        """
        # 提取模块结构信息
        module_structure = ""
        for dir_ctx in context.directories[:20]:
            if dir_ctx.children:
                module_structure += f"{dir_ctx.path}: {', '.join(dir_ctx.children[:10])}\n"
        
        # 构建简化的依赖关系图
        dependency_graph = ""
        for file_ctx in context.files[:20]:
            if file_ctx.content and len(file_ctx.content) > 0:
                lines = file_ctx.content.split('\n')[:15]
                imports = [line.strip() for line in lines if 'import' in line.lower()]
                if imports:
                    dependency_graph += f"{file_ctx.file_path} -> {imports[0][:50]}\n"
        
        # 构建上下文摘要
        context_summary = f"""
仓库名称: {context.repo_name}
仓库路径: {context.repo_path}
目录数量: {len(context.directories)}
文件总数: {len(context.files)}
主要语言: {', '.join(context.languages[:5]) if context.languages else '未检测到'}
"""
        
        variables = {
            "repo_name": context.repo_name,
            "context": context_summary,
            "module_structure": module_structure,
            "dependency_graph": dependency_graph[:2000],  # 限制长度
        }
        
        logger.debug(f"ArchitectureDiagramExecutor 构建变量完成: {list(variables.keys())}")
        
        return variables
    
    def validate_output(self, content: str) -> bool:
        """
        校验 LLM 输出是否有效。
        
        校验规则：
        - 内容非空
        - 包含 Mermaid 关键字（graph、flowchart、sequenceDiagram 等）
        - 长度合理（至少 50 字符）
        
        Args:
            content: LLM 输出的原始内容
            
        Returns:
            bool: 输出是否有效
        """
        if not content or len(content.strip()) < 50:
            logger.warning("ArchitectureDiagramExecutor 输出内容过短")
            return False
        
        # 检查是否包含 Mermaid 关键字
        mermaid_keywords = ["graph", "flowchart", "sequenceDiagram", "classDiagram", "stateDiagram", "mermaid"]
        has_mermaid_keyword = any(keyword in content.lower() for keyword in mermaid_keywords)
        
        if not has_mermaid_keyword:
            logger.warning("ArchitectureDiagramExecutor 输出缺少 Mermaid 关键字")
            return False
        
        logger.debug("ArchitectureDiagramExecutor 输出校验通过")
        return True
