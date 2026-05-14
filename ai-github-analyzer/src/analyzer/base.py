"""
基础分析器抽象类

职责：
定义所有分析器的通用接口和行为规范。

当前状态：
骨架阶段，仅包含抽象方法定义。

TODO:
1. 实现具体分析方法
2. 添加错误处理机制
3. 支持异步分析操作
"""

from abc import ABC, abstractmethod
from typing import Any


class BaseAnalyzer(ABC):
    """
    基础分析器抽象类
    
    所有具体的分析器都应继承此类并实现 analyze 方法。
    """
    
    @abstractmethod
    def analyze(self, scan_result: Any) -> Any:
        """
        执行分析操作
        
        Args:
            scan_result: 扫描结果数据
            
        Returns:
            分析结果
            
        Raises:
            NotImplementedError: 子类必须实现此方法
        """
        raise NotImplementedError("子类必须实现 analyze 方法")
