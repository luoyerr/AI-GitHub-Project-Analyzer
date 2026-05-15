"""
上下文数据模型模块。

定义上下文构建过程中使用的核心数据结构和枚举类型。
包括文件优先级、文件分类、上下文文件、上下文包等模型。
"""

from enum import Enum


class ContextPriority(Enum):
    """
    上下文优先级枚举。

    定义文件的处理优先级，用于排序和预算控制。
    """

    # TODO(context-builder): 定义优先级级别（如 CRITICAL, HIGH, MEDIUM, LOW）
    pass


class FileCategory(Enum):
    """
    文件分类枚举。

    定义文件的类型分类，用于筛选和处理策略选择。
    """

    # TODO(context-builder): 定义文件分类（如 CONFIG, ENTRY, SOURCE, DOC, TEST 等）
    pass


class ContextFile:
    """
    上下文文件模型。

    表示一个经过处理的文件，包含路径、内容、优先级、分类等信息。
    """

    def __init__(self) -> None:
        """初始化上下文文件模型。"""
        # TODO(context-builder): 定义文件模型的字段
        # 应包含：path, content, priority, category, size, language 等
        pass


class ContextBundle:
    """
    上下文包模型。

    表示完整的分析上下文，包含所有处理后的文件和相关元数据。
    """

    def __init__(self) -> None:
        """初始化上下文包模型。"""
        # TODO(context-builder): 定义上下文包的字段
        # 应包含：files, metadata, total_tokens, summary 等
        pass
