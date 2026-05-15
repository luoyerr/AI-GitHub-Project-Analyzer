"""
AI 上下文模型。

定义传递给 AI 模型的上下文数据结构。
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class FileContext(BaseModel):
    """文件上下文信息。"""
    file_path: str
    content: str
    language: Optional[str] = None
    line_count: int = 0
    is_truncated: bool = False
    priority: str = "low"  # low, medium, high, critical


class RepositoryContext(BaseModel):
    """仓库上下文信息。"""
    repository_url: str
    repository_name: str
    total_files: int = 0
    total_lines: int = 0
    directory_structure: Dict[str, Any] = Field(default_factory=dict)
    key_files: List[FileContext] = Field(default_factory=list)
    config_files: List[FileContext] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskContext(BaseModel):
    """任务执行上下文。"""
    task_name: str
    repository_context: RepositoryContext
    additional_context: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    previous_results: Dict[str, Any] = Field(default_factory=dict)


class ContextBudget(BaseModel):
    """上下文预算配置。"""
    max_tokens: int = 10000
    max_files: int = 50
    max_file_size_kb: int = 500
    truncation_strategy: str = "priority_based"  # priority_based, size_based, hybrid
    reserved_tokens: int = 1000  # 预留给响应和系统提示的 token


class AIContext(BaseModel):
    """完整的 AI 分析上下文。"""
    task_context: TaskContext
    context_budget: ContextBudget = Field(default_factory=ContextBudget)
    formatted_prompt: Optional[str] = None
    token_estimate: Optional[int] = None
    
    class Config:
        """Pydantic 配置。"""
        arbitrary_types_allowed = True
