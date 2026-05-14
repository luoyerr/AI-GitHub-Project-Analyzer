"""
Base models for inter-module communication.
All modules should use these models to exchange data.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AnalysisStatus(str, Enum):
    """Analysis execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RepositoryInfo(BaseModel):
    """Basic repository information."""
    url: str = ""
    name: str = "unknown"
    owner: str = "unknown"
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    last_updated: Optional[datetime] = None


class AnalysisConfig(BaseModel):
    """Configuration for analysis execution."""
    repo_url: str
    output_format: str = "markdown"
    include_tests: bool = True
    max_depth: int = 10
    timeout: int = 300


class AnalysisResult(BaseModel):
    """Final analysis result structure."""
    repo_info: RepositoryInfo
    status: AnalysisStatus = AnalysisStatus.PENDING
    summary: Optional[str] = None
    tech_stack: List[str] = []
    architecture_patterns: List[str] = []
    quality_metrics: Dict[str, Any] = {}
    recommendations: List[str] = []
    generated_at: datetime = Field(default_factory=datetime.now)


class ScanResult(BaseModel):
    """Result from scanner module."""
    file_tree: Dict[str, Any] = {}
    total_files: int = 0
    total_lines: int = 0
    languages: Dict[str, int] = {}
    dependencies: List[str] = []


class ClassificationResult(BaseModel):
    """Result from classifier module."""
    repo_type: str = "unknown"
    primary_language: str = "unknown"
    frameworks: List[str] = []
    patterns: List[str] = []
    confidence: float = 0.0
