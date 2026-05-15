"""
DAG（有向无环图）任务调度器。

实现基于静态任务顺序的DAG调度，为未来真正的并行DAG执行做准备。
当前阶段按预定义顺序串行执行任务。
"""

from typing import List
from loguru import logger

from .task_dependency import TaskDependencyManager


class DAGScheduler:
    """
    DAG调度器。
    
    职责：
    - 管理任务的执行顺序
    - 提供静态任务顺序（当前实现）
    - 为未来并行执行预留接口
    - 验证DAG的有效性
    
    设计原则：
    - 简单优先：当前使用静态顺序
    - 可扩展：预留并行执行接口
    - 可观测：记录执行顺序和状态
    """
    
    # 预定义的 task 执行顺序（按照架构设计要求）
    STATIC_EXECUTION_ORDER: List[str] = [
        "tech_stack",           # 1. 技术栈分析
        "directory_structure",  # 2. 目录结构分析
        "core_modules",         # 3. 核心模块分析
        "startup_flow",         # 4. 启动流程分析
        "config_analysis",      # 5. 配置分析
        "risks",                # 6. 风险分析
        "architecture_diagram", # 7. 架构图
        "learning_path",        # 8. 学习路径
    ]
    
    def __init__(self) -> None:
        """初始化DAG调度器。"""
        self._dependency_manager = TaskDependencyManager()
        self._execution_order: List[str] = self.STATIC_EXECUTION_ORDER.copy()
        logger.info(f"DAG调度器初始化完成，执行顺序: {self._execution_order}")
    
    def get_execution_order(self) -> List[str]:
        """
        获取任务执行顺序。
        
        当前返回静态顺序，未来可以根据依赖关系动态计算。
        
        Returns:
            List[str]: 任务执行顺序列表
        """
        logger.debug(f"获取执行顺序: {self._execution_order}")
        return self._execution_order.copy()
    
    def set_execution_order(self, order: List[str]) -> None:
        """
        设置自定义执行顺序。
        
        Args:
            order: 任务执行顺序列表
            
        Raises:
            ValueError: 当顺序无效时
        """
        if not order:
            error_msg = "执行顺序不能为空"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # 验证所有任务都在注册表中
        from .registry import TaskRegistry
        registry = TaskRegistry()
        registered_tasks = set(registry.get_task_names())
        
        for task in order:
            if task not in registered_tasks:
                error_msg = f"未知任务: {task}"
                logger.error(error_msg)
                raise ValueError(error_msg)
        
        self._execution_order = order.copy()
        logger.info(f"设置自定义执行顺序: {order}")
    
    def validate_dag(self) -> bool:
        """
        验证DAG的有效性（检查循环依赖）。
        
        Returns:
            bool: DAG是否有效
        """
        is_valid = not self._dependency_manager.has_circular_dependency()
        if is_valid:
            logger.info("DAG验证通过：无循环依赖")
        else:
            logger.error("DAG验证失败：存在循环依赖")
        return is_valid
    
    def get_next_tasks(self, completed_tasks: List[str]) -> List[str]:
        """
        获取下一个可以执行的任务列表。
        
        当前实现返回顺序中的下一个任务，未来可以支持并行任务组。
        
        Args:
            completed_tasks: 已完成的任务列表
            
        Returns:
            List[str]: 下一个可以执行的任务列表
        """
        completed_set = set(completed_tasks)
        next_tasks = []
        
        for task in self._execution_order:
            if task not in completed_set:
                # 检查该任务的所有依赖是否已完成
                deps = self._dependency_manager.get_dependencies(task)
                if all(dep in completed_set for dep in deps):
                    next_tasks.append(task)
                    break  # 当前只返回一个任务（串行执行）
        
        logger.debug(f"已完成: {completed_tasks}, 下一个任务: {next_tasks}")
        return next_tasks
    
    def get_parallel_groups(self) -> List[List[str]]:
        """
        获取可以并行执行的任务组。
        
        为未来并行执行预留，当前每个任务单独一组。
        
        Returns:
            List[List[str]]: 并行任务组列表
        """
        # 当前实现：每个任务单独一组（串行执行）
        parallel_groups = [[task] for task in self._execution_order]
        logger.debug(f"并行任务组（当前为串行）: {parallel_groups}")
        return parallel_groups
    
    def get_task_position(self, task_name: str) -> int:
        """
        获取任务在执行顺序中的位置。
        
        Args:
            task_name: 任务名称
            
        Returns:
            int: 任务位置索引（从0开始），未找到返回-1
        """
        try:
            position = self._execution_order.index(task_name)
            logger.debug(f"任务 {task_name} 的位置: {position}")
            return position
        except ValueError:
            logger.warning(f"任务 {task_name} 不在执行顺序中")
            return -1
    
    def reset(self) -> None:
        """重置调度器到初始状态。"""
        self._execution_order = self.STATIC_EXECUTION_ORDER.copy()
        logger.info("DAG调度器已重置")
