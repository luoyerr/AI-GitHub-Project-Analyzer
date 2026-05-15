"""
任务模块。

定义所有 AI 分析任务的基类和具体实现。
"""

from .base import BaseTask
from .tech_stack_task import TechStackTask
from .directory_task import DirectoryTask
from .core_modules_task import CoreModulesTask
from .startup_task import StartupTask
from .config_task import ConfigTask
from .risks_task import RisksTask
from .architecture_task import ArchitectureTask
from .learning_path_task import LearningPathTask

__all__ = [
    "BaseTask",
    "TechStackTask",
    "DirectoryTask",
    "CoreModulesTask",
    "StartupTask",
    "ConfigTask",
    "RisksTask",
    "ArchitectureTask",
    "LearningPathTask",
]
