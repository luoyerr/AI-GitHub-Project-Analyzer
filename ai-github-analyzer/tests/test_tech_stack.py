"""
技术栈模型测试。

验证 ProjectTechStack 的各项功能：
- 字段默认值
- confidence 范围限制
- to_markdown() 输出格式
- to_dict() 序列化
- merge() 合并逻辑
"""

import sys
from pathlib import Path

# 确保可以导入 src 模块
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.tech_stack import ProjectTechStack


def test_default_values():
    """测试字段默认值。"""
    stack = ProjectTechStack()

    assert stack.languages == []
    assert stack.frameworks == []
    assert stack.libraries == []
    assert stack.build_tools == []
    assert stack.package_managers == []
    assert stack.databases == []
    assert stack.ci_cd == []
    assert stack.containers == []
    assert stack.cloud_native == []
    assert stack.testing_tools == []
    assert stack.confidence == 0.0

    print("✓ 默认值测试通过")


def test_confidence_clamping():
    """测试 confidence 范围限制。"""
    # 正常值
    stack1 = ProjectTechStack(confidence=0.5)
    assert stack1.confidence == 0.5

    # 超过上限
    stack2 = ProjectTechStack(confidence=1.2)
    assert stack2.confidence == 1.0

    # 低于下限
    stack3 = ProjectTechStack(confidence=-0.5)
    assert stack3.confidence == 0.0

    print("✓ Confidence 范围限制测试通过")


def test_to_dict():
    """测试 to_dict() 方法。"""
    stack = ProjectTechStack(
        languages=["Python", "Go"],
        frameworks=["FastAPI"],
        confidence=0.92
    )

    result = stack.to_dict()

    assert isinstance(result, dict)
    assert result["languages"] == ["Python", "Go"]
    assert result["frameworks"] == ["FastAPI"]
    assert result["confidence"] == 0.92

    print("✓ to_dict() 测试通过")


def test_to_markdown():
    """测试 to_markdown() 方法。"""
    stack = ProjectTechStack(
        languages=["Python"],
        frameworks=["Typer"],
        libraries=["Rich", "Loguru"],
        ci_cd=["GitHub Actions"],
        confidence=0.91
    )

    markdown = stack.to_markdown()

    # 验证基本结构
    assert "## 技术栈分析" in markdown
    assert "### 编程语言" in markdown
    assert "- Python" in markdown
    assert "### 框架" in markdown
    assert "- Typer" in markdown
    assert "### 库" in markdown
    assert "- Rich" in markdown
    assert "- Loguru" in markdown
    assert "### CI/CD" in markdown
    assert "- GitHub Actions" in markdown

    # 验证空列表显示为"未识别"
    assert "### 数据库" in markdown
    assert "未识别" in markdown

    # 验证可信度百分比
    assert "### 识别可信度" in markdown
    assert "91%" in markdown

    print("✓ to_markdown() 测试通过")
    print("\n生成的 Markdown 示例：")
    print("-" * 60)
    print(markdown)
    print("-" * 60)


def test_merge():
    """测试 merge() 方法。"""
    # 第一个解析器结果（Python）
    python_stack = ProjectTechStack(
        languages=["Python"],
        frameworks=["FastAPI"],
        libraries=["Pydantic"],
        package_managers=["pip"],
        testing_tools=["Pytest"],
        confidence=0.85
    )

    # 第二个解析器结果（Docker）
    docker_stack = ProjectTechStack(
        containers=["Docker"],
        cloud_native=["Kubernetes"],
        confidence=0.90
    )

    # 第三个解析器结果（GitHub Actions）
    ci_stack = ProjectTechStack(
        ci_cd=["GitHub Actions"],
        confidence=0.75
    )

    # 合并所有结果
    merged = python_stack.merge(docker_stack).merge(ci_stack)

    # 验证合并结果
    assert "Python" in merged.languages
    assert "FastAPI" in merged.frameworks
    assert "Pydantic" in merged.libraries
    assert "pip" in merged.package_managers
    assert "Pytest" in merged.testing_tools
    assert "Docker" in merged.containers
    assert "Kubernetes" in merged.cloud_native
    assert "GitHub Actions" in merged.ci_cd

    # 验证保留最大可信度
    assert merged.confidence == 0.90

    print("✓ merge() 测试通过")
    print("\n合并后的技术栈：")
    print("-" * 60)
    print(merged.to_markdown())
    print("-" * 60)


def test_merge_deduplication():
    """测试 merge() 去重功能。"""
    stack1 = ProjectTechStack(
        languages=["Python", "Go"],
        frameworks=["FastAPI"],
        confidence=0.80
    )

    stack2 = ProjectTechStack(
        languages=["Python", "JavaScript"],  # Python 重复
        frameworks=["FastAPI", "React"],      # FastAPI 重复
        confidence=0.85
    )

    merged = stack1.merge(stack2)

    # 验证去重
    assert len(merged.languages) == 3  # Python, Go, JavaScript
    assert len(merged.frameworks) == 2  # FastAPI, React
    assert "Python" in merged.languages
    assert "Go" in merged.languages
    assert "JavaScript" in merged.languages

    print("✓ merge() 去重测试通过")


if __name__ == "__main__":
    print("开始运行技术栈模型测试...\n")
    print("=" * 60)

    test_default_values()
    test_confidence_clamping()
    test_to_dict()
    test_to_markdown()
    test_merge()
    test_merge_deduplication()

    print("=" * 60)
    print("\n✅ 所有测试通过！")
