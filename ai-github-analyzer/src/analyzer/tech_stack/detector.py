"""
技术栈检测器

职责：
基于规则匹配实现确定性的技术栈检测。

设计原则：
1. 配置驱动 - 禁止硬编码，全部从 rules.py 读取规则
2. 确定性检测 - 禁止 AI 推理、禁止调用大模型、禁止猜测
3. 异常安全 - 解析失败时记录 warning 日志并继续分析
4. 高内聚低耦合 - 拆分为多个私有方法，避免巨型函数
5. 中文注释和日志 - 所有注释和日志使用中文

检测流程（固定顺序）：
1. 文件规则检测 - 通过特征文件识别语言、构建工具、包管理器
2. 依赖规则检测 - 解析依赖文件识别框架和库
3. 目录规则检测 - 通过目录结构识别 CI/CD、容器化、云原生工具
4. 统一结果合并 - 自动去重
5. confidence 计算 - 文件规则 0.4 + 依赖规则 0.4 + infra 0.2

支持的技术栈（第一阶段）：
- Python
- Node.js (JavaScript/TypeScript)
- Java
- Go
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Set

from loguru import logger

from src.analyzer.tech_stack.rules import TECH_STACK_RULES
from src.models.tech_stack import ProjectTechStack
from src.scanner.models import RepositorySnapshot


class TechStackDetector:
    """技术栈检测器。

    基于规则匹配实现确定性的技术栈检测，不使用 AI 推理。

    输入：RepositorySnapshot（仓库扫描结果）
    输出：ProjectTechStack（项目技术栈）
    """

    # 置信度权重配置
    CONFIDENCE_WEIGHT_FILES = 0.4  # 文件规则权重
    CONFIDENCE_WEIGHT_DEPS = 0.4  # 依赖规则权重
    CONFIDENCE_WEIGHT_INFRA = 0.2  # 基础设施权重

    def __init__(self):
        """初始化技术栈检测器。

        从 rules.py 加载所有规则配置。
        """
        self.language_rules = TECH_STACK_RULES["language"]
        self.framework_rules = TECH_STACK_RULES["framework"]
        self.build_tool_rules = TECH_STACK_RULES["build_tool"]
        self.ci_cd_rules = TECH_STACK_RULES["ci_cd"]
        self.container_rules = TECH_STACK_RULES["container"]
        self.cloud_native_rules = TECH_STACK_RULES["cloud_native"]
        self.testing_rules = TECH_STACK_RULES["testing"]

        logger.info("技术栈检测器已初始化，规则加载完成")

    def detect(self, scan_result: RepositorySnapshot) -> ProjectTechStack:
        """执行技术栈检测。

        Args:
            scan_result: 仓库扫描结果

        Returns:
            项目技术栈模型
        """
        logger.info(f"开始技术栈检测，仓库：{scan_result.repo_name}")

        # 步骤 1：文件规则检测
        file_result = self._detect_by_files(scan_result)

        # 步骤 2：依赖规则检测
        deps_result = self._detect_dependencies(scan_result)

        # 步骤 3：目录规则检测
        dir_result = self._detect_directories(scan_result)

        # 步骤 4：统一结果合并
        merged_result = self._merge_results(file_result, deps_result, dir_result)

        # 步骤 5：confidence 计算
        final_result = self._calculate_confidence(
            merged_result, file_result, deps_result, dir_result
        )

        logger.info(
            f"技术栈检测完成，识别到 {len(final_result.languages)} 种语言，"
            f"{len(final_result.frameworks)} 个框架，"
            f"可信度：{final_result.confidence:.2f}"
        )

        return final_result

    def _detect_by_files(self, snapshot: RepositorySnapshot) -> ProjectTechStack:
        """通过文件规则检测技术栈。

        根据仓库中的特征文件识别：
        - 编程语言
        - 构建工具
        - 包管理器

        Args:
            snapshot: 仓库快照

        Returns:
            部分技术栈结果（仅包含文件和目录检测到的内容）
        """
        logger.info("开始文件规则检测")

        languages: Set[str] = set()
        build_tools: Set[str] = set()
        package_managers: Set[str] = set()

        # 遍历所有文件，匹配规则
        for file_meta in snapshot.files:
            file_name = Path(file_meta.relative_path).name
            file_extension = file_meta.extension

            # 检查文件名匹配（如 package.json, requirements.txt）
            if file_name in self.language_rules:
                lang = self.language_rules[file_name]
                languages.add(lang)
                logger.debug(f"通过文件 '{file_name}' 识别语言：{lang}")

            # 检查构建工具规则
            if file_name in self.build_tool_rules:
                tool_info = self.build_tool_rules[file_name]
                tool_name = tool_info["name"]
                category = tool_info["category"]

                if category == "Build Tool":
                    build_tools.add(tool_name)
                elif category == "Package Manager":
                    package_managers.add(tool_name)

                logger.debug(f"通过文件 '{file_name}' 识别工具：{tool_name} ({category})")

            # 检查文件扩展名匹配（如 *.py, *.js）
            if file_extension:
                pattern = f"*.{file_extension.lstrip('.')}"
                if pattern in self.language_rules:
                    lang = self.language_rules[pattern]
                    languages.add(lang)
                    logger.debug(f"通过扩展名 '{pattern}' 识别语言：{lang}")

        result = ProjectTechStack(
            languages=list(languages),
            build_tools=list(build_tools),
            package_managers=list(package_managers),
        )

        logger.info(
            f"文件规则检测完成：{len(languages)} 种语言，"
            f"{len(build_tools)} 个构建工具，"
            f"{len(package_managers)} 个包管理器"
        )

        return result

    def _detect_dependencies(self, snapshot: RepositorySnapshot) -> ProjectTechStack:
        """通过依赖规则检测技术栈。

        解析依赖配置文件识别：
        - 框架
        - 库
        - 测试工具

        Args:
            snapshot: 仓库快照

        Returns:
            部分技术栈结果（仅包含依赖检测到的内容）
        """
        logger.info("开始依赖规则检测")

        frameworks: Set[str] = set()
        libraries: Set[str] = set()
        testing_tools: Set[str] = set()

        # 遍历所有文件，查找依赖配置文件
        for file_meta in snapshot.files:
            file_name = Path(file_meta.relative_path).name
            file_path = Path(snapshot.repo_path) / file_meta.relative_path

            try:
                if file_name == "package.json":
                    self._parse_package_json(
                        file_path, frameworks, libraries, testing_tools
                    )
                elif file_name == "requirements.txt":
                    self._parse_requirements_txt(
                        file_path, frameworks, libraries, testing_tools
                    )
                elif file_name == "pyproject.toml":
                    self._parse_pyproject_toml(
                        file_path, frameworks, libraries, testing_tools
                    )
                elif file_name == "pom.xml":
                    self._parse_pom_xml(
                        file_path, frameworks, libraries, testing_tools
                    )
                elif file_name == "go.mod":
                    self._parse_go_mod(
                        file_path, frameworks, libraries, testing_tools
                    )
            except Exception as e:
                logger.warning(f"解析依赖文件 '{file_name}' 失败：{str(e)}，跳过该文件")
                continue

        result = ProjectTechStack(
            frameworks=list(frameworks),
            libraries=list(libraries),
            testing_tools=list(testing_tools),
        )

        logger.info(
            f"依赖规则检测完成：{len(frameworks)} 个框架，"
            f"{len(libraries)} 个库，"
            f"{len(testing_tools)} 个测试工具"
        )

        return result

    def _detect_directories(self, snapshot: RepositorySnapshot) -> ProjectTechStack:
        """通过目录规则检测技术栈。

        根据目录结构和特殊文件识别：
        - CI/CD 工具
        - 容器化工具
        - 云原生工具

        Args:
            snapshot: 仓库快照

        Returns:
            部分技术栈结果（仅包含基础设施检测到的内容）
        """
        logger.info("开始目录规则检测")

        ci_cd: Set[str] = set()
        containers: Set[str] = set()
        cloud_native: Set[str] = set()

        # 收集所有目录路径
        dir_paths = [dir_meta.relative_path for dir_meta in snapshot.directories]
        # 收集所有文件路径
        file_paths = [file_meta.relative_path for file_meta in snapshot.files]

        # 检查 CI/CD 规则
        for dir_path in dir_paths:
            normalized_path = Path(dir_path).as_posix()

            # 检查 .github/workflows
            if ".github/workflows" in normalized_path:
                ci_cd.add("GitHub Actions")
                logger.debug(f"通过目录 '{dir_path}' 识别 CI/CD：GitHub Actions")

        # 检查文件级别的 CI/CD 规则
        for file_path in file_paths:
            file_name = Path(file_path).name

            if file_name in self.ci_cd_rules:
                ci_tool = self.ci_cd_rules[file_name]
                ci_cd.add(ci_tool)
                logger.debug(f"通过文件 '{file_name}' 识别 CI/CD：{ci_tool}")

        # 检查容器化规则
        for file_path in file_paths:
            file_name = Path(file_path).name

            if file_name in self.container_rules:
                container_info = self.container_rules[file_name]
                container_name = container_info["name"]
                containers.add(container_name)
                logger.debug(f"通过文件 '{file_name}' 识别容器化：{container_name}")

        # 检查云原生规则
        for dir_path in dir_paths:
            normalized_path = Path(dir_path).as_posix()

            # 检查 charts/ 或 helm/ 目录
            if normalized_path.endswith("/charts") or normalized_path == "charts":
                cloud_native.add("Helm")
                logger.debug(f"通过目录 '{dir_path}' 识别云原生：Helm")
            elif normalized_path.endswith("/helm") or normalized_path == "helm":
                cloud_native.add("Helm")
                logger.debug(f"通过目录 '{dir_path}' 识别云原生：Helm")

            # 检查 k8s/ 或 kubernetes/ 目录
            elif normalized_path.endswith("/k8s") or normalized_path == "k8s":
                cloud_native.add("Kubernetes")
                logger.debug(f"通过目录 '{dir_path}' 识别云原生：Kubernetes")
            elif (
                normalized_path.endswith("/kubernetes") or normalized_path == "kubernetes"
            ):
                cloud_native.add("Kubernetes")
                logger.debug(f"通过目录 '{dir_path}' 识别云原生：Kubernetes")

        # 检查文件级别的云原生规则
        for file_path in file_paths:
            file_name = Path(file_path).name

            if file_name == "Chart.yaml":
                cloud_native.add("Helm")
                logger.debug("通过文件 'Chart.yaml' 识别云原生：Helm")

        result = ProjectTechStack(
            ci_cd=list(ci_cd),
            containers=list(containers),
            cloud_native=list(cloud_native),
        )

        logger.info(
            f"目录规则检测完成：{len(ci_cd)} 个 CI/CD 工具，"
            f"{len(containers)} 个容器化工具，"
            f"{len(cloud_native)} 个云原生工具"
        )

        return result

    def _parse_package_json(
        self,
        file_path: Path,
        frameworks: Set[str],
        libraries: Set[str],
        testing_tools: Set[str],
    ) -> None:
        """解析 package.json 文件。

        Args:
            file_path: package.json 文件路径
            frameworks: 框架集合（输出参数）
            libraries: 库集合（输出参数）
            testing_tools: 测试工具集合（输出参数）
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 合并 dependencies 和 devDependencies
            all_deps = {}
            if "dependencies" in data:
                all_deps.update(data["dependencies"])
            if "devDependencies" in data:
                all_deps.update(data["devDependencies"])

            # 遍历依赖，匹配规则
            for dep_name in all_deps.keys():
                dep_lower = dep_name.lower()

                # 检查框架规则
                for rule_key, rule_value in self.framework_rules.items():
                    if rule_key.lower() in dep_lower:
                        framework_name = rule_value["name"]
                        frameworks.add(framework_name)
                        logger.debug(f"通过依赖 '{dep_name}' 识别框架：{framework_name}")

                # 检查测试工具规则
                for rule_key, rule_value in self.testing_rules.items():
                    if rule_key.lower() in dep_lower:
                        tool_name = rule_value["name"]
                        testing_tools.add(tool_name)
                        logger.debug(f"通过依赖 '{dep_name}' 识别测试工具：{tool_name}")

                # 其他依赖归类为库
                # 排除已识别的框架和测试工具
                is_framework = any(
                    rule_key.lower() in dep_lower
                    for rule_key in self.framework_rules.keys()
                )
                is_testing = any(
                    rule_key.lower() in dep_lower
                    for rule_key in self.testing_rules.keys()
                )

                if not is_framework and not is_testing:
                    # 只添加知名的库，避免添加过多普通依赖
                    known_libraries = [
                        "lodash",
                        "axios",
                        "moment",
                        "dayjs",
                        "uuid",
                        "chalk",
                        "commander",
                        "dotenv",
                        "cors",
                        "helmet",
                        "morgan",
                    ]
                    if dep_lower in known_libraries:
                        libraries.add(dep_name)
                        logger.debug(f"通过依赖 '{dep_name}' 识别库")

        except json.JSONDecodeError as e:
            logger.warning(f"package.json JSON 解析失败：{str(e)}")
        except Exception as e:
            logger.warning(f"解析 package.json 时发生错误：{str(e)}")

    def _parse_requirements_txt(
        self,
        file_path: Path,
        frameworks: Set[str],
        libraries: Set[str],
        testing_tools: Set[str],
    ) -> None:
        """解析 requirements.txt 文件。

        Args:
            file_path: requirements.txt 文件路径
            frameworks: 框架集合（输出参数）
            libraries: 库集合（输出参数）
            testing_tools: 测试工具集合（输出参数）
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()

                # 跳过空行和注释
                if not line or line.startswith("#"):
                    continue

                # 提取包名（去除版本信息）
                # 支持格式：package==1.0.0, package>=1.0.0, package~=1.0.0
                match = re.match(r"^([a-zA-Z0-9_-]+)", line)
                if match:
                    package_name = match.group(1).lower()

                    # 检查框架规则
                    for rule_key, rule_value in self.framework_rules.items():
                        if rule_key.lower() == package_name:
                            framework_name = rule_value["name"]
                            frameworks.add(framework_name)
                            logger.debug(
                                f"通过依赖 '{package_name}' 识别框架：{framework_name}"
                            )

                    # 检查测试工具规则
                    for rule_key, rule_value in self.testing_rules.items():
                        if rule_key.lower() == package_name:
                            tool_name = rule_value["name"]
                            testing_tools.add(tool_name)
                            logger.debug(
                                f"通过依赖 '{package_name}' 识别测试工具：{tool_name}"
                            )

                    # 检查库规则（主要是 Python 生态的知名库）
                    python_libraries = [
                        "rich",
                        "loguru",
                        "pydantic",
                        "requests",
                        "httpx",
                        "sqlalchemy",
                        "celery",
                        "redis",
                        "pillow",
                        "numpy",
                        "pandas",
                        "scikit-learn",
                        "typer",
                    ]
                    if package_name in python_libraries:
                        # 将首字母大写作为库名
                        lib_name = package_name.capitalize()
                        if package_name == "pydantic":
                            lib_name = "Pydantic"
                        elif package_name == "typer":
                            lib_name = "Typer"
                        libraries.add(lib_name)
                        logger.debug(f"通过依赖 '{package_name}' 识别库：{lib_name}")

        except Exception as e:
            logger.warning(f"解析 requirements.txt 时发生错误：{str(e)}")

    def _parse_pyproject_toml(
        self,
        file_path: Path,
        frameworks: Set[str],
        libraries: Set[str],
        testing_tools: Set[str],
    ) -> None:
        """解析 pyproject.toml 文件。

        Args:
            file_path: pyproject.toml 文件路径
            frameworks: 框架集合（输出参数）
            libraries: 库集合（输出参数）
            testing_tools: 测试工具集合（输出参数）
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 提取 dependencies 数组中的依赖项
            # 支持格式：dependencies = ["typer>=0.9.0", "rich>=13.7.0", ...]
            in_dependencies = False
            for line in content.split("\n"):
                line_stripped = line.strip()

                # 检测 dependencies 数组开始
                if line_stripped.startswith("dependencies = ["):
                    in_dependencies = True
                    # 检查是否在同一行有结束括号
                    if "]" in line_stripped:
                        # 单行格式：dependencies = ["typer", "rich"]
                        deps_str = line_stripped.split("=", 1)[1].strip()
                        deps_str = deps_str.strip("[]")
                        # 解析依赖项
                        self._parse_dependency_list(
                            deps_str, frameworks, libraries, testing_tools
                        )
                        in_dependencies = False
                    continue

                # 如果在 dependencies 数组中
                if in_dependencies:
                    # 检测数组结束
                    if line_stripped == "]":
                        in_dependencies = False
                        continue

                    # 解析依赖项（去除引号和版本号）
                    # 格式："typer>=0.9.0",
                    match = re.match(r'^"([a-zA-Z0-9_-]+)', line_stripped)
                    if match:
                        package_name = match.group(1).lower()
                        self._check_package_against_rules(
                            package_name, frameworks, libraries, testing_tools
                        )

        except Exception as e:
            logger.warning(f"解析 pyproject.toml 时发生错误：{str(e)}")

    def _parse_pom_xml(
        self,
        file_path: Path,
        frameworks: Set[str],
        libraries: Set[str],
        testing_tools: Set[str],
    ) -> None:
        """解析 pom.xml 文件。

        Args:
            file_path: pom.xml 文件路径
            frameworks: 框架集合（输出参数）
            libraries: 库集合（输出参数）
            testing_tools: 测试工具集合（输出参数）
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 简单解析：查找 artifactId
            # 使用正则表达式提取 <artifactId>xxx</artifactId>
            artifact_ids = re.findall(r"<artifactId>([^<]+)</artifactId>", content)

            for artifact_id in artifact_ids:
                artifact_lower = artifact_id.lower()

                # 检查框架规则
                for rule_key, rule_value in self.framework_rules.items():
                    if rule_key.lower() in artifact_lower:
                        framework_name = rule_value["name"]
                        frameworks.add(framework_name)
                        logger.debug(
                            f"通过依赖 '{artifact_id}' 识别框架：{framework_name}"
                        )

                # 检查测试工具规则
                for rule_key, rule_value in self.testing_rules.items():
                    if rule_key.lower() in artifact_lower:
                        tool_name = rule_value["name"]
                        testing_tools.add(tool_name)
                        logger.debug(
                            f"通过依赖 '{artifact_id}' 识别测试工具：{tool_name}"
                        )

        except Exception as e:
            logger.warning(f"解析 pom.xml 时发生错误：{str(e)}")

    def _parse_go_mod(
        self,
        file_path: Path,
        frameworks: Set[str],
        libraries: Set[str],
        testing_tools: Set[str],
    ) -> None:
        """解析 go.mod 文件。

        Args:
            file_path: go.mod 文件路径
            frameworks: 框架集合（输出参数）
            libraries: 库集合（输出参数）
            testing_tools: 测试工具集合（输出参数）
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            in_require = False
            for line in lines:
                line = line.strip()

                # 检测 require 块开始
                if line.startswith("require ("):
                    in_require = True
                    continue

                # 检测 require 块结束
                if line == ")" and in_require:
                    in_require = False
                    continue

                # 解析单个 require 语句
                if in_require or line.startswith("require "):
                    # 提取模块路径
                    # 格式：github.com/gin-gonic/gin v1.9.0
                    parts = line.split()
                    if len(parts) >= 2:
                        module_path = parts[0] if not line.startswith("require ") else parts[1]

                        # 提取最后一段作为包名
                        package_name = module_path.split("/")[-1].lower()

                        # 检查框架规则
                        for rule_key, rule_value in self.framework_rules.items():
                            if rule_key.lower() == package_name:
                                framework_name = rule_value["name"]
                                frameworks.add(framework_name)
                                logger.debug(
                                    f"通过依赖 '{module_path}' 识别框架：{framework_name}"
                                )

                        # 检查测试工具规则
                        for rule_key, rule_value in self.testing_rules.items():
                            if rule_key.lower() == package_name:
                                tool_name = rule_value["name"]
                                testing_tools.add(tool_name)
                                logger.debug(
                                    f"通过依赖 '{module_path}' 识别测试工具：{tool_name}"
                                )

        except Exception as e:
            logger.warning(f"解析 go.mod 时发生错误：{str(e)}")

    def _parse_dependency_list(
        self,
        deps_str: str,
        frameworks: Set[str],
        libraries: Set[str],
        testing_tools: Set[str],
    ) -> None:
        """解析依赖列表字符串。

        Args:
            deps_str: 依赖列表字符串，如 '"typer>=0.9.0", "rich>=13.7.0"'
            frameworks: 框架集合（输出参数）
            libraries: 库集合（输出参数）
            testing_tools: 测试工具集合（输出参数）
        """
        # 分割依赖项
        deps = [dep.strip() for dep in deps_str.split(",") if dep.strip()]

        for dep in deps:
            # 提取包名（去除引号和版本号）
            match = re.match(r'^"([a-zA-Z0-9_-]+)', dep)
            if match:
                package_name = match.group(1).lower()
                self._check_package_against_rules(
                    package_name, frameworks, libraries, testing_tools
                )

    def _check_package_against_rules(
        self,
        package_name: str,
        frameworks: Set[str],
        libraries: Set[str],
        testing_tools: Set[str],
    ) -> None:
        """检查包名是否匹配规则。

        Args:
            package_name: 包名（小写）
            frameworks: 框架集合（输出参数）
            libraries: 库集合（输出参数）
            testing_tools: 测试工具集合（输出参数）
        """
        # 标记是否已识别为框架或测试工具
        is_framework = False
        is_testing = False

        # 检查框架规则
        for rule_key, rule_value in self.framework_rules.items():
            if rule_key.lower() == package_name:
                framework_name = rule_value["name"]
                frameworks.add(framework_name)
                logger.debug(f"通过依赖 '{package_name}' 识别框架：{framework_name}")
                is_framework = True

        # 检查测试工具规则
        for rule_key, rule_value in self.testing_rules.items():
            if rule_key.lower() == package_name:
                tool_name = rule_value["name"]
                testing_tools.add(tool_name)
                logger.debug(f"通过依赖 '{package_name}' 识别测试工具：{tool_name}")
                is_testing = True

        # 如果已经识别为框架或测试工具，就不再归类为库
        if is_framework or is_testing:
            return

        # 检查库规则（Python 生态的知名库）
        python_libraries = [
            "rich",
            "loguru",
            "pydantic",
            "requests",
            "httpx",
            "sqlalchemy",
            "celery",
            "redis",
            "pillow",
            "numpy",
            "pandas",
            "scikit-learn",
            "typer",
        ]
        if package_name in python_libraries:
            # 将首字母大写作为库名
            lib_name = package_name.capitalize()
            if package_name == "pydantic":
                lib_name = "Pydantic"
            elif package_name == "typer":
                lib_name = "Typer"
            libraries.add(lib_name)
            logger.debug(f"通过依赖 '{package_name}' 识别库：{lib_name}")

    def _merge_results(
        self,
        file_result: ProjectTechStack,
        deps_result: ProjectTechStack,
        dir_result: ProjectTechStack,
    ) -> ProjectTechStack:
        """合并三个检测结果。

        使用 ProjectTechStack.merge() 方法自动去重。

        Args:
            file_result: 文件规则检测结果
            deps_result: 依赖规则检测结果
            dir_result: 目录规则检测结果

        Returns:
            合并后的技术栈结果
        """
        logger.info("开始合并检测结果")

        # 先合并文件和依赖结果
        merged = file_result.merge(deps_result)

        # 再合并目录结果
        merged = merged.merge(dir_result)

        logger.info("检测结果合并完成")

        return merged

    def _calculate_confidence(
        self,
        merged_result: ProjectTechStack,
        file_result: ProjectTechStack,
        deps_result: ProjectTechStack,
        dir_result: ProjectTechStack,
    ) -> ProjectTechStack:
        """计算最终的可信度。

        计算公式：
        confidence = (文件规则得分 × 0.4) + (依赖规则得分 × 0.4) + (infra 得分 × 0.2)

        规则：
        - 文件规则得分：检测到语言得 1.0，否则 0.0
        - 依赖规则得分：检测到框架或库得 1.0，否则 0.0
        - infra 得分：检测到 CI/CD、容器化或云原生工具得 1.0，否则 0.0

        最后 clamp 到 0~1 范围。

        Args:
            merged_result: 合并后的技术栈结果
            file_result: 文件规则检测结果
            deps_result: 依赖规则检测结果
            dir_result: 目录规则检测结果

        Returns:
            带有可信度的最终技术栈结果
        """
        logger.info("开始计算可信度")

        # 文件规则得分
        file_score = 1.0 if merged_result.languages else 0.0

        # 依赖规则得分
        deps_score = (
            1.0 if (merged_result.frameworks or merged_result.libraries) else 0.0
        )

        # infra 得分
        infra_score = (
            1.0
            if (
                merged_result.ci_cd
                or merged_result.containers
                or merged_result.cloud_native
            )
            else 0.0
        )

        # 加权计算
        confidence = (
            file_score * self.CONFIDENCE_WEIGHT_FILES
            + deps_score * self.CONFIDENCE_WEIGHT_DEPS
            + infra_score * self.CONFIDENCE_WEIGHT_INFRA
        )

        # Clamp 到 0~1 范围（虽然理论上不会超出，但为了安全）
        confidence = max(0.0, min(1.0, confidence))

        logger.info(
            f"可信度计算完成：文件={file_score:.1f}, 依赖={deps_score:.1f}, "
            f"infra={infra_score:.1f}, 最终={confidence:.2f}"
        )

        # 创建新的结果对象，保留所有字段，只更新 confidence
        final_result = ProjectTechStack(
            languages=merged_result.languages,
            frameworks=merged_result.frameworks,
            libraries=merged_result.libraries,
            build_tools=merged_result.build_tools,
            package_managers=merged_result.package_managers,
            databases=merged_result.databases,
            ci_cd=merged_result.ci_cd,
            containers=merged_result.containers,
            cloud_native=merged_result.cloud_native,
            testing_tools=merged_result.testing_tools,
            confidence=confidence,
        )

        return final_result
