"""
AI GitHub Analyzer - Main CLI entry point.

Usage:
    python main.py analyze <repo_url_or_path>
"""

# Windows 控制台 UTF-8 编码设置
import sys
import io
import time

if sys.platform == "win32":
    # 确保 Windows 控制台使用 UTF-8 编码
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import typer
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from loguru import logger
from pathlib import Path

# 将 src 目录添加到导入路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.scanner import RepoResolver, RepositorySnapshot
from src.analyzer.tech_stack import TechStackAnalyzer
from src.context_builder import ContextBuilder
from src.ai_engine.orchestrator import AIOrchestrator
from src.report.generator import MarkdownReportGenerator
from src.ui import CLIDashboard

app = typer.Typer(
    name="ai-github-analyzer",
    help="企业级 AI 驱动的 GitHub 项目分析器",
    add_completion=False,
)

console = Console()


# 特殊文件技术信号映射
SPECIAL_FILE_SIGNALS = {
    'dockerfile': 'Docker',
    'package.json': 'Node.js',
    'pom.xml': 'Maven / Java',
    'build.gradle': 'Gradle / Java',
    'go.mod': 'Go',
    'requirements.txt': 'Python',
    'pyproject.toml': 'Python',
    'pnpm-lock.yaml': 'pnpm',
    'yarn.lock': 'yarn',
    'package-lock.json': 'npm',
}

# 文件类型映射
FILE_TYPE_MAP = {
    'readme.md': '项目说明',
    'readme': '项目说明',
    '.gitignore': '忽略文件',
    '.env': '敏感配置',
    '.env.example': '示例配置',
    'dockerfile': '容器配置',
    'docker-compose.yml': '容器配置',
    'docker-compose.yaml': '容器配置',
    'license': '许可证',
    'license.md': '许可证',
    'license.txt': '许可证',
    'contributing.md': '贡献指南',
    'changelog.md': '变更日志',
    'changes.md': '变更日志',
}

# 构建配置文件映射
BUILD_CONFIG_FILES = {
    'package.json': 'Node.js',
    'pom.xml': 'Maven/Java',
    'build.gradle': 'Gradle/Java',
    'go.mod': 'Go',
    'requirements.txt': 'Python',
    'pyproject.toml': 'Python',
    'setup.py': 'Python',
    'cargo.toml': 'Rust',
    'gemfile': 'Ruby',
    'composer.json': 'PHP',
}


def _get_file_signal(file_path: str, extension: str) -> str:
    """
    获取文件的技术信号
    
    Args:
        file_path: 文件相对路径
        extension: 文件后缀名
        
    Returns:
        str: 技术信号（后缀或特殊标识）
    """
    # 提取文件名（不含路径）
    file_name = Path(file_path).name.lower()
    
    # 检查是否是特殊文件
    if file_name in SPECIAL_FILE_SIGNALS:
        return SPECIAL_FILE_SIGNALS[file_name]
    
    # 特殊处理 .env.example 这类文件
    if file_name.startswith('.env'):
        return '配置'
    
    # 普通文件返回后缀
    return extension if extension else '无'



def _format_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 文件大小（字节）
        
    Returns:
        str: 格式化后的大小（如 12.5 KB, 13.2 MB）
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def _get_file_type(file_name: str) -> str:
    """
    获取文件类型
    
    Args:
        file_name: 文件名（不含路径）
        
    Returns:
        str: 文件类型描述
    """
    file_name_lower = file_name.lower()
    
    # 检查特殊文件类型
    if file_name_lower in FILE_TYPE_MAP:
        return FILE_TYPE_MAP[file_name_lower]
    
    # 检查是否是构建配置文件
    if file_name_lower in BUILD_CONFIG_FILES:
        return '构建配置'
    
    # 普通文件
    return '文件'


