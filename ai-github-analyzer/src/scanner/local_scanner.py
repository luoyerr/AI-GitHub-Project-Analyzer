"""
本地路径扫描器

职责：
- 校验本地路径是否合法
- 验证路径是否存在
- 提供中文错误提示
"""

from pathlib import Path
from loguru import logger


class LocalScanner:
    """本地路径扫描器。"""
    
    @staticmethod
    def validate_path(path_str: str) -> Path:
        """
        验证本地路径
        
        Args:
            path_str: 路径字符串
            
        Returns:
            Path: 验证后的路径对象
            
        Raises:
            ValueError: 路径不合法或不存在
        """
        try:
            path = Path(path_str).resolve()
            
            # 检查路径是否存在
            if not path.exists():
                error_msg = f"错误：路径不存在 - {path_str}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # 检查是否是目录
            if not path.is_dir():
                error_msg = f"错误：路径不是目录 - {path_str}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"本地路径验证通过：{path}")
            return path
            
        except ValueError:
            raise
        except Exception as e:
            error_msg = f"错误：无效的路径 - {path_str}（{str(e)}）"
            logger.error(error_msg)
            raise ValueError(error_msg)
