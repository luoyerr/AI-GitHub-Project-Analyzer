"""
规则引擎验证脚本

用于验证技术栈规则是否正确配置
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.analyzer.tech_stack.rules import (
    TECH_STACK_RULES,
    LANGUAGE_RULES,
    FRAMEWORK_RULES,
    BUILD_TOOL_RULES,
    CI_CD_RULES,
    CONTAINER_RULES,
    CLOUD_NATIVE_RULES,
    TESTING_RULES,
)


def main():
    """主函数：验证规则配置"""
    print("=" * 60)
    print("技术栈规则引擎验证")
    print("=" * 60)
    
    # 1. 验证规则分类
    print("\n【1】规则分类统计:")
    print(f"  - 语言识别规则: {len(LANGUAGE_RULES)} 条")
    print(f"  - 框架识别规则: {len(FRAMEWORK_RULES)} 条")
    print(f"  - 构建工具规则: {len(BUILD_TOOL_RULES)} 条")
    print(f"  - CI/CD 规则: {len(CI_CD_RULES)} 条")
    print(f"  - 容器化规则: {len(CONTAINER_RULES)} 条")
    print(f"  - 云原生规则: {len(CLOUD_NATIVE_RULES)} 条")
    print(f"  - 测试框架规则: {len(TESTING_RULES)} 条")
    print(f"  - 总规则分类数: {len(TECH_STACK_RULES)} 类")
    
    # 2. 验证当前项目（AI GitHub Project Analyzer）
    print("\n【2】当前项目识别验证 (AI GitHub Project Analyzer):")
    print(f"  - pyproject.toml -> {LANGUAGE_RULES.get('pyproject.toml', '未找到')}")
    print(f"  - typer 框架: {'typer' in FRAMEWORK_RULES}")
    print(f"  - rich 框架: {'rich' in FRAMEWORK_RULES}")
    print(f"  - loguru 框架: {'loguru' in FRAMEWORK_RULES}")
    print(f"  - pydantic 框架: {'pydantic' in FRAMEWORK_RULES}")
    print(f"  - GitHub Actions: {'.github/workflows' in CI_CD_RULES}")
    
    # 3. 验证 Harness 项目识别
    print("\n【3】Harness 项目识别验证:")
    print(f"  - go.mod -> {LANGUAGE_RULES.get('go.mod', '未找到')}")
    print(f"  - package.json -> {LANGUAGE_RULES.get('package.json', '未找到')}")
    print(f"  - Dockerfile -> {CONTAINER_RULES.get('Dockerfile', {}).get('name', '未找到')}")
    print(f"  - Chart.yaml -> {CLOUD_NATIVE_RULES.get('Chart.yaml', {}).get('name', '未找到')}")
    print(f"  - GitHub Actions: {'.github/workflows' in CI_CD_RULES}")
    
    # 4. 验证 Spring Boot 项目识别
    print("\n【4】Spring Boot 项目识别验证:")
    print(f"  - pom.xml -> {LANGUAGE_RULES.get('pom.xml', '未找到')}")
    print(f"  - spring-boot-starter: {'spring-boot-starter' in FRAMEWORK_RULES}")
    print(f"  - Maven: {BUILD_TOOL_RULES.get('pom.xml', {}).get('name', '未找到')}")
    print(f"  - JUnit: {'junit' in TESTING_RULES}")
    
    # 5. 验证 Vue2 项目识别
    print("\n【5】Vue2 项目识别验证:")
    print(f"  - package.json -> {LANGUAGE_RULES.get('package.json', '未找到')}")
    print(f"  - vue 框架: {'vue' in FRAMEWORK_RULES}")
    print(f"  - Webpack: {'webpack.config.js' in BUILD_TOOL_RULES}")
    print(f"  - npm: {BUILD_TOOL_RULES.get('package.json', {}).get('name', '未找到')}")
    print(f"  - Jest: {'jest' in TESTING_RULES}")
    
    # 6. 验证规则结构
    print("\n【6】规则结构验证:")
    print(f"  - TECH_STACK_RULES 包含的键: {list(TECH_STACK_RULES.keys())}")
    print(f"  - 所有规则分类都已聚合: {set(['language', 'framework', 'build_tool', 'ci_cd', 'container', 'cloud_native', 'testing']) == set(TECH_STACK_RULES.keys())}")
    
    print("\n" + "=" * 60)
    print("验证完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