def _calculate_dir_stats(snapshot: RepositorySnapshot, dir_relative_path: str) -> tuple:
    """
    计算目录的递归统计信息（基于真实仓库完整数据）
    
    Args:
        snapshot: 仓库快照（必须包含完整未裁剪的文件和目录列表）
        dir_relative_path: 目录相对路径
        
    Returns:
        tuple: (总大小字节数, 子目录数, 文件数)
    """
    total_size = 0
    subdirs = set()
    files_count = 0
    
    # 规范化目录路径
    dir_path_normalized = Path(dir_relative_path).as_posix() if dir_relative_path else ''
    
    # 遍历所有文件，递归统计属于该目录及其子目录的所有文件
    for file_meta in snapshot.files:
        file_path_normalized = Path(file_meta.relative_path).as_posix()
        
        # 检查文件是否在该目录下（包括所有子目录）
        if dir_path_normalized == '':
            # 根目录：统计所有文件
            total_size += file_meta.size_bytes
            files_count += 1
        else:
            # 子目录：检查文件路径是否以目录路径开头
            # 例如：dir="src/agents", file="src/agents/tech_agent.py" ✓
            # 例如：dir="src", file="src/agents/tech_agent.py" ✓
            if file_path_normalized.startswith(dir_path_normalized + '/') or file_path_normalized == dir_path_normalized:
                total_size += file_meta.size_bytes
                files_count += 1
    
    # 遍历所有目录，递归统计所有后代子目录
    for dir_meta in snapshot.directories:
        if dir_meta.relative_path == dir_relative_path:
            continue
        
        subdir_path_normalized = Path(dir_meta.relative_path).as_posix()
        
        # 检查是否是该目录的后代目录（包括直接子目录和更深层的子目录）
        if dir_path_normalized == '':
            # 根目录：统计所有目录
            subdirs.add(dir_meta.relative_path)
        else:
            # 子目录：检查目录路径是否以当前目录路径开头
            # 例如：current="src", subdir="src/agents" ✓
            # 例如：current="src", subdir="src/agents/tech" ✓
            if subdir_path_normalized.startswith(dir_path_normalized + '/'):
                subdirs.add(dir_meta.relative_path)
    
    return total_size, len(subdirs), files_count


def _display_snapshot(console: Console, snapshot: RepositorySnapshot):
    """
    显示仓库根目录概览（GitHub 风格）
    
    Args:
        console: Rich 控制台
        snapshot: 仓库快照
    """
    console.print("\n[bold green]✓ 仓库扫描完成！[/bold green]\n")
    
    # 基本信息
    console.print(f"[bold]仓库名称：[/bold] {snapshot.repo_name}")
    console.print(f"[bold]仓库路径：[/bold] {snapshot.repo_path}\n")
    
    # 根目录概览表格
    console.print("[bold blue]📁 仓库根目录概览[/bold blue]\n")
    
    table = Table(show_header=True, header_style="bold cyan", show_lines=True)
    table.add_column("名称", style="green", no_wrap=False)
    table.add_column("类型", style="yellow", width=12)
    table.add_column("后缀/技术信号", style="magenta", width=18)
    table.add_column("大小", style="cyan", justify="right", width=12)
    # table.add_column("信息", style="white", justify="left")
    
    # 收集根目录下的所有项（文件和目录）
    root_items = []
    
    # 添加根目录下的文件
    for file_meta in snapshot.files:
        file_path = Path(file_meta.relative_path)
        # 只处理根目录下的文件（没有父目录或父目录是 '.'）
        if file_path.parent == Path('.') or str(file_path.parent) == '.':
            root_items.append(('file', file_meta))
    
    # 添加根目录下的直接子目录
    for dir_meta in snapshot.directories:
        dir_path = Path(dir_meta.relative_path)
        # 只处理根目录下的直接子目录
        if dir_path.parent == Path('.') or str(dir_path.parent) == '.':
            root_items.append(('dir', dir_meta))
    
    # 按名称排序（目录优先，然后按字母顺序）
    def sort_key(item):
        item_type, item_meta = item
        name = item_meta.relative_path.split('/')[0].split('\\')[0]
        # 目录排在前面 (0)，文件排在后面 (1)
        type_order = 0 if item_type == 'dir' else 1
        return (type_order, name.lower())
    
    root_items.sort(key=sort_key)
    
    # 渲染每一行
    for item_type, item_meta in root_items:
        if item_type == 'file':
            file_meta = item_meta
            file_name = Path(file_meta.relative_path).name
            
            # 获取文件类型
            file_type = _get_file_type(file_name)
            
            # 获取技术信号
            signal = _get_file_signal(file_meta.relative_path, file_meta.extension)
            
            # 格式化大小
            size_str = _format_size(file_meta.size_bytes)
            
            table.add_row(
                file_name,
                file_type,
                signal,
                size_str,
                # info
            )
        else:
            dir_meta = item_meta
            dir_name = Path(dir_meta.relative_path).name
            
            # 计算目录统计信息
            total_size, subdir_count, file_count = _calculate_dir_stats(
                snapshot, 
                dir_meta.relative_path
            )
            
            # 格式化大小
            size_str = _format_size(total_size)
            
            # 信息列：x目录 / x文件
            
            table.add_row(
                f"📁 {dir_name}/",
                '目录',
                '',  # 目录不显示后缀
                size_str,
                # info
            )
    
    console.print(table)
    console.print()


