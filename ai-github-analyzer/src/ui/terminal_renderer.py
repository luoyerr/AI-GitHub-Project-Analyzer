"""
终端渲染器。

使用 Rich 库渲染 Dashboard UI，包括：
- 顶部信息面板
- 任务状态列表
- 进度条
- Spinner 动画

设计原则：
- 纯渲染逻辑，不包含业务逻辑
- 与 ProgressManager 解耦，通过数据接口通信
- 支持 Live 刷新，不闪屏
"""

from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.spinner import Spinner
from rich.text import Text

# 任务名称中文映射
TASK_NAME_MAPPING = {
    "tech_stack": "技术栈分析",
    "directory_structure": "项目目录分析",
    "core_modules": "核心模块分析",
    "startup_flow": "启动流程分析",
    "config_analysis": "配置分析",
    "risks": "风险分析",
    "architecture_diagram": "架构图生成",
    "learning_path": "学习路线生成",
}

# 状态文本中文映射
STATUS_TEXT_MAPPING = {
    "running": "AI 深度分析中...",
    "calling_llm": "正在调用 AI 模型...",
    "failed": "执行失败",
    "success": "分析完成",
    "pending": "等待中...",
}


class TerminalRenderer:
    """
    终端渲染器。
    
    职责：
    - 根据 ProgressManager 的数据渲染 Dashboard
    - 使用 Rich Live 实现无闪烁刷新
    - 提供统一的渲染接口
    
    注意：
    - 本类只负责"如何显示"，不负责"显示什么"
    - 所有数据来源自 ProgressManager
    """
    
    def __init__(self, console: Optional[Console] = None) -> None:
        """
        初始化渲染器。
        
        Args:
            console: Rich Console 实例，默认为标准输出
        """
        self.console = console or Console()
    
    def render_dashboard(
        self,
        repo_name: str,
        model_name: str,
        provider_name: str,
        elapsed_time: float,
        current_task: Optional[str],
        completed_count: int,
        total_count: int,
        progress_percentage: float,
        tasks_info: dict,
    ) -> Panel:
        """
        渲染完整的 Dashboard 面板。
        
        Args:
            repo_name: 仓库名称
            model_name: AI 模型名称
            provider_name: AI 提供商
            elapsed_time: 总耗时（秒）
            current_task: 当前执行的任务名称
            completed_count: 已完成任务数
            total_count: 总任务数
            progress_percentage: 进度百分比
            tasks_info: 所有任务的详细信息 {task_name: TaskInfo}
            
        Returns:
            Panel: 可渲染的 Rich Panel 对象
        """
        # 创建布局
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=10),
            Layout(name="progress", size=4),
            Layout(name="tasks"),
        )
        
        # 渲染各个部分
        header_panel = self._render_header(
            repo_name, model_name, provider_name,
            elapsed_time, current_task, completed_count, total_count
        )
        progress_panel = self._render_progress(progress_percentage)
        tasks_table = self._render_tasks(tasks_info, current_task)
        
        # 组装布局
        layout["header"].update(header_panel)
        layout["progress"].update(progress_panel)
        layout["tasks"].update(tasks_table)
        
        return Panel(layout, title="[bold blue]AI GitHub 项目分析器[/bold blue]", border_style="blue")
    
    def _render_header(
        self,
        repo_name: str,
        model_name: str,
        provider_name: str,
        elapsed_time: float,
        current_task: Optional[str],
        completed_count: int,
        total_count: int,
    ) -> Panel:
        """渲染顶部信息区域。"""
        # 格式化时间
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        # 计算进度百分比
        if total_count > 0:
            percentage = int((completed_count / total_count) * 100)
        else:
            percentage = 0
        
        # 构建信息文本
        info_text = Text()
        info_text.append(f"{'仓库名称':<12}: ", style="cyan")
        info_text.append(f"{repo_name}\n", style="white")
        info_text.append(f"{'AI 模型':<12}: ", style="cyan")
        info_text.append(f"{model_name}\n", style="white")
        info_text.append(f"{'AI 提供商':<12}: ", style="cyan")
        info_text.append(f"{provider_name}\n", style="white")
        info_text.append(f"{'已耗时长':<12}: ", style="cyan")
        info_text.append(f"{time_str}\n", style="yellow")
        info_text.append(f"{'当前任务':<12}: ", style="cyan")
        # 将内部任务名转换为中文显示
        display_task = TASK_NAME_MAPPING.get(current_task, current_task) if current_task else "等待中..."
        info_text.append(f"{display_task}\n", style="green" if current_task else "dim")
        info_text.append(f"{'当前进度':<12}: ", style="cyan")
        info_text.append(f"{completed_count}/{total_count} ({percentage}%)\n", style="bold magenta")
        
        return Panel(info_text, border_style="cyan", title="📊 分析状态")
    
    def _render_progress(self, percentage: float) -> Panel:
        """渲染进度条区域。"""
        # 创建进度条
        progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=None),
            TextColumn("[bold]{task.percentage:>3.0f}%"),
            expand=True,
        )
        
        # 添加一个虚拟任务来显示进度
        task_id = progress.add_task("分析进度", total=100, completed=percentage)
        
        # 将 Progress 放入 Panel
        return Panel(progress, border_style="green", title="📈 整体进度")
    
    def _render_tasks(self, tasks_info: dict, current_task: Optional[str]) -> Table:
        """渲染任务状态列表。"""
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("Status", width=3)
        table.add_column("Task Name", width=20)
        table.add_column("Detail", justify="left")
        
        for task_name, task_info in tasks_info.items():
            # 获取中文任务名
            display_name = TASK_NAME_MAPPING.get(task_name, task_name)
            
            # 根据状态选择图标和样式
            if task_info.status.value == "running":
                status_icon = "⏳"
                status_style = "yellow"
                
                # 显示 Spinner 和动态消息
                if task_name == current_task:
                    detail = Text(STATUS_TEXT_MAPPING["running"], style="yellow italic")
                else:
                    detail = Text(STATUS_TEXT_MAPPING["calling_llm"], style="yellow")
            elif task_info.status.value == "success":
                status_icon = "✅"
                status_style = "green"
                detail = Text(f"({task_info.display_duration})", style="dim")
            elif task_info.status.value == "failed":
                status_icon = "❌"
                status_style = "red"
                error_msg = task_info.error_message or "未知错误"
                detail = Text(f"{STATUS_TEXT_MAPPING['failed']}: {error_msg[:50]}", style="red")
            else:  # pending
                status_icon = "⏸️"
                status_style = "dim"
                detail = Text("", style="dim")
            
            # 添加行
            table.add_row(
                Text(status_icon, style=status_style),
                Text(display_name, style="bold white" if task_name == current_task else "white"),
                detail,
            )
        
        return table
    
    def render_summary(
        self,
        repo_name: str,
        total_duration: float,
        report_path: str,
        successful_tasks: int,
        total_tasks: int,
        model_name: str = "unknown",
    ) -> Panel:
        """
        渲染分析完成后的摘要面板。
        
        Args:
            repo_name: 仓库名称
            total_duration: 总耗时（秒）
            report_path: 报告文件路径
            successful_tasks: 成功任务数
            total_tasks: 总任务数
            model_name: AI 模型名称
            
        Returns:
            Panel: 可渲染的 Rich Panel 对象
        """
        # 格式化时间
        minutes = int(total_duration // 60)
        seconds = int(total_duration % 60)
        if minutes > 0:
            time_str = f"{minutes}分{seconds}秒"
        else:
            time_str = f"{seconds:.1f}秒"
        
        # 构建摘要内容
        summary_text = Text()
        summary_text.append("\n")
        summary_text.append(f"{'仓库名称':<20}: ", style="cyan")
        summary_text.append(f"{repo_name}\n", style="bold white")
        summary_text.append(f"{'AI 模型':<20}: ", style="cyan")
        summary_text.append(f"{model_name}\n", style="bold white")
        summary_text.append(f"{'总耗时':<20}: ", style="cyan")
        summary_text.append(f"{time_str}\n", style="yellow")
        summary_text.append(f"{'完成任务数':<20}: ", style="cyan")
        summary_text.append(f"{successful_tasks}/{total_tasks}\n", style="green")
        summary_text.append(f"\n{'分析报告':<20}: ", style="cyan")
        summary_text.append(f"{report_path}\n", style="bold green underline")
        summary_text.append("\n")
        
        return Panel(
            summary_text,
            title="[bold green]✅ 分析完成[/bold green]",
            border_style="green",
        )
