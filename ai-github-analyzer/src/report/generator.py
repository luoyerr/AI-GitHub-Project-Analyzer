"""
Markdown 报告生成器核心模块。

实现 MarkdownReportGenerator 类，负责将 AnalysisResult 转换为
PROJECT_ANALYSIS.md 文件。

核心流程：
1. 渲染模板
2. 格式化 Markdown
3. 质量校验
4. 写入文件

本模块仅负责报告生成，不包含业务逻辑、Prompt 或 LLM 调用。
"""

import time
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger

from ..models.analysis_result import AnalysisResult
from .template import ReportTemplate
from .formatter import MarkdownFormatter
from .validator import ReportValidator, ValidationResult
from .markdown_writer import MarkdownWriter


class MarkdownReportGenerator:
    """
    Markdown 报告生成器类。

    将 AnalysisResult 对象转换为 PROJECT_ANALYSIS.md 文件。
    遵循 Harness Engineering 架构，仅负责报告生成，不包含业务逻辑。

    使用示例:
        >>> from src.models.analysis_result import AnalysisResult
        >>> from src.report import MarkdownReportGenerator
        >>>
        >>> generator = MarkdownReportGenerator()
        >>> result = generator.generate(analysis_result, repo_path)
        >>> print(f"报告已生成: {result['output_path']}")
    """

    def __init__(self):
        """
        初始化报告生成器。

        注意:
            所有依赖组件均为静态方法，无需注入。
        """
        logger.debug("MarkdownReportGenerator 初始化完成")

    def generate(
        self,
        analysis_result: AnalysisResult,
        repo_path: Optional[Path] = None,
        output_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        生成 Markdown 分析报告。

        参数:
            analysis_result: AI 分析结果对象（包含 8 个章节数据）。
            repo_path: 仓库根目录路径（用于确定输出位置）。
            output_path: 可选的自定义输出路径。如果提供，优先使用。

        返回:
            包含生成结果的字典：
            - success: 是否成功生成
            - output_path: 输出文件路径
            - validation_result: 校验结果
            - elapsed_time: 生成耗时（秒）
            - error: 错误信息（如果失败）

        异常:
            ValueError: 当输入参数无效时抛出。
            IOError: 当文件写入失败时抛出。

        注意:
            - 完整流程：渲染 → 格式化 → 校验 → 写入
            - 任何步骤失败都会记录日志并返回错误信息
            - 即使校验失败，文件仍会写入（但会在结果中标记）
        """
        start_time = time.time()
        logger.info("=" * 60)
        logger.info("开始生成 Markdown 分析报告")
        logger.info(f"仓库名称: {analysis_result.repo_name}")
        logger.info(f"仓库路径: {repo_path}")

        try:
            # 第 1 步：渲染模板
            logger.info("步骤 1/4: 渲染模板...")
            rendered_content = self._render_template(analysis_result)
            logger.success(f"模板渲染完成 (长度: {len(rendered_content)} 字符)")

            # 第 2 步：格式化 Markdown
            logger.info("步骤 2/4: 格式化 Markdown...")
            formatted_content = self._format_markdown(rendered_content)
            logger.success(f"格式化完成 (长度: {len(formatted_content)} 字符)")

            # 第 3 步：质量校验
            logger.info("步骤 3/4: 质量校验...")
            validation_result = self._validate_report(formatted_content)
            if validation_result.passed:
                logger.success("✅ 质量校验通过")
            else:
                logger.warning(f"⚠️ 质量校验失败 ({len(validation_result.errors)} 个错误)")
                for error_type, error_desc in validation_result.errors:
                    logger.warning(f"  - [{error_type}] {error_desc}")

            # 第 4 步：写入文件
            logger.info("步骤 4/4: 写入文件...")
            output_file = self._write_file(formatted_content, repo_path, output_path)
            logger.success(f"文件写入完成: {output_file}")
            logger.success(f"报告生成成功")
            logger.success(f"路径: {output_file.absolute()}")

            # 计算耗时
            elapsed_time = time.time() - start_time
            logger.info(f"报告生成总耗时: {elapsed_time:.2f} 秒")
            logger.info("=" * 60)

            return {
                "success": True,
                "output_path": output_file,
                "validation_result": validation_result,
                "elapsed_time": elapsed_time,
                "error": None,
            }

        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"❌ 报告生成失败: {e}")
            logger.error(f"耗时: {elapsed_time:.2f} 秒")
            logger.exception("详细错误信息:")

            return {
                "success": False,
                "output_path": None,
                "validation_result": None,
                "elapsed_time": elapsed_time,
                "error": str(e),
            }

    def _render_template(self, analysis_result: AnalysisResult) -> str:
        """
        渲染 Markdown 模板。

        参数:
            analysis_result: AI 分析结果对象。

        返回:
            渲染后的 Markdown 字符串（未格式化）。

        注意:
            - 将 AnalysisResult 转换为模板所需的字典格式
            - 保留所有 8 个章节的数据
        """
        logger.debug("开始渲染模板...")

        # 构建模板数据字典
        template_data = {
            "repo_name": analysis_result.repo_name,
            "analysis_time": analysis_result.analysis_time,
            "tech_stack": analysis_result.tech_stack,
            "directory_structure": analysis_result.directory_structure,
            "core_modules": analysis_result.core_modules,
            "startup_flow": analysis_result.startup_flow,
            "config_analysis": analysis_result.config_analysis,
            "risks": analysis_result.risks,
            "architecture_diagram": analysis_result.architecture_diagram,
            "learning_path": analysis_result.learning_path,
        }

        # 调用模板引擎
        content = ReportTemplate.generate_template(template_data)

        logger.debug("模板渲染完成")
        return content

    def _format_markdown(self, content: str) -> str:
        """
        格式化 Markdown 内容。

        参数:
            content: 原始 Markdown 字符串。

        返回:
            格式化后的 Markdown 字符串。

        注意:
            - 统一标题格式
            - 规范空行和列表
            - 格式化代码块和 Mermaid
            - 修复常见 Markdown 问题
        """
        logger.debug("开始格式化 Markdown...")

        # 执行标准格式化
        formatted = MarkdownFormatter.format(content)

        # 修复常见问题
        formatted = MarkdownFormatter.fix_common_issues(formatted)

        logger.debug("Markdown 格式化完成")
        return formatted

    def _validate_report(self, content: str) -> ValidationResult:
        """
        校验报告质量。

        参数:
            content: Markdown 报告字符串。

        返回:
            ValidationResult 对象，包含校验结果和详细信息。

        注意:
            - 检查 8 个章节完整性
            - 检查 Mermaid 存在性
            - 检查文件大小（3KB ~ 30KB）
            - 检查风险分析三段式结构
            - 检查 Markdown 基础语法
        """
        logger.debug("开始质量校验...")

        # 执行完整校验
        result = ReportValidator.validate(content)

        # 记录校验摘要
        summary = ReportValidator.get_validation_summary(result)
        logger.debug(f"校验结果:\n{summary}")

        return result

    def _write_file(
        self,
        content: str,
        repo_path: Optional[Path] = None,
        output_path: Optional[Path] = None,
    ) -> Path:
        """
        写入 Markdown 文件。

        参数:
            content: Markdown 字符串内容。
            repo_path: 仓库根目录路径。
            output_path: 可选的自定义输出路径。

        返回:
            实际写入的文件路径。

        异常:
            IOError: 当文件写入失败时抛出。
        """
        logger.debug(f"开始写入文件 (repo_path={repo_path}, output_path={output_path})")

        # 调用文件写入器
        file_path = MarkdownWriter.write(
            content=content,
            output_path=output_path,
            repo_path=repo_path,
        )

        logger.debug(f"文件写入完成: {file_path}")
        return file_path

    @staticmethod
    def get_output_preview(content: str, max_lines: int = 20) -> str:
        """
        获取报告内容的预览（用于调试）。

        参数:
            content: Markdown 字符串。
            max_lines: 最大显示行数，默认为 20。

        返回:
            预览字符串。
        """
        lines = content.split('\n')
        preview_lines = lines[:max_lines]

        preview = '\n'.join(preview_lines)
        if len(lines) > max_lines:
            preview += f"\n... ({len(lines) - max_lines} 更多行)"

        return preview
