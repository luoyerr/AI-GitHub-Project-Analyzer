"""
风险分析执行器。

负责识别项目的潜在风险和待改进点。
输出格式要求：风险、影响、建议三段式。
"""

from typing import Dict, Any
from loguru import logger

# 使用绝对导入
from src.models import AIContext
from src.ai_engine.executors.base_executor import BaseExecutor


class RisksExecutor(BaseExecutor):
    """
    风险分析执行器。
    
    职责：
    - 识别安全风险（硬编码密钥、注入漏洞等）
    - 识别性能风险（N+1 查询、内存泄漏等）
    - 识别可维护性风险（代码重复、复杂度过高等）
    - 识别扩展性风险（紧耦合、缺乏接口等）
    - 识别技术债（过时依赖、废弃 API 等）
    - 识别文档风险（缺少文档、文档过时等）
    
    输出要求：
    - 基于代码证据分析
    - 按严重程度排序
    - 提供改进建议
    - 避免过度批评
    
    输出格式：
    每个风险必须包含三段：
    1. 风险描述
    2. 影响说明
    3. 改进建议
    """

    def get_task_name(self) -> str:
        """
        获取任务名称。
        
        Returns:
            str: 任务名称 "risks"
        """
        return "risks"

    def build_variables(self, context: AIContext) -> Dict[str, Any]:
        """
        构建 Prompt 变量。
        
        从 AIContext 中提取：
        - 仓库名称
        - 项目上下文摘要
        - 代码样本
        - 依赖信息
        - 测试覆盖率（如果有）
        
        Args:
            context: AI 分析上下文
            
        Returns:
            Dict[str, Any]: 变量字典
        """
        # 提取代码样本（优先选择核心模块文件）
        code_samples = []
        for file_ctx in context.files[:30]:
            if file_ctx.content and len(file_ctx.content) > 0:
                # 只取前 50 行作为样本
                sample_lines = file_ctx.content.split('\n')[:50]
                code_samples.append(f"文件: {file_ctx.file_path}\n" + "\n".join(sample_lines))

        code_samples_str = "\n\n".join(code_samples[:10]) if code_samples else "无代码样本"

        # 提取依赖信息
        dependency_info = ""
        if context.tech_stack and context.tech_stack.dependencies:
            dependency_info = "\n".join(context.tech_stack.dependencies[:30])

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
            "code_samples": code_samples_str[:3000],  # 限制长度
            "dependency_info": dependency_info,
            "test_coverage": "未知",  # 当前阶段暂不提供测试覆盖率
        }

        logger.debug(f"RisksExecutor 构建变量完成: {list(variables.keys())}")

        return variables

    def validate_output(self, content: str) -> bool:
        """
        校验 LLM 输出是否有效。
        
        校验规则：
        - 内容非空
        - 长度合理（至少 150 字符）
        - 包含风险相关关键词
        - 包含建议或改进相关词汇
        
        Args:
            content: LLM 输出的原始内容
            
        Returns:
            bool: 输出是否有效
        """
        if not content or len(content.strip()) < 150:
            logger.warning("RisksExecutor 输出内容过短")
            return False

        # 检查是否包含风险和建议相关词汇
        risk_keywords = ["风险", "问题", "隐患", "缺陷"]
        suggestion_keywords = ["建议", "改进", "优化", "修复"]

        has_risk_keyword = any(keyword in content for keyword in risk_keywords)
        has_suggestion_keyword = any(keyword in content for keyword in suggestion_keywords)

        if not has_risk_keyword:
            logger.warning("RisksExecutor 输出缺少风险关键词")
            return False

        if not has_suggestion_keyword:
            logger.warning("RisksExecutor 输出缺少建议关键词")
            return False

        logger.debug("RisksExecutor 输出校验通过")
        return True
