"""
核心模块分析执行器。

负责识别和分析项目的核心模块及其职责。
"""

from typing import Dict, Any
from loguru import logger

# 使用绝对导入
from src.models import AIContext
from src.ai_engine.executors.base_executor import BaseExecutor


class CoreModulesExecutor(BaseExecutor):
    """
    核心模块分析执行器。
    
    职责：
    - 识别 Controller/API 层
    - 识别 Service/业务逻辑层
    - 识别 Repository/数据访问层
    - 识别 Domain/领域模型层
    - 识别 Middleware/中间件层
    - 识别 Utils/工具类
    
    输出要求：
    - 识别模块间依赖关系
    - 说明每个模块的核心职责
    - 评估模块设计合理性
    - 标记耦合度高的模块
    """
    
    def get_task_name(self) -> str:
        """
        获取任务名称。
        
        Returns:
            str: 任务名称 "core_modules"
        """
        return "core_modules"
    
    def build_variables(self, context: AIContext) -> Dict[str, Any]:
        """
        构建 Prompt 变量。
        
        从 AIContext 中提取：
        - 仓库名称
        - 项目上下文摘要
        - 模块相关文件
        - 导入关系图（简化版）
        
        Args:
            context: AI 分析上下文
            
        Returns:
            Dict[str, Any]: 变量字典
        """
        # 提取模块相关文件（优先选择源代码文件）
        module_files = []
        for file_ctx in context.files[:50]:
            if any(keyword in file_ctx.file_path.lower() for keyword in 
                   ['controller', 'service', 'repository', 'domain', 'middleware', 'utils', 'api']):
                module_files.append(file_ctx.file_path)
        
        module_files_str = "\n".join(module_files[:30]) if module_files else "未检测到明显模块文件"
        
        # 构建简化的导入关系图
        import_graph = ""
        for file_ctx in context.files[:20]:
            if file_ctx.content and len(file_ctx.content) > 0:
                # 简单提取 import 语句
                lines = file_ctx.content.split('\n')[:20]
                imports = [line.strip() for line in lines if 'import' in line.lower()]
                if imports:
                    import_graph += f"{file_ctx.file_path}:\n"
                    import_graph += "\n".join(imports[:5]) + "\n\n"
        
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
            "module_files": module_files_str,
            "import_graph": import_graph[:2000] if import_graph else "无导入信息",  # 限制长度
        }
        
        logger.debug(f"CoreModulesExecutor 构建变量完成: {list(variables.keys())}")
        
        return variables
    
    def validate_output(self, content: str) -> bool:
        """
        校验 LLM 输出是否有效。
        
        校验规则：
        - 内容非空
        - 长度合理（至少 100 字符）
        - 包含模块相关关键词
        
        Args:
            content: LLM 输出的原始内容
            
        Returns:
            bool: 输出是否有效
        """
        if not content or len(content.strip()) < 100:
            logger.warning("CoreModulesExecutor 输出内容过短")
            return False
        
        # 检查是否包含模块相关词汇
        keywords = ["模块", "Controller", "Service", "Repository", "职责", "层"]
        has_keyword = any(keyword in content for keyword in keywords)
        
        if not has_keyword:
            logger.warning("CoreModulesExecutor 输出缺少关键模块关键词")
            return False
        
        logger.debug("CoreModulesExecutor 输出校验通过")
        return True
