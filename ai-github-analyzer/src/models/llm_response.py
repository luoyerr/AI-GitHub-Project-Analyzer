"""
LLM 响应模型。

定义与大语言模型交互后的响应数据结构，包含成功状态、内容、模型信息、Token 使用统计等。
"""

from typing import Optional
from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    """
    LLM 响应模型。
    
    封装与大语言模型交互后的完整响应信息，包括执行状态、返回内容、
    使用的模型、Token 消耗、耗时和错误信息等。
    """
    
    success: bool = Field(description="请求是否成功")
    content: Optional[str] = Field(default=None, description="AI 返回的内容")
    model: Optional[str] = Field(default=None, description="使用的模型名称")
    token_usage: Optional[dict] = Field(default=None, description="Token 使用统计")
    elapsed_time: float = Field(default=0.0, ge=0.0, description="请求耗时（秒）")
    error_message: Optional[str] = Field(default=None, description="错误信息（失败时）")
