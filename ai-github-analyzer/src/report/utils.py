"""
工具函数模块。

提供报告生成过程中使用的通用工具函数，包括：
- 时间戳格式化
- 目录确保存在
- 路径处理
- 字符串处理

本模块为纯工具函数集合，无状态设计。
"""

from pathlib import Path
from datetime import datetime
from typing import Optional


def format_timestamp(dt: Optional[datetime] = None, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化时间戳为人类可读的字符串。

    参数:
        dt: 待格式化的 datetime 对象。如果为 None，使用当前时间。
        fmt: 时间格式字符串，默认为 "%Y-%m-%d %H:%M:%S"。

    返回:
        格式化后的时间字符串。

    示例:
        >>> format_timestamp()
        '2026-05-15 14:30:00'
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(fmt)


def ensure_directory(path: Path) -> Path:
    """
    确保目录存在，如果不存在则创建。

    参数:
        path: 目录路径。

    返回:
        确认存在的目录路径。

    异常:
        PermissionError: 当没有权限创建目录时抛出。
        OSError: 当目录创建失败时抛出。

    注意:
        - 自动创建所有父目录（parents=True）
        - 如果目录已存在，不执行任何操作（exist_ok=True）
        - 返回的是绝对路径
    """
    # 转换为绝对路径
    abs_path = path.resolve()

    # 创建目录（如果不存在）
    abs_path.mkdir(parents=True, exist_ok=True)

    return abs_path


def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """
    清理文件名，移除或替换非法字符。

    参数:
        filename: 原始文件名。
        replacement: 用于替换非法字符的字符串，默认为 "_"。

    返回:
        清理后的安全文件名。

    注意:
        - 移除 Windows 和 Unix 系统中的非法字符
        - 保留中文、英文、数字、下划线、连字符、点号
        - 去除首尾空格
    """
    # 定义非法字符（Windows 和 Unix 通用）
    illegal_chars = '<>:"/\\|?*'

    # 替换非法字符
    sanitized = filename
    for char in illegal_chars:
        sanitized = sanitized.replace(char, replacement)

    # 去除首尾空格和点号
    sanitized = sanitized.strip(' .')

    # 限制长度（Windows 最大 255 字符）
    if len(sanitized) > 255:
        # 保留扩展名
        if '.' in sanitized:
            name, ext = sanitized.rsplit('.', 1)
            max_name_len = 255 - len(ext) - 1
            sanitized = name[:max_name_len] + '.' + ext
        else:
            sanitized = sanitized[:255]

    # 如果结果为空，使用默认名称
    if not sanitized:
        sanitized = "unnamed"

    return sanitized


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断字符串到指定长度。

    参数:
        text: 原始字符串。
        max_length: 最大长度（包含后缀）。
        suffix: 截断后添加的后缀，默认为 "..."。

    返回:
        截断后的字符串。

    注意:
        - 如果文本长度未超过 max_length，返回原文本
        - 截断时会尽量在单词边界处断开
    """
    if len(text) <= max_length:
        return text

    # 计算实际可用长度（减去后缀长度）
    available_length = max_length - len(suffix)

    if available_length <= 0:
        return suffix

    # 截断并添加后缀
    truncated = text[:available_length].rstrip()

    # 尝试在空格处断开（避免切断单词）
    last_space = truncated.rfind(' ')
    if last_space > available_length * 0.5:
        truncated = truncated[:last_space]

    return truncated + suffix


def calculate_reading_time(content: str, words_per_minute: int = 200) -> str:
    """
    估算阅读时间。

    参数:
        content: 文本内容。
        words_per_minute: 每分钟阅读字数，默认为 200。

    返回:
        估算的阅读时间字符串（如 "5 分钟"）。

    注意:
        - 中文字符按字计数
        - 英文按单词计数
        - 结果向上取整
    """
    # 简单估算：中文字符数 + 英文单词数
    chinese_chars = sum(1 for char in content if '\u4e00' <= char <= '\u9fff')
    
    # 英文单词数（粗略估算）
    english_words = len(content.split())

    # 总字数
    total_words = chinese_chars + english_words

    # 计算分钟数
    minutes = max(1, (total_words + words_per_minute - 1) // words_per_minute)

    return f"{minutes} 分钟"


def bytes_to_human_readable(size_bytes: int) -> str:
    """
    将字节数转换为人类可读的大小表示。

    参数:
        size_bytes: 字节数。

    返回:
        人类可读的大小字符串（如 "1.5 MB"）。

    注意:
        - 自动选择合适的单位（B, KB, MB, GB）
        - 保留一位小数
    """
    if size_bytes < 0:
        return "0 B"

    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    if unit_index == 0:
        return f"{int(size)} B"
    else:
        return f"{size:.1f} {units[unit_index]}"