def _display_tech_stack(console: Console, tech_stack):
    """
    显示技术栈分析结果
    
    Args:
        console: Rich 控制台
        tech_stack: 技术栈模型
    """
    from rich.panel import Panel
    
    console.print("[bold green]✨ 技术栈分析结果[/bold green]\n")
    
    # 创建面板内容
    lines = []
    
    # 编程语言
    if tech_stack.languages:
        lines.append(f"[bold]编程语言：[/bold] {', '.join(tech_stack.languages)}")
    else:
        lines.append("[bold]编程语言：[/bold] 未识别")
    
    # 框架
    if tech_stack.frameworks:
        lines.append(f"[bold]框架：[/bold] {', '.join(tech_stack.frameworks)}")
    else:
        lines.append("[bold]框架：[/bold] 未识别")
    
    # 库
    if tech_stack.libraries:
        lines.append(f"[bold]类库：[/bold] {', '.join(tech_stack.libraries)}")
    else:
        lines.append("[bold]类库：[/bold] 未识别")
    
    # 构建工具
    if tech_stack.build_tools:
        lines.append(f"[bold]构建工具：[/bold] {', '.join(tech_stack.build_tools)}")
    else:
        lines.append("[bold]构建工具：[/bold] 未识别")
    
    # 包管理器
    if tech_stack.package_managers:
        lines.append(f"[bold]包管理器：[/bold] {', '.join(tech_stack.package_managers)}")
    else:
        lines.append("[bold]包管理器：[/bold] 未识别")
    
    # 数据库
    if tech_stack.databases:
        lines.append(f"[bold]数据库：[/bold] {', '.join(tech_stack.databases)}")
    else:
        lines.append("[bold]数据库：[/bold] 未识别")
    
    # CI/CD
    if tech_stack.ci_cd:
        lines.append(f"[bold]CI/CD：[/bold] {', '.join(tech_stack.ci_cd)}")
    else:
        lines.append("[bold]CI/CD：[/bold] 未识别")
    
    # 容器化
    if tech_stack.containers:
        lines.append(f"[bold]容器化：[/bold] {', '.join(tech_stack.containers)}")
    else:
        lines.append("[bold]容器化：[/bold] 未识别")
    
    # 云原生
    if tech_stack.cloud_native:
        lines.append(f"[bold]云原生：[/bold] {', '.join(tech_stack.cloud_native)}")
    else:
        lines.append("[bold]云原生：[/bold] 未识别")
    
    # 测试工具
    if tech_stack.testing_tools:
        lines.append(f"[bold]测试工具：[/bold] {', '.join(tech_stack.testing_tools)}")
    else:
        lines.append("[bold]测试工具：[/bold] 未识别")
    
    # 可信度
    confidence_percent = int(tech_stack.confidence * 100)
    lines.append(f"\n[bold]识别可信度：[/bold] {confidence_percent}%")
    
    # 显示面板
    content = "\n".join(lines)
    console.print(Panel(content, title="技术栈详情", border_style="green"))
    console.print()


