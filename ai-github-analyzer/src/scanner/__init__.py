"""
扫描器模块 - Phase 1: Repository Scanner

职责：
- 扫描本地路径或 GitHub 仓库
- 生成 RepositorySnapshot
- 支持文件限制和自动清理

禁止：
- AI 推断
- 读取文件内容
- 技术栈分析
"""

from .models import RepositorySnapshot, FileMetadata, DirectoryMetadata, SnapshotMetadata
from .repo_resolver import RepoResolver
from .local_scanner import LocalScanner
from .github_cloner import GitHubCloner
from .file_scanner import FileScanner
from .repo_cache_manager import RepoCacheManager

__all__ = [
    'RepositorySnapshot',
    'FileMetadata',
    'DirectoryMetadata',
    'SnapshotMetadata',
    'RepoResolver',
    'LocalScanner',
    'GitHubCloner',
    'FileScanner',
    'RepoCacheManager',
]
