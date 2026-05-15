"""
AI 总调度器（AI Orchestrator）。

统一调度8个AI Task Executor，顺序执行并收集结果，最终聚合为AnalysisResult。
遵循Harness Engineering架构，支持失败继续、日志记录和高扩展性。
"""

import time
from typing import Dict, Optional
from datetime import datetime
from loguru import logger

from ..models import AIContext, TaskContext, PromptResult
from ..models.analysis_result import (
    AnalysisResult,
    TechStackAnalysis,
    DirectoryStructureAnalysis,
    CoreModuleAnalysis,
    StartupFlowAnalysis,
    ConfigAnalysis,
    RiskAnalysis,
    ArchitectureDiagram,
    LearningPath,
)
from .registry import TaskRegistry
from .dag import DAGScheduler


class AIOrchestrator:
    """
    AI 总调度器。
    
    职责：
    - 统一调度8个AI Task Executor
    - 顺序执行任务并收集PromptResult
    - 处理单个任务失败（记录日志，不中断流程）
    - 最终聚合所有结果为AnalysisResult
    
    执行顺序：
    1. tech_stack
    2. directory_structure
    3. core_modules
    4. startup_flow
    5. config_analysis
    6. risks
    7. architecture_diagram
    8. learning_path
    
    设计原则：
    - 简单优先：当前串行执行，无并行、无retry、无复杂DAG
    - 失败继续：单任务失败不中断整个流程
    - 可观测：完整记录开始、成功、失败、耗时
    - 高扩展：兼容未来的retry、parallel、DAG、缓存
    """
    
    def __init__(self) -> None:
        """初始化AI总调度器。"""
        self._registry = TaskRegistry()
        self._dag_scheduler = DAGScheduler()
        self._prompt_results: Dict[str, PromptResult] = {}
        logger.info("AI总调度器初始化完成")
    
    def run(self, context: AIContext) -> AnalysisResult:
        """
        执行完整的AI分析流程。
        
        Args:
            context: AI分析上下文
            
        Returns:
            AnalysisResult: 完整的分析结果
        """
        start_time = time.time()
        logger.info(f"开始执行AI分析流程，仓库: {context.repo_name}")
        
        # 清空之前的结果
        self._prompt_results.clear()
        
        # 获取执行顺序
        execution_order = self._dag_scheduler.get_execution_order()
        logger.info(f"任务执行顺序: {execution_order}")
        
        # 顺序执行每个任务
        for task_name in execution_order:
            self._execute_single_task(task_name, context)
        
        # 聚合结果
        elapsed_time = time.time() - start_time
        result = self._build_analysis_result(context.repo_name, elapsed_time)
        
        logger.info(f"AI分析流程完成，总耗时: {elapsed_time:.2f}秒")
        return result
    
    def _execute_single_task(self, task_name: str, context: AIContext) -> None:
        """
        执行单个任务。
        
        Args:
            task_name: 任务名称
            context: AI分析上下文
        """
        task_start_time = time.time()
        logger.info(f"开始执行任务: {task_name}")
        
        try:
            # 获取任务实例
            task = self._registry.get_task(task_name)
            
            # 构建任务上下文
            task_context = TaskContext(ai_context=context)
            
            # 执行任务
            result = task.execute(task_context)
            
            # 计算耗时
            elapsed_time = time.time() - task_start_time
            
            # 创建PromptResult（这里简化处理，实际应该从LLM调用中获取）
            prompt_result = PromptResult(
                task_name=task_name,
                success=True,
                content=str(result) if result else "",
                elapsed_time=elapsed_time,
            )
            
            # 保存结果
            self._prompt_results[task_name] = prompt_result
            
            logger.info(f"任务 {task_name} 执行成功，耗时: {elapsed_time:.2f}秒")
            
        except Exception as e:
            # 处理失败
            elapsed_time = time.time() - task_start_time
            self._handle_failure(task_name, e, elapsed_time)
    
    def _handle_failure(self, task_name: str, error: Exception, elapsed_time: float) -> None:
        """
        处理任务失败。
        
        策略：失败继续，记录日志，写入分析失败标记，不中断整个流程。
        
        Args:
            task_name: 任务名称
            error: 发生的异常
            elapsed_time: 执行耗时
        """
        error_msg = f"任务 {task_name} 执行失败: {str(error)}"
        logger.error(error_msg)
        
        # 创建失败的PromptResult
        prompt_result = PromptResult(
            task_name=task_name,
            success=False,
            error_message=error_msg,
            elapsed_time=elapsed_time,
        )
        
        # 保存失败结果
        self._prompt_results[task_name] = prompt_result
        
        logger.warning(f"任务 {task_name} 失败已记录，继续执行后续任务")
    
    def _build_analysis_result(self, repo_name: str, elapsed_time: float) -> AnalysisResult:
        """
        构建最终的分析结果。
        
        把8个PromptResult转换为AnalysisResult，进行字段映射。
        
        Args:
            repo_name: 仓库名称
            elapsed_time: 总执行耗时
            
        Returns:
            AnalysisResult: 完整的分析结果
        """
        logger.info("开始构建最终分析结果")
        
        # 从PromptResult中提取各个分析结果
        # 注意：这里需要根据实际的PromptResult.content进行解析
        # 当前简化处理，直接映射
        
        analysis_result = AnalysisResult(
            repo_name=repo_name,
            analysis_time=datetime.now(),
            tech_stack=self._extract_tech_stack(),
            directory_structure=self._extract_directory_structure(),
            core_modules=self._extract_core_modules(),
            startup_flow=self._extract_startup_flow(),
            config_analysis=self._extract_config_analysis(),
            risks=self._extract_risks(),
            architecture_diagram=self._extract_architecture_diagram(),
            learning_path=self._extract_learning_path(),
            elapsed_time=elapsed_time,
        )
        
        logger.info(f"分析结果构建完成，包含 {self._count_successful_tasks()} 个成功任务")
        return analysis_result
    
    def _extract_tech_stack(self) -> Optional[TechStackAnalysis]:
        """提取技术栈分析结果。"""
        result = self._prompt_results.get("tech_stack")
        if result and result.success:
            # TODO: 从result.content解析TechStackAnalysis
            return TechStackAnalysis()
        return None
    
    def _extract_directory_structure(self) -> Optional[DirectoryStructureAnalysis]:
        """提取目录结构分析结果。"""
        result = self._prompt_results.get("directory_structure")
        if result and result.success:
            # TODO: 从result.content解析DirectoryStructureAnalysis
            return DirectoryStructureAnalysis(description="")
        return None
    
    def _extract_core_modules(self) -> Optional[CoreModuleAnalysis]:
        """提取核心模块分析结果。"""
        result = self._prompt_results.get("core_modules")
        if result and result.success:
            # TODO: 从result.content解析CoreModuleAnalysis
            return CoreModuleAnalysis()
        return None
    
    def _extract_startup_flow(self) -> Optional[StartupFlowAnalysis]:
        """提取启动流程分析结果。"""
        result = self._prompt_results.get("startup_flow")
        if result and result.success:
            # TODO: 从result.content解析StartupFlowAnalysis
            return StartupFlowAnalysis()
        return None
    
    def _extract_config_analysis(self) -> Optional[ConfigAnalysis]:
        """提取配置分析结果。"""
        result = self._prompt_results.get("config_analysis")
        if result and result.success:
            # TODO: 从result.content解析ConfigAnalysis
            return ConfigAnalysis()
        return None
    
    def _extract_risks(self) -> Optional[RiskAnalysis]:
        """提取风险分析结果。"""
        result = self._prompt_results.get("risks")
        if result and result.success:
            # TODO: 从result.content解析RiskAnalysis
            return RiskAnalysis(summary="")
        return None
    
    def _extract_architecture_diagram(self) -> Optional[ArchitectureDiagram]:
        """提取架构图分析结果。"""
        result = self._prompt_results.get("architecture_diagram")
        if result and result.success:
            # TODO: 从result.content解析ArchitectureDiagram
            return ArchitectureDiagram(mermaid_code="", description="")
        return None
    
    def _extract_learning_path(self) -> Optional[LearningPath]:
        """提取学习路径分析结果。"""
        result = self._prompt_results.get("learning_path")
        if result and result.success:
            # TODO: 从result.content解析LearningPath
            return LearningPath()
        return None
    
    def _count_successful_tasks(self) -> int:
        """统计成功执行的任务数量。"""
        return sum(1 for result in self._prompt_results.values() if result.success)
