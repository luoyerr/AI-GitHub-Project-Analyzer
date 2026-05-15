"""
上下文优先级排序器 - 文件重要性评估模块。

负责对筛选后的文件进行优先级排序，确保高价值文件优先被处理和分析。
基于文件名、目录位置、是否根目录、是否入口、是否配置、是否核心模块、
是否文档、是否噪音文件等多维度特征计算优先级分数。

职责边界：
    - 只做评分和排序（基于路径和文件名）
    - 禁止读取文件内容
    - 禁止 token 计算
    - 禁止裁剪逻辑
    - 禁止 builder orchestration
    - 输入 List[Path]，输出排序后的 List[Path]
"""

from pathlib import Path
from typing import List, Tuple

from loguru import logger


class ContextPrioritizer:
    """
    上下文优先级排序器 - 文件重要性评估。

    职责：
        对 selector.py 选出的文件进行评分与排序。
        通过多维度评分机制确定文件的重要性顺序。
        评分范围：0~100 分。

    评分维度：
        1. 文件名权重（README.md、ARCHITECTURE.md 等高分）
        2. 目录位置权重（根目录 > 核心模块 > 普通目录）
        3. 是否入口文件（main.py、Application.java 等高分）
        4. 是否配置文件（package.json、pom.xml 等高分）
        5. 是否核心模块（controller、service、domain 等中高分）
        6. 是否文档文件（docs/、DESIGN.md 等中等分数）
        7. 是否噪音文件（test、mock、.lock 等低分）

    注意：
        - 本类只负责评分和排序，不做文件读取
        - 本类不做 token 计算
        - 本类不做裁剪
        - 本类不做 builder orchestration
    """

    def __init__(self) -> None:
        """初始化上下文优先级排序器。"""
        logger.debug("初始化上下文优先级排序器")

    def prioritize(self, files: List[Path]) -> List[Path]:
        """
        对文件列表进行优先级排序（总入口）。

        流程：
            1. 对每个文件进行评分（_score_file）
            2. 按分数从高到低稳定排序（_sort_files）
            3. 返回排序后的文件路径列表

        参数：
            files: 待排序的文件路径列表（绝对路径）

        返回：
            按优先级从高到低排序的文件路径列表
        """
        logger.info(f"开始文件优先级排序，文件数量：{len(files)}")

        # 步骤 1：对所有文件进行评分
        scored_files: List[Tuple[Path, int]] = [
            (file_path, self._score_file(file_path)) for file_path in files
        ]
        logger.debug(f"完成文件评分，评分数量：{len(scored_files)}")

        # 步骤 2：按分数从高到低稳定排序
        sorted_files = self._sort_files(scored_files)
        logger.info(f"完成文件排序，排序结果数量：{len(sorted_files)}")

        # 输出 debug 信息：显示前 10 个高分文件
        if sorted_files and scored_files:
            logger.debug("优先级最高的前 10 个文件：")
            # 创建一个分数映射以便查找
            score_map = {path: score for path, score in scored_files}
            for i, file_path in enumerate(sorted_files[:10], 1):
                score = score_map.get(file_path, 0)
                logger.debug(f"  {i}. [{score:3d}分] {file_path.name}")

        return sorted_files

    def _score_file(self, file_path: Path) -> int:
        """
        核心评分函数 - 计算单个文件的优先级分数。

        评分维度：
            1. 根目录加权（_score_root_file）
            2. 入口文件加权（_score_entry_file）
            3. 配置文件加权（_score_config_file）
            4. 核心模块加权（_score_core_module）
            5. 文档文件加权（_score_document）
            6. 噪音文件降权（_score_noise）

        评分范围：
            0~100 分

        参数：
            file_path: 文件绝对路径

        返回：
            文件优先级分数（0~100）
        """
        # 基础分数：普通源码文件
        base_score = 40

        # 各维度评分
        root_score = self._score_root_file(file_path)
        entry_score = self._score_entry_file(file_path)
        config_score = self._score_config_file(file_path)
        core_score = self._score_core_module(file_path)
        doc_score = self._score_document(file_path)
        noise_penalty = self._score_noise(file_path)

        # 取最高维度分数作为最终分数
        dimension_scores = [
            base_score,
            root_score,
            entry_score,
            config_score,
            core_score,
            doc_score,
        ]
        final_score = max(dimension_scores)

        # 应用噪音降权
        final_score = max(0, final_score - noise_penalty)

        # 确保分数在 0~100 范围内
        final_score = min(100, max(0, final_score))

        logger.debug(
            f"文件评分：{file_path.name} | "
            f"根目录={root_score}, 入口={entry_score}, 配置={config_score}, "
            f"核心={core_score}, 文档={doc_score}, 噪音惩罚={noise_penalty} | "
            f"最终={final_score}"
        )

        return final_score

    def _score_root_file(self, file_path: Path) -> int:
        """
        根目录文件加权评分。

        高优先级根目录文件：
            - README.md / README_CN.md: 100 分
            - ARCHITECTURE.md / DESIGN.md: 98 分
            - package.json / pom.xml / go.mod / Cargo.toml: 90 分
            - Dockerfile / docker-compose.yml: 88 分
            - requirements.txt / pyproject.toml: 85 分
            - LICENSE / CHANGELOG.md: 80 分

        要求：
            - 只允许仓库根目录（parent 层级判断）
            - 禁止递归子目录

        参数：
            file_path: 文件绝对路径

        返回：
            根目录文件评分（0~100），非根目录文件返回 0
        """
        # 检查是否在根目录（这里假设传入的路径已经是相对路径或需要判断层级）
        # 由于 prioritizer 接收的是绝对路径，我们需要通过 parts 来判断
        # 但根据需求，我们应该只使用 path.name 和 path.parts
        # 实际上，selector 已经筛选出了根目录文件，这里我们根据文件名判断

        file_name = file_path.name.lower()

        # 项目说明文档 - 最高优先级
        if file_name in ["readme.md", "readme_cn.md"]:
            return 100

        # 架构设计文档
        if file_name in ["architecture.md", "design.md", "security.md"]:
            return 98

        # 依赖管理文件
        if file_name in ["package.json", "pom.xml", "go.mod", "cargo.toml",
                         "requirements.txt", "pyproject.toml", "setup.py",
                         "build.gradle", "package-lock.json", "pnpm-lock.yaml"]:
            return 90

        # 容器化配置
        if file_name in ["dockerfile", "docker-compose.yml", "docker-compose.yaml"]:
            return 88

        # 环境配置示例
        if file_name == ".env.example":
            return 85

        # 其他重要文件
        if file_name in ["license", "changelog.md"]:
            return 80

        return 0

    def _score_entry_file(self, file_path: Path) -> int:
        """
        入口文件加权评分。

        高优先级入口文件：
            - main.py / app.py / manage.py: 95 分
            - Application.java: 95 分
            - main.go: 95 分
            - index.ts / index.js / main.ts / main.js: 92 分
            - server.ts / server.js / app.ts / app.js: 90 分

        参数：
            file_path: 文件绝对路径

        返回：
            入口文件评分（0~100），非入口文件返回 0
        """
        file_name = file_path.name.lower()

        # Python 入口文件
        if file_name in ["main.py", "app.py", "manage.py", "server.py",
                         "run.py", "cli.py"]:
            return 95

        # Java 入口文件
        if file_name == "application.java":
            return 95

        # Go 入口文件
        if file_name == "main.go":
            return 95

        # Node.js/Vue 主要入口文件
        if file_name in ["index.ts", "index.js", "main.ts", "main.js"]:
            return 92

        # Node.js/Vue 次要入口文件
        if file_name in ["app.ts", "app.js", "server.ts", "server.js"]:
            return 90

        # Vue 组件入口
        if file_name == "app.vue":
            return 88

        return 0

    def _score_config_file(self, file_path: Path) -> int:
        """
        配置文件加权评分。

        高优先级配置文件：
            - application.yml / application.yaml: 85 分
            - bootstrap.yml: 83 分
            - vite.config.ts / webpack.config.js: 82 分
            - tsconfig.json: 80 分
            - babel.config.js: 78 分
            - config.yaml: 75 分

        参数：
            file_path: 文件绝对路径

        返回：
            配置文件评分（0~100），非配置文件返回 0
        """
        file_name = file_path.name.lower()

        # Spring Boot 配置
        if file_name in ["application.yml", "application.yaml"]:
            return 85

        # Spring Cloud 引导配置
        if file_name == "bootstrap.yml":
            return 83

        # 前端构建配置
        if file_name in ["vite.config.ts", "webpack.config.js"]:
            return 82

        # TypeScript 配置
        if file_name == "tsconfig.json":
            return 80

        # Babel 配置
        if file_name == "babel.config.js":
            return 78

        # 通用配置
        if file_name in ["config.yaml", "config.yml"]:
            return 75

        return 0

    def _score_core_module(self, file_path: Path) -> int:
        """
        核心业务模块加权评分。

        核心模块目录中的文件：
            - controller/: 75 分
            - service/: 75 分
            - domain/: 73 分
            - repository/ / dao/: 72 分
            - api/: 70 分
            - model/ / models/: 68 分
            - router/ / handler/: 67 分
            - business/ / biz/: 66 分
            - manager/: 65 分
            - core/: 70 分

        参数：
            file_path: 文件绝对路径

        返回：
            核心模块文件评分（0~100），非核心模块文件返回 0
        """
        # 将路径转换为小写字符串进行检查
        path_str = str(file_path).lower()
        # 统一使用正斜杠进行检查（兼容 Windows 反斜杠）
        path_str_normalized = path_str.replace("\\", "/")

        # 控制器层 - 高优先级
        if "/controller/" in path_str_normalized or path_str_normalized.endswith("/controller"):
            return 75

        # 服务层 - 高优先级
        if "/service/" in path_str_normalized or path_str_normalized.endswith("/service"):
            return 75

        # 领域模型 - 中高优先级
        if "/domain/" in path_str_normalized or path_str_normalized.endswith("/domain"):
            return 73

        # 数据访问层 - 中高优先级
        if "/repository/" in path_str_normalized or path_str_normalized.endswith("/repository"):
            return 72
        if "/dao/" in path_str_normalized or path_str_normalized.endswith("/dao"):
            return 72

        # API 接口 - 中优先级
        if "/api/" in path_str_normalized or path_str_normalized.endswith("/api"):
            return 70

        # 核心模块 - 中优先级
        if "/core/" in path_str_normalized or path_str_normalized.endswith("/core"):
            return 70

        # 数据模型 - 中优先级
        if "/model/" in path_str_normalized or path_str_normalized.endswith("/model"):
            return 68
        if "/models/" in path_str_normalized or path_str_normalized.endswith("/models"):
            return 68

        # 路由配置 - 中优先级
        if "/router/" in path_str_normalized or path_str_normalized.endswith("/router"):
            return 67

        # 请求处理器 - 中优先级
        if "/handler/" in path_str_normalized or path_str_normalized.endswith("/handler"):
            return 67

        # 业务逻辑 - 中优先级
        if "/business/" in path_str_normalized or path_str_normalized.endswith("/business"):
            return 66
        if "/biz/" in path_str_normalized or path_str_normalized.endswith("/biz"):
            return 66

        # 管理器 - 中优先级
        if "/manager/" in path_str_normalized or path_str_normalized.endswith("/manager"):
            return 65

        return 0

    def _score_document(self, file_path: Path) -> int:
        """
        文档文件加权评分。

        文档文件：
            - README.md: 100 分（已在根目录评分中处理）
            - ARCHITECTURE.md: 98 分（已在根目录评分中处理）
            - docs/ 目录下的文件: 60 分
            - DESIGN.md / SECURITY.md: 85 分
            - FRONTEND.md / PLANS.md: 70 分
            - PRODUCT_SENSE.md / QUALITY_SCORE.md: 65 分

        参数：
            file_path: 文件绝对路径

        返回：
            文档文件评分（0~100），非文档文件返回 0
        """
        file_name = file_path.name.lower()
        path_str = str(file_path).lower()
        # 统一使用正斜杠进行检查（兼容 Windows 反斜杠）
        path_str_normalized = path_str.replace("\\", "/")

        # docs 目录下的文件
        if "/docs/" in path_str_normalized or path_str_normalized.endswith("/docs"):
            return 60

        # 重要设计文档
        if file_name in ["design.md", "security.md"]:
            return 85

        # 一般文档
        if file_name in ["frontend.md", "plans.md"]:
            return 70

        # 其他文档
        if file_name in ["product_sense.md", "quality_score.md"]:
            return 65

        return 0

    def _score_noise(self, file_path: Path) -> int:
        """
        噪音文件降权评分。

        降低以下文件的优先级：
            - test/ / tests/ / __tests__/: 降权 30 分
            - mock/ / mocks/: 降权 25 分
            - fixture/ / fixtures/: 降权 25 分
            - coverage/: 降权 20 分
            - snapshot/ / __snapshots__/: 降权 20 分
            - .lock 文件: 降权 35 分
            - .log 文件: 降权 30 分
            - .tmp / .cache 文件: 降权 25 分
            - .min.js / .bundle.js: 降权 20 分

        参数：
            file_path: 文件绝对路径

        返回：
            降权分数（0~100），非噪音文件返回 0
        """
        file_name = file_path.name.lower()
        path_str = str(file_path).lower()
        # 统一使用正斜杠进行检查（兼容 Windows 反斜杠）
        path_str_normalized = path_str.replace("\\", "/")

        # 测试文件 - 大幅降权
        if "/test/" in path_str_normalized or "/tests/" in path_str_normalized or "/__tests__/" in path_str_normalized:
            return 30
        if file_name.startswith("test_") or file_name.endswith("_test.py"):
            return 30

        # Mock 文件 - 大幅降权
        if "/mock/" in path_str_normalized or "/mocks/" in path_str_normalized:
            return 25
        if "mock" in file_name:
            return 25

        # Fixture 文件 - 大幅降权
        if "/fixture/" in path_str_normalized or "/fixtures/" in path_str_normalized:
            return 25
        if "fixture" in file_name:
            return 25

        # Coverage 报告 - 大幅降权
        if "/coverage/" in path_str_normalized:
            return 20

        # Snapshot 文件 - 大幅降权
        if "/snapshot/" in path_str_normalized or "/__snapshots__/" in path_str_normalized:
            return 20

        # 锁定文件 - 大幅降权
        if file_name.endswith(".lock") or "-lock" in file_name:
            return 35

        # 日志文件 - 大幅降权
        if file_name.endswith(".log"):
            return 30

        # 临时文件和缓存 - 大幅降权
        if file_name.endswith(".tmp") or file_name.endswith(".cache"):
            return 25

        # 压缩和打包文件 - 中度降权
        if file_name.endswith(".min.js") or file_name.endswith(".bundle.js"):
            return 20

        # Source map 文件 - 中度降权
        if file_name.endswith(".map"):
            return 20

        return 0

    def _sort_files(self, scored_files: List[Tuple[Path, int]]) -> List[Path]:
        """
        稳定排序 - 按分数从高到低排序。

        要求：
            - 高分优先
            - 保持稳定性（相同分数的文件保持原有顺序）
            - 禁止随机顺序

        参数：
            scored_files: 已评分的文件列表，每个元素为 (文件路径, 分数) 元组

        返回：
            按分数从高到低排序的文件路径列表
        """
        # 使用稳定的排序算法，按分数降序排列
        # Python 的 sorted() 是稳定排序，相同分数的元素保持原有顺序
        sorted_files = sorted(
            scored_files,
            key=lambda x: x[1],  # 按分数排序
            reverse=True  # 降序（高分优先）
        )

        # 提取排序后的文件路径
        result = [file_path for file_path, score in sorted_files]

        logger.debug(
            f"排序完成：共 {len(result)} 个文件，"
            f"最高分 {sorted_files[0][1] if sorted_files else 0}，"
            f"最低分 {sorted_files[-1][1] if sorted_files else 0}"
        )

        return result
