"""
仓库缓存管理器 - Repository Cache Manager

职责：
- 管理 GitHub 仓库的本地缓存
- 支持四种模式：keep / delete / reuse / ask
- 自动检测已有仓库并复用
- 使用 git pull 更新已有仓库（而非重新 clone）
"""

import os
import asyncio
from pathlib import Path
from typing import Optional, Literal
from loguru import logger
from rich.console import Console


class RepoCacheManager:
    """仓库缓存管理器。"""
    
    # 缓存模式类型
    CacheMode = Literal["keep", "delete", "reuse", "ask"]
    
    def __init__(self, console: Optional[Console] = None):
        """
        初始化缓存管理器
        
        Args:
            console: Rich 控制台实例（用于用户交互）
        """
        self.console = console or Console()
        self.mode = self._load_mode_from_env()
        logger.info(f"仓库缓存模式：{self.mode}")
    
    def _load_mode_from_env(self) -> CacheMode:
        """
        从环境变量加载缓存模式
        
        Returns:
            CacheMode: 缓存模式
        """
        mode = os.getenv("REPO_CLEANUP_MODE", "reuse").lower()
        
        valid_modes = ["keep", "delete", "reuse", "ask"]
        if mode not in valid_modes:
            logger.warning(f"无效的缓存模式 '{mode}'，使用默认值 'reuse'")
            mode = "reuse"
        
        return mode  # type: ignore
    
    async def get_repo_path(
        self, 
        repo_url: str, 
        temp_repos_dir: Optional[Path] = None
    ) -> tuple[Path, bool]:
        """
        获取仓库路径（可能复用缓存或克隆新仓库）
        
        Args:
            repo_url: GitHub 仓库 URL
            temp_repos_dir: 临时仓库目录（默认：项目根目录/temp_repos）
            
        Returns:
            tuple[Path, bool]: (仓库路径, 是否为新克隆)
        """
        # 提取仓库名称
        repo_name = self._extract_repo_name(repo_url)
        
        # 确定临时仓库目录
        if temp_repos_dir is None:
            project_root = Path(__file__).parent.parent.parent  # ai-github-analyzer/
            temp_repos_dir = project_root / "temp_repos"
        
        # 确保目录存在
        temp_repos_dir.mkdir(parents=True, exist_ok=True)
        
        # 目标路径
        repo_path = temp_repos_dir / repo_name
        
        # 根据模式处理
        if self.mode == "ask":
            actual_mode = await self._ask_user_mode()
        else:
            actual_mode = self.mode
        
        if actual_mode in ["reuse", "keep"]:
            # 检查是否已存在
            if repo_path.exists():
                logger.info(f"检测到本地仓库缓存：{repo_name}")
                self.console.print(f"\n[bold green]✓[/bold green] 检测到本地仓库缓存")
                self.console.print(f"  仓库: [cyan]{repo_name}[/cyan]")
                self.console.print(f"  路径: [dim]{repo_path}[/dim]")
                
                # 尝试更新（git pull）
                updated = await self._update_existing_repo(repo_path, repo_url)
                if updated:
                    self.console.print(f"  [green]正在同步最新代码... 更新完成[/green]\n")
                else:
                    self.console.print(f"  [yellow]跳过更新（保持当前版本）[/yellow]\n")
                
                return repo_path, False  # 不是新克隆
            else:
                # 不存在，需要克隆
                logger.info(f"缓存不存在，将克隆新仓库：{repo_name}")
                self.console.print(f"\n[yellow]⚠ 缓存不存在，将克隆新仓库[/yellow]\n")
                return repo_path, True  # 需要新克隆
        
        elif actual_mode == "delete":
            # 删除模式：总是克隆新的
            logger.info(f"删除模式：将克隆新仓库")
            return repo_path, True
        
        else:
            raise ValueError(f"未知的缓存模式：{actual_mode}")
    
    async def should_cleanup(self) -> bool:
        """
        判断是否应该清理仓库
        
        Returns:
            bool: 是否应该清理
        """
        if self.mode == "ask":
            actual_mode = await self._ask_user_mode()
        else:
            actual_mode = self.mode
        
        return actual_mode == "delete"
    
    async def _ask_user_mode(self) -> CacheMode:
        """
        运行时询问用户选择模式
        
        Returns:
            CacheMode: 用户选择的模式
        """
        self.console.print("\n[bold yellow]请选择仓库处理模式：[/bold yellow]")
        self.console.print("  [1] 保留本地仓库（推荐）")
        self.console.print("  [2] 分析完成自动删除")
        self.console.print("  [3] 如果已存在则复用\n")
        
        try:
            # 在异步环境中获取输入
            choice = await asyncio.to_thread(input, "请输入 (默认 3): ")
            choice = choice.strip() or "3"
            
            if choice == "1":
                return "keep"
            elif choice == "2":
                return "delete"
            else:
                return "reuse"
        
        except Exception as e:
            logger.warning(f"读取用户输入失败，使用默认模式 'reuse'：{e}")
            return "reuse"
    
    async def _update_existing_repo(self, repo_path: Path, repo_url: str) -> bool:
        """
        更新已有仓库（git pull）
        
        Args:
            repo_path: 仓库路径
            repo_url: 仓库 URL
            
        Returns:
            bool: 是否成功更新
        """
        try:
            logger.debug(f"正在更新仓库：{repo_path}")
            
            # 执行 git pull
            cmd = ["git", "-C", str(repo_path), "pull"]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=60  # pull 超时 60 秒
            )
            
            if process.returncode == 0:
                logger.info(f"仓库更新成功：{repo_path}")
                return True
            else:
                error_msg = stderr.decode('utf-8', errors='ignore').strip()
                logger.warning(f"仓库更新失败（将继续使用当前版本）：{error_msg}")
                return False
        
        except asyncio.TimeoutError:
            logger.warning(f"仓库更新超时（将继续使用当前版本）")
            return False
        
        except Exception as e:
            logger.warning(f"仓库更新异常（将继续使用当前版本）：{e}")
            return False
    
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
    
    def cleanup(self, repo_path: Path) -> bool:
        """
        清理指定仓库（仅在 delete 模式下调用）
        
        Args:
            repo_path: 要清理的仓库路径
            
        Returns:
            bool: 是否成功清理
        """
        import shutil
        import gc
        
        if not repo_path.exists():
            logger.debug(f"无需清理，路径不存在：{repo_path}")
            return True
        
        # 路径安全检查
        if "temp_repos" not in repo_path.parts:
            logger.error(f"路径安全检查失败，拒绝删除：{repo_path}")
            return False
        
        try:
            logger.info(f"开始清理仓库：{repo_path}")
            
            # 强制垃圾回收
            gc.collect()
            
            # 删除目录
            shutil.rmtree(repo_path, onerror=self._remove_readonly)
            
            logger.info(f"✓ 已清理仓库：{repo_path}")
            return True
        
        except Exception as e:
            logger.error(f"清理仓库失败：{e}")
            return False
    
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
