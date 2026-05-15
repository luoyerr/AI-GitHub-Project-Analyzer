"""
智能上下文裁剪器 - 结构化文件内容裁剪模块。

负责对文件内容进行结构化裁剪，保留关键结构信息（如函数签名、类定义、导入语句等），
移除详细实现细节，以减少 token 消耗同时保持代码的可理解性。

本模块仅负责内容裁剪，不包含：
- 文件读取逻辑
- 文件筛选逻辑
- 文件排序逻辑
- AI 分析逻辑
- Prompt 生成
"""

import re

from loguru import logger

from .models import ContextFile


# 敏感信息关键词列表（用于脱敏）
SENSITIVE_KEYWORDS = [
    "password",
    "secret",
    "token",
    "credential",
    "private",
    "key",
    "api_key",
    "apikey",
    "access_token",
    "refresh_token",
]

# 最大保留行数（兜底裁剪）
MAX_LINES_DEFAULT = 300


class ContextTruncator:
    """
    智能上下文裁剪器 - 结构化文件内容裁剪。

    职责：
        对文件内容进行结构化裁剪，保留关键结构信息，移除实现细节。
        支持多种编程语言的特定裁剪策略。

    裁剪策略：
        1. Python: 保留导入、类定义、函数签名、文档字符串、路由装饰器
        2. Java: 保留注解、类声明、方法签名、接口定义
        3. Go: 保留包声明、导入、函数/结构体/接口签名、路由注册
        4. Vue: 保留模板结构、脚本导出、props/data/methods/computed/watch
        5. 配置文件: 保留结构并自动脱敏敏感信息
        6. Markdown: 保留标题结构和前 200 行
        7. 通用: 兜底裁剪，保留前 200-300 行

    使用示例：
        >>> truncator = ContextTruncator()
        >>> truncated_file = truncator.truncate(context_file)
    """

    def __init__(self, max_lines: int = MAX_LINES_DEFAULT) -> None:
        """
        初始化智能上下文裁剪器。

        参数：
            max_lines: 单个文件最大保留行数，默认 300 行
        """
        self.max_lines = max_lines
        logger.debug("初始化 ContextTruncator，最大行数: {}", max_lines)

    def truncate(self, context_file: ContextFile) -> ContextFile:
        """
        总入口：对单个上下文文件进行智能裁剪。

        流程：
            1. 识别文件语言类型
            2. 选择对应的裁剪策略
            3. 执行裁剪操作
            4. 更新元数据（is_truncated, truncated_reason）
            5. 返回裁剪后的 ContextFile

        参数：
            context_file: 待裁剪的上下文文件对象

        返回：
            裁剪后的上下文文件对象

        注意：
            如果文件内容为空或无需裁剪，直接返回原对象。
        """
        # 检查是否需要裁剪
        if not context_file.content:
            logger.debug("文件内容为空，跳过裁剪: {}", context_file.path)
            return context_file

        lines = context_file.content.splitlines()
        if len(lines) <= self.max_lines:
            logger.debug(
                "文件行数 {} 未超过限制 {}，无需裁剪: {}",
                len(lines),
                self.max_lines,
                context_file.path,
            )
            return context_file

        # 识别语言类型
        language = self._detect_language(context_file)
        logger.info(
            "开始裁剪文件: {}, 语言: {}, 原始行数: {}",
            context_file.path,
            language,
            len(lines),
        )

        # 选择裁剪策略并执行
        original_line_count = len(lines)
        truncated_content = self._apply_truncation(context_file.content, language)

        # 计算裁剪比例
        truncated_lines = truncated_content.splitlines()
        new_line_count = len(truncated_lines)
        truncation_ratio = (
            (original_line_count - new_line_count) / original_line_count * 100
            if original_line_count > 0
            else 0
        )

        # 更新元数据
        context_file.content = truncated_content
        context_file.is_truncated = True
        context_file.truncated_reason = self._generate_truncation_reason(
            language, original_line_count, new_line_count
        )

        logger.success(
            "裁剪完成: {}, 语言: {}, 原始行数: {}, 裁剪后行数: {}, 裁剪比例: {:.1f}%",
            context_file.path,
            language,
            original_line_count,
            new_line_count,
            truncation_ratio,
        )

        return context_file

    def _detect_language(self, context_file: ContextFile) -> str:
        """
        识别文件的编程语言类型。

        优先级：
            1. 使用 ContextFile 中已有的 language 字段
            2. 根据文件扩展名推断

        参数：
            context_file: 上下文文件对象

        返回：
            语言类型字符串，如 "python", "java", "go", "vue", "config", "markdown", "unknown"
        """
        # 优先使用已有的 language 字段
        if context_file.language:
            return context_file.language.lower()

        # 根据文件扩展名推断
        path_lower = context_file.path.lower()

        if path_lower.endswith(".py"):
            return "python"
        elif path_lower.endswith((".java", ".kt", ".scala")):
            return "java"
        elif path_lower.endswith(".go"):
            return "go"
        elif path_lower.endswith((".vue",)):
            return "vue"
        elif path_lower.endswith((".yaml", ".yml", ".json", ".toml", ".env.example")):
            return "config"
        elif path_lower.endswith((".md", ".markdown")):
            return "markdown"
        else:
            return "unknown"

    def _apply_truncation(self, content: str, language: str) -> str:
        """
        根据语言类型应用对应的裁剪策略。

        参数：
            content: 原始文件内容
            language: 语言类型

        返回：
            裁剪后的文件内容
        """
        if language == "python":
            return self._truncate_python(content)
        elif language == "java":
            return self._truncate_java(content)
        elif language == "go":
            return self._truncate_go(content)
        elif language == "vue":
            return self._truncate_vue(content)
        elif language == "config":
            return self._truncate_config(content)
        elif language == "markdown":
            return self._truncate_markdown(content)
        else:
            return self._truncate_by_lines(content)

    def _truncate_python(self, content: str) -> str:
        """
        裁剪 Python 文件内容。

        保留内容：
            - import 语句
            - class 定义和文档字符串
            - def 函数签名和文档字符串
            - 路由装饰器（@app.route, @router.get 等）
            - main 入口函数

        裁剪策略：
            - 函数实现只保留前几行
            - 其余部分用 "# ... 已省略" 替代

        参数：
            content: 原始 Python 代码内容

        返回：
            裁剪后的 Python 代码
        """
        lines = content.splitlines()
        result_lines = []
        in_function = False
        function_indent = 0
        function_start_line = 0

        for i, line in enumerate(lines):
            stripped = line.strip()

            # 检测函数定义
            if re.match(r"^\s*(async\s+)?def\s+\w+", line):
                # 如果之前在函数内，先添加省略标记
                if in_function:
                    result_lines.append(f"{' ' * function_indent}# ... 已省略")
                    result_lines.append("")

                # 添加函数签名
                result_lines.append(line)
                in_function = True
                function_indent = len(line) - len(line.lstrip())
                function_start_line = i
                continue

            # 检测类定义
            if re.match(r"^\s*class\s+\w+", line):
                # 如果之前在函数内，先添加省略标记
                if in_function:
                    result_lines.append(f"{' ' * function_indent}# ... 已省略")
                    result_lines.append("")
                    in_function = False

                # 添加类定义
                result_lines.append(line)
                continue

            # 在函数内部的处理
            if in_function:
                current_indent = len(line) - len(line.lstrip()) if stripped else function_indent + 4

                # 如果是函数体的第一层缩进（通常是 docstring 或简单语句）
                if current_indent > function_indent and i - function_start_line <= 5:
                    result_lines.append(line)
                # 如果遇到同级别或更外层的代码，说明函数结束
                elif current_indent <= function_indent and stripped:
                    result_lines.append(f"{' ' * function_indent}# ... 已省略")
                    result_lines.append("")
                    result_lines.append(line)
                    in_function = False
                # 其他情况跳过（省略函数实现）
                else:
                    continue
            else:
                # 非函数内的代码直接保留（import、注释、装饰器等）
                result_lines.append(line)

        # 如果最后一个函数没有闭合，添加省略标记
        if in_function:
            result_lines.append(f"{' ' * function_indent}# ... 已省略")

        return "\n".join(result_lines)

    def _truncate_java(self, content: str) -> str:
        """
        裁剪 Java 文件内容。

        保留内容：
            - @RestController, @Service, @Repository 等注解
            - class 和 interface 声明
            - 方法签名（包括注解）

        裁剪策略：
            - 方法实现全部裁剪
            - 保留大括号结构

        参数：
            content: 原始 Java 代码内容

        返回：
            裁剪后的 Java 代码
        """
        lines = content.splitlines()
        result_lines = []
        brace_depth = 0
        in_method = False
        method_indent = 0

        for line in lines:
            stripped = line.strip()

            # 检测方法定义（包含注解）
            if re.match(r"^\s*(@|public|private|protected|static).*\([^)]*\)\s*\{?", line) and not stripped.startswith(
                "//"
            ):
                if in_method:
                    # 结束上一个方法
                    result_lines.append(f"{' ' * method_indent}// ... 已省略")
                    result_lines.append(f"{' ' * method_indent}}}")
                    result_lines.append("")

                # 添加方法签名
                if "{" in line:
                    # 方法签名带左括号
                    parts = line.split("{", 1)
                    result_lines.append(parts[0].rstrip() + " {")
                    method_indent = len(line) - len(line.lstrip())
                    in_method = True
                    brace_depth = 1
                else:
                    result_lines.append(line)
                    method_indent = len(line) - len(line.lstrip())
                    in_method = True
                    brace_depth = 0
                continue

            # 跟踪大括号深度
            if in_method:
                brace_depth += line.count("{") - line.count("}")

                # 方法的第一行或注解行
                if brace_depth <= 1 and stripped and not stripped.startswith("//"):
                    if stripped == "{" or stripped == "}":
                        result_lines.append(line)
                    elif brace_depth == 0 and "{" not in line:
                        # 可能是多行方法签名的继续
                        result_lines.append(line)
                    else:
                        # 方法体内的内容，跳过
                        continue
                elif brace_depth <= 0:
                    # 方法结束
                    result_lines.append(f"{' ' * method_indent}// ... 已省略")
                    if "}" not in line:
                        result_lines.append(f"{' ' * method_indent}}}")
                    else:
                        result_lines.append(line)
                    result_lines.append("")
                    in_method = False
                    brace_depth = 0
            else:
                # 非方法内的代码直接保留
                result_lines.append(line)

        # 如果最后一个方法没有闭合
        if in_method:
            result_lines.append(f"{' ' * method_indent}// ... 已省略")
            result_lines.append(f"{' ' * method_indent}}}")

        return "\n".join(result_lines)

    def _truncate_go(self, content: str) -> str:
        """
        裁剪 Go 文件内容。

        保留内容：
            - package 声明
            - import 语句
            - func 函数签名
            - struct 结构体定义
            - interface 接口定义
            - router 路由注册

        裁剪策略：
            - 函数实现全部裁剪
            - 保留大括号结构

        参数：
            content: 原始 Go 代码内容

        返回：
            裁剪后的 Go 代码
        """
        lines = content.splitlines()
        result_lines = []
        in_function = False
        function_indent = 0
        brace_depth = 0

        for line in lines:
            stripped = line.strip()

            # 检测函数定义
            if re.match(r"^func\s+", line):
                if in_function:
                    result_lines.append(f"{' ' * function_indent}// ... 已省略")
                    result_lines.append(f"{' ' * function_indent}}}")
                    result_lines.append("")

                # 添加函数签名
                if "{" in line:
                    parts = line.split("{", 1)
                    result_lines.append(parts[0].rstrip() + " {")
                    function_indent = len(line) - len(line.lstrip())
                    in_function = True
                    brace_depth = 1
                else:
                    result_lines.append(line)
                    function_indent = len(line) - len(line.lstrip())
                    in_function = True
                    brace_depth = 0
                continue

            # 检测结构体或接口定义
            if re.match(r"^type\s+\w+\s+(struct|interface)", line):
                if in_function:
                    result_lines.append(f"{' ' * function_indent}// ... 已省略")
                    result_lines.append(f"{' ' * function_indent}}}")
                    result_lines.append("")
                    in_function = False
                    brace_depth = 0

                result_lines.append(line)
                continue

            # 在函数内部的处理
            if in_function:
                brace_depth += line.count("{") - line.count("}")

                if brace_depth <= 1 and stripped:
                    if stripped == "{" or stripped == "}":
                        result_lines.append(line)
                    elif brace_depth == 0:
                        # 函数签名 continuation
                        result_lines.append(line)
                    else:
                        continue
                elif brace_depth <= 0:
                    result_lines.append(f"{' ' * function_indent}// ... 已省略")
                    if "}" not in line:
                        result_lines.append(f"{' ' * function_indent}}}")
                    else:
                        result_lines.append(line)
                    result_lines.append("")
                    in_function = False
                    brace_depth = 0
            else:
                # 非函数内的代码直接保留（package, import, type 等）
                result_lines.append(line)

        # 如果最后一个函数没有闭合
        if in_function:
            result_lines.append(f"{' ' * function_indent}// ... 已省略")
            result_lines.append(f"{' ' * function_indent}}}")

        return "\n".join(result_lines)

    def _truncate_vue(self, content: str) -> str:
        """
        裁剪 Vue 文件内容（支持 Vue 2）。

        保留内容：
            - template 结构（简化版）
            - script 标签和 export default
            - props 定义
            - data 返回对象结构
            - methods/computed/watch 的方法签名

        裁剪策略：
            - 删除超长 CSS 样式
            - 方法实现只保留签名

        参数：
            content: 原始 Vue 组件内容

        返回：
            裁剪后的 Vue 组件内容
        """
        lines = content.splitlines()
        result_lines = []
        in_script = False
        in_style = False
        in_methods = False
        in_data = False
        indent_level = 0

        for line in lines:
            stripped = line.strip()

            # 检测 style 标签（裁剪整个 style 块）
            if "<style" in line.lower():
                in_style = True
                result_lines.append(line)
                continue

            if in_style:
                if "</style>" in line.lower():
                    result_lines.append("/* ... 样式已省略 ... */")
                    result_lines.append(line)
                    in_style = False
                continue

            # 检测 script 标签
            if "<script" in line.lower():
                in_script = True
                result_lines.append(line)
                continue

            if "</script>" in line.lower():
                in_script = False
                result_lines.append(line)
                continue

            # 在 script 内部的处理
            if in_script:
                # 检测 methods/computed/watch
                if re.match(r"^(methods|computed|watch)\s*:", stripped):
                    in_methods = True
                    indent_level = len(line) - len(line.lstrip())
                    result_lines.append(line)
                    continue

                # 检测 data 函数
                if re.match(r"^data\s*\(\)\s*\{", stripped) or re.match(r"^data:\s*function", stripped):
                    in_data = True
                    indent_level = len(line) - len(line.lstrip())
                    result_lines.append(line)
                    continue

                # 在 methods/computed/watch 内部
                if in_methods:
                    current_indent = len(line) - len(line.lstrip()) if stripped else indent_level + 2

                    # 检测方法定义
                    if re.match(r"^\w+\s*\(", stripped) or re.match(r"^\w+\s*:", stripped):
                        # 添加方法签名
                        if "{" in line:
                            parts = line.split("{", 1)
                            result_lines.append(parts[0].rstrip() + " {")
                            result_lines.append(f"{' ' * (current_indent + 2)}// ... 已省略")
                            result_lines.append(f"{' ' * current_indent}}},")
                        else:
                            result_lines.append(line)
                    elif current_indent <= indent_level and stripped:
                        # 退出 methods 块
                        in_methods = False
                        result_lines.append(line)
                    else:
                        # 跳过方法实现
                        continue
                elif in_data:
                    current_indent = len(line) - len(line.lstrip()) if stripped else indent_level + 2

                    # 保留 data 的结构但省略详细内容
                    if "return" in stripped:
                        result_lines.append(line)
                    elif current_indent <= indent_level and stripped:
                        in_data = False
                        result_lines.append(line)
                    elif "{" in stripped or "}" in stripped:
                        result_lines.append(line)
                    else:
                        continue
                else:
                    # 其他 script 内容直接保留（export default, props 等）
                    result_lines.append(line)
            else:
                # template 部分直接保留（可能已经很大，后续会兜底裁剪）
                result_lines.append(line)

        return "\n".join(result_lines)

    def _truncate_config(self, content: str) -> str:
        """
        裁剪配置文件内容（yaml/json/toml/.env.example）。

        特性：
            - 保留完整结构
            - 自动脱敏敏感信息（password/secret/token/key 等）

        参数：
            content: 原始配置文件内容

        返回：
            脱敏后的配置文件内容
        """
        # 对配置文件进行敏感信息脱敏
        masked_content = self._mask_sensitive_info(content)

        # 如果仍然过长，使用兜底裁剪
        lines = masked_content.splitlines()
        if len(lines) > self.max_lines:
            return self._truncate_by_lines(masked_content)

        return masked_content

    def _truncate_markdown(self, content: str) -> str:
        """
        裁剪 Markdown 文件内容。

        保留内容：
            - 标题结构（# ## ### 等）
            - 前 200 行

        参数：
            content: 原始 Markdown 内容

        返回：
            裁剪后的 Markdown 内容
        """
        lines = content.splitlines()

        # 如果不超过限制，直接返回
        if len(lines) <= 200:
            return content

        # 保留前 200 行
        truncated_lines = lines[:200]
        truncated_lines.append("")
        truncated_lines.append("<!-- ... 内容已省略 ... -->")

        return "\n".join(truncated_lines)

    def _mask_sensitive_info(self, content: str) -> str:
        """
        统一脱敏处理：替换敏感信息为 ******。

        支持的敏感关键词：
            - password
            - secret
            - token
            - credential
            - private
            - key
            - api_key
            - apikey
            - access_token
            - refresh_token

        脱敏规则：
            - 匹配模式：keyword: value 或 keyword=value
            - 替换值部分为 ******

        参数：
            content: 原始文本内容

        返回：
            脱敏后的文本内容
        """
        masked = content

        for keyword in SENSITIVE_KEYWORDS:
            # 匹配 YAML/JSON 格式: key: value
            pattern1 = rf'({keyword}\s*[:=]\s*)(["\']?)([^"\'\s\n]+)(\2)'
            masked = re.sub(pattern1, r'\1\2******\4', masked, flags=re.IGNORECASE)

            # 匹配环境变量格式: KEY=value
            pattern2 = rf'({keyword.upper()}\s*=\s*)(["\']?)([^"\'\s\n]+)(\2)'
            masked = re.sub(pattern2, r'\1\2******\4', masked, flags=re.IGNORECASE)

        logger.debug("完成敏感信息脱敏处理")
        return masked

    def _truncate_by_lines(self, content: str) -> str:
        """
        兜底裁剪：按行数裁剪。

        策略：
            - 保留前 max_lines 行
            - 添加省略标记

        参数：
            content: 原始文件内容

        返回：
            裁剪后的内容
        """
        lines = content.splitlines()

        if len(lines) <= self.max_lines:
            return content

        truncated_lines = lines[: self.max_lines]
        truncated_lines.append("")
        truncated_lines.append("# ... 文件过长，已截断 ...")

        return "\n".join(truncated_lines)

    def _generate_truncation_reason(
        self, language: str, original_lines: int, truncated_lines: int
    ) -> str:
        """
        生成裁剪原因说明。

        参数：
            language: 语言类型
            original_lines: 原始行数
            truncated_lines: 裁剪后行数

        返回：
            裁剪原因字符串
        """
        reduction = original_lines - truncated_lines
        ratio = (reduction / original_lines * 100) if original_lines > 0 else 0

        reasons = {
            "python": "Python 函数体裁剪，保留结构信息",
            "java": "Java 方法实现裁剪，保留签名和注解",
            "go": "Go 函数实现裁剪，保留签名和类型定义",
            "vue": "Vue 组件方法裁剪，保留模板和关键配置",
            "config": "配置文件敏感信息脱敏",
            "markdown": "Markdown 文档保留标题结构和前 200 行",
            "unknown": "文件过长，保留前 {} 行".format(self.max_lines),
        }

        base_reason = reasons.get(language, reasons["unknown"])
        detail = "（减少 {} 行，裁剪比例 {:.1f}%）".format(reduction, ratio)

        return base_reason + detail
