"""
仓库解析器 - 统一入口

职责：
- 判断输入是本地路径还是 GitHub URL
- 调用相应的扫描器
- 管理生命周期（克隆、扫描、清理）
- 返回 RepositorySnapshot
"""

import asyncio
from pathlib import Path
from typing import Union
from loguru import logger

from .models import RepositorySnapshot
from .local_scanner import LocalScanner
from .github_cloner import GitHubCloner
from .file_scanner import FileScanner
from .repo_cache_manager import RepoCacheManager


class RepoResolver:
    """仓库解析器。"""
    
    def __init__(self):
        """初始化解析器。"""
        self.local_scanner = LocalScanner()
        self.github_cloner = GitHubCloner()
        self.cache_manager = RepoCacheManager()
        self.is_temp_clone = False  # 标记是否是临时克隆
    
    async def resolve(self, repo_input: str) -> RepositorySnapshot:
        """
        解析仓库并生成快照
        
        Args:
            repo_input: 仓库输入（本地路径或 GitHub URL）
            
        Returns:
            RepositorySnapshot: 仓库快照
            
        Raises:
            ValueError: 输入无效
            RuntimeError: 处理失败
        """
        logger.info(f"开始解析仓库：{repo_input}")
        
        try:
            # 判断输入类型
            if self._is_github_url(repo_input):
                # GitHub URL
                return await self._handle_github_url(repo_input)
            else:
                # 本地路径
                return await self._handle_local_path(repo_input)
                
        except Exception as e:
            logger.error(f"解析仓库失败：{e}")
            # 确保清理临时目录
            if self.is_temp_clone:
                await self.github_cloner.cleanup()
            raise
    
    def _is_github_url(self, input_str: str) -> bool:
        """
        判断是否是 GitHub URL
        
        Args:
            input_str: 输入字符串
            
        Returns:
            bool: 是否是 GitHub URL
        """
        return (
            input_str.startswith('https://github.com/') or
            input_str.startswith('http://github.com/') or
            input_str.startswith('git@github.com:')
        )
    
    async def _handle_local_path(self, path_str: str) -> RepositorySnapshot:
        """
        处理本地路径
        
        Args:
            path_str: 本地路径字符串
            
        Returns:
            RepositorySnapshot: 仓库快照
        """
        logger.info("处理本地路径")
        
        # 验证路径
        repo_path = self.local_scanner.validate_path(path_str)
        
        # 扫描文件
        file_scanner = FileScanner(repo_path)
        snapshot = await file_scanner.scan()
        
        return snapshot
    
    async def _handle_github_url(self, repo_url: str) -> RepositorySnapshot:
        """
        处理 GitHub URL
        
        Args:
            repo_url: GitHub 仓库 URL
            
        Returns:
            RepositorySnapshot: 仓库快照
        """
        logger.info("处理 GitHub URL")
        
        # 使用缓存管理器获取仓库路径
        cloned_path, is_new_clone = await self.github_cloner.clone(repo_url)
        self.is_temp_clone = True
        
        try:
            # 扫描文件
            file_scanner = FileScanner(cloned_path)
            snapshot = await file_scanner.scan()
            
            return snapshot
            
        except Exception:
            # 如果扫描失败，也要清理临时目录
            logger.info("开始清理临时克隆目录")
            await self.github_cloner.cleanup()
            self.is_temp_clone = False
            raise
