"""
AI 分析引擎模块。

提供 AI 驱动的代码仓库分析能力，包括技术栈识别、架构分析、风险评估等功能。

主要组件：
- AIOrchestrator: AI总调度器
- TaskRegistry: 任务注册中心
- DAGScheduler: DAG调度器
- TaskDependencyManager: 任务依赖管理器

使用示例：
    from ai_engine.orchestrator import AIOrchestrator
    from ai_engine.registry import TaskRegistry
    from ai_engine.dag import DAGScheduler
"""

# 注意：为了避免循环导入和相对导入问题，使用时请直接导入具体模块
# 例如：from ai_engine.orchestrator import AIOrchestrator

__all__ = [
    # 核心组件（请通过具体模块导入）
    # "AIOrchestrator",  # from ai_engine.orchestrator import AIOrchestrator
    # "TaskRegistry",    # from ai_engine.registry import TaskRegistry
    # "DAGScheduler",    # from ai_engine.dag import DAGScheduler
]
