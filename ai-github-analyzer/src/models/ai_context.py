"""
AI 输入上下文模型。

定义传递给 AI 模型的完整上下文数据结构，包括仓库信息、文件内容、技术栈等。
用于 DAG 工作流中各 Agent 节点的输入数据契约。
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FileContext(BaseModel):
    """单个文件的上下文信息。"""

    file_path: str = Field(description="文件相对路径")
    content: str = Field(description="文件内容（可能被截断）")
    language: Optional[str] = Field(default=None, description="编程语言")
    line_count: int = Field(default=0, description="文件行数")
    is_truncated: bool = Field(default=False, description="内容是否被截断")
    priority: str = Field(default="low", description="文件优先级：low/medium/high/critical")
    size_bytes: int = Field(default=0, description="文件大小（字节）")


class DirectoryContext(BaseModel):
    """目录结构上下文信息。"""

    path: str = Field(description="目录相对路径")
    children: List[str] = Field(default_factory=list, description="子文件或子目录列表")
    depth: int = Field(default=0, description="目录深度")


class TechStackContext(BaseModel):
    """技术栈上下文信息。"""

    languages: List[str] = Field(default_factory=list, description="检测到的编程语言列表")
    frameworks: List[str] = Field(default_factory=list, description="检测到的框架列表")
    dependencies: List[str] = Field(default_factory=list, description="核心依赖列表")
    build_tools: List[str] = Field(default_factory=list, description="构建工具列表")
    config_files: List[str] = Field(default_factory=list, description="配置文件列表")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="技术栈识别置信度")


class SelectedFileContext(BaseModel):
    """经过优先级筛选后的文件上下文。"""

    file_path: str = Field(description="文件相对路径")
    summary: str = Field(description="文件摘要或关键代码片段")
    relevance_score: float = Field(ge=0.0, le=1.0, description="相关性评分")
    purpose: str = Field(description="文件用途说明")


class ContextChunk(BaseModel):
    """上下文分块（用于大文件裁剪）。"""

    file_path: str = Field(description="文件相对路径")
    chunk_index: int = Field(description="分块索引")
    total_chunks: int = Field(description="总分块数")
    content: str = Field(description="分块内容")
    start_line: int = Field(description="起始行号")
    end_line: int = Field(description="结束行号")
    is_truncated: bool = Field(default=False, description="是否被截断")


class AIContext(BaseModel):
    """
    AI 输入上下文模型。

    完整的 AI 分析上下文，包含仓库元信息、文件树、技术栈、
    精选文件和上下文分块，支持 Token 预算控制和截断标记。
    """

    repo_name: str = Field(description="仓库名称")
    repo_path: str = Field(description="仓库本地路径")
    repo_type: Optional[str] = Field(default=None, description="仓库类型（web/api/cli/library等）")

    files: List[FileContext] = Field(default_factory=list, description="文件列表")
    directories: List[DirectoryContext] = Field(default_factory=list, description="目录结构列表")
    languages: List[str] = Field(default_factory=list, description="主要编程语言列表")

    tech_stack: Optional[TechStackContext] = Field(default=None, description="技术栈上下文")

    selected_files: List[SelectedFileContext] = Field(
        default_factory=list, description="经过优先级筛选的文件列表"
    )
    context_chunks: List[ContextChunk] = Field(
        default_factory=list, description="上下文分块列表（用于大文件）"
    )

    token_budget: int = Field(default=10000, gt=0, description="Token 预算上限")
    is_truncated: bool = Field(default=False, description="上下文是否被截断")
    created_at: datetime = Field(default_factory=datetime.now, description="上下文创建时间")

    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="扩展元数据（支持未来字段扩展）"
    )
