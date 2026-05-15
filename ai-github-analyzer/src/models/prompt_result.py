"""
Prompt 结果模型。

定义 Prompt 执行后的结果数据结构。
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PromptMetrics(BaseModel):
    """Prompt 执行指标。"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    execution_time_ms: int = 0
    retry_count: int = 0


class ValidationResult(BaseModel):
    """验证结果。"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    validation_details: Dict[str, Any] = Field(default_factory=dict)


class PromptResult(BaseModel):
    """Prompt 执行结果。"""
    prompt_name: str
    raw_response: str = ""
    parsed_response: Optional[Any] = None
    success: bool = True
    error_message: Optional[str] = None
    validation_result: Optional[ValidationResult] = None
    metrics: PromptMetrics = Field(default_factory=PromptMetrics)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        """Pydantic 配置。"""
        arbitrary_types_allowed = True


class PromptTemplate(BaseModel):
    """Prompt 模板定义。"""
    name: str
    template_path: str
    version: str = "1.0.0"
    description: str = ""
    input_schema: Dict[str, Any] = Field(default_factory=dict)
    output_schema: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    retry_policy: Dict[str, Any] = Field(default_factory=dict)


class PromptExecutionConfig(BaseModel):
    """Prompt 执行配置。"""
    temperature: float = 0.2
    max_tokens: int = 4000
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    timeout_seconds: int = 60
    max_retries: int = 3
    retry_delay_seconds: float = 2.0
