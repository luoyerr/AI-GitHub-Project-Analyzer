"""
任务进度管理器。

负责管理所有 AI 分析任务的状态、耗时和进度计算。
与 UI 层解耦，提供纯粹的数据接口。
"""

from enum import Enum
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime


class TaskStatus(Enum):
    """任务状态枚举。"""
    PENDING = "pending"      # 未开始
    RUNNING = "running"      # 执行中
    SUCCESS = "success"      # 成功
    FAILED = "failed"        # 失败


@dataclass
class TaskInfo:
    """单个任务的详细信息。"""
    name: str                          # 任务名称
    status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: float = 0.0             # 耗时（秒）
    error_message: Optional[str] = None
    
    @property
    def is_completed(self) -> bool:
        """是否已完成（成功或失败）。"""
        return self.status in (TaskStatus.SUCCESS, TaskStatus.FAILED)
    
    @property
    def display_duration(self) -> str:
        """格式化的耗时字符串。"""
        if self.duration > 0:
            return f"{self.duration:.1f}s"
        return ""


class ProgressManager:
    """
    任务进度管理器。
    
    职责：
    - 管理所有任务的状态
    - 计算整体进度百分比
    - 记录每个任务的耗时
    - 提供查询接口给 UI 层使用
    
    设计原则：
    - 纯数据管理，不包含任何 UI 逻辑
    - 线程安全（为未来并行执行预留）
    - 可观测性：随时可查询任意任务状态
    """
    
    def __init__(self, task_names: list[str]) -> None:
        """
        初始化进度管理器。
        
        Args:
            task_names: 所有任务名称列表（按执行顺序）
        """
        self._tasks: Dict[str, TaskInfo] = {
            name: TaskInfo(name=name) for name in task_names
        }
        self._task_order = task_names  # 保持任务顺序
        self._current_task: Optional[str] = None
        self._start_time: Optional[datetime] = None
    
    @property
    def total_tasks(self) -> int:
        """总任务数。"""
        return len(self._tasks)
    
    @property
    def completed_tasks(self) -> int:
        """已完成的任务数（包括成功和失败）。"""
        return sum(1 for task in self._tasks.values() if task.is_completed)
    
    @property
    def successful_tasks(self) -> int:
        """成功完成的任务数。"""
        return sum(1 for task in self._tasks.values() if task.status == TaskStatus.SUCCESS)
    
    @property
    def failed_tasks(self) -> int:
        """失败的任务数。"""
        return sum(1 for task in self._tasks.values() if task.status == TaskStatus.FAILED)
    
    @property
    def progress_percentage(self) -> float:
        """进度百分比（0-100）。"""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks / self.total_tasks) * 100
    
    @property
    def current_task_name(self) -> Optional[str]:
        """当前正在执行的任务名称。"""
        return self._current_task
    
    @property
    def elapsed_time(self) -> float:
        """从开始到现在的总耗时（秒）。"""
        if not self._start_time:
            return 0.0
        return (datetime.now() - self._start_time).total_seconds()
    
    def get_task_info(self, task_name: str) -> Optional[TaskInfo]:
        """
        获取指定任务的详细信息。
        
        Args:
            task_name: 任务名称
            
        Returns:
            TaskInfo 或 None（如果任务不存在）
        """
        return self._tasks.get(task_name)
    
    def get_all_tasks(self) -> Dict[str, TaskInfo]:
        """获取所有任务信息（按执行顺序）。"""
        return {name: self._tasks[name] for name in self._task_order}
    
    def start(self) -> None:
        """标记整个流程开始。"""
        self._start_time = datetime.now()
    
    def start_task(self, task_name: str) -> None:
        """
        标记任务开始执行。
        
        Args:
            task_name: 任务名称
        """
        if task_name not in self._tasks:
            raise ValueError(f"未知任务: {task_name}")
        
        self._current_task = task_name
        task = self._tasks[task_name]
        task.status = TaskStatus.RUNNING
        task.start_time = datetime.now()
    
    def finish_task(self, task_name: str, duration: float = 0.0) -> None:
        """
        标记任务成功完成。
        
        Args:
            task_name: 任务名称
            duration: 任务耗时（秒），如果为 0 则自动计算
        """
        if task_name not in self._tasks:
            raise ValueError(f"未知任务: {task_name}")
        
        task = self._tasks[task_name]
        task.status = TaskStatus.SUCCESS
        task.end_time = datetime.now()
        
        if duration > 0:
            task.duration = duration
        elif task.start_time:
            task.duration = (task.end_time - task.start_time).total_seconds()
        
        # 如果没有当前任务，清空
        if self._current_task == task_name:
            self._current_task = None
    
    def fail_task(self, task_name: str, error_message: str, duration: float = 0.0) -> None:
        """
        标记任务失败。
        
        Args:
            task_name: 任务名称
            error_message: 错误信息
            duration: 任务耗时（秒），如果为 0 则自动计算
        """
        if task_name not in self._tasks:
            raise ValueError(f"未知任务: {task_name}")
        
        task = self._tasks[task_name]
        task.status = TaskStatus.FAILED
        task.error_message = error_message
        task.end_time = datetime.now()
        
        if duration > 0:
            task.duration = duration
        elif task.start_time:
            task.duration = (task.end_time - task.start_time).total_seconds()
        
        # 如果没有当前任务，清空
        if self._current_task == task_name:
            self._current_task = None
    
    def finish(self) -> None:
        """标记整个流程结束。"""
        # 可以在这里做最终统计
        pass
