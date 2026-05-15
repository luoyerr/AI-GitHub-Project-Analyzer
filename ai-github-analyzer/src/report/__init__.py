"""
Markdown 报告生成器模块。

负责将 AnalysisResult 转换为 PROJECT_ANALYSIS.md 文件，
包含模板渲染、格式化、质量校验和文件写入功能。
"""

from .generator import MarkdownReportGenerator
from .template import ReportTemplate
from .formatter import MarkdownFormatter
from .validator import ReportValidator
from .markdown_writer import MarkdownWriter
from .utils import format_timestamp, ensure_directory

__all__ = [
    "MarkdownReportGenerator",
    "ReportTemplate",
    "MarkdownFormatter",
    "ReportValidator",
    "MarkdownWriter",
    "format_timestamp",
    "ensure_directory",
]
