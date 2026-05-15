"""
模型模块 - 用于模块间通信的 Pydantic 数据模型。

包含 AI 上下文、Prompt 结果和分析结果的统一数据契约。
"""

from .base_models import (
    AnalysisStatus,
    RepositoryInfo,
    AnalysisConfig,
    BaseAnalysisResult,
    ScanResult,
    ClassificationResult,
)
from .tech_stack import ProjectTechStack
from .ai_context import (
    AIContext,
    ContextChunk,
    DirectoryContext,
    FileContext,
    SelectedFileContext,
    TechStackContext,
)
from .prompt_result import PromptResult, TokenUsage
from .llm_response import LLMResponse
from .task_context import TaskContext
from .analysis_result import (
    AnalysisResult,
    ArchitectureDiagram,
    ConfigAnalysis,
    ConfigFileInfo,
    CoreModuleAnalysis,
    CoreModuleInfo,
    DirectoryStructureAnalysis,
    LearningPath,
    LearningPathStep,
    ModuleRelationship,
    RiskAnalysis,
    RiskItem,
    StartupFlowAnalysis,
    TechStackAnalysis,
    ValidationIssue,
)

__all__ = [
    # 基础模型
    "AnalysisStatus",
    "RepositoryInfo",
    "AnalysisConfig",
    "BaseAnalysisResult",
    "ScanResult",
    "ClassificationResult",
    "ProjectTechStack",
    # AI 上下文模型
    "AIContext",
    "FileContext",
    "DirectoryContext",
    "TechStackContext",
    "SelectedFileContext",
    "ContextChunk",
    # Prompt 结果模型
    "PromptResult",
    "TokenUsage",
    "LLMResponse",
    # 任务上下文模型
    "TaskContext",
    # 分析结果模型
    "AnalysisResult",
    "TechStackAnalysis",
    "DirectoryStructureAnalysis",
    "CoreModuleAnalysis",
    "CoreModuleInfo",
    "ModuleRelationship",
    "StartupFlowAnalysis",
    "ConfigAnalysis",
    "ConfigFileInfo",
    "RiskAnalysis",
    "RiskItem",
    "ArchitectureDiagram",
    "LearningPath",
    "LearningPathStep",
    "ValidationIssue",
]
