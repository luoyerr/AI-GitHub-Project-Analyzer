"""
CLI Dashboard 主控制器。

整合 ProgressManager 和 TerminalRenderer，提供高层 API 给 Orchestrator 使用。
使用 Rich Live 实现无闪烁的动态刷新。

架构设计：
- Dashboard: 对外接口，Orchestrator 只与此类交互
- ProgressManager: 管理任务状态数据
- TerminalRenderer: 负责渲染 UI

职责分离：
- Orchestrator 不直接操作 UI
- Dashboard 不执行业务逻辑
- 便于未来替换为 Web UI / TUI / Electron
"""

from typing import Optional
from rich.console import Console
from rich.live import Live
from .progress_manager import ProgressManager, TaskStatus
from .terminal_renderer import TerminalRenderer


class CLIDashboard:
    """
    CLI Dashboard 控制器。
    
    提供给 Orchestrator 的接口：
    - start(): 启动 Dashboard
    - start_task(task_name): 开始执行任务
    - finish_task(task_name, duration): 任务成功完成
    - fail_task(task_name, error, duration): 任务失败
    - finish(): 结束 Dashboard
    
    使用示例：
        dashboard = CLIDashboard(
            repo_name="fastapi",
            model_name="qwen3-coder-free",
            provider_name="qwen",
            task_names=["tech_stack", "directory", ...]
        )
        
        with dashboard:
            for task in tasks:
                dashboard.start_task(task.name)
                # ... 执行任务 ...
                dashboard.finish_task(task.name, duration)
    """
    
    def __init__(
        self,
        repo_name: str,
        model_name: str = "unknown",
        provider_name: str = "unknown",
        task_names: Optional[list[str]] = None,
        console: Optional[Console] = None,
    ) -> None:
        """
        初始化 Dashboard。
        
        Args:
            repo_name: 仓库名称
            model_name: AI 模型名称
            provider_name: AI 提供商名称
            task_names: 任务名称列表（按执行顺序）
            console: Rich Console 实例
        """
        self.repo_name = repo_name
        self.model_name = model_name
        self.provider_name = provider_name
        
        # 初始化进度管理器
        self._progress_manager = ProgressManager(task_names or [])
        
        # 初始化渲染器
        self._renderer = TerminalRenderer(console or Console())
        
        # Live 上下文管理器
        self._live: Optional[Live] = None
        self._console = console or Console()
    
    def start(self) -> None:
        """启动 Dashboard（进入 Live 模式）。"""
        self._progress_manager.start()
        
        # 创建 Live 上下文
        self._live = Live(
            self._render(),
            console=self._console,
            refresh_per_second=4,  # 每秒刷新 4 次，平衡流畅度和性能
            screen=False,  # 不使用全屏模式
        )
        self._live.start()
    
    def stop(self) -> None:
        """停止 Dashboard（退出 Live 模式）。"""
        if self._live:
            self._live.stop()
            self._live = None
    
    def start_task(self, task_name: str) -> None:
        """
        标记任务开始执行。
        
        Args:
            task_name: 任务名称
        """
        self._progress_manager.start_task(task_name)
        self._refresh()
    
    def finish_task(self, task_name: str, duration: float = 0.0) -> None:
        """
        标记任务成功完成。
        
        Args:
            task_name: 任务名称
            duration: 任务耗时（秒），如果为 0 则自动计算
        """
        self._progress_manager.finish_task(task_name, duration)
        self._refresh()
    
    def fail_task(self, task_name: str, error_message: str, duration: float = 0.0) -> None:
        """
        标记任务失败。
        
        Args:
            task_name: 任务名称
            error_message: 错误信息
            duration: 任务耗时（秒），如果为 0 则自动计算
        """
        self._progress_manager.fail_task(task_name, error_message, duration)
        self._refresh()
    
    def finish(self) -> None:
        """标记整个流程结束，显示最终摘要。"""
        self._progress_manager.finish()
        self._refresh()
    
    def show_summary(
        self,
        total_duration: float,
        report_path: str,
    ) -> None:
        """
        显示分析完成的摘要面板。
        
        Args:
            total_duration: 总耗时（秒）
            report_path: 报告文件路径
        """
        # 先停止 Live
        self.stop()
        
        # 渲染并显示摘要
        summary_panel = self._renderer.render_summary(
            repo_name=self.repo_name,
            model_name=self.model_name,
            total_duration=total_duration,
            report_path=report_path,
            successful_tasks=self._progress_manager.successful_tasks,
            total_tasks=self._progress_manager.total_tasks,
        )
        self._console.print(summary_panel)
    
    def _refresh(self) -> None:
        """刷新 UI 显示。"""
        if self._live:
            self._live.update(self._render())
    
    def _render(self):
        """渲染当前状态的 Dashboard。"""
        return self._renderer.render_dashboard(
            repo_name=self.repo_name,
            model_name=self.model_name,
            provider_name=self.provider_name,
            elapsed_time=self._progress_manager.elapsed_time,
            current_task=self._progress_manager.current_task_name,
            completed_count=self._progress_manager.completed_tasks,
            total_count=self._progress_manager.total_tasks,
            progress_percentage=self._progress_manager.progress_percentage,
            tasks_info=self._progress_manager.get_all_tasks(),
        )
    
    def __enter__(self):
        """支持上下文管理器协议。"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时自动停止 Dashboard。"""
        self.stop()
        return False  # 不抑制异常
