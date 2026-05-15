"""
UI 模块。

提供企业级 CLI Dashboard 功能，包括：
- CLIDashboard: Dashboard 主控制器
- ProgressManager: 任务进度管理器
- TerminalRenderer: 终端渲染器
"""

from .cli_dashboard import CLIDashboard
from .progress_manager import ProgressManager, TaskStatus, TaskInfo
from .terminal_renderer import TerminalRenderer

__all__ = [
    "CLIDashboard",
    "ProgressManager",
    "TaskStatus",
    "TaskInfo",
    "TerminalRenderer",
]
