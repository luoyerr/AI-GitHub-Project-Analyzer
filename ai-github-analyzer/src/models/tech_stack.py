"""
技术栈分析模型。

定义用于存储和展示项目技术栈信息的 Pydantic v2 数据模型。
"""

from pydantic import BaseModel, Field, field_validator
from typing import List


class ProjectTechStack(BaseModel):
    """
    项目技术栈信息模型。
    
    用于存储和分析项目的技术栈组成，包括编程语言、框架、库等。
    所有字段均使用中文注释，支持 UTF-8 编码。
    """
    
    # 编程语言列表（如 Python, JavaScript, Go 等）
    languages: List[str] = Field(
        default_factory=list,
        description="编程语言列表"
    )
    
    # 框架列表（如 FastAPI, Django, React 等）
    frameworks: List[str] = Field(
        default_factory=list,
        description="框架列表"
    )
    
    # 库/依赖包列表（如 requests, numpy, pandas 等）
    libraries: List[str] = Field(
        default_factory=list,
        description="库和依赖包列表"
    )
    
    # 构建工具列表（如 Poetry, Make, CMake 等）
    build_tools: List[str] = Field(
        default_factory=list,
        description="构建工具列表"
    )
    
    # 包管理器列表（如 pip, npm, yarn 等）
    package_managers: List[str] = Field(
        default_factory=list,
        description="包管理器列表"
    )
    
    # 数据库列表（如 PostgreSQL, MySQL, MongoDB 等）
    databases: List[str] = Field(
        default_factory=list,
        description="数据库列表"
    )
    
    # CI/CD 工具列表（如 GitHub Actions, Jenkins 等）
    ci_cd: List[str] = Field(
        default_factory=list,
        description="CI/CD 工具列表"
    )
    
    # 容器化技术列表（如 Docker, Kubernetes 等）
    containers: List[str] = Field(
        default_factory=list,
        description="容器化技术列表"
    )
    
    # 云原生技术列表（如 AWS, Azure, GCP 等）
    cloud_native: List[str] = Field(
        default_factory=list,
        description="云原生技术列表"
    )
    
    # 测试工具列表（如 pytest, Jest, Selenium 等）
    testing_tools: List[str] = Field(
        default_factory=list,
        description="测试工具列表"
    )
    
    # 置信度评分（0.0 ~ 1.0）
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="技术栈识别的置信度（0.0 到 1.0）"
    )
    
    @field_validator('confidence')
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        """验证置信度值在有效范围内。"""
        if not (0.0 <= v <= 1.0):
            raise ValueError("置信度必须在 0.0 到 1.0 之间")
        return v
    
    def to_markdown(self) -> str:
        """
        将技术栈信息转换为中文 Markdown 格式。
        
        Returns:
            str: 格式化的 Markdown 字符串
            
        Example:
            ## 技术栈分析
            
            ### 编程语言
            - Python
            - JavaScript
            
            ### 框架
            - FastAPI
            
            ### 构建工具
            - Poetry
            
            ### CI/CD
            - GitHub Actions
            
            如果某个分类为空，则显示"未识别"
        """
        lines = ["## 技术栈分析\n"]
        
        # 定义分类映射（英文键 -> 中文标题）
        categories = {
            "languages": "编程语言",
            "frameworks": "框架",
            "libraries": "库和依赖",
            "build_tools": "构建工具",
            "package_managers": "包管理器",
            "databases": "数据库",
            "ci_cd": "CI/CD",
            "containers": "容器化",
            "cloud_native": "云原生",
            "testing_tools": "测试工具",
        }
        
        # 遍历每个分类并生成 Markdown
        for key, title in categories.items():
            items = getattr(self, key)
            lines.append(f"### {title}")
            
            if items:
                # 如果有内容，列出所有项目
                for item in items:
                    lines.append(f"- {item}")
            else:
                # 如果为空，显示未识别
                lines.append("未识别")
            
            lines.append("")  # 空行分隔
        
        # 添加置信度信息
        lines.append(f"### 置信度")
        lines.append(f"{self.confidence:.1%}\n")
        
        return "\n".join(lines)
