"""
Markdown 文件写入器模块。

负责安全地将 Markdown 内容写入文件系统，包括：
- UTF-8 编码支持
- 自动覆盖已有文件
- 完善的异常处理
- 默认输出到仓库根目录的 PROJECT_ANALYSIS.md

本模块仅负责文件 I/O 操作，不包含业务逻辑。
"""

import os
from pathlib import Path
from typing import Optional
from loguru import logger


class MarkdownWriter:
    """
    Markdown 文件写入器类。

    提供安全的文件写入功能，确保生成的报告能够正确保存到目标位置。
    支持自定义输出路径，默认为仓库根目录下的 PROJECT_ANALYSIS.md。
    """

    # 默认输出文件名
    DEFAULT_FILENAME = "PROJECT_ANALYSIS.md"

    @staticmethod
    def write(
        content: str,
        output_path: Optional[Path] = None,
        repo_path: Optional[Path] = None,
    ) -> Path:
        """
        将 Markdown 内容写入文件。

        参数:
            content: Markdown 字符串内容。
            output_path: 可选的完整输出路径。如果提供，直接使用该路径。
            repo_path: 仓库根目录路径。当 output_path 未提供时使用。

        返回:
            实际写入的文件路径。

        异常:
            ValueError: 当 content 为空时抛出。
            IOError: 当文件写入失败时抛出。

        注意:
            - 优先使用 output_path，其次使用 repo_path + 默认文件名
            - 如果两者都未提供，使用当前工作目录
            - 自动创建不存在的父目录
            - 使用 UTF-8 编码写入
            - 自动覆盖已有文件
        """
        # 验证内容
        if not content:
            raise ValueError("无法写入空内容")

        # 确定输出路径
        if output_path:
            file_path = output_path
        elif repo_path:
            # 使用新的默认路径逻辑（reports/{repo_name}/PROJECT_ANALYSIS.md）
            file_path = MarkdownWriter.get_default_output_path(repo_path)
        else:
            # 默认使用当前工作目录
            file_path = Path.cwd() / MarkdownWriter.DEFAULT_FILENAME

        # 确保路径是 Path 对象
        if isinstance(file_path, str):
            file_path = Path(file_path)

        # 记录开始写入
        logger.info(f"开始写入报告文件: {file_path}")

        try:
            # 确保父目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # 写入文件（UTF-8 编码）
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # 记录成功
            file_size = len(content.encode('utf-8'))
            logger.success(f"报告文件写入成功: {file_path} ({file_size / 1024:.1f} KB)")

            return file_path

        except PermissionError as e:
            logger.error(f"文件写入权限不足: {file_path}")
            raise IOError(f"无法写入文件（权限不足）: {file_path}") from e

        except OSError as e:
            logger.error(f"文件写入失败: {file_path}, 错误: {e}")
            raise IOError(f"文件写入失败: {file_path}") from e

        except Exception as e:
            logger.error(f"未知错误导致文件写入失败: {e}")
            raise IOError(f"文件写入失败: {str(e)}") from e

    @staticmethod
    def validate_output_path(path: Path) -> bool:
        """
        验证输出路径是否合法。

        参数:
            path: 待验证的文件路径。

        返回:
            True 如果路径合法，False 否则。

        注意:
            - 检查路径是否为目录
            - 检查路径是否在允许的范围内（防止路径遍历攻击）
            - 检查父目录是否可写
        """
        # 检查是否为绝对路径
        if not path.is_absolute():
            logger.warning(f"输出路径不是绝对路径: {path}")

        # 检查父目录是否存在或可创建
        parent_dir = path.parent
        try:
            parent_dir.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError):
            logger.error(f"无法创建父目录: {parent_dir}")
            return False

        # 检查父目录是否可写
        if not os.access(str(parent_dir), os.W_OK):
            logger.error(f"父目录不可写: {parent_dir}")
            return False

        return True

    @staticmethod
    def get_default_output_path(repo_path: Optional[Path] = None) -> Path:
        """
        获取默认的输出文件路径。

        参数:
            repo_path: 仓库根目录路径。如果未提供，使用当前工作目录。

        返回:
            默认的完整文件路径（项目根目录/reports/{repo_name}/PROJECT_ANALYSIS.md）。
        """
        if repo_path:
            # 从 repo_path 提取仓库名称
            repo_name = repo_path.name
            
            # 获取项目根目录（ai-github-analyzer 目录）
            # repo_path 可能是 temp_repos/{repo_name}，需要向上找到项目根目录
            project_root = MarkdownWriter._find_project_root(repo_path)
            
            # 构建报告路径：项目根目录/reports/{repo_name}/PROJECT_ANALYSIS.md
            report_dir = project_root / "reports" / repo_name
            return report_dir / MarkdownWriter.DEFAULT_FILENAME
        else:
            return Path.cwd() / MarkdownWriter.DEFAULT_FILENAME
    
    @staticmethod
    def _find_project_root(current_path: Path) -> Path:
        """
        查找项目根目录（包含 ai-github-analyzer 目录的父目录）。
        
        参数:
            current_path: 当前路径（可能是 temp_repos/{repo_name}）
            
        返回:
            项目根目录路径
        """
        # 从当前路径向上查找，直到找到包含 'ai-github-analyzer' 的目录
        path = current_path
        max_levels = 10  # 防止无限循环
        
        for _ in range(max_levels):
            if path.name == 'ai-github-analyzer':
                return path
            parent = path.parent
            if parent == path:  # 到达根目录
                break
            path = parent
        
        # 如果没找到，返回当前路径的父目录（保守策略）
        logger.warning(f"未能找到项目根目录，使用当前路径的父目录: {current_path.parent}")
        return current_path.parent
