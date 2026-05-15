"""
上下文选择器 - 智能文件筛选模块。

负责根据预定义规则和模式，从扫描结果中智能筛选出对分析最有价值的文件。
包括入口文件、配置文件、核心模块、文档等的识别和过滤。

职责边界：
    - 只做文件筛选（基于路径和文件名）
    - 禁止读取文件内容
    - 禁止 token 计算
    - 禁止排序逻辑
    - 禁止裁剪逻辑
    - 返回 List[Path] 供后续处理
"""

from pathlib import Path
from typing import Dict, List

from loguru import logger

from .rules import (
    ROOT_IMPORTANT_FILES,
    ENTRY_PATTERNS,
    CONFIG_PATTERNS,
    CORE_MODULE_PATTERNS,
    DOCUMENT_PATTERNS,
    IGNORE_PATTERNS,
    SENSITIVE_PATTERNS,
    SENSITIVE_ALLOWLIST,
    LOW_VALUE_EXTENSIONS,
)
from ..scanner.models import RepositorySnapshot, FileMetadata


class ContextSelector:
    """
    上下文选择器 - 智能文件筛选。

    职责：
        从仓库扫描结果中智能筛选高价值文件。
        目标是从数千个文件筛选到几十~一百多个文件，
        供 Context Builder 后续处理。

    筛选流程：
        1. 过滤忽略目录（node_modules, .git, dist 等）
        2. 过滤敏感文件（.env, .pem, .key 等，但允许 .env.example）
        3. 选择根目录高价值文件（README.md, Dockerfile, package.json 等）
        4. 选择入口文件（main.py, app.js, index.ts 等）
        5. 选择配置文件（application.yml, vite.config.ts 等）
        6. 选择核心业务模块（controller, service, domain 等）
        7. 选择文档文件（README.md, docs/, ARCHITECTURE.md 等）
        8. 过滤低价值文件（.log, .lock, .map, .min.js 等）
        9. 去重（保持顺序）

    注意：
        - 本类只负责筛选，不做文件读取
        - 本类不做 token 计算
        - 本类不做排序
        - 本类不做裁剪
    """

    def __init__(self) -> None:
        """初始化上下文选择器。"""
        logger.debug("初始化上下文选择器")

    def select(self, snapshot: RepositorySnapshot) -> List[Path]:
        """
        执行完整的文件筛选流程（总入口）。

        流程固定：
            1. 过滤忽略目录
            2. 过滤敏感文件
            3. 选择根目录文件
            4. 选择入口文件
            5. 选择配置文件
            6. 选择核心模块
            7. 选择文档
            8. 过滤低价值文件
            9. 去重

        参数：
            snapshot: 仓库扫描快照，包含所有文件和目录信息

        返回：
            筛选后的高价值文件路径列表（绝对路径）
        """
        logger.info(f"开始文件筛选，原始文件数：{len(snapshot.files)}")

        repo_path = Path(snapshot.repo_path)

        # 步骤 1：过滤忽略目录
        filtered_files = self._filter_ignored(snapshot.files, repo_path)
        logger.debug(f"过滤忽略目录后剩余文件数：{len(filtered_files)}")

        # 步骤 2：过滤敏感文件
        filtered_files = self._filter_sensitive_files(filtered_files, repo_path)
        logger.debug(f"过滤敏感文件后剩余文件数：{len(filtered_files)}")

        # 步骤 3-7：选择各类高价值文件
        selected_files: List[Path] = []

        # 选择根目录文件
        root_files = self._select_root_files(filtered_files, repo_path)
        selected_files.extend(root_files)
        logger.debug(f"选择根目录文件数：{len(root_files)}")

        # 选择入口文件
        entry_files = self._select_entry_files(filtered_files, repo_path)
        selected_files.extend(entry_files)
        logger.debug(f"选择入口文件数：{len(entry_files)}")

        # 选择配置文件
        config_files = self._select_config_files(filtered_files, repo_path)
        selected_files.extend(config_files)
        logger.debug(f"选择配置文件数：{len(config_files)}")

        # 选择核心模块
        core_files = self._select_core_modules(filtered_files, repo_path)
        selected_files.extend(core_files)
        logger.debug(f"选择核心模块文件数：{len(core_files)}")

        # 选择文档
        doc_files = self._select_docs(filtered_files, repo_path)
        selected_files.extend(doc_files)
        logger.debug(f"选择文档文件数：{len(doc_files)}")

        # 步骤 8：过滤低价值文件
        selected_files = self._filter_low_value_files(selected_files)
        logger.debug(f"过滤低价值文件后剩余文件数：{len(selected_files)}")

        # 步骤 9：去重
        final_files = self._deduplicate(selected_files)
        logger.info(f"文件筛选完成，最终文件数：{len(final_files)}")

        return final_files

    def _filter_ignored(
        self, files: List[FileMetadata], repo_path: Path
    ) -> List[FileMetadata]:
        """
        过滤忽略目录中的文件。

        忽略以下目录：
            - node_modules
            - .git
            - dist
            - coverage
            - build
            - temp
            - 其他在 rules.py 中定义的 IGNORE_PATTERNS

        参数：
            files: 待过滤的文件列表
            repo_path: 仓库根路径

        返回：
            过滤后的文件列表
        """
        filtered = []
        for file_meta in files:
            file_path = repo_path / file_meta.relative_path
            # 检查文件路径是否包含任何忽略模式
            if not any(pattern in file_path.parts for pattern in IGNORE_PATTERNS):
                filtered.append(file_meta)
            else:
                logger.debug(f"忽略文件（匹配忽略模式）：{file_meta.relative_path}")

        return filtered

    def _filter_sensitive_files(
        self, files: List[FileMetadata], repo_path: Path
    ) -> List[FileMetadata]:
        """
        过滤敏感文件。

        过滤以下敏感文件：
            - .env
            - .pem
            - .key
            - secret
            - token
            - credential
            - private_key

        允许以下例外：
            - .env.example（在 SENSITIVE_ALLOWLIST 中）

        参数：
            files: 待过滤的文件列表
            repo_path: 仓库根路径

        返回：
            过滤后的文件列表
        """
        filtered = []
        for file_meta in files:
            file_name = file_meta.relative_path.lower()

            # 检查是否在允许列表中
            is_allowed = any(
                file_meta.relative_path.endswith(allowed)
                for allowed in SENSITIVE_ALLOWLIST
            )

            if is_allowed:
                filtered.append(file_meta)
                continue

            # 检查是否匹配敏感模式
            is_sensitive = any(pattern in file_name for pattern in SENSITIVE_PATTERNS)

            if is_sensitive:
                logger.debug(f"过滤敏感文件：{file_meta.relative_path}")
            else:
                filtered.append(file_meta)

        return filtered

    def _select_root_files(
        self, files: List[FileMetadata], repo_path: Path
    ) -> List[Path]:
        """
        选择根目录下的高价值文件。

        挑选以下根目录文件：
            - README.md
            - Dockerfile
            - package.json
            - pom.xml
            - requirements.txt
            - 其他在 rules.py 中定义的 ROOT_IMPORTANT_FILES

        限制：
            - 只允许仓库根目录（relative_path 不包含 '/'）
            - 禁止递归子目录

        参数：
            files: 待筛选的文件列表
            repo_path: 仓库根路径

        返回：
            根目录高价值文件的绝对路径列表
        """
        selected = []
        for file_meta in files:
            # 只处理根目录文件（relative_path 不包含路径分隔符）
            if "/" in file_meta.relative_path or "\\" in file_meta.relative_path:
                continue

            # 检查是否匹配根目录重要文件
            if file_meta.relative_path in ROOT_IMPORTANT_FILES:
                abs_path = repo_path / file_meta.relative_path
                selected.append(abs_path)
                logger.debug(f"选择根目录文件：{file_meta.relative_path}")

        return selected

    def _select_entry_files(
        self, files: List[FileMetadata], repo_path: Path
    ) -> List[Path]:
        """
        选择入口文件。

        支持以下技术栈的入口文件：
            - Python: main.py, app.py, manage.py, server.py, run.py, cli.py
            - Java: Application.java
            - Go: main.go, cmd/
            - Node: index.ts, index.js, main.ts, main.js, app.ts, app.js, server.ts, server.js
            - Vue: main.js, main.ts, App.vue, router/, store/

        依赖：
            rules.py 中的 ENTRY_PATTERNS

        参数：
            files: 待筛选的文件列表
            repo_path: 仓库根路径

        返回：
            入口文件的绝对路径列表
        """
        selected = []
        for file_meta in files:
            file_name = file_meta.relative_path.lower()

            # 检查是否匹配任何入口文件模式
            for tech_stack, patterns in ENTRY_PATTERNS.items():
                for pattern in patterns:
                    pattern_lower = pattern.lower()
                    # 精确匹配文件名或路径包含模式
                    if file_name == pattern_lower or file_name.endswith("/" + pattern_lower):
                        abs_path = repo_path / file_meta.relative_path
                        selected.append(abs_path)
                        logger.debug(f"选择入口文件（{tech_stack}）：{file_meta.relative_path}")
                        break  # 避免重复添加

        return selected

    def _select_config_files(
        self, files: List[FileMetadata], repo_path: Path
    ) -> List[Path]:
        """
        选择配置文件。

        挑选以下配置文件：
            - application.yml / application.yaml
            - bootstrap.yml
            - config.yaml
            - vite.config.ts
            - webpack.config.js
            - babel.config.js
            - tsconfig.json
            - docker-compose.yml

        依赖：
            rules.py 中的 CONFIG_PATTERNS

        参数：
            files: 待筛选的文件列表
            repo_path: 仓库根路径

        返回：
            配置文件的绝对路径列表
        """
        selected = []
        for file_meta in files:
            file_name = file_meta.relative_path.lower()

            # 检查是否匹配任何配置模式
            for pattern in CONFIG_PATTERNS:
                pattern_lower = pattern.lower()
                # 精确匹配或路径结尾匹配
                if file_name == pattern_lower or file_name.endswith("/" + pattern_lower):
                    abs_path = repo_path / file_meta.relative_path
                    selected.append(abs_path)
                    logger.debug(f"选择配置文件：{file_meta.relative_path}")
                    break  # 避免重复添加

        return selected

    def _select_core_modules(
        self, files: List[FileMetadata], repo_path: Path
    ) -> List[Path]:
        """
        选择核心业务模块文件。

        挑选以下核心模块目录中的文件：
            - controller
            - service
            - api
            - core
            - domain
            - model / models
            - router
            - handler
            - business / biz
            - manager
            - repository / dao

        要求：
            - 避免全量选择，防止 token 爆炸
            - 单目录最多选择 5~10 个文件

        依赖：
            rules.py 中的 CORE_MODULE_PATTERNS

        参数：
            files: 待筛选的文件列表
            repo_path: 仓库根路径

        返回：
            核心模块文件的绝对路径列表
        """
        selected = []
        # 按目录分组，限制每个目录的文件数量
        dir_file_count: Dict[str, int] = {}
        max_files_per_dir = 15  # 单目录最多 15 个文件（从 8 增加到 15）

        for file_meta in files:
            file_path = file_meta.relative_path.lower()

            # 检查文件是否在核心模块目录中
            matched_pattern = None
            for pattern in CORE_MODULE_PATTERNS:
                pattern_lower = pattern.lower()
                # 检查路径中是否包含核心模块目录名
                if f"/{pattern_lower}/" in file_path or file_path.startswith(
                    pattern_lower + "/"
                ):
                    matched_pattern = pattern_lower
                    break

            if matched_pattern:
                # 统计该目录已选择的文件数
                dir_key = matched_pattern
                current_count = dir_file_count.get(dir_key, 0)

                if current_count < max_files_per_dir:
                    abs_path = repo_path / file_meta.relative_path
                    selected.append(abs_path)
                    dir_file_count[dir_key] = current_count + 1
                    logger.debug(
                        f"选择核心模块文件（{matched_pattern}）：{file_meta.relative_path}"
                    )
                else:
                    logger.debug(
                        f"跳过核心模块文件（目录已达上限）：{file_meta.relative_path}"
                    )

        return selected

    def _select_docs(
        self, files: List[FileMetadata], repo_path: Path
    ) -> List[Path]:
        """
        选择文档文件。

        挑选以下文档：
            - README.md
            - docs/ 目录下的文件
            - ARCHITECTURE.md
            - DESIGN.md
            - SECURITY.md
            - FRONTEND.md
            - PLANS.md
            - PRODUCT_SENSE.md
            - QUALITY_SCORE.md

        依赖：
            rules.py 中的 DOCUMENT_PATTERNS

        参数：
            files: 待筛选的文件列表
            repo_path: 仓库根路径

        返回：
            文档文件的绝对路径列表
        """
        selected = []
        for file_meta in files:
            file_name = file_meta.relative_path.lower()

            # 检查是否匹配任何文档模式
            for pattern in DOCUMENT_PATTERNS:
                pattern_lower = pattern.lower()
                # 精确匹配或路径开头匹配（用于目录如 docs/）
                if (
                    file_name == pattern_lower
                    or file_name.startswith(pattern_lower)
                    or file_name.endswith("/" + pattern_lower)
                ):
                    abs_path = repo_path / file_meta.relative_path
                    selected.append(abs_path)
                    logger.debug(f"选择文档文件：{file_meta.relative_path}")
                    break  # 避免重复添加

        return selected

    def _filter_low_value_files(self, files: List[Path]) -> List[Path]:
        """
        过滤低价值文件。

        过滤以下低价值文件：
            - .log（日志文件）
            - .lock（锁定文件）
            - .tmp（临时文件）
            - .cache（缓存文件）
            - .map（source map 文件）
            - .min.js（压缩 JavaScript 文件）
            - .bundle.js（打包 JavaScript 文件）

        依赖：
            rules.py 中的 LOW_VALUE_EXTENSIONS

        参数：
            files: 待过滤的文件路径列表

        返回：
            过滤后的文件路径列表
        """
        filtered = []
        for file_path in files:
            file_name = file_path.name.lower()

            # 检查是否匹配低价值后缀
            is_low_value = any(file_name.endswith(ext) for ext in LOW_VALUE_EXTENSIONS)

            if is_low_value:
                logger.debug(f"过滤低价值文件：{file_path}")
            else:
                filtered.append(file_path)

        return filtered

    def _deduplicate(self, files: List[Path]) -> List[Path]:
        """
        去重并保持顺序。

        例如：
            README.md 可能被多次选中（根目录文件 + 文档文件），
            最终只保留一次。

        要求：
            - 保持原有顺序
            - 去除重复路径

        参数：
            files: 可能包含重复的文件路径列表

        返回：
            去重后的文件路径列表
        """
        seen = set()
        deduplicated = []

        for file_path in files:
            # 使用绝对路径的字符串形式作为唯一标识
            path_str = str(file_path.absolute())
            if path_str not in seen:
                seen.add(path_str)
                deduplicated.append(file_path)
            else:
                logger.debug(f"去重文件：{file_path}")

        return deduplicated
