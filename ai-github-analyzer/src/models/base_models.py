"""
模块间通信的基础模型。
所有模块应使用这些模型进行数据交换。
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AnalysisStatus(str, Enum):
    """分析执行状态。"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RepositoryInfo(BaseModel):
    """仓库基本信息。"""
    url: str = ""
    name: str = "unknown"
    owner: str = "unknown"
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    last_updated: Optional[datetime] = None


class AnalysisConfig(BaseModel):
    """分析执行的配置。"""
    repo_url: str
    output_format: str = "markdown"
    include_tests: bool = True
    max_depth: int = 10
    timeout: int = 300


class BaseAnalysisResult(BaseModel):
    """基础分析结果结构（旧版，保留用于兼容）。"""
    repo_info: RepositoryInfo
    status: AnalysisStatus = AnalysisStatus.PENDING
    summary: Optional[str] = None
    tech_stack: List[str] = []
    architecture_patterns: List[str] = []
    quality_metrics: Dict[str, Any] = {}
    recommendations: List[str] = []
    generated_at: datetime = Field(default_factory=datetime.now)


class ScanResult(BaseModel):
    """扫描器模块的结果。"""
    file_tree: Dict[str, Any] = {}
    total_files: int = 0
    total_lines: int = 0
    languages: Dict[str, int] = {}
    dependencies: List[str] = []


class ClassificationResult(BaseModel):
    """分类器模块的结果。"""
    repo_type: str = "unknown"
    primary_language: str = "unknown"
    frameworks: List[str] = []
    patterns: List[str] = []
    confidence: float = 0.0
