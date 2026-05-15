"""
Markdown 报告模板模块。

定义 PROJECT_ANALYSIS.md 的固定模板结构，严格包含 8 个章节：
1. 技术栈分析
2. 项目目录说明
3. 核心模块职责
4. 启动流程
5. 配置说明
6. 风险分析
7. 架构图（Mermaid）
8. 学习路线

本模块仅负责模板定义，不包含业务逻辑。
"""

from typing import Dict, Any
from datetime import datetime


class ReportTemplate:
    """
    Markdown 报告模板类。

    提供固定的 Markdown 模板结构，确保生成的报告包含所有必需章节。
    模板使用占位符格式，由后续渲染步骤填充实际内容。
    """

    # 必需的 8 个章节标识
    REQUIRED_SECTIONS = [
        "tech_stack",
        "directory_structure",
        "core_modules",
        "startup_flow",
        "config_analysis",
        "risks",
        "architecture_diagram",
        "learning_path",
    ]

    @staticmethod
    def generate_template(data: Dict[str, Any]) -> str:
        """
        生成完整的 Markdown 报告。

        参数:
            data: 包含所有章节数据的字典，键名为章节标识，值为章节内容。

        返回:
            完整的 Markdown 字符串。

        注意:
            - 所有缺失的章节会标记为"待补充"
            - 保持严格的章节顺序
            - 自动添加报告元信息头部
        """
        repo_name = data.get("repo_name", "未知仓库")
        analysis_time = data.get("analysis_time", datetime.now())

        # 格式化时间
        if isinstance(analysis_time, datetime):
            time_str = analysis_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            time_str = str(analysis_time)

        # 构建报告头部
        header = f"""# {repo_name} - 项目分析报告

> **生成时间**: {time_str}  
> **分析工具**: AI GitHub Project Analyzer  
> **架构风格**: Harness Engineering

---

"""

        # 构建各章节内容
        sections = []

        # 第 1 章：技术栈分析
        sections.append(ReportTemplate._render_tech_stack(data.get("tech_stack")))

        # 第 2 章：项目目录说明
        sections.append(ReportTemplate._render_directory_structure(data.get("directory_structure")))

        # 第 3 章：核心模块职责
        sections.append(ReportTemplate._render_core_modules(data.get("core_modules")))

        # 第 4 章：启动流程
        sections.append(ReportTemplate._render_startup_flow(data.get("startup_flow")))

        # 第 5 章：配置说明
        sections.append(ReportTemplate._render_config_analysis(data.get("config_analysis")))

        # 第 6 章：风险分析
        sections.append(ReportTemplate._render_risks(data.get("risks")))

        # 第 7 章：架构图（Mermaid）
        sections.append(ReportTemplate._render_architecture_diagram(data.get("architecture_diagram")))

        # 第 8 章：学习路线
        sections.append(ReportTemplate._render_learning_path(data.get("learning_path")))

        # 拼接完整报告
        report = header + "\n\n".join(sections) + "\n"

        return report

    @staticmethod
    def _render_tech_stack(data: Any) -> str:
        """
        渲染技术栈分析章节。

        参数:
            data: TechStackAnalysis 模型数据或 None。

        返回:
            Markdown 格式的章节内容。
        """
        section = "## 一、技术栈分析\n\n"

        if not data:
            return section + "*待补充*\n"

        # 编程语言
        if hasattr(data, "languages") and data.languages:
            section += "### 编程语言\n\n"
            for lang in data.languages:
                section += f"- {lang}\n"
            section += "\n"

        # 框架
        if hasattr(data, "frameworks") and data.frameworks:
            section += "### 框架\n\n"
            for framework in data.frameworks:
                section += f"- {framework}\n"
            section += "\n"

        # 核心依赖
        if hasattr(data, "dependencies") and data.dependencies:
            section += "### 核心依赖\n\n"
            for dep in data.dependencies:
                section += f"- {dep}\n"
            section += "\n"

        # 构建工具
        if hasattr(data, "build_tools") and data.build_tools:
            section += "### 构建工具\n\n"
            for tool in data.build_tools:
                section += f"- {tool}\n"
            section += "\n"

        # 部署工具
        if hasattr(data, "deployment_tools") and data.deployment_tools:
            section += "### 部署工具\n\n"
            for tool in data.deployment_tools:
                section += f"- {tool}\n"
            section += "\n"

        # 置信度
        if hasattr(data, "confidence"):
            section += f"**识别置信度**: {data.confidence:.0%}\n\n"

        # 证据文件
        if hasattr(data, "evidence_files") and data.evidence_files:
            section += "**证据文件**:\n\n"
            for file in data.evidence_files:
                section += f"- `{file}`\n"
            section += "\n"

        return section

    @staticmethod
    def _render_directory_structure(data: Any) -> str:
        """
        渲染项目目录说明章节。

        参数:
            data: DirectoryStructureAnalysis 模型数据或 None。

        返回:
            Markdown 格式的章节内容。
        """
        section = "## 二、项目目录说明\n\n"

        if not data:
            return section + "*待补充*\n"

        # 整体描述
        if hasattr(data, "description") and data.description:
            section += f"{data.description}\n\n"

        # 根目录说明
        if hasattr(data, "root_directories") and data.root_directories:
            section += "### 根目录职责\n\n"
            for dir_name, description in data.root_directories.items():
                section += f"- **`{dir_name}/`**: {description}\n"
            section += "\n"

        # 关键文件
        if hasattr(data, "key_files") and data.key_files:
            section += "### 关键文件\n\n"
            for file_path, description in data.key_files.items():
                section += f"- **`{file_path}`**: {description}\n"
            section += "\n"

        # 架构模式
        if hasattr(data, "architecture_pattern") and data.architecture_pattern:
            section += f"**架构模式**: {data.architecture_pattern}\n\n"

        return section

    @staticmethod
    def _render_core_modules(data: Any) -> str:
        """
        渲染核心模块职责章节。

        参数:
            data: CoreModuleAnalysis 模型数据或 None。

        返回:
            Markdown 格式的章节内容。
        """
        section = "## 三、核心模块职责\n\n"

        if not data:
            return section + "*待补充*\n"

        # 模块列表
        if hasattr(data, "modules") and data.modules:
            section += "### 核心模块\n\n"
            for module in data.modules:
                section += f"#### {module.name}\n\n"
                section += f"- **路径**: `{module.path}`\n"
                section += f"- **职责**: {module.responsibility}\n"
                if hasattr(module, "key_classes") and module.key_classes:
                    section += "- **关键类/函数**:\n"
                    for cls in module.key_classes:
                        section += f"  - `{cls}`\n"
                section += "\n"

        # 入口点
        if hasattr(data, "entry_points") and data.entry_points:
            section += "### 入口点\n\n"
            for entry in data.entry_points:
                section += f"- `{entry}`\n"
            section += "\n"

        # 模块关系
        if hasattr(data, "relationships") and data.relationships:
            section += "### 模块关系\n\n"
            for rel in data.relationships:
                desc = f" ({rel.description})" if hasattr(rel, "description") and rel.description else ""
                section += f"- `{rel.source}` → `{rel.target}` ({rel.relationship_type}){desc}\n"
            section += "\n"

        return section

    @staticmethod
    def _render_startup_flow(data: Any) -> str:
        """
        渲染启动流程章节。

        参数:
            data: StartupFlowAnalysis 模型数据或 None。

        返回:
            Markdown 格式的章节内容。
        """
        section = "## 四、启动流程\n\n"

        if not data:
            return section + "*待补充*\n"

        # 环境准备
        if hasattr(data, "environment_setup") and data.environment_setup:
            section += "### 环境准备\n\n"
            for step in data.environment_setup:
                section += f"1. {step}\n"
            section += "\n"

        # 安装依赖
        if hasattr(data, "installation_steps") and data.installation_steps:
            section += "### 安装依赖\n\n"
            for step in data.installation_steps:
                section += f"1. {step}\n"
            section += "\n"

        # 构建命令
        if hasattr(data, "build_commands") and data.build_commands:
            section += "### 构建命令\n\n"
            for cmd in data.build_commands:
                section += f"```bash\n{cmd}\n```\n\n"

        # 启动命令
        if hasattr(data, "startup_commands") and data.startup_commands:
            section += "### 启动命令\n\n"
            for cmd in data.startup_commands:
                section += f"```bash\n{cmd}\n```\n\n"

        # 数据库初始化
        if hasattr(data, "database_init") and data.database_init:
            section += "### 数据库初始化\n\n"
            section += f"{data.database_init}\n\n"

        return section

    @staticmethod
    def _render_config_analysis(data: Any) -> str:
        """
        渲染配置说明章节。

        参数:
            data: ConfigAnalysis 模型数据或 None。

        返回:
            Markdown 格式的章节内容。
        """
        section = "## 五、配置说明\n\n"

        if not data:
            return section + "*待补充*\n"

        # 配置文件列表
        if hasattr(data, "config_files") and data.config_files:
            section += "### 配置文件\n\n"
            for config in data.config_files:
                section += f"#### `{config.file_path}`\n\n"
                section += f"- **格式**: {config.format_type}\n"
                section += f"- **用途**: {config.purpose}\n"
                if hasattr(config, "key_settings") and config.key_settings:
                    section += "- **关键配置项**:\n"
                    for setting in config.key_settings:
                        section += f"  - `{setting}`\n"
                section += "\n"

        # 环境变量
        if hasattr(data, "environment_variables") and data.environment_variables:
            section += "### 环境变量\n\n"
            for var in data.environment_variables:
                section += f"- `{var}`\n"
            section += "\n"

        # 关键配置摘要
        if hasattr(data, "key_configurations") and data.key_configurations:
            section += "### 关键配置摘要\n\n"
            for key, value in data.key_configurations.items():
                section += f"- **{key}**: {value}\n"
            section += "\n"

        return section

    @staticmethod
    def _render_risks(data: Any) -> str:
        """
        渲染风险分析章节。

        采用三段式结构：风险、影响、建议。

        参数:
            data: RiskAnalysis 模型数据或 None。

        返回:
            Markdown 格式的章节内容。
        """
        section = "## 六、风险分析\n\n"

        if not data:
            return section + "*待补充*\n"

        # 总体摘要
        if hasattr(data, "summary") and data.summary:
            section += f"**总体评估**: {data.summary}\n\n"

        # 风险列表
        if hasattr(data, "risks") and data.risks:
            section += "### 详细风险\n\n"
            for idx, risk in enumerate(data.risks, 1):
                severity_emoji = {
                    "critical": "🔴",
                    "high": "🟠",
                    "medium": "🟡",
                    "low": "🟢",
                }.get(getattr(risk, "severity", "").lower(), "⚪")

                section += f"#### {idx}. {severity_emoji} {risk.category}\n\n"
                section += f"**风险**: {risk.description}\n\n"

                location = getattr(risk, "location", None)
                if location:
                    section += f"**位置**: `{location}`\n\n"

                section += f"**严重程度**: {risk.severity.upper()}\n\n"

                recommendation = getattr(risk, "recommendation", None)
                if recommendation:
                    section += f"**建议**: {recommendation}\n\n"

                section += "---\n\n"

        return section

    @staticmethod
    def _render_architecture_diagram(data: Any) -> str:
        """
        渲染架构图章节（Mermaid）。

        参数:
            data: ArchitectureDiagram 模型数据或 None。

        返回:
            Markdown 格式的章节内容。
        """
        section = "## 七、架构图\n\n"

        if not data:
            return section + "*待补充*\n"

        # Mermaid 代码块
        if hasattr(data, "mermaid_code") and data.mermaid_code:
            section += "```mermaid\n"
            section += data.mermaid_code.strip() + "\n"
            section += "```\n\n"

        # 架构图说明
        if hasattr(data, "description") and data.description:
            section += f"**说明**: {data.description}\n\n"

        # 组件列表
        if hasattr(data, "components") and data.components:
            section += "### 主要组件\n\n"
            for component in data.components:
                section += f"- {component}\n"
            section += "\n"

        return section

    @staticmethod
    def _render_learning_path(data: Any) -> str:
        """
        渲染学习路线章节。

        参数:
            data: LearningPath 模型数据或 None。

        返回:
            Markdown 格式的章节内容。
        """
        section = "## 八、学习路线\n\n"

        if not data:
            return section + "*待补充*\n"

        # 优先学习模块
        if hasattr(data, "priority_modules") and data.priority_modules:
            section += "### 优先学习模块\n\n"
            for module in data.priority_modules:
                section += f"- {module}\n"
            section += "\n"

        # 建议阅读顺序
        if hasattr(data, "recommended_order") and data.recommended_order:
            section += "### 建议阅读顺序\n\n"
            for idx, item in enumerate(data.recommended_order, 1):
                section += f"{idx}. {item}\n"
            section += "\n"

        # 详细学习步骤
        if hasattr(data, "learning_steps") and data.learning_steps:
            section += "### 详细学习步骤\n\n"
            for step in data.learning_steps:
                section += f"#### 步骤 {step.step_number}: {step.title}\n\n"
                section += f"{step.description}\n\n"

                if hasattr(step, "recommended_files") and step.recommended_files:
                    section += "**推荐阅读文件**:\n\n"
                    for file in step.recommended_files:
                        section += f"- `{file}`\n"
                    section += "\n"

                estimated_time = getattr(step, "estimated_time", None)
                if estimated_time:
                    section += f"**预计耗时**: {estimated_time}\n\n"

        # 总预计耗时
        total_time = getattr(data, "estimated_total_time", None)
        if total_time:
            section += f"**总预计耗时**: {total_time}\n\n"

        return section
