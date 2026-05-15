"""
Markdown 报告质量校验器模块。

负责验证生成的 PROJECT_ANALYSIS.md 是否满足质量标准，包括：
1. 8 个章节完整性检查
2. Mermaid 图表存在性检查
3. 文件大小检查（3KB ~ 30KB）
4. 空内容检查
5. 风险分析三段式检查（风险、影响、建议）
6. Markdown 基础合法性检查

校验失败时返回详细的错误信息列表。
"""

import re
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """
    校验结果数据类。

    属性:
        passed: 是否通过所有校验。
        errors: 错误信息列表，每项为 (错误类型, 错误描述)。
        warnings: 警告信息列表，每项为 (警告类型, 警告描述)。
    """
    passed: bool
    errors: List[Tuple[str, str]]
    warnings: List[Tuple[str, str]]


class ReportValidator:
    """
    Markdown 报告校验器类。

    提供多种校验方法，确保生成的报告符合质量标准。
    所有校验方法返回 ValidationResult，包含详细的错误和警告信息。
    """

    # 必需的 8 个章节标题（中文）
    REQUIRED_SECTIONS = [
        ("技术栈分析", "tech_stack"),
        ("项目目录说明", "directory_structure"),
        ("核心模块职责", "core_modules"),
        ("启动流程", "startup_flow"),
        ("配置说明", "config_analysis"),
        ("风险分析", "risks"),
        ("架构图", "architecture_diagram"),
        ("学习路线", "learning_path"),
    ]

    # 文件大小限制（字节）
    MIN_SIZE = 3 * 1024  # 3 KB
    MAX_SIZE = 30 * 1024  # 30 KB

    @staticmethod
    def validate(content: str) -> ValidationResult:
        """
        执行完整的报告质量校验。

        参数:
            content: Markdown 报告字符串。

        返回:
            ValidationResult，包含校验结果、错误和警告信息。

        注意:
            按顺序执行以下校验：
            1. 空内容检查
            2. 章节完整性检查
            3. Mermaid 存在性检查
            4. 文件大小检查
            5. 风险分析三段式检查
            6. Markdown 基础合法性检查
        """
        errors: List[Tuple[str, str]] = []
        warnings: List[Tuple[str, str]] = []

        # 1. 空内容检查
        if not content or not content.strip():
            return ValidationResult(
                passed=False,
                errors=[("empty_content", "报告内容为空")],
                warnings=[]
            )

        # 2. 章节完整性检查
        section_errors = ReportValidator._check_sections(content)
        errors.extend(section_errors)

        # 3. Mermaid 存在性检查
        mermaid_errors, mermaid_warnings = ReportValidator._check_mermaid(content)
        errors.extend(mermaid_errors)
        warnings.extend(mermaid_warnings)

        # 4. 文件大小检查
        size_errors, size_warnings = ReportValidator._check_size(content)
        errors.extend(size_errors)
        warnings.extend(size_warnings)

        # 5. 风险分析三段式检查
        risk_errors, risk_warnings = ReportValidator._check_risk_format(content)
        errors.extend(risk_errors)
        warnings.extend(risk_warnings)

        # 6. Markdown 基础合法性检查
        markdown_errors, markdown_warnings = ReportValidator._check_markdown_syntax(content)
        errors.extend(markdown_errors)
        warnings.extend(markdown_warnings)

        # 判断是否通过
        passed = len(errors) == 0

        return ValidationResult(
            passed=passed,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def _check_sections(content: str) -> List[Tuple[str, str]]:
        """
        检查 8 个必需章节的完整性。

        参数:
            content: Markdown 报告字符串。

        返回:
            错误信息列表，每项为 (错误类型, 错误描述)。
        """
        errors = []

        for section_name, section_id in ReportValidator.REQUIRED_SECTIONS:
            # 匹配章节标题（支持 ## 或 ### 级别）
            pattern = rf'##+\s+.*{re.escape(section_name)}'
            if not re.search(pattern, content):
                errors.append((
                    "missing_section",
                    f"缺少必需章节: {section_name}"
                ))

        return errors

    @staticmethod
    def _check_mermaid(content: str) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
        """
        检查 Mermaid 图表是否存在且格式正确。

        参数:
            content: Markdown 报告字符串。

        返回:
            (错误列表, 警告列表)。
        """
        errors: List[Tuple[str, str]] = []
        warnings: List[Tuple[str, str]] = []

        # 检查是否存在 mermaid 代码块
        mermaid_pattern = r'```mermaid\s*\n.*?\n```'
        if not re.search(mermaid_pattern, content, re.DOTALL | re.IGNORECASE):
            errors.append(("missing_mermaid", "缺少 Mermaid 架构图"))
            return errors, warnings

        # 检查 Mermaid 代码是否为空
        mermaid_matches = re.findall(mermaid_pattern, content, re.DOTALL | re.IGNORECASE)
        for match in mermaid_matches:
            code: str = match.strip()
            # 去除标记后检查实际内容
            code_content = re.sub(r'```mermaid\s*', '', code, flags=re.IGNORECASE)
            code_content = re.sub(r'```', '', code_content).strip()

            if not code_content or len(code_content) < 10:
                warnings.append(("empty_mermaid", "Mermaid 图表内容过少"))

        return errors, warnings

    @staticmethod
    def _check_size(content: str) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
        """
        检查报告文件大小是否在合理范围内。

        参数:
            content: Markdown 报告字符串。

        返回:
            (错误列表, 警告列表)。
        """
        errors: List[Tuple[str, str]] = []
        warnings: List[Tuple[str, str]] = []

        size_bytes = len(content.encode('utf-8'))
        size_kb = size_bytes / 1024

        if size_bytes < ReportValidator.MIN_SIZE:
            errors.append((
                "file_too_small",
                f"报告文件过小: {size_kb:.1f} KB (最小要求: {ReportValidator.MIN_SIZE / 1024} KB)"
            ))
        elif size_bytes > ReportValidator.MAX_SIZE:
            errors.append((
                "file_too_large",
                f"报告文件过大: {size_kb:.1f} KB (最大限制: {ReportValidator.MAX_SIZE / 1024} KB)"
            ))
        elif size_bytes < ReportValidator.MIN_SIZE * 1.5:
            warnings.append((
                "file_small_warning",
                f"报告文件偏小: {size_kb:.1f} KB，可能内容不够详细"
            ))

        return errors, warnings

    @staticmethod
    def _check_risk_format(content: str) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
        """
        检查风险分析章节是否采用三段式结构（风险、影响/严重程度、建议）。

        参数:
            content: Markdown 报告字符串。

        返回:
            (错误列表, 警告列表)。
        """
        errors: List[Tuple[str, str]] = []
        warnings: List[Tuple[str, str]] = []

        # 定位风险分析章节
        risk_section_pattern = r'##+\s+.*风险分析\s*\n(.*?)(?=##+\s+|$)'
        risk_match = re.search(risk_section_pattern, content, re.DOTALL)

        if not risk_match:
            # 如果没有风险分析章节，_check_sections 已经报错
            return errors, warnings

        risk_section = risk_match.group(1)

        # 检查是否有风险项
        if "待补充" in risk_section or not risk_section.strip():
            return errors, warnings

        # 检查三段式结构
        has_risk = bool(re.search(r'\*\*风险\*\*[：:]', risk_section))
        has_severity = bool(re.search(r'\*\*严重(?:程度|级别)\*\*[：:]', risk_section))
        has_recommendation = bool(re.search(r'\*\*建议\*\*[：:]', risk_section))

        if not has_risk:
            warnings.append(("risk_missing_description", "风险分析缺少'风险'描述字段"))

        if not has_severity:
            warnings.append(("risk_missing_severity", "风险分析缺少'严重程度'字段"))

        if not has_recommendation:
            warnings.append(("risk_missing_recommendation", "风险分析缺少'建议'字段"))

        # 如果三段都缺失，视为错误
        if not has_risk and not has_severity and not has_recommendation:
            errors.append((
                "risk_format_invalid",
                "风险分析未采用三段式结构（风险、严重程度、建议）"
            ))

        return errors, warnings

    @staticmethod
    def _check_markdown_syntax(content: str) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
        """
        检查 Markdown 基础语法合法性。

        检查项：
        - 未闭合的代码块
        - 未闭合的粗体/斜体标记
        - 无效的链接格式
        - 表格格式问题

        参数:
            content: Markdown 报告字符串。

        返回:
            (错误列表, 警告列表)。
        """
        errors: List[Tuple[str, str]] = []
        warnings: List[Tuple[str, str]] = []

        # 检查未闭合的代码块
        code_block_count = content.count('```')
        if code_block_count % 2 != 0:
            errors.append(("unclosed_code_block", "存在未闭合的代码块标记 ```"))

        # 检查未闭合的粗体标记 **
        bold_pattern = r'\*\*[^*]*$'
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if re.search(bold_pattern, line):
                # 检查是否是行尾的粗体开始
                if line.count('**') % 2 != 0:
                    warnings.append((
                        "unclosed_bold",
                        f"第 {i} 行可能存在未闭合的粗体标记 **"
                    ))

        # 检查无效链接格式
        invalid_link_pattern = r'\[[^\]]*\]\s*[^(]'
        if re.search(invalid_link_pattern, content):
            warnings.append(("invalid_link_format", "存在格式可疑的链接"))

        # 检查空标题
        empty_heading_pattern = r'^#{1,6}\s*$'
        for i, line in enumerate(lines, 1):
            if re.match(empty_heading_pattern, line):
                errors.append((
                    "empty_heading",
                    f"第 {i} 行存在空标题"
                ))

        return errors, warnings

    @staticmethod
    def get_validation_summary(result: ValidationResult) -> str:
        """
        生成校验结果的摘要信息。

        参数:
            result: ValidationResult 对象。

        返回:
            人类可读的校验摘要字符串。
        """
        summary_lines = []

        if result.passed:
            summary_lines.append("✅ 校验通过")
        else:
            summary_lines.append(f"❌ 校验失败 ({len(result.errors)} 个错误)")

        if result.errors:
            summary_lines.append("\n错误:")
            for error_type, error_desc in result.errors:
                summary_lines.append(f"  - [{error_type}] {error_desc}")

        if result.warnings:
            summary_lines.append(f"\n警告 ({len(result.warnings)} 个):")
            for warn_type, warn_desc in result.warnings:
                summary_lines.append(f"  - [{warn_type}] {warn_desc}")

        return '\n'.join(summary_lines)
