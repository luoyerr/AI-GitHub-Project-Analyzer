"""
GitHub URL 克隆器

职责：
- 支持 GitHub 仓库 URL
- 自动执行 git clone --depth 1（浅克隆）
- clone timeout: 60 秒
- 失败时自动 cleanup
- 项目内临时目录管理（temp_repos/）
"""

import asyncio
import gc
import time
import shutil
from pathlib import Path
from typing import Optional
from loguru import logger


class GitHubCloner:
    """GitHub 仓库克隆器。"""
    
    CLONE_TIMEOUT = 60  # 克隆超时时间（秒）
    MAX_CLEANUP_RETRIES = 3  # 最大清理重试次数
    CLEANUP_RETRY_DELAYS = [1, 2, 3]  # 指数退避延迟（秒）
    
    def __init__(self):
        """初始化克隆器。"""
        self.temp_dir: Optional[Path] = None
        self._repo_name: Optional[str] = None  # 记录仓库名称用于安全检查
    
    async def clone(self, repo_url: str) -> Path:
        """
        克隆 GitHub 仓库
        
        Args:
            repo_url: GitHub 仓库 URL
            
        Returns:
            Path: 克隆后的本地路径
            
        Raises:
            RuntimeError: 克隆失败
        """
        logger.info(f"开始克隆仓库：{repo_url}")
        
        try:
            # 提取仓库名称
            self._repo_name = self._extract_repo_name(repo_url)
            
            # 创建项目内临时目录：temp_repos/<repo_name>
            project_root = Path(__file__).parent.parent.parent  # ai-github-analyzer/
            temp_repos_dir = project_root / "temp_repos"
            
            # 确保 temp_repos 目录存在
            temp_repos_dir.mkdir(parents=True, exist_ok=True)
            logger.debug(f"使用临时目录：{temp_repos_dir}")
            
            # 目标路径：temp_repos/<repo_name>
            self.temp_dir = temp_repos_dir / self._repo_name
            
            # 如果目录已存在，先清理（避免冲突）
            if self.temp_dir.exists():
                logger.warning(f"检测到已存在的目录，先清理：{self.temp_dir}")
                await self._force_cleanup(self.temp_dir)
            
            # 执行 git clone --depth 1
            await self._execute_clone(repo_url, self.temp_dir)
            
            logger.info(f"克隆成功：{self.temp_dir}")
            return self.temp_dir
            
        except Exception as e:
            logger.error(f"克隆失败：{e}")
            # 失败时自动清理
            await self.cleanup()
            raise RuntimeError(f"克隆仓库失败：{str(e)}")
    
    async def _execute_clone(self, repo_url: str, target_path: Path):
        """
        执行 git clone 命令
        
        Args:
            repo_url: 仓库 URL
            target_path: 目标路径
        """
        cmd = [
            "git", "clone",
            "--depth", "1",
            repo_url,
            str(target_path)
        ]
        
        logger.debug(f"执行命令：{' '.join(cmd)}")
        
        process = None
        try:
            # 使用 asyncio.create_subprocess_exec 执行命令
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # 等待完成，带超时
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.CLONE_TIMEOUT
                )
                
                if process.returncode != 0:
                    error_msg = stderr.decode('utf-8', errors='ignore').strip()
                    raise RuntimeError(f"Git 克隆失败：{error_msg}")
                
                logger.debug(f"克隆输出：{stdout.decode('utf-8', errors='ignore')}")
                
            except asyncio.TimeoutError:
                # 超时后终止进程
                if process:
                    process.kill()
                    await process.wait()
                raise RuntimeError(f"克隆超时（{self.CLONE_TIMEOUT}秒）")
                
        except FileNotFoundError:
            raise RuntimeError("未找到 git 命令，请确保已安装 Git")
        except Exception as e:
            raise RuntimeError(f"执行克隆命令失败：{str(e)}")
        finally:
            # 确保进程资源释放
            if process and process.returncode is None:
                try:
                    process.kill()
                    await process.wait()
                except Exception:
                    pass
    
    @staticmethod
    def _extract_repo_name(repo_url: str) -> str:
        """
        从 URL 提取仓库名称
        
        Args:
            repo_url: GitHub 仓库 URL
            
        Returns:
            str: 仓库名称
        """
        # 移除 .git 后缀
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        
        # 提取最后一部分作为仓库名
        repo_name = repo_url.rstrip('/').split('/')[-1]
        
        return repo_name
    
    async def cleanup(self):
        """
        清理临时目录
        
        采用指数退避重试机制，确保 Windows 下文件句柄完全释放。
        """
        if not self.temp_dir or not self.temp_dir.exists():
            logger.debug("无需清理临时目录")
            return
        
        # 路径安全检查：确保只删除当前克隆的仓库目录
        if not self._validate_cleanup_path(self.temp_dir):
            logger.error(f"路径安全检查失败，拒绝删除：{self.temp_dir}")
            return
        
        logger.info(f"开始清理临时目录：{self.temp_dir}")
        
        # 指数退避重试
        for attempt in range(self.MAX_CLEANUP_RETRIES):
            try:
                # 强制垃圾回收，释放可能的文件句柄
                gc.collect()
                
                # 小延迟，等待文件系统操作完成
                await asyncio.sleep(0.5)
                
                # 执行删除
                await self._force_cleanup(self.temp_dir)
                
                logger.info(f"✓ 已清理临时目录：{self.temp_dir}")
                self.temp_dir = None
                self._repo_name = None
                return
                
            except PermissionError as e:
                delay = self.CLEANUP_RETRY_DELAYS[attempt] if attempt < len(self.CLEANUP_RETRY_DELAYS) else 3
                if attempt < self.MAX_CLEANUP_RETRIES - 1:
                    logger.warning(
                        f"清理失败（尝试 {attempt + 1}/{self.MAX_CLEANUP_RETRIES}），"
                        f"{delay}秒后重试：{e}"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"⚠ 清理失败（已重试 {self.MAX_CLEANUP_RETRIES} 次），"
                        f"请手动删除目录：{self.temp_dir}\n"
                        f"错误信息：{e}"
                    )
                    # 不抛出异常，不影响主流程
                    
            except Exception as e:
                logger.error(f"清理临时目录时发生未知错误：{e}")
                break
    
    async def _force_cleanup(self, target_path: Path):
        """
        强制删除目录（处理 Windows 文件锁问题）
        
        Args:
            target_path: 要删除的目标路径
        """
        try:
            # 使用 to_thread 在后台线程执行阻塞操作
            await asyncio.to_thread(shutil.rmtree, target_path, onerror=self._remove_readonly)
        except Exception as e:
            raise
    
    @staticmethod
    def _remove_readonly(func, path, excinfo):
        """
        处理只读文件的删除回调（Windows 兼容）
        
        Args:
            func: 失败的函数
            path: 文件路径
            excinfo: 异常信息
        """
        import stat
        import os
        
        # 检查是否是权限问题
        if not os.access(path, os.W_OK):
            # 赋予写权限后重试
            os.chmod(path, stat.S_IWUSR | stat.S_IRUSR)
            func(path)
    
    def _validate_cleanup_path(self, path: Path) -> bool:
        """
        路径安全检查：确保只删除预期的临时仓库目录
        
        Args:
            path: 待删除的路径
            
        Returns:
            bool: 是否安全
        """
        # 必须包含 temp_repos 目录
        if "temp_repos" not in path.parts:
            logger.error(f"路径不包含 temp_repos，拒绝删除：{path}")
            return False
        
        # 必须是 temp_repos 的直接子目录
        temp_repos_idx = path.parts.index("temp_repos")
        if len(path.parts) != temp_repos_idx + 2:
            logger.error(f"路径层级不正确，拒绝删除：{path}")
            return False
        
        # 必须有记录的仓库名称
        if self._repo_name and path.name != self._repo_name:
            logger.error(f"仓库名称不匹配，拒绝删除：{path.name} != {self._repo_name}")
            return False
        
        return True
