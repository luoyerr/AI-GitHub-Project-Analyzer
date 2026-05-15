"""
上下文构建器数据模型模块。

定义上下文构建过程中使用的核心数据结构和枚举类型。
包括文件优先级、文件分类、上下文文件、上下文包等模型。

本模块仅负责数据模型定义，不包含任何业务逻辑。
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ContextPriority(str, Enum):
    """
    上下文优先级枚举。

    定义文件的处理优先级，用于排序和预算控制。
    优先级从高到低依次为：S > A > B > C > D
    """

    S = "S"
    """最高价值 - 核心架构文件、关键配置文件"""

    A = "A"
    """入口文件 - 应用启动入口、主模块文件"""

    B = "B"
    """核心模块 - 主要业务逻辑、核心功能实现"""

    C = "C"
    """普通源码 - 辅助代码、工具类、次要模块"""

    D = "D"
    """低价值 - 测试文件、文档、生成代码"""


class FileCategory(str, Enum):
    """
    文件分类枚举。

    定义文件的类型分类，用于筛选和处理策略选择。
    不同分类的文件具有不同的处理优先级和裁剪策略。
    """

    ENTRY = "ENTRY"
    """入口文件 - 应用启动点、主程序文件"""

    CONFIG = "CONFIG"
    """配置文件 - 项目配置、依赖管理、环境配置"""

    SOURCE = "SOURCE"
    """源代码 - 业务逻辑、功能实现代码"""

    DOCUMENT = "DOCUMENT"
    """文档文件 - README、设计文档、说明文档"""

    BUILD = "BUILD"
    """构建文件 - 构建脚本、打包配置"""

    TEST = "TEST"
    """测试文件 - 单元测试、集成测试"""

    CI_CD = "CI_CD"
    """持续集成/部署 - CI/CD 配置文件"""

    DOCKER = "DOCKER"
    """容器化文件 - Dockerfile、docker-compose 配置"""

    UNKNOWN = "UNKNOWN"
    """未知类型 - 无法识别的文件类型"""


class ContextFile(BaseModel):
    """
    上下文文件模型。

    表示单个经过处理的上下文文件，包含文件路径、内容、
    优先级、分类、大小等信息。用于在分析过程中传递文件数据。
    """

    model_config = ConfigDict(
        extra="ignore",
        frozen=False,
        str_strip_whitespace=True,
    )

    path: str = Field(..., description="文件的绝对路径")
    relative_path: str = Field(..., description="相对于仓库根目录的路径")
    category: FileCategory = Field(..., description="文件分类类型")
    priority: ContextPriority = Field(..., description="文件处理优先级")
    language: Optional[str] = Field(None, description="编程语言或文件格式")
    size: int = Field(..., description="文件大小（字节）")
    content: Optional[str] = Field(None, description="文件内容，可能为 None 或被截断")
    is_truncated: bool = Field(False, description="文件内容是否被截断")
    truncated_reason: Optional[str] = Field(
        None, description="文件被截断的原因说明"
    )
    estimated_tokens: Optional[int] = Field(
        None, description="预估的 token 数量"
    )


class FileReadResult(BaseModel):
    """
    文件读取结果模型。

    表示单个文件的读取结果，包含文件内容、编码信息、
    截断状态和文件大小等元数据。用于在 Context Builder
    中传递文件读取的完整信息。
    """

    model_config = ConfigDict(
        extra="ignore",
        frozen=False,
        str_strip_whitespace=True,
    )

    content: Optional[str] = Field(None, description="文件文本内容")
    encoding: str = Field(..., description="检测到的文件编码")
    is_truncated: bool = Field(False, description="文件内容是否被截断")
    truncated_reason: Optional[str] = Field(
        None, description="文件被截断的原因说明"
    )
    size: int = Field(..., description="文件实际大小（字节）")


class ContextBundle(BaseModel):
    """
    上下文包模型。

    表示整个仓库的完整上下文，包含所有选中的文件列表、
    统计信息和元数据。作为 Context Builder 的最终输出，
    传递给后续的 Agent 进行分析。
    """

    model_config = ConfigDict(
        extra="allow",
        frozen=False,
        str_strip_whitespace=True,
    )

    repo_name: str = Field(..., description="仓库名称")
    repo_path: str = Field(..., description="仓库本地路径")
    total_files: int = Field(..., description="扫描到的文件总数")
    selected_files: int = Field(..., description="选中纳入上下文的文件数")
    truncated_files: int = Field(0, description="被截断的文件数量")
    estimated_tokens: int = Field(0, description="预估的总 token 数量")
    files: List[ContextFile] = Field(default_factory=list, description="上下文文件列表")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="元数据信息，用于未来扩展（如语言分布、框架信息、入口点等）",
    )
