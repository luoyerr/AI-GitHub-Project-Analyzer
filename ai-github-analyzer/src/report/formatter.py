"""
Markdown 格式化工具模块。

负责 Markdown 内容的美化和标准化，包括：
- 统一标题格式
- 规范空行
- 标准化列表格式
- 代码块格式化
- Mermaid 图表格式化
- 自动修复常见 Markdown 问题

本模块仅负责格式化，不包含业务逻辑。
"""

import re


class MarkdownFormatter:
    """
    Markdown 格式化器类。

    提供多种 Markdown 内容格式化方法，确保生成的报告格式统一、美观。
    所有方法均为静态方法，无状态设计。
    """

    @staticmethod
    def format(content: str) -> str:
        """
        执行完整的 Markdown 格式化流程。

        参数:
            content: 原始 Markdown 字符串。

        返回:
            格式化后的 Markdown 字符串。

        注意:
            按顺序执行以下格式化步骤：
            1. 清理多余空行
            2. 统一标题格式
            3. 标准化列表
            4. 格式化代码块
            5. 格式化 Mermaid
            6. 最终清理
        """
        formatted = content

        # 依次执行格式化步骤
        formatted = MarkdownFormatter._normalize_empty_lines(formatted)
        formatted = MarkdownFormatter._normalize_headings(formatted)
        formatted = MarkdownFormatter._normalize_lists(formatted)
        formatted = MarkdownFormatter._normalize_code_blocks(formatted)
        formatted = MarkdownFormatter._normalize_mermaid(formatted)
        formatted = MarkdownFormatter._final_cleanup(formatted)

        return formatted

    @staticmethod
    def _normalize_empty_lines(content: str) -> str:
        """
        规范化空行。

        规则：
        - 连续多个空行合并为两个空行（章节间）
        - 标题前后保留一个空行
        - 列表项之间不插入额外空行

        参数:
            content: Markdown 字符串。

        返回:
            规范化空行后的字符串。
        """
        # 将 3 个或更多连续空行替换为 2 个空行
        content = re.sub(r'\n{3,}', '\n\n', content)

        # 确保标题前有一个空行（除非是文档开头）
        content = re.sub(r'([^\n])\n(#{1,6}\s)', r'\1\n\n\2', content)

        # 确保标题后有一个空行
        content = re.sub(r'(#{1,6}\s[^\n]+)\n([^\n#])', r'\1\n\n\2', content)

        return content

    @staticmethod
    def _normalize_headings(content: str) -> str:
        """
        统一标题格式。

        规则：
        - 标题符号 # 后必须有一个空格
        - 标题文本后不能有 trailing spaces
        - 保持标题层级一致性
        - 禁止出现重复的 # (# #、## #、### #)

        参数:
            content: Markdown 字符串。

        返回:
            规范化标题后的字符串。
        """
        lines = content.split('\n')
        normalized_lines = []

        for line in lines:
            # 匹配标题行（包括错误的 # # 格式）
            heading_match = re.match(r'^(#{1,6})\s*(#{0,6})\s*(.*)$', line)
            if heading_match:
                hashes = heading_match.group(1)
                extra_hashes = heading_match.group(2).strip()
                text = heading_match.group(3).strip()
                
                # 如果有多余的 #，移除它们
                if extra_hashes:
                    # 移除文本开头可能存在的额外 #
                    text = re.sub(r'^#+\s*', '', text)
                
                # 确保标题格式正确：# 后面有空格，然后是文本
                if text:
                    normalized_lines.append(f"{hashes} {text}")
                else:
                    # 如果没有文本，保留原始行但去除多余 #
                    normalized_lines.append(f"{hashes}")
            else:
                # 非标题行，去除尾部空格
                normalized_lines.append(line.rstrip())

        return '\n'.join(normalized_lines)

    @staticmethod
    def _normalize_lists(content: str) -> str:
        """
        标准化列表格式。

        规则：
        - 无序列表使用 "- " 格式（短横线 + 空格）
        - 有序列表保持 "数字. " 格式
        - 列表项缩进统一为 2 或 4 个空格
        - 列表项文本对齐

        参数:
            content: Markdown 字符串。

        返回:
            规范化列表后的字符串。
        """
        lines = content.split('\n')
        normalized_lines = []

        for line in lines:
            # 匹配无序列表项（支持 *, -, + 开头）
            unordered_match = re.match(r'^(\s*)[\*\+\-]\s+(.+)$', line)
            if unordered_match:
                indent = unordered_match.group(1)
                text = unordered_match.group(2)
                # 统一使用 "- " 格式
                normalized_lines.append(f"{indent}- {text}")
                continue

            # 匹配有序列表项
            ordered_match = re.match(r'^(\s*)\d+\.\s+(.+)$', line)
            if ordered_match:
                # 保持原有格式，只确保有空格
                normalized_lines.append(line)
                continue

            normalized_lines.append(line)

        return '\n'.join(normalized_lines)

    @staticmethod
    def _normalize_code_blocks(content: str) -> str:
        """
        格式化代码块。

        规则：
        - 代码块标记 ``` 前后各保留一个空行
        - 语言标识符统一小写
        - 代码块内部去除首尾空行
        - bash 代码块保持一致性

        参数:
            content: Markdown 字符串。

        返回:
            规范化代码块后的字符串。
        """
        # 匹配代码块并处理
        def process_code_block(match):
            lang = match.group(1) or ""
            code = match.group(2)

            # 语言标识符小写化
            lang = lang.strip().lower()

            # 去除代码内部首尾空行
            code = code.strip()

            # 构建标准代码块
            if lang:
                return f"\n```{lang}\n{code}\n```\n"
            else:
                return f"\n```\n{code}\n```\n"

        # 匹配 ```lang ... ``` 格式的代码块
        pattern = r'```(\w*)\s*\n(.*?)\n```'
        content = re.sub(pattern, process_code_block, content, flags=re.DOTALL)

        return content

    @staticmethod
    def _normalize_mermaid(content: str) -> str:
        """
        格式化 Mermaid 图表。

        规则：
        - mermaid 代码块前后保留空行
        - 确保使用 ```mermaid 标记
        - Mermaid 代码内部保持原样（不修改语法）

        参数:
            content: Markdown 字符串。

        返回:
            规范化 Mermaid 后的字符串。
        """
        # 匹配 mermaid 代码块
        def process_mermaid(match):
            code = match.group(1).strip()
            return f"\n```mermaid\n{code}\n```\n"

        # 匹配各种 mermaid 代码块写法
        patterns = [
            r'```mermaid\s*\n(.*?)\n```',
            r'```Mermaid\s*\n(.*?)\n```',
            r'```MERMAID\s*\n(.*?)\n```',
        ]

        for pattern in patterns:
            content = re.sub(pattern, process_mermaid, content, flags=re.DOTALL)

        return content

    @staticmethod
    def _final_cleanup(content: str) -> str:
        """
        最终清理。

        规则：
        - 去除文档开头的多余空行
        - 确保文档以单个换行符结尾
        - 去除每行的尾部空格
        - 统一换行符为 \n

        参数:
            content: Markdown 字符串。

        返回:
            最终清理后的字符串。
        """
        # 统一换行符
        content = content.replace('\r\n', '\n').replace('\r', '\n')

        # 去除每行尾部空格
        lines = content.split('\n')
        lines = [line.rstrip() for line in lines]
        content = '\n'.join(lines)

        # 去除开头空行
        content = content.lstrip('\n')

        # 确保以单个换行符结尾
        content = content.rstrip('\n') + '\n'

        return content

    @staticmethod
    def clean_mermaid(content: str) -> str:
        """
        清洗 Mermaid 内容，去除 Markdown fence 和隐藏字符。
        
        功能：
        - 删除 ```mermaid 标记
        - 删除 ``` 标记
        - 删除隐藏 Unicode 字符（如 \u200b）
        - 返回纯 Mermaid 代码
        
        参数:
            content: 可能包含 Markdown fence 的 Mermaid 字符串。
        
        返回:
            纯 Mermaid 代码字符串。
        
        注意:
            此函数确保 AI 返回的内容不会导致双重包裹问题。
        """
        if not content:
            return ""
        
        # 删除隐藏 Unicode 字符（零宽空格等）
        content = content.replace("\u200b", "")
        content = content.replace("\u200c", "")
        content = content.replace("\u200d", "")
        content = content.replace("\ufeff", "")
        
        # 删除 ```mermaid 标记（不区分大小写）
        content = re.sub(r'```\s*mermaid\s*', '', content, flags=re.IGNORECASE)
        
        # 删除剩余的 ``` 标记
        content = re.sub(r'```', '', content)
        
        # 去除首尾空白
        content = content.strip()
        
        return content

    @staticmethod
    def fix_common_issues(content: str) -> str:
        """
        修复常见的 Markdown 问题。

        修复项：
        - 中文标点后缺少空格（可选，根据风格决定）
        - 链接格式错误
        - 图片格式错误
        - 表格对齐问题
        - 强调符号不规范
        - 重复的 # 符号（# #、## #、### #）
        - Markdown fence 未闭合（自动补充）

        参数:
            content: Markdown 字符串。

        返回:
            修复后的字符串。
        """
        # 修复重复的 # 符号（全局兜底）
        content = MarkdownFormatter._remove_duplicate_hashes(content)
        
        # 修复 Markdown fence 未闭合问题
        content = MarkdownFormatter._fix_unclosed_fences(content)
        
        # 修复链接格式 [text](url) 中间不应有空格
        content = re.sub(r'\[([^\]]+)\]\s*\(\s*([^)]+)\s*\)', r'[\1](\2)', content)

        # 修复图片格式 ![alt](url)
        content = re.sub(r'!\[([^\]]*)\]\s*\(\s*([^)]+)\s*\)', r'![\1](\2)', content)

        # 标准化粗体 **text**
        content = re.sub(r'\*{2,}([^*]+)\*{2,}', r'**\1**', content)

        # 标准化斜体 *text*
        content = re.sub(r'(?<!\*)\*(?!\*)([^*]+)(?<!\*)\*(?!\*)', r'*\1*', content)

        return content
    
    @staticmethod
    def _fix_unclosed_fences(content: str) -> str:
        """
        修复未闭合的 Markdown fence。
        
        如果 ``` 标记数量为奇数，自动在文档末尾补充一个 ``` 来闭合。
        
        参数:
            content: Markdown 字符串。
        
        返回:
            修复后的字符串。
        """
        fence_count = content.count('```')
        
        # 如果数量为奇数，补充一个 ```
        if fence_count % 2 != 0:
            # 在文档末尾添加闭合标记
            content = content.rstrip() + '\n```\n'
        
        return content
    
    @staticmethod
    def _remove_duplicate_hashes(content: str) -> str:
        """
        移除重复的 # 符号。
        
        将 "# # 标题" 转换为 "# 标题"
        将 "## # 标题" 转换为 "## 标题"
        将 "### # 标题" 转换为 "### 标题"
        
        参数:
            content: Markdown 字符串。
            
        返回:
            修复后的字符串。
        """
        lines = content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # 匹配 # #、## #、### # 等模式
            match = re.match(r'^(#{1,6})\s+#+\s+(.*)$', line)
            if match:
                correct_hashes = match.group(1)
                text = match.group(2).strip()
                # 移除文本中可能还存在的多余 #
                text = re.sub(r'^#+\s*', '', text)
                fixed_lines.append(f"{correct_hashes} {text}")
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
