"""
上下文构建规则配置模块。

定义文件筛选、优先级排序、安全过滤等各个环节使用的规则模式和配置项。
所有规则以常量形式定义，便于统一管理和后续扩展。
"""

# 入口文件模式列表
# 用于识别项目的入口点文件
ENTRY_PATTERNS: list[str] = []

# 配置文件模式列表
# 用于识别项目配置文件（如 package.json, requirements.txt 等）
CONFIG_PATTERNS: list[str] = []

# 核心模块模式列表
# 用于识别核心业务代码目录和文件
CORE_MODULE_PATTERNS: list[str] = []

# 忽略文件模式列表
# 用于过滤低价值文件（如测试文件、生成文件、构建产物等）
IGNORE_PATTERNS: list[str] = []

# 敏感文件模式列表
# 用于过滤包含敏感信息的文件（如 .env, credentials, private keys 等）
SENSITIVE_PATTERNS: list[str] = []

# 文档文件模式列表
# 用于识别项目文档文件（如 README.md, docs/, CHANGELOG.md 等）
DOCUMENT_PATTERNS: list[str] = []
