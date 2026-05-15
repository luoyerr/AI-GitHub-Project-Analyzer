"""
任务注册中心。

统一管理所有AI分析任务的注册和获取，避免if-else地狱。
使用字典映射任务名称到任务实例，支持动态扩展。
"""

from typing import Dict, Type
from loguru import logger

from .tasks.base import BaseTask
from .tasks.tech_stack_task import TechStackTask
from .tasks.directory_task import DirectoryTask
from .tasks.core_modules_task import CoreModulesTask
from .tasks.startup_task import StartupTask
from .tasks.config_task import ConfigTask
from .tasks.risks_task import RisksTask
from .tasks.architecture_task import ArchitectureTask
from .tasks.learning_path_task import LearningPathTask


# 任务注册表：任务名称 -> 任务类
TASK_REGISTRY: Dict[str, Type[BaseTask]] = {
    "tech_stack": TechStackTask,
    "directory_structure": DirectoryTask,
    "core_modules": CoreModulesTask,
    "startup_flow": StartupTask,
    "config_analysis": ConfigTask,
    "risks": RisksTask,
    "architecture_diagram": ArchitectureTask,
    "learning_path": LearningPathTask,
}


class TaskRegistry:
    """
    任务注册中心。
    
    职责：
    - 管理所有可用任务的注册
    - 根据任务名称获取任务实例
    - 支持动态注册新任务
    - 提供任务列表查询
    
    设计原则：
    - 单一职责：只负责任务的注册和获取
    - 开闭原则：可以扩展新任务而不修改现有代码
    - 依赖倒置：依赖于抽象（BaseTask）而非具体实现
    """
    
    def __init__(self) -> None:
        """初始化任务注册中心。"""
        self._registry: Dict[str, Type[BaseTask]] = TASK_REGISTRY.copy()
        logger.info(f"任务注册中心初始化完成，已注册 {len(self._registry)} 个任务")
    
    def get_task(self, task_name: str) -> BaseTask:
        """
        根据任务名称获取任务实例。
        
        Args:
            task_name: 任务名称
            
        Returns:
            BaseTask: 任务实例
            
        Raises:
            ValueError: 当任务名称不存在时
        """
        if task_name not in self._registry:
            error_msg = f"未找到任务: {task_name}，可用任务: {list(self._registry.keys())}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        task_class = self._registry[task_name]
        task_instance = task_class()
        logger.debug(f"获取任务实例: {task_name} -> {task_class.__name__}")
        return task_instance
    
    def get_all_tasks(self) -> Dict[str, Type[BaseTask]]:
        """
        获取所有已注册的任务。
        
        Returns:
            Dict[str, Type[BaseTask]]: 任务名称到任务类的映射
        """
        return self._registry.copy()
    
    def get_task_names(self) -> list:
        """
        获取所有已注册任务的名称列表。
        
        Returns:
            list: 任务名称列表
        """
        return list(self._registry.keys())
    
    def register_task(self, task_name: str, task_class: Type[BaseTask]) -> None:
        """
        动态注册新任务。
        
        Args:
            task_name: 任务名称
            task_class: 任务类（必须是BaseTask的子类）
            
        Raises:
            TypeError: 当task_class不是BaseTask的子类时
            ValueError: 当任务名称已存在时
        """
        if not issubclass(task_class, BaseTask):
            error_msg = f"任务类必须是BaseTask的子类: {task_class}"
            logger.error(error_msg)
            raise TypeError(error_msg)
        
        if task_name in self._registry:
            error_msg = f"任务名称已存在: {task_name}"
            logger.warning(error_msg)
            raise ValueError(error_msg)
        
        self._registry[task_name] = task_class
        logger.info(f"动态注册新任务: {task_name} -> {task_class.__name__}")
    
    def unregister_task(self, task_name: str) -> None:
        """
        注销任务。
        
        Args:
            task_name: 要注销的任务名称
            
        Raises:
            ValueError: 当任务名称不存在时
        """
        if task_name not in self._registry:
            error_msg = f"任务名称不存在: {task_name}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        del self._registry[task_name]
        logger.info(f"注销任务: {task_name}")
    
    def has_task(self, task_name: str) -> bool:
        """
        检查任务是否已注册。
        
        Args:
            task_name: 任务名称
            
        Returns:
            bool: 任务是否已注册
        """
        return task_name in self._registry
