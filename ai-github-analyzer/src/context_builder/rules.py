"""
上下文构建规则配置模块。

定义文件筛选、优先级排序、安全过滤等各个环节使用的规则模式和配置项。
所有规则以常量形式定义，便于统一管理和后续扩展。
本模块仅负责规则定义，不包含任何业务逻辑。
"""

from typing import Dict, List

# ==================== 根目录高价值文件规则 ====================

# 根目录下的高价值文件列表
# 这些文件通常包含项目的关键信息和元数据
ROOT_IMPORTANT_FILES: List[str] = [
    "README.md",           # 项目说明文档
    "README_CN.md",        # 中文项目说明文档
    "LICENSE",             # 许可证文件
    "CHANGELOG.md",        # 变更日志
    "requirements.txt",    # Python 依赖文件
    "pyproject.toml",      # Python 项目配置文件
    "setup.py",            # Python 安装脚本
    "package.json",        # Node.js 包配置文件
    "package-lock.json",   # Node.js 锁定文件
    "pnpm-lock.yaml",      # pnpm 锁定文件
    "pom.xml",             # Maven 配置文件
    "build.gradle",        # Gradle 构建文件
    "go.mod",              # Go 模块文件
    "Cargo.toml",          # Rust Cargo 配置文件
    "Dockerfile",          # Docker 构建文件
    "docker-compose.yml",  # Docker Compose 配置文件
    ".env.example",        # 环境变量示例文件
]

# ==================== 入口文件模式规则 ====================

# 入口文件识别模式
# 用于识别不同技术栈的项目入口点
ENTRY_PATTERNS: Dict[str, List[str]] = {
    "python": [           # Python 入口文件
        "main.py",
        "app.py",
        "manage.py",
        "server.py",
        "run.py",
        "cli.py",
    ],
    "java": [             # Java 入口文件
        "Application.java",
    ],
    "go": [               # Go 入口文件
        "main.go",
        "cmd/",            # Go cmd 目录
    ],
    "node": [             # Node.js 入口文件
        "index.ts",
        "index.js",
        "main.ts",
        "main.js",
        "app.ts",
        "app.js",
        "server.ts",
        "server.js",
    ],
    "vue": [              # Vue 项目入口文件
        "main.js",
        "main.ts",
        "App.vue",
        "router/",         # 路由目录
        "store/",          # 状态管理目录
    ],
}

# ==================== 配置文件模式规则 ====================

# 配置文件识别模式
# 用于识别各种类型的配置文件
CONFIG_PATTERNS: List[str] = [
    "application.yml",     # Spring Boot 配置文件
    "application.yaml",    # Spring Boot YAML 配置
    "bootstrap.yml",       # Spring Cloud 引导配置
    "config.yaml",         # 通用 YAML 配置
    "vite.config.ts",      # Vite 构建配置
    "webpack.config.js",   # Webpack 构建配置
    "babel.config.js",     # Babel 转译配置
    "tsconfig.json",       # TypeScript 配置
    "docker-compose.yml",  # Docker Compose 配置
]

# ==================== 核心业务目录模式规则 ====================

# 核心业务模块目录模式
# 用于识别包含主要业务逻辑的目录
CORE_MODULE_PATTERNS: List[str] = [
    "controller",          # 控制器层
    "service",             # 服务层
    "api",                 # API 接口
    "core",                # 核心模块
    "domain",              # 领域模型
    "model",               # 数据模型
    "models",              # 数据模型（复数）
    "router",              # 路由配置
    "handler",             # 请求处理器
    "business",            # 业务逻辑
    "biz",                 # 业务逻辑（缩写）
    "manager",             # 管理器
    "repository",          # 数据访问层
    "dao",                 # 数据访问对象
    "src",                 # 源代码目录（通用）
    "lib",                 # 库代码目录
    "packages",            # 多包项目目录
    "modules",             # 模块目录
]

# ==================== 文档文件模式规则 ====================

# 文档文件识别模式
# 用于识别项目中的各类文档
DOCUMENT_PATTERNS: List[str] = [
    "README.md",           # 项目说明文档
    "docs/",               # 文档目录
    "ARCHITECTURE.md",     # 架构设计文档
    "DESIGN.md",           # 设计文档
    "SECURITY.md",         # 安全说明文档
    "FRONTEND.md",         # 前端说明文档
    "PLANS.md",            # 计划文档
    "PRODUCT_SENSE.md",    # 产品感知文档
    "QUALITY_SCORE.md",    # 质量评分文档
]

# ==================== 忽略目录模式规则 ====================

# 需要忽略的目录和文件模式
# 这些通常是临时文件、缓存、IDE 配置等非源码内容
IGNORE_PATTERNS: List[str] = [
    "node_modules",        # Node.js 依赖目录
    "dist",                # 构建输出目录
    "build",               # 构建目录
    "coverage",            # 测试覆盖率报告
    "logs",                # 日志目录
    "tmp",                 # 临时文件目录
    "temp",                # 临时文件目录
    ".idea",               # IntelliJ IDEA 配置
    ".vscode",             # VS Code 配置
    ".git",                # Git 版本控制目录
    "target",              # Maven 构建输出
    "vendor",              # 第三方依赖目录
    "bin",                 # 二进制文件目录
    "obj",                 # 编译对象目录
    ".cache",              # 缓存目录
    ".next",               # Next.js 构建输出
    ".nuxt",               # Nuxt.js 构建输出
    "__pycache__",         # Python 字节码缓存
]

# ==================== 敏感文件模式规则 ====================

# 敏感文件识别模式
# 这些文件可能包含密码、密钥等敏感信息，应禁止读取
SENSITIVE_PATTERNS: List[str] = [
    ".env",                # 环境变量文件
    ".env.local",          # 本地环境变量
    ".env.production",     # 生产环境变量
    ".env.dev",            # 开发环境变量
    ".pem",                # PEM 证书文件
    ".key",                # 私钥文件
    "id_rsa",              # SSH 私钥
    "credential",          # 凭据文件
    "secret",              # 秘密文件
    "token",               # 令牌文件
    "private",             # 私有文件
]

# 允许读取的敏感文件例外列表
# 这些文件虽然匹配敏感模式，但通常是安全的示例文件
SENSITIVE_ALLOWLIST: List[str] = [
    ".env.example",        # 环境变量示例文件（允许读取）
]

# ==================== 低价值文件后缀规则 ====================

# 低价值文件后缀列表
# 这些文件通常对分析帮助不大，可以优先排除
LOW_VALUE_EXTENSIONS: List[str] = [
    ".log",                # 日志文件
    ".lock",               # 锁定文件
    ".tmp",                # 临时文件
    ".cache",              # 缓存文件
    ".map",                # Source map 文件
    ".min.js",             # 压缩 JavaScript 文件
    ".bundle.js",          # 打包 JavaScript 文件
]

# ==================== 上下文预算限制规则 ====================

# 上下文预算配置
# 用于控制分析过程中的资源使用
CONTEXT_LIMITS: Dict[str, int] = {
    "max_root_files": 20,      # 根目录文件最大数量
    "max_entry_files": 10,     # 入口文件最大数量
    "max_config_files": 15,    # 配置文件最大数量
    "max_core_files": 50,      # 核心模块文件最大数量
    "max_document_files": 10,  # 文档文件最大数量
    "max_total_files": 500,    # 总文件数量上限
    "max_file_size_kb": 500,   # 单文件最大大小（KB）
    "max_file_lines": 300,     # 单文件最大读取行数
}

