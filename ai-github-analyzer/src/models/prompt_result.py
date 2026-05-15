"""
单 Task 输出模型。

定义单个 Prompt 任务执行后的结果数据结构，支持失败重试场景、
Token 使用统计、错误信息和元数据记录。
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    """Token 使用统计。"""

    prompt_tokens: int = Field(default=0, ge=0, description="输入 Token 数量")
    completion_tokens: int = Field(default=0, ge=0, description="输出 Token 数量")
    total_tokens: int = Field(default=0, ge=0, description="总 Token 数量")


class PromptResult(BaseModel):
    """
    单 Task 输出模型。

    记录单个 Prompt 任务的执行结果，包括成功/失败状态、
    响应内容、Token 使用、耗时、重试次数和错误信息。
    支持 DAG 工作流中的节点级重试和恢复。
    """

    task_name: str = Field(description="任务名称（对应 Agent 或 Node 名称）")
    success: bool = Field(description="任务是否成功执行")

    prompt: Optional[str] = Field(default=None, description="实际使用的 Prompt 内容")
    content: Optional[str] = Field(default=None, description="AI 响应内容（原始或解析后）")

    model_name: Optional[str] = Field(default=None, description="使用的 LLM 模型名称")
    token_usage: Optional[TokenUsage] = Field(default=None, description="Token 使用统计")
    elapsed_time: float = Field(default=0.0, ge=0.0, description="执行耗时（秒）")
    retry_count: int = Field(default=0, ge=0, description="重试次数")

    error_message: Optional[str] = Field(default=None, description="错误信息（失败时）")

    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="扩展元数据（支持未来字段扩展）"
    )
    created_at: datetime = Field(default_factory=datetime.now, description="结果创建时间")
