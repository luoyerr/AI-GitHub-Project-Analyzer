"""
仓库扫描器模块 - Phase 1: Repository Scanner

职责：
- 扫描本地路径或 GitHub 仓库
- 生成 RepositorySnapshot
- 支持文件限制和自动清理

禁止：
- AI 推断
- 读取文件内容
- 技术栈分析
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from pathlib import Path


class FileMetadata(BaseModel):
    """文件元数据。"""
    relative_path: str = Field(..., description="相对路径")
    size_bytes: int = Field(..., description="文件大小（字节）")
    extension: str = Field(..., description="文件后缀名")


class DirectoryMetadata(BaseModel):
    """目录元数据。"""
    relative_path: str = Field(..., description="相对路径")


class SnapshotMetadata(BaseModel):
    """快照元数据。"""
    file_count: int = Field(..., description="文件数量")
    directory_count: int = Field(..., description="目录数量")
    inferred_languages: List[str] = Field(default_factory=list, description="推测语言列表")
    truncated: bool = Field(default=False, description="是否被截断")


class RepositorySnapshot(BaseModel):
    """
    仓库快照模型
    
    输出字段：
    - 仓库名称
    - 仓库路径
    - 文件列表
    - 目录列表
    - 元数据
    """
    repo_name: str = Field(..., description="仓库名称")
    repo_path: str = Field(..., description="仓库路径（绝对路径）")
    files: List[FileMetadata] = Field(default_factory=list, description="文件列表")
    directories: List[DirectoryMetadata] = Field(default_factory=list, description="目录列表")
    metadata: SnapshotMetadata = Field(..., description="元数据")
