"""
模型模块 - 用于模块间通信的 Pydantic 数据模型。
"""

from .base_models import (
    AnalysisStatus,
    RepositoryInfo,
    AnalysisConfig,
    AnalysisResult,
    ScanResult,
    ClassificationResult,
)
from .tech_stack import ProjectTechStack
from .analysis_result import (
    AnalysisSection,
    SectionResult,
    TechStackAnalysis,
    DirectoryStructureAnalysis,
    CoreModuleAnalysis,
    StartupFlowAnalysis,
    ConfigAnalysis,
    RiskItem,
    RiskAnalysis,
    ArchitectureDiagram,
    LearningPath,
    CompleteAnalysisResult,
)
from .ai_context import (
    FileContext,
    RepositoryContext,
    TaskContext,
    ContextBudget,
    AIContext,
)
from .prompt_result import (
    PromptMetrics,
    ValidationResult,
    PromptResult,
    PromptTemplate,
    PromptExecutionConfig,
)

__all__ = [
    "AnalysisStatus",
    "RepositoryInfo",
    "AnalysisConfig",
    "AnalysisResult",
    "ScanResult",
    "ClassificationResult",
    "ProjectTechStack",
    # 分析结果模型
    "AnalysisSection",
    "SectionResult",
    "TechStackAnalysis",
    "DirectoryStructureAnalysis",
    "CoreModuleAnalysis",
    "StartupFlowAnalysis",
    "ConfigAnalysis",
    "RiskItem",
    "RiskAnalysis",
    "ArchitectureDiagram",
    "LearningPath",
    "CompleteAnalysisResult",
    # AI 上下文模型
    "FileContext",
    "RepositoryContext",
    "TaskContext",
    "ContextBudget",
    "AIContext",
    # Prompt 结果模型
    "PromptMetrics",
    "ValidationResult",
    "PromptResult",
    "PromptTemplate",
    "PromptExecutionConfig",
]
