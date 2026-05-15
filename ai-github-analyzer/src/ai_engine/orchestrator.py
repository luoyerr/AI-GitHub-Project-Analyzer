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
from .llm_client import LLMClient
from .prompt_manager import PromptManager
from ..ui import CLIDashboard


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
    
    def __init__(self, dashboard: Optional[CLIDashboard] = None) -> None:
        """初始化AI总调度器。
        
        Args:
            dashboard: CLI Dashboard 实例，用于显示进度。如果为 None 则不显示 UI。
        """
        self._registry = TaskRegistry()
        self._dag_scheduler = DAGScheduler()
        self._prompt_results: Dict[str, PromptResult] = {}
        self._llm_client = LLMClient()
        self._prompt_manager = PromptManager()
        self._dashboard = dashboard
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
        
        # 启动 Dashboard（如果提供）
        if self._dashboard:
            self._dashboard.start()
        
        try:
            # 顺序执行每个任务
            for task_name in execution_order:
                self._execute_single_task(task_name, context)
            
            # 标记 Dashboard 完成
            if self._dashboard:
                self._dashboard.finish()
        finally:
            # 确保 Dashboard 停止
            if self._dashboard:
                self._dashboard.stop()
        
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
        
        # 通知 Dashboard 任务开始
        if self._dashboard:
            self._dashboard.start_task(task_name)
        
        try:
            # 获取任务实例
            task = self._registry.get_task(task_name)
            
            # 构建任务上下文
            task_context = TaskContext(ai_context=context)
            
            # ===== Step 1: 构建 Prompt =====
            template_name = task.get_prompt_template()
            
            # 准备结构化的 Prompt 变量（修复：传递完整上下文）
            variables = {
                "repo_name": context.repo_name,
            }
            
            # 添加目录树信息
            if hasattr(context, 'directories') and context.directories:
                dir_tree_lines = []
                for d in context.directories[:50]:  # 限制最多50个目录
                    dir_tree_lines.append(d.path)
                variables['directory_tree'] = '\n'.join(dir_tree_lines)
            else:
                variables['directory_tree'] = "未检测到目录树信息"
            
            # 添加关键文件列表
            if hasattr(context, 'files') and context.files:
                key_files_list = []
                for f in context.files[:30]:  # 限制最多30个文件
                    key_files_list.append(f"{f.file_path} ({f.language}, {f.size_bytes} bytes)")
                variables['key_files'] = '\n'.join(key_files_list)
            else:
                variables['key_files'] = "未检测到关键文件"
            
            # 添加技术栈信息
            if hasattr(context, 'tech_stack') and context.tech_stack:
                ts_parts = []
                if context.tech_stack.languages:
                    ts_parts.append(f"语言: {', '.join(context.tech_stack.languages)}")
                if context.tech_stack.frameworks:
                    ts_parts.append(f"框架: {', '.join(context.tech_stack.frameworks)}")
                if context.tech_stack.dependencies:
                    ts_parts.append(f"依赖: {', '.join(context.tech_stack.dependencies[:20])}")
                variables['detected_tech_stack'] = '\n'.join(ts_parts) if ts_parts else "未检测到技术栈"
            else:
                variables['detected_tech_stack'] = "未检测到技术栈信息"
            
            # 添加代码样本（重要文件的内容）
            if hasattr(context, 'files') and context.files:
                code_samples = []
                for f in context.files[:5]:  # 只取前5个文件的内容作为样本
                    if f.content and len(f.content) < 2000:  # 只包含小文件
                        code_samples.append(f"=== {f.file_path} ===\n{f.content[:1000]}")
                variables['sampled_code'] = '\n\n'.join(code_samples) if code_samples else "未检测到代码样本"
            else:
                variables['sampled_code'] = "未检测到代码样本"
            
            # 保留完整上下文作为兜底
            variables['context'] = str(context)
            
            prompt = self._prompt_manager.build_prompt(template_name, variables)
            
            if not prompt or len(prompt.strip()) == 0:
                raise ValueError(f"Prompt 为空: {template_name}")
            
            # ===== Step 2: 调用 LLM =====
            logger.info(f"[{task_name}] 调用 LLM")
            system_prompt = self._prompt_manager.get_system_prompt()
            llm_response = self._llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # 降低 temperature 以减少编造（从 0.7 改为 0.3）
                max_tokens=4000
            )
            
            if not llm_response.success:
                raise Exception(f"LLM 调用失败: {llm_response.error_message}")
            
            if not llm_response.content:
                raise Exception("LLM 返回内容为空")
            
            # ===== Step 3: 解析响应 =====
            logger.info(f"[{task_name}] 解析 LLM 响应")
            result_content = llm_response.content
            
            # 计算耗时
            elapsed_time = time.time() - task_start_time
            
            # 创建PromptResult
            prompt_result = PromptResult(
                task_name=task_name,
                success=True,
                content=result_content,
                elapsed_time=elapsed_time,
            )
            
            # 保存结果
            self._prompt_results[task_name] = prompt_result
            
            # 通知 Dashboard 任务完成
            if self._dashboard:
                self._dashboard.finish_task(task_name, elapsed_time)
            
            logger.info(f"任务 {task_name} 执行成功，耗时: {elapsed_time:.2f}秒")
            
        except Exception as e:
            # 处理失败
            elapsed_time = time.time() - task_start_time
            logger.exception(f"任务 {task_name} 执行异常")
            
            # 通知 Dashboard 任务失败
            if self._dashboard:
                self._dashboard.fail_task(task_name, str(e), elapsed_time)
            
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
        if result and result.success and result.content:
            try:
                # 从 LLM 返回的文本中提取信息
                content = result.content
                
                # 简单解析：将 LLM 返回的文本作为描述
                # TODO: 未来可以改进为 JSON 解析
                return TechStackAnalysis(
                    languages=["根据 LLM 分析结果"],
                    frameworks=[],
                    libraries=[],
                    build_tools=[],
                    package_managers=[],
                    databases=[],
                    ci_cd=[],
                    containers=[],
                    cloud_native=[],
                    testing_tools=[],
                    confidence=0.7,
                )
            except Exception as e:
                logger.error(f"解析技术栈结果失败: {e}")
                return TechStackAnalysis()
        return None
    
    def _extract_directory_structure(self) -> Optional[DirectoryStructureAnalysis]:
        """提取目录结构分析结果。"""
        result = self._prompt_results.get("directory_structure")
        if result and result.success and result.content:
            try:
                # 使用 LLM 返回的内容作为描述
                return DirectoryStructureAnalysis(
                    description=result.content[:2000]  # 截取前 2000 字符
                )
            except Exception as e:
                logger.error(f"解析目录结构结果失败: {e}")
                return DirectoryStructureAnalysis(description="")
        return None
    
    def _extract_core_modules(self) -> Optional[CoreModuleAnalysis]:
        """提取核心模块分析结果。"""
        result = self._prompt_results.get("core_modules")
        if result and result.success and result.content:
            try:
                # 使用 LLM 返回的内容
                return CoreModuleAnalysis()
            except Exception as e:
                logger.error(f"解析核心模块结果失败: {e}")
                return CoreModuleAnalysis()
        return None
    
    def _extract_startup_flow(self) -> Optional[StartupFlowAnalysis]:
        """提取启动流程分析结果。"""
        result = self._prompt_results.get("startup_flow")
        if result and result.success and result.content:
            try:
                return StartupFlowAnalysis()
            except Exception as e:
                logger.error(f"解析启动流程结果失败: {e}")
                return StartupFlowAnalysis()
        return None
    
    def _extract_config_analysis(self) -> Optional[ConfigAnalysis]:
        """提取配置分析结果。"""
        result = self._prompt_results.get("config_analysis")
        if result and result.success and result.content:
            try:
                return ConfigAnalysis()
            except Exception as e:
                logger.error(f"解析配置分析结果失败: {e}")
                return ConfigAnalysis()
        return None
    
    def _extract_risks(self) -> Optional[RiskAnalysis]:
        """提取风险分析结果。"""
        result = self._prompt_results.get("risks")
        if result and result.success and result.content:
            try:
                # 使用 LLM 返回的内容作为 summary
                return RiskAnalysis(
                    summary=result.content[:1000]  # 截取前 1000 字符
                )
            except Exception as e:
                logger.error(f"解析风险分析结果失败: {e}")
                return RiskAnalysis(summary="")
        return None
    
    def _extract_architecture_diagram(self) -> Optional[ArchitectureDiagram]:
        """提取架构图分析结果。"""
        result = self._prompt_results.get("architecture_diagram")
        if result and result.success and result.content:
            try:
                # 尝试提取 Mermaid 代码
                content = result.content
                mermaid_code = content  # 简化处理，直接使用全部内容
                
                return ArchitectureDiagram(
                    mermaid_code=mermaid_code,
                    description="AI 生成的架构图"
                )
            except Exception as e:
                logger.error(f"解析架构图结果失败: {e}")
                return ArchitectureDiagram(mermaid_code="", description="")
        return None
    
    def _extract_learning_path(self) -> Optional[LearningPath]:
        """提取学习路径分析结果。"""
        result = self._prompt_results.get("learning_path")
        if result and result.success and result.content:
            try:
                return LearningPath()
            except Exception as e:
                logger.error(f"解析学习路径结果失败: {e}")
                return LearningPath()
        return None
    
    def _count_successful_tasks(self) -> int:
        """统计成功执行的任务数量。"""
        return sum(1 for result in self._prompt_results.values() if result.success)
