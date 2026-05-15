"""
最终分析报告模型。

定义 AI 分析引擎输出的完整结构化报告，包含 8 个必需章节、
质量评分、验证状态和 LLM 调用统计。强类型设计，避免 dict 地狱。
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class TechStackAnalysis(BaseModel):
    """技术栈分析结果。"""

    languages: List[str] = Field(default_factory=list, description="编程语言列表")
    frameworks: List[str] = Field(default_factory=list, description="框架列表")
    dependencies: List[str] = Field(default_factory=list, description="核心依赖列表")
    build_tools: List[str] = Field(default_factory=list, description="构建工具列表")
    deployment_tools: List[str] = Field(default_factory=list, description="部署工具列表")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="识别置信度")
    evidence_files: List[str] = Field(default_factory=list, description="证据文件列表")


class DirectoryStructureAnalysis(BaseModel):
    """目录结构分析结果。"""

    root_directories: Dict[str, str] = Field(
        default_factory=dict, description="根目录说明（目录名 -> 职责描述）"
    )
    key_files: Dict[str, str] = Field(
        default_factory=dict, description="关键文件说明（文件路径 -> 职责描述）"
    )
    architecture_pattern: Optional[str] = Field(default=None, description="架构模式")
    description: str = Field(description="目录结构整体说明")


class CoreModuleInfo(BaseModel):
    """核心模块信息。"""

    name: str = Field(description="模块名称")
    path: str = Field(description="模块路径")
    responsibility: str = Field(description="模块职责")
    key_classes: List[str] = Field(default_factory=list, description="关键类或函数列表")


class ModuleRelationship(BaseModel):
    """模块间关系。"""

    source: str = Field(description="源模块")
    target: str = Field(description="目标模块")
    relationship_type: str = Field(description="关系类型（depends/calls/imports等）")
    description: Optional[str] = Field(default=None, description="关系说明")


class CoreModuleAnalysis(BaseModel):
    """核心模块分析结果。"""

    modules: List[CoreModuleInfo] = Field(default_factory=list, description="核心模块列表")
    relationships: List[ModuleRelationship] = Field(
        default_factory=list, description="模块间关系列表"
    )
    entry_points: List[str] = Field(default_factory=list, description="入口点列表")


class StartupFlowAnalysis(BaseModel):
    """启动流程分析结果。"""

    environment_setup: List[str] = Field(default_factory=list, description="环境准备步骤")
    installation_steps: List[str] = Field(default_factory=list, description="安装依赖步骤")
    startup_commands: List[str] = Field(default_factory=list, description="启动命令列表")
    build_commands: List[str] = Field(default_factory=list, description="构建命令列表")
    database_init: Optional[str] = Field(default=None, description="数据库初始化说明")


class ConfigFileInfo(BaseModel):
    """配置文件信息。"""

    file_path: str = Field(description="配置文件路径")
    format_type: str = Field(description="配置格式（yaml/json/env/properties等）")
    purpose: str = Field(description="配置用途")
    key_settings: List[str] = Field(default_factory=list, description="关键配置项列表")


class ConfigAnalysis(BaseModel):
    """配置分析结果。"""

    config_files: List[ConfigFileInfo] = Field(default_factory=list, description="配置文件列表")
    environment_variables: List[str] = Field(default_factory=list, description="环境变量列表")
    key_configurations: Dict[str, Any] = Field(
        default_factory=dict, description="关键配置摘要"
    )


class RiskItem(BaseModel):
    """风险项。"""

    category: str = Field(description="风险类别（安全/性能/可维护性/扩展性/技术债）")
    severity: str = Field(description="严重程度（low/medium/high/critical）")
    description: str = Field(description="风险描述")
    location: Optional[str] = Field(default=None, description="风险位置（文件路径或模块）")
    recommendation: Optional[str] = Field(default=None, description="修复建议")


class RiskAnalysis(BaseModel):
    """风险分析结果。"""

    risks: List[RiskItem] = Field(default_factory=list, description="风险项列表")
    summary: str = Field(description="风险总体摘要")


class ArchitectureDiagram(BaseModel):
    """架构图分析结果。"""

    mermaid_code: str = Field(description="Mermaid 架构图代码")
    description: str = Field(description="架构图说明")
    components: List[str] = Field(default_factory=list, description="组件列表")


class LearningPathStep(BaseModel):
    """学习路径步骤。"""

    step_number: int = Field(ge=1, description="步骤序号")
    title: str = Field(description="步骤标题")
    description: str = Field(description="步骤说明")
    recommended_files: List[str] = Field(
        default_factory=list, description="推荐阅读文件列表"
    )
    estimated_time: Optional[str] = Field(default=None, description="预计耗时")


class LearningPath(BaseModel):
    """学习路径分析结果。"""

    recommended_order: List[str] = Field(
        default_factory=list, description="建议阅读顺序（模块或文件）"
    )
    priority_modules: List[str] = Field(default_factory=list, description="优先学习模块")
    learning_steps: List[LearningPathStep] = Field(
        default_factory=list, description="详细学习步骤"
    )
    estimated_total_time: Optional[str] = Field(default=None, description="总预计耗时")


class ValidationIssue(BaseModel):
    """验证问题。"""

    issue_type: str = Field(description="问题类型（missing/inconsistent/invalid等）")
    severity: str = Field(description="严重程度（warning/error）")
    description: str = Field(description="问题描述")
    affected_section: Optional[str] = Field(default=None, description="影响的章节")


class AnalysisResult(BaseModel):
    """
    最终分析报告模型。

    完整的 AI 分析结果，包含 8 个必需章节（技术栈、目录结构、核心模块、
    启动流程、配置分析、风险、架构图、学习路径），以及质量评分、
    验证状态和 LLM 调用统计。强类型设计，支持 DAG 工作流输出。
    """

    repo_name: str = Field(description="仓库名称")
    analysis_time: datetime = Field(default_factory=datetime.now, description="分析完成时间")

    # 8 个必需章节（缺一不可）
    tech_stack: Optional[TechStackAnalysis] = Field(
        default=None, description="技术栈分析结果"
    )
    directory_structure: Optional[DirectoryStructureAnalysis] = Field(
        default=None, description="目录结构分析结果"
    )
    core_modules: Optional[CoreModuleAnalysis] = Field(
        default=None, description="核心模块分析结果"
    )
    startup_flow: Optional[StartupFlowAnalysis] = Field(
        default=None, description="启动流程分析结果"
    )
    config_analysis: Optional[ConfigAnalysis] = Field(
        default=None, description="配置分析结果"
    )
    risks: Optional[RiskAnalysis] = Field(default=None, description="风险分析结果")
    architecture_diagram: Optional[ArchitectureDiagram] = Field(
        default=None, description="架构图分析结果"
    )
    learning_path: Optional[LearningPath] = Field(default=None, description="学习路径分析结果")

    # 质量评估
    quality_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="整体质量评分（0-1）"
    )
    validation_passed: bool = Field(default=False, description="是否通过验证")
    issues: List[ValidationIssue] = Field(default_factory=list, description="验证问题列表")

    # LLM 调用统计
    llm_provider: Optional[str] = Field(default=None, description="LLM 提供商")
    elapsed_time: float = Field(default=0.0, ge=0.0, description="总执行耗时（秒）")
    token_usage: Dict[str, int] = Field(
        default_factory=dict, description="Token 使用统计（prompt/completion/total）"
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="扩展元数据（支持未来字段扩展）"
    )
