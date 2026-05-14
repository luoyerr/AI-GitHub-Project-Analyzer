"""
统一技术栈输出模型。

定义 ProjectTechStack 作为技术栈分析的统一输出协议，
支持多解析器结果合并、Markdown 渲染和字典序列化。
"""

from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field, field_validator


class ProjectTechStack(BaseModel):
    """项目技术栈统一输出模型。

    作为技术栈分析的统一输出协议，整合来自不同解析器
    （如 Python 解析器、Docker 解析器、GitHub Actions 解析器等）
    的技术栈信息。
    """

    # ==================== 技术栈分类字段 ====================

    languages: List[str] = Field(
        default_factory=list,
        description="编程语言列表，例如：Python、Go、JavaScript"
    )

    frameworks: List[str] = Field(
        default_factory=list,
        description="框架列表，例如：FastAPI、Django、React"
    )

    libraries: List[str] = Field(
        default_factory=list,
        description="库/依赖列表，例如：Rich、Loguru、Requests"
    )

    build_tools: List[str] = Field(
        default_factory=list,
        description="构建工具列表，例如：Poetry、Maven、Webpack"
    )

    package_managers: List[str] = Field(
        default_factory=list,
        description="包管理器列表，例如：pip、npm、cargo"
    )

    databases: List[str] = Field(
        default_factory=list,
        description="数据库列表，例如：PostgreSQL、MongoDB、Redis"
    )

    ci_cd: List[str] = Field(
        default_factory=list,
        description="持续集成/持续部署工具列表，例如：GitHub Actions、Jenkins"
    )

    containers: List[str] = Field(
        default_factory=list,
        description="容器化工具列表，例如：Docker、Podman"
    )

    cloud_native: List[str] = Field(
        default_factory=list,
        description="云原生技术列表，例如：Kubernetes、Helm、Istio"
    )

    testing_tools: List[str] = Field(
        default_factory=list,
        description="测试工具列表，例如：Pytest、Jest、JUnit"
    )

    # ==================== 可信度字段 ====================

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="识别可信度，范围 0.0~1.0，超出范围自动限制"
    )

    # ==================== 验证器 ====================

    @field_validator("confidence", mode="before")
    @classmethod
    def clamp_confidence(cls, value: float) -> float:
        """限制可信度在 0.0~1.0 范围内。

        Args:
            value: 原始可信度值

        Returns:
            限制后的可信度值
        """
        if value < 0.0:
            return 0.0
        if value > 1.0:
            return 1.0
        return value

    # ==================== 核心方法 ====================

    def to_dict(self) -> dict:
        """将技术栈模型转换为字典。

        用于 JSON 输出或与其他系统交互。

        Returns:
            包含所有技术栈信息的字典
        """
        return self.model_dump()

    def to_markdown(self) -> str:
        """生成中文 Markdown 格式的技术栈报告。

        空列表显示为“未识别”，可信度转换为百分比格式。

        Returns:
            格式化的 Markdown 字符串
        """
        lines = ["## 技术栈分析\n"]

        # 辅助函数：格式化列表项
        def format_list(items: List[str], title: str) -> str:
            """格式化单个分类的列表项。

            Args:
                items: 技术项列表
                title: 分类标题

            Returns:
                格式化的 Markdown 段落
            """
            section = f"### {title}\n"
            if not items:
                section += "未识别\n"
            else:
                for item in items:
                    section += f"- {item}\n"
            return section + "\n"

        # 按顺序添加各个分类
        lines.append(format_list(self.languages, "编程语言"))
        lines.append(format_list(self.frameworks, "框架"))
        lines.append(format_list(self.libraries, "库"))
        lines.append(format_list(self.build_tools, "构建工具"))
        lines.append(format_list(self.package_managers, "包管理器"))
        lines.append(format_list(self.databases, "数据库"))
        lines.append(format_list(self.ci_cd, "CI/CD"))
        lines.append(format_list(self.containers, "容器化"))
        lines.append(format_list(self.cloud_native, "云原生"))
        lines.append(format_list(self.testing_tools, "测试工具"))

        # 添加可信度
        confidence_percent = int(self.confidence * 100)
        lines.append(f"### 识别可信度\n{confidence_percent}%\n")

        return "".join(lines)

    def merge(self, other: ProjectTechStack) -> ProjectTechStack:
        """合并另一个技术栈模型。

        支持多个解析器结果的统一合并，自动去重并保留最大可信度。

        Args:
            other: 要合并的另一个技术栈模型

        Returns:
            合并后的新技术栈模型
        """
        # 合并所有列表字段并去重
        merged_languages = list(set(self.languages + other.languages))
        merged_frameworks = list(set(self.frameworks + other.frameworks))
        merged_libraries = list(set(self.libraries + other.libraries))
        merged_build_tools = list(set(self.build_tools + other.build_tools))
        merged_package_managers = list(
            set(self.package_managers + other.package_managers)
        )
        merged_databases = list(set(self.databases + other.databases))
        merged_ci_cd = list(set(self.ci_cd + other.ci_cd))
        merged_containers = list(set(self.containers + other.containers))
        merged_cloud_native = list(set(self.cloud_native + other.cloud_native))
        merged_testing_tools = list(set(self.testing_tools + other.testing_tools))

        # 保留最大可信度
        merged_confidence = max(self.confidence, other.confidence)

        return ProjectTechStack(
            languages=merged_languages,
            frameworks=merged_frameworks,
            libraries=merged_libraries,
            build_tools=merged_build_tools,
            package_managers=merged_package_managers,
            databases=merged_databases,
            ci_cd=merged_ci_cd,
            containers=merged_containers,
            cloud_native=merged_cloud_native,
            testing_tools=merged_testing_tools,
            confidence=merged_confidence,
        )
