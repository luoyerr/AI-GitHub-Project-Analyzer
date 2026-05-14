"""
文件扫描器 - 扫描仓库文件和目录

职责：
- 扫描全部文件和目录
- 记录相对路径、文件大小、后缀名
- 支持文件数量限制（最多500个）
- 按优先级截断

禁止：
- 读取文件内容
"""

import asyncio
from pathlib import Path
from typing import List, Tuple
from loguru import logger

from .models import FileMetadata, DirectoryMetadata, RepositorySnapshot, SnapshotMetadata


# 文件类型优先级（从高到低）
FILE_PRIORITY = {
    'config': ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.env.example'],
    'entry': ['main.py', 'app.py', 'index.js', 'server.js', '__init__.py'],
    'source': ['.py', '.js', '.ts', '.java', '.go', '.rs', '.cpp', '.c', '.h'],
    'doc': ['.md', '.rst', '.txt', '.doc'],
    'test': ['.test.py', '.spec.js', '_test.go', 'test_*.py'],
}

MAX_FILES = 500  # 最大文件数量限制


class FileScanner:
    """文件扫描器。"""
    
    def __init__(self, repo_path: Path):
        """
        初始化文件扫描器
        
        Args:
            repo_path: 仓库根路径
        """
        self.repo_path = repo_path
        self.files: List[FileMetadata] = []
        self.directories: List[DirectoryMetadata] = []
    
    async def scan(self) -> RepositorySnapshot:
        """
        执行扫描
        
        Returns:
            RepositorySnapshot: 仓库快照（包含完整未裁剪的数据）
        """
        logger.info(f"开始扫描仓库：{self.repo_path}")
        
        # 异步扫描文件和目录
        await self._scan_recursive()
        
        # 检查是否需要截断（仅记录标志，不实际裁剪）
        truncated = len(self.files) > MAX_FILES
        
        if truncated:
            logger.warning(f"文件数量超过限制（{len(self.files)} > {MAX_FILES}）")
        
        # 推测语言（基于完整文件列表）
        inferred_languages = self._infer_languages()
        
        # 构建快照（使用完整未裁剪的数据）
        # 注意：RepositorySnapshot 包含所有文件和目录
        # 裁剪逻辑应该在 Context Builder 层进行，而不是在 Scanner 层
        snapshot = RepositorySnapshot(
            repo_name=self.repo_path.name,
            repo_path=str(self.repo_path.absolute()),
            files=self.files,  # 完整文件列表
            directories=self.directories,  # 完整目录列表
            metadata=SnapshotMetadata(
                file_count=len(self.files),
                directory_count=len(self.directories),
                inferred_languages=inferred_languages,
                truncated=truncated
            )
        )
        
        logger.info(
            f"扫描完成：{len(self.files)} 个文件，"
            f"{len(self.directories)} 个目录，"
            f"截断标志={truncated}"
        )
        
        return snapshot
    
    async def _scan_recursive(self):
        """递归扫描仓库。"""
        try:
            # 使用 asyncio 并发扫描
            tasks = []
            
            for item in self.repo_path.iterdir():
                # 跳过特定的隐藏文件和目录（.git, .env, .secret 等敏感文件）
                if item.name in ['.git', '.env', '.secret']:
                    continue
                
                if item.is_file():
                    tasks.append(self._scan_file(item))
                elif item.is_dir():
                    tasks.append(self._scan_directory(item))
            
            if tasks:
                await asyncio.gather(*tasks)
                
        except Exception as e:
            logger.error(f"扫描失败：{e}")
            raise
    
    async def _scan_file(self, file_path: Path):
        """
        扫描单个文件
        
        Args:
            file_path: 文件路径
        """
        try:
            relative_path = str(file_path.relative_to(self.repo_path))
            size_bytes = file_path.stat().st_size
            extension = file_path.suffix.lower() if file_path.suffix else ''
            
            file_meta = FileMetadata(
                relative_path=relative_path,
                size_bytes=size_bytes,
                extension=extension
            )
            
            self.files.append(file_meta)
            
        except Exception as e:
            logger.warning(f"无法扫描文件 {file_path}：{e}")
    
    async def _scan_directory(self, dir_path: Path):
        """
        扫描目录（递归）
        
        Args:
            dir_path: 目录路径
        """
        try:
            relative_path = str(dir_path.relative_to(self.repo_path))
            
            dir_meta = DirectoryMetadata(relative_path=relative_path)
            self.directories.append(dir_meta)
            
            # 递归扫描子目录
            for item in dir_path.iterdir():
                # 跳过特定的隐藏文件和目录（.git, .env, .secret 等敏感文件）
                if item.name in ['.git', '.env', '.secret']:
                    continue
                
                if item.is_file():
                    await self._scan_file(item)
                elif item.is_dir():
                    await self._scan_directory(item)
                    
        except Exception as e:
            logger.warning(f"无法扫描目录 {dir_path}：{e}")
    
    def _apply_file_limit(self) -> bool:
        """
        应用文件数量限制
        
        Returns:
            bool: 是否被截断
        """
        if len(self.files) <= MAX_FILES:
            return False
        
        logger.warning(f"文件数量超过限制（{len(self.files)} > {MAX_FILES}），按优先级截断")
        
        # 按优先级排序
        prioritized_files = self._prioritize_files()
        
        # 截断
        self.files = prioritized_files[:MAX_FILES]
        
        return True
    
    def _prioritize_files(self) -> List[FileMetadata]:
        """
        按优先级排序文件
        
        Returns:
            List[FileMetadata]: 排序后的文件列表
        """
        def get_priority_score(file_meta: FileMetadata) -> int:
            """获取文件优先级分数（越低越优先）。"""
            path_lower = file_meta.relative_path.lower()
            ext = file_meta.extension
            
            # 配置文件优先级最高
            for priority_level, extensions in FILE_PRIORITY.items():
                for ext_pattern in extensions:
                    if ext == ext_pattern or path_lower.endswith(ext_pattern):
                        priority_map = {
                            'config': 0,
                            'entry': 1,
                            'source': 2,
                            'doc': 3,
                            'test': 4,
                        }
                        return priority_map.get(priority_level, 5)
            
            # 默认优先级
            return 5
        
        # 排序
        sorted_files = sorted(self.files, key=get_priority_score)
        
        return sorted_files
    
    def _infer_languages(self) -> List[str]:
        """
        根据文件后缀推测编程语言
        
        Returns:
            List[str]: 推测的语言列表
        """
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.cs': 'C#',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.r': 'R',
            '.sql': 'SQL',
            '.sh': 'Shell',
            '.html': 'HTML',
            '.css': 'CSS',
        }
        
        # 统计语言出现次数
        language_count = {}
        for file_meta in self.files:
            ext = file_meta.extension
            if ext in language_map:
                lang = language_map[ext]
                language_count[lang] = language_count.get(lang, 0) + 1
        
        # 按出现次数排序
        sorted_languages = sorted(
            language_count.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [lang for lang, count in sorted_languages]
