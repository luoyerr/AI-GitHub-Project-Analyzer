"""
任务上下文模型。

定义传递给各个分析任务的上下文数据结构，包含仓库信息、文件内容、技术栈等。
用于DAG工作流中各Agent节点的输入数据契约。
"""

from typing import Any, Dict
from pydantic import BaseModel, Field

from .ai_context import AIContext


class TaskContext(BaseModel):
    """
    任务执行上下文模型。
    
    封装了执行单个分析任务所需的所有上下文信息，包括AI上下文、
    任务特定的配置和元数据。支持DAG工作流中的节点级执行。
    """
    
    # AI上下文，包含仓库信息、文件列表、目录结构等
    ai_context: AIContext = Field(description="AI分析上下文")
    
    # 任务特定的配置
    task_config: Dict[str, Any] = Field(
        default_factory=dict, 
        description="任务特定配置参数"
    )
    
    # 依赖任务的结果（如果有的话）
    dependency_results: Dict[str, Any] = Field(
        default_factory=dict,
        description="依赖任务的执行结果"
    )
    
    # 扩展元数据
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="扩展元数据（支持未来字段扩展）"
    )