def setup_logging():
    """配置 loguru 日志系统。"""
    logger.remove()  # 移除默认处理器
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{"
               "function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True,
    )
    logger.add(
        "logs/ai_analyzer_{time}.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
        encoding="utf-8",
    )


@app.callback()
def callback():
    """AI GitHub Analyzer - 使用 AI 代理分析 GitHub 仓库。"""
    setup_logging()
    logger.info("AI GitHub Analyzer 已初始化")


@app.command()
def analyze(
    repo_url: str = typer.Argument(
        ...,
        help="要分析的 GitHub 仓库 URL 或本地路径",
    ),
    output_format: str = typer.Option(
        "markdown",
        "--format",
        "-f",
        help="输出格式（markdown、json、html）",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="启用详细输出",
    ),
):
    """
    全链路分析 GitHub 仓库。
    
    流程：
    Phase 1: 扫描仓库 (Scanner)
    Phase 2: 技术栈分析 (Tech Stack Analyzer)
    Phase 3: 上下文构建 (Context Builder)
    Phase 4: AI 分析 (AI Orchestrator)
    Phase 5: 报告生成 (Markdown Generator)
    """
    total_start_time = time.time()
    logger.info(f"开始全链路分析：{repo_url}")
    
    try:
        # ==================== Phase 1: 扫描仓库 ====================
        console.print(Panel.fit("[bold blue]Phase 1: 扫描仓库[/bold blue]", border_style="blue"))
        phase1_start = time.time()
        
        resolver = RepoResolver()
        
        # 显示仓库下载状态
        from pathlib import Path as PathLib
        repo_name = PathLib(repo_url.rstrip('/')).name
        if repo_name.endswith('.git'):
            repo_name = repo_name[:-4]
        
        temp_repos_path = Path(__file__).parent / "temp_repos" / repo_name
        if temp_repos_path.exists():
            console.print(f"\n[bold green]✓[/bold green] [green]检测到本地仓库缓存[/green]")
            console.print(f"  仓库: [cyan]{repo_name}[/cyan]")
            console.print(f"  路径: [dim]{temp_repos_path}[/dim]")
            console.print(f"  [yellow]正在同步最新代码...[/yellow]")
        else:
            console.print(f"\n[yellow]⚠ 正在克隆仓库...[/yellow]")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task("[cyan]正在扫描仓库...", total=None)
            snapshot = asyncio.run(resolver.resolve(repo_url))
            progress.update(task, description="[green]扫描完成！")
        
        _display_snapshot(console, snapshot)
        phase1_elapsed = time.time() - phase1_start
        console.print(f"[bold green]✓ Phase 1 完成，耗时: {phase1_elapsed:.2f}秒[/bold green]\n")
        
        # ==================== Phase 2: 技术栈分析 ====================
        console.print(Panel.fit("[bold blue]Phase 2: 技术栈分析[/bold blue]", border_style="blue"))
        phase2_start = time.time()
        
        analyzer = TechStackAnalyzer()
        tech_stack = analyzer.analyze(snapshot)
        _display_tech_stack(console, tech_stack)
        
        phase2_elapsed = time.time() - phase2_start
        console.print(f"[bold green]✓ Phase 2 完成，耗时: {phase2_elapsed:.2f}秒[/bold green]\n")
        
        # ==================== Phase 3: 上下文构建 ====================
        console.print(Panel.fit("[bold blue]Phase 3: 上下文构建[/bold blue]", border_style="blue"))
        phase3_start = time.time()
        
        context_builder = ContextBuilder()
        ai_context = context_builder.build(snapshot, tech_stack)
        
        phase3_elapsed = time.time() - phase3_start
        console.print(f"[bold green]✓ Phase 3 完成，选中文件数: {len(ai_context.files)}，耗时: {phase3_elapsed:.2f}秒[/bold green]\n")
        
        # ==================== Phase 4: AI 分析 ====================
        console.print(Panel.fit("[bold blue]Phase 4: AI 分析[/bold blue]", border_style="blue"))
        phase4_start = time.time()
        
        # 获取任务列表（从 DAG 调度器）
        from src.ai_engine.dag import DAGScheduler
        dag_scheduler = DAGScheduler()
        task_names = dag_scheduler.get_execution_order()
        
        # 先创建 Orchestrator（内部会初始化 LLMClient）
        orchestrator = AIOrchestrator()
        
        # 从 LLMClient 获取真实运行时的模型信息
        model_name = orchestrator._llm_client.model
        provider_name = orchestrator._llm_client.provider
        
        logger.info(f"Dashboard Runtime Model: {model_name}")
        logger.info(f"Dashboard Runtime Provider: {provider_name}")
        
        # 创建 Dashboard，注入真实的 runtime 信息
        dashboard = CLIDashboard(
            repo_name=snapshot.repo_name,
            model_name=model_name,
            provider_name=provider_name,
            task_names=task_names,
            console=console,
        )
        
        # 将 Dashboard 注入到 Orchestrator
        orchestrator._dashboard = dashboard
        analysis_result = orchestrator.run(ai_context)
        
        phase4_elapsed = time.time() - phase4_start
        
        # 显示完成摘要
        report_path = None
        dashboard.show_summary(
            total_duration=phase4_elapsed,
            report_path="等待报告生成...",
        )
        
        # ==================== Phase 5: 报告生成 ====================
        console.print(Panel.fit("[bold blue]Phase 5: 报告生成[/bold blue]", border_style="blue"))
        phase5_start = time.time()
        
        report_generator = MarkdownReportGenerator()
        repo_path = Path(snapshot.repo_path)
        result = report_generator.generate(analysis_result, repo_path)
        
        if result["success"]:
            output_path = result['output_path']
            console.print(f"[bold green]✓ 报告已生成: {output_path}[/bold green]")
            console.print(f"[dim]路径: {output_path.absolute()}[/dim]")
            
            # 更新 Dashboard 摘要中的报告路径
            dashboard.show_summary(
                total_duration=phase4_elapsed,
                report_path=str(output_path.absolute()),
            )
        else:
            console.print(f"[bold red]✗ 报告生成失败: {result.get('error')}[/bold red]")
        
        phase5_elapsed = time.time() - phase5_start
        console.print(f"[bold green]✓ Phase 5 完成，耗时: {phase5_elapsed:.2f}秒[/bold green]\n")
        
        # ==================== 总结 ====================
        total_elapsed = time.time() - total_start_time
        summary_panel = Panel.fit(
            f"[bold green]全链路分析成功完成！[/bold green]\n总耗时: [bold]{total_elapsed:.2f}秒[/bold]",
            title="🎉 分析结果",
            border_style="green"
        )
        console.print(summary_panel)
        
        # 最后清理临时克隆目录（在所有阶段完成后）
        if resolver.is_temp_clone:
            # 根据缓存模式决定是否清理
            should_cleanup = asyncio.run(resolver.cache_manager.should_cleanup())
            
            if should_cleanup:
                logger.info("开始清理临时克隆目录")
                asyncio.run(resolver.github_cloner.cleanup())
                console.print(f"\n[bold yellow]✓[/bold yellow] [yellow]已自动清理临时仓库[/yellow]")
            else:
                logger.info(f"跳过清理，仓库保留在：{snapshot.repo_path}")
                console.print(f"\n[bold green]✓[/bold green] [green]仓库已保留：{Path(snapshot.repo_path).name}[/green]")
            
            resolver.is_temp_clone = False
        
        return analysis_result
        
    except Exception as e:
        error_msg = f"分析过程中发生错误: {str(e)}"
        console.print(f"\n[bold red]✗ {error_msg}[/bold red]")
        logger.exception(error_msg)
        sys.exit(1)


@app.command()
def version():
    """显示版本信息。"""
    from src import __version__
    console.print(f"[bold blue]AI GitHub Analyzer[/bold blue] v{__version__}")


if __name__ == "__main__":
    app()
