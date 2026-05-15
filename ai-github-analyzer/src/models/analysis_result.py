"""
AI 分析结果模型。

定义 AI 分析引擎输出的结构化结果模型。
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AnalysisSection(str, Enum):
    """分析章节类型枚举。"""
    TECH_STACK = "tech_stack"
    DIRECTORY_STRUCTURE = "directory_structure"
    CORE_MODULES = "core_modules"
    STARTUP_FLOW = "startup_flow"
    CONFIG_ANALYSIS = "config_analysis"
    RISKS = "risks"
    ARCHITECTURE_DIAGRAM = "architecture_diagram"
    LEARNING_PATH = "learning_path"


class SectionResult(BaseModel):
    """单个分析章节的结果。"""
    section: AnalysisSection
    content: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    retry_count: int = 0


class TechStackAnalysis(BaseModel):
    """技术栈分析结果。"""
    languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    build_tools: List[str] = Field(default_factory=list)
    deployment_tools: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    evidence_files: List[str] = Field(default_factory=list)


class DirectoryStructureAnalysis(BaseModel):
    """目录结构分析结果。"""
    root_directories: Dict[str, str] = Field(default_factory=dict)
    key_files: Dict[str, str] = Field(default_factory=dict)
    architecture_pattern: Optional[str] = None
    description: str = ""


class CoreModuleAnalysis(BaseModel):
    """核心模块分析结果。"""
    modules: List[Dict[str, str]] = Field(default_factory=list)
    relationships: List[Dict[str, str]] = Field(default_factory=list)
    entry_points: List[str] = Field(default_factory=list)


class StartupFlowAnalysis(BaseModel):
    """启动流程分析结果。"""
    environment_setup: List[str] = Field(default_factory=list)
    installation_steps: List[str] = Field(default_factory=list)
    startup_commands: List[str] = Field(default_factory=list)
    build_commands: List[str] = Field(default_factory=list)
    database_init: Optional[str] = None


class ConfigAnalysis(BaseModel):
    """配置分析结果。"""
    config_files: List[str] = Field(default_factory=list)
    environment_variables: List[str] = Field(default_factory=list)
    key_configurations: Dict[str, Any] = Field(default_factory=dict)


class RiskItem(BaseModel):
    """风险项。"""
    category: str
    severity: str  # low, medium, high, critical
    description: str
    location: Optional[str] = None
    recommendation: Optional[str] = None


class RiskAnalysis(BaseModel):
    """风险分析结果。"""
    risks: List[RiskItem] = Field(default_factory=list)
    summary: str = ""


class ArchitectureDiagram(BaseModel):
    """架构图分析结果。"""
    mermaid_code: str = ""
    description: str = ""
    components: List[str] = Field(default_factory=list)


class LearningPath(BaseModel):
    """学习路径分析结果。"""
    recommended_order: List[str] = Field(default_factory=list)
    priority_modules: List[str] = Field(default_factory=list)
    learning_steps: List[str] = Field(default_factory=list)
    estimated_time: Optional[str] = None


class CompleteAnalysisResult(BaseModel):
    """完整分析结果。"""
    repository_url: str
    repository_name: str
    analysis_timestamp: datetime = Field(default_factory=datetime.now)
    
    tech_stack: Optional[TechStackAnalysis] = None
    directory_structure: Optional[DirectoryStructureAnalysis] = None
    core_modules: Optional[CoreModuleAnalysis] = None
    startup_flow: Optional[StartupFlowAnalysis] = None
    config_analysis: Optional[ConfigAnalysis] = None
    risks: Optional[RiskAnalysis] = None
    architecture_diagram: Optional[ArchitectureDiagram] = None
    learning_path: Optional[LearningPath] = None
    
    overall_status: str = "pending"  # pending, running, completed, failed, partial
    sections_completed: List[str] = Field(default_factory=list)
    sections_failed: List[str] = Field(default_factory=list)
    total_execution_time_ms: Optional[int] = None
    error_summary: Optional[str] = None
