"""
任务依赖定义。

定义各个分析任务之间的依赖关系，用于后续实现真正的DAG调度和并行执行。
当前阶段仅用于记录依赖关系，为未来扩展做准备。
"""

from typing import Dict, List, Set
from loguru import logger


# 任务依赖关系：任务名称 -> 依赖的任务名称列表
TASK_DEPENDENCIES: Dict[str, List[str]] = {
    # 技术栈分析：无依赖，可以第一个执行
    "tech_stack": [],
    
    # 目录结构分析：无依赖，可以并行执行
    "directory_structure": [],
    
    # 核心模块分析：依赖目录结构（需要了解目录组织）
    "core_modules": ["directory_structure"],
    
    # 启动流程分析：依赖技术栈和核心模块
    "startup_flow": ["tech_stack", "core_modules"],
    
    # 配置分析：依赖技术栈（了解框架后更好理解配置）
    "config_analysis": ["tech_stack"],
    
    # 风险分析：依赖技术栈和核心模块
    "risks": ["tech_stack", "core_modules"],
    
    # 架构图：依赖核心模块和目录结构
    "architecture_diagram": ["core_modules", "directory_structure"],
    
    # 学习路径：依赖技术栈、核心模块和启动流程
    "learning_path": ["tech_stack", "core_modules", "startup_flow"],
}


class TaskDependencyManager:
    """
    任务依赖管理器。
    
    职责：
    - 管理任务间的依赖关系
    - 计算任务的执行顺序（拓扑排序）
    - 检测循环依赖
    - 获取任务的直接和间接依赖
    
    设计原则：
    - 单一职责：只负责依赖关系管理
    - 可扩展：支持动态添加/修改依赖
    - 可观测：提供依赖查询和验证功能
    """
    
    def __init__(self) -> None:
        """初始化任务依赖管理器。"""
        self._dependencies: Dict[str, List[str]] = TASK_DEPENDENCIES.copy()
        logger.info(f"任务依赖管理器初始化完成，管理 {len(self._dependencies)} 个任务的依赖关系")
    
    def get_dependencies(self, task_name: str) -> List[str]:
        """
        获取任务的直接依赖。
        
        Args:
            task_name: 任务名称
            
        Returns:
            List[str]: 依赖的任务名称列表
        """
        deps = self._dependencies.get(task_name, [])
        logger.debug(f"任务 {task_name} 的直接依赖: {deps}")
        return deps.copy()
    
    def get_all_dependencies(self, task_name: str) -> Set[str]:
        """
        获取任务的所有依赖（包括间接依赖）。
        
        Args:
            task_name: 任务名称
            
        Returns:
            Set[str]: 所有依赖的任务名称集合
        """
        all_deps: Set[str] = set()
        self._collect_dependencies(task_name, all_deps)
        logger.debug(f"任务 {task_name} 的所有依赖: {all_deps}")
        return all_deps
    
    def _collect_dependencies(self, task_name: str, collected: Set[str]) -> None:
        """
        递归收集所有依赖。
        
        Args:
            task_name: 当前任务名称
            collected: 已收集的依赖集合
        """
        direct_deps = self._dependencies.get(task_name, [])
        for dep in direct_deps:
            if dep not in collected:
                collected.add(dep)
                self._collect_dependencies(dep, collected)
    
    def get_execution_order(self) -> List[str]:
        """
        根据依赖关系计算任务的执行顺序（拓扑排序）。
        
        Returns:
            List[str]: 任务的执行顺序列表
            
        Raises:
            ValueError: 当存在循环依赖时
        """
        # 使用Kahn算法进行拓扑排序
        in_degree: Dict[str, int] = {task: 0 for task in self._dependencies}
        
        # 计算每个节点的入度
        for task, deps in self._dependencies.items():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] = in_degree.get(dep, 0) + 1
        
        # 找出所有入度为0的节点
        queue: List[str] = [task for task, degree in in_degree.items() if degree == 0]
        execution_order: List[str] = []
        
        while queue:
            # 按字母顺序排序以确保确定性
            queue.sort()
            current = queue.pop(0)
            execution_order.append(current)
            
            # 减少依赖于当前节点的其他节点的入度
            for task, deps in self._dependencies.items():
                if current in deps:
                    in_degree[task] -= 1
                    if in_degree[task] == 0:
                        queue.append(task)
        
        # 检查是否有循环依赖
        if len(execution_order) != len(self._dependencies):
            error_msg = "检测到循环依赖，无法计算执行顺序"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"计算出的执行顺序: {execution_order}")
        return execution_order
    
    def has_circular_dependency(self) -> bool:
        """
        检测是否存在循环依赖。
        
        Returns:
            bool: 是否存在循环依赖
        """
        try:
            self.get_execution_order()
            return False
        except ValueError:
            return True
    
    def add_dependency(self, task_name: str, depends_on: List[str]) -> None:
        """
        添加或更新任务的依赖关系。
        
        Args:
            task_name: 任务名称
            depends_on: 依赖的任务名称列表
        """
        self._dependencies[task_name] = depends_on.copy()
        logger.info(f"更新任务 {task_name} 的依赖: {depends_on}")
    
    def remove_dependency(self, task_name: str) -> None:
        """
        移除任务的依赖关系。
        
        Args:
            task_name: 任务名称
        """
        if task_name in self._dependencies:
            del self._dependencies[task_name]
            logger.info(f"移除任务 {task_name} 的依赖关系")
    
    def get_dependents(self, task_name: str) -> List[str]:
        """
        获取依赖于指定任务的所有任务。
        
        Args:
            task_name: 任务名称
            
        Returns:
            List[str]: 依赖于该任务的任务列表
        """
        dependents = []
        for task, deps in self._dependencies.items():
            if task_name in deps:
                dependents.append(task)
        logger.debug(f"依赖于任务 {task_name} 的任务: {dependents}")
        return dependents
    
    def validate_dependencies(self) -> bool:
        """
        验证所有依赖关系是否有效（依赖的任务都存在）。
        
        Returns:
            bool: 依赖关系是否有效
        """
        all_tasks = set(self._dependencies.keys())
        invalid_deps = []
        
        for task, deps in self._dependencies.items():
            for dep in deps:
                if dep not in all_tasks:
                    invalid_deps.append((task, dep))
        
        if invalid_deps:
            error_msg = f"发现无效的依赖关系: {invalid_deps}"
            logger.error(error_msg)
            return False
        
        logger.info("所有依赖关系验证通过")
        return True
