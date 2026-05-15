"""
上下文构建器 - 总编排器模块。

负责协调选择器、优先级排序器、文件读取器、裁剪器等组件，
从扫描结果中构建完整的分析上下文。
"""

from pathlib import Path
from typing import List

from loguru import logger

from .selector import ContextSelector
from .prioritizer import ContextPrioritizer
from .file_reader import ContextFileReader
from .truncator import ContextTruncator
from .models import ContextFile, FileCategory, ContextPriority
from ..scanner.models import RepositorySnapshot
from ..models.ai_context import AIContext, FileContext, DirectoryContext, TechStackContext
from ..models.tech_stack import ProjectTechStack


class ContextBuilder:
    """
    上下文构建器 - 总编排器。

    职责：
        协调各个子组件，从扫描结果中构建完整的分析上下文。
        包括文件选择、优先级排序、安全读取、智能裁剪等步骤。

    工作流程：
        1. selector: 智能文件筛选
        2. prioritizer: 优先级排序
        3. reader: 安全文件读取
        4. truncator: 智能裁剪
        5. bundle: 打包最终上下文
    """

    def __init__(self) -> None:
        """初始化上下文构建器。"""
        self.selector = ContextSelector()
        self.prioritizer = ContextPrioritizer()
        self.reader = ContextFileReader()
        self.truncator = ContextTruncator()
        logger.info("上下文构建器初始化完成")

    def build(self, snapshot: RepositorySnapshot, tech_stack: ProjectTechStack) -> AIContext:
        """
        构建完整的 AI 分析上下文。

        参数：
            snapshot: 仓库扫描快照
            tech_stack: 技术栈分析结果

        返回：
            构建完成的 AIContext 对象

        流程：
            1. 调用 selector 进行文件筛选
            2. 调用 prioritizer 进行优先级排序
            3. 调用 reader 安全读取文件内容
            4. 调用 truncator 对大文件进行智能裁剪
            5. 打包所有结果为 AIContext
        """
        logger.info(f"开始构建 AI 上下文，仓库: {snapshot.repo_name}")
        
        # 1. 智能文件筛选
        selected_paths = self.selector.select(snapshot)
        logger.info(f"文件筛选完成，选中 {len(selected_paths)} 个文件")

        # 2. 优先级排序
        prioritized_paths = self.prioritizer.prioritize(selected_paths)
        logger.info("文件优先级排序完成")

        # 3. 安全读取与 4. 智能裁剪
        context_files: List[ContextFile] = []
        for path in prioritized_paths:
            read_result = self.reader.read(path)
            if read_result and read_result.content:
                # 确定文件分类和优先级（简化处理，实际可根据路径进一步细化）
                category = self._guess_category(path)
                priority = self._guess_priority(path)
                
                context_file = ContextFile(
                    path=str(path),
                    relative_path=str(path.relative_to(snapshot.repo_path)),
                    category=category,
                    priority=priority,
                    language=path.suffix.lstrip('.'),
                    size=read_result.size,
                    content=read_result.content,
                    is_truncated=read_result.is_truncated,
                    truncated_reason=read_result.truncated_reason,
                    estimated_tokens=0,  # 简化处理，暂不计算 token
                )
                
                # 执行裁剪
                truncated_file = self.truncator.truncate(context_file)
                context_files.append(truncated_file)

        logger.info(f"文件读取与裁剪完成，成功处理 {len(context_files)} 个文件")

        # 5. 打包为 AIContext
        ai_context = self._bundle_to_ai_context(snapshot, tech_stack, context_files)
        logger.info("AI 上下文构建完成")
        
        return ai_context

    def _guess_category(self, path: Path) -> FileCategory:
        """根据路径猜测文件分类。"""
        name = path.name.lower()
        parts = path.parts
        
        if any(p in ['controller', 'service', 'api', 'domain', 'model'] for p in parts):
            return FileCategory.SOURCE
        if name.endswith(('.yml', '.yaml', '.json', '.toml', '.env.example')):
            return FileCategory.CONFIG
        if name.startswith(('test_', 'test')) or 'test' in parts:
            return FileCategory.TEST
        if name.endswith(('.md', '.txt')):
            return FileCategory.DOCUMENT
        if name in ['main.py', 'app.py', 'index.js', 'main.go']:
            return FileCategory.ENTRY
            
        return FileCategory.SOURCE

    def _guess_priority(self, path: Path) -> ContextPriority:
        """根据路径猜测文件优先级。"""
        name = path.name.lower()
        if name in ['readme.md', 'dockerfile', 'package.json', 'pom.xml', 'go.mod']:
            return ContextPriority.S
        if name in ['main.py', 'app.py', 'index.ts', 'main.go']:
            return ContextPriority.A
        if 'controller' in str(path) or 'service' in str(path):
            return ContextPriority.B
        return ContextPriority.C

    def _bundle_to_ai_context(
        self, 
        snapshot: RepositorySnapshot, 
        tech_stack: ProjectTechStack, 
        context_files: List[ContextFile]
    ) -> AIContext:
        """
        将处理后的文件打包为 AIContext 模型。

        参数：
            snapshot: 仓库扫描快照
            tech_stack: 技术栈分析结果
            context_files: 经过处理的文件列表

        返回：
            AIContext 对象
        """
        # 转换文件列表
        file_contexts = [
            FileContext(
                file_path=cf.relative_path,
                content=cf.content or "",
                language=cf.language,
                line_count=len((cf.content or "").splitlines()),
                is_truncated=cf.is_truncated,
                priority=cf.priority.value,
                size_bytes=cf.size,
            )
            for cf in context_files
        ]

        # 构建目录树文本表示
        dir_tree_lines = []
        for d in snapshot.directories:
            indent = "  " * len(Path(d.relative_path).parts)
            dir_tree_lines.append(f"{indent}{d.relative_path}/")
        directory_tree = "\n".join(dir_tree_lines) if dir_tree_lines else "无目录信息"

        # 构建关键文件列表
        key_files_list = [
            f"{cf.relative_path} ({cf.language}, {cf.size} bytes, priority={cf.priority.value})"
            for cf in context_files
        ]

        # 构建代码样本（拼接所有文件内容，限制总长度）
        code_samples = []
        total_code_length = 0
        max_code_length = 50000  # 限制代码样本总长度
        
        for cf in context_files:
            if cf.content and cf.category in [FileCategory.SOURCE, FileCategory.ENTRY, FileCategory.CONFIG]:
                sample = f"\n=== File: {cf.relative_path} ===\n{cf.content}\n"
                if total_code_length + len(sample) > max_code_length:
                    sample = sample[:max_code_length - total_code_length] + "\n... (truncated)"
                    code_samples.append(sample)
                    break
                code_samples.append(sample)
                total_code_length += len(sample)
        
        sampled_code = "\n".join(code_samples) if code_samples else "无代码样本"

        # 转换目录列表
        dir_contexts = [
            DirectoryContext(
                path=d.relative_path,
                children=[],  # 简化处理，暂不填充子节点
                depth=len(Path(d.relative_path).parts),
            )
            for d in snapshot.directories
        ]

        # 转换技术栈
        ts_context = TechStackContext(
            languages=tech_stack.languages,
            frameworks=tech_stack.frameworks,
            dependencies=tech_stack.libraries,
            build_tools=tech_stack.build_tools,
            config_files=[],  # 可以从 context_files 中提取
            confidence=tech_stack.confidence,
        )

        return AIContext(
            repo_name=snapshot.repo_name,
            repo_path=snapshot.repo_path,
            files=file_contexts,
            directories=dir_contexts,
            languages=tech_stack.languages,
            tech_stack=ts_context,
            directory_tree=directory_tree,
            key_files=key_files_list,
            sampled_code=sampled_code,
            token_budget=50000,  # 默认预算
        )
