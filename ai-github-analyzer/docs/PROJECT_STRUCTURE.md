# 项目结构指南

## 完整目录结构

```
ai-github-analyzer/
│
├── src/                          # 源代码（src 布局模式）
│   ├── __init__.py              # 包初始化，版本信息
│   │
│   ├── orchestrator/            # 🎯 工作流协调
│   │   └── __init__.py
│   │   # 职责：
│   │   # - 协调分析管道执行
│   │   # - 管理模块生命周期
│   │   # - 处理错误和重试
│   │   # - 跟踪进度和状态
│   │   # 未来文件：
│   │   # - orchestrator.py: 主协调器类
│   │   # - workflow.py: 工作流定义
│   │   # - task_manager.py: 异步任务管理
│   │
│   ├── scanner/                 # 🔍 仓库扫描
│   │   └── __init__.py
│   │   # 职责：
│   │   # - 克隆/访问仓库（本地/远程）
│   │   # - 构建文件树结构
│   │   # - 统计文件、行数、目录
│   │   # - 检测编程语言
│   │   # - 提取依赖信息
│   │   # 未来文件：
│   │   # - repo_scanner.py: 核心扫描逻辑
│   │   # - file_analyzer.py: 文件级分析
│   │   # - language_detector.py: 语言识别
│   │   # - dependency_extractor.py: 依赖解析
│   │
│   ├── classifier/              # 🏷️ 技术分类
│   │   └── __init__.py
│   │   # 职责：
│   │   # - 识别主要编程语言
│   │   # - 检测框架和库
│   │   # - 分类仓库类型
│   │   # - 识别架构模式
│   │   # - 计算置信度分数
│   │   # 未来文件：
│   │   # - tech_classifier.py: 技术检测
│   │   # - pattern_recognizer.py: 模式匹配
│   │   # - repo_categorizer.py: 仓库分类
│   │   # - rules_engine.py: 分类规则
│   │
│   ├── context_builder/         # 📚 上下文聚合
│   │   └── __init__.py
│   │   # 职责：
│   │   # - 合并扫描和分类结果
│   │   # - 构建全面的仓库上下文
│   │   # - 提取关键文件（README、配置）
│   │   # - 为 AI 代理准备上下文
│   │   # - 优化上下文大小以适应 token 限制
│   │   # 未来文件：
│   │   # - context_assembler.py: 上下文构建
│   │   # - file_extractor.py: 关键文件提取
│   │   # - context_optimizer.py: 大小优化
│   │
│   ├── agents/                  # 🤖 AI 代理实现
│   │   └── __init__.py
│   │   # 职责：
│   │   # - 架构分析代理
│   │   # - 代码质量评估代理
│   │   # - 安全漏洞检测代理
│   │   # - 文档评估代理
│   │   # - 建议生成代理
│   │   # - 依赖健康分析代理
│   │   # - 性能瓶颈检测代理
│   │   # 未来文件：
│   │   # - base_agent.py: 基础代理类
│   │   # - architecture_agent.py
│   │   # - quality_agent.py
│   │   # - security_agent.py
│   │   # - documentation_agent.py
│   │   # - recommendation_agent.py
│   │   # - dependency_agent.py
│   │   # - performance_agent.py
│   │   # - agent_registry.py: 代理管理
│   │
│   ├── validators/              # ✅ 结果验证
│   │   └── __init__.py
│   │   # 职责：
│   │   # - 验证分析完整性
│   │   # - 检查数据一致性
│   │   # - 验证结果完整性
│   │   # - 应用验证规则
│   │   # - 生成验证报告
│   │   # 未来文件：
│   │   # - result_validator.py: 主验证器
│   │   # - rule_engine.py: 验证规则
│   │   # - quality_checker.py: 质量检查
│   │
│   ├── renderer/                # 📊 输出渲染
│   │   └── __init__.py
│   │   # 职责：
│   │   # - 格式化结果（Markdown、JSON、HTML）
│   │   # - 应用样式和格式化
│   │   # - 使用 Rich 生成终端输出
│   │   # - 导出到文件
│   │   # - 支持自定义模板
│   │   # 未来文件：
│   │   # - markdown_renderer.py
│   │   # - json_renderer.py
│   │   # - html_renderer.py
│   │   # - terminal_renderer.py: 基于 Rich 的输出
│   │   # - template_engine.py: 模板处理
│   │
│   ├── models/                  # 📦 Pydantic 数据模型
│   │   ├── __init__.py
│   │   └── base_models.py      # 核心数据模型（已创建）
│   │   # 职责：
│   │   # - 定义所有数据结构
│   │   # - 确保类型安全
│   │   # - 提供验证
│   │   # - 记录数据契约
│   │   # 未来文件：
│   │   # - agent_models.py: 代理特定模型
│   │   # - config_models.py: 配置模型
│   │   # - result_models.py: 结果模型
│   │
│   ├── infrastructure/          # 🔧 核心基础设施
│   │   └── __init__.py
│   │   # 职责：
│   │   # - 配置管理
│   │   # - 日志设置
│   │   # - 错误处理工具
│   │   # - 异步辅助工具
│   │   # - 外部服务客户端
│   │   # 未来文件：
│   │   # - config.py: 设置管理
│   │   # - logging_config.py: Loguru 配置
│   │   # - github_client.py: GitHub API 客户端
│   │   # - ai_client.py: AI 提供商客户端
│   │   # - exceptions.py: 自定义异常
│   │   # - async_utils.py: 异步工具
│   │
│   └── utils/                   # 🛠️ 实用函数
│       └── __init__.py
│       # 职责：
│       # - 文件系统操作
│       # - 字符串操作
│       # - 日期/时间辅助工具
│       # - 常用算法
│       # - 辅助函数
│       # 未来文件：
│       # - file_utils.py: 文件操作
│       # - string_utils.py: 字符串辅助工具
│       # - git_utils.py: Git 操作
│       # - path_utils.py: 路径操作
│       # - time_utils.py: 时间工具
│
├── prompts/                     # 💬 AI 提示模板
│   # 目的：将 AI 提示模板与代码分开存储
│   # 优势：
│   # - 无需代码更改即可轻松修改
│   # - 提示的版本控制
│   # - A/B 测试不同提示
│   # 未来文件：
│   # - architecture_agent_prompt.txt
│   # - quality_agent_prompt.txt
│   # - security_agent_prompt.txt
│   # - documentation_agent_prompt.txt
│   # - recommendation_agent_prompt.txt
│   # - system_prompt.txt
│
├── schemas/                     # 📋 JSON 模式
│   # 目的：用于外部集成的 JSON 模式定义
│   # 优势：
│   # - API 契约验证
│   # - 外部工具集成
│   # - 数据交换标准
│   # 未来文件：
│   # - analysis_result_schema.json
│   # - agent_input_schema.json
│   # - agent_output_schema.json
│
├── traces/                      # 🔎 执行追踪
│   # 目的：存储执行追踪以进行调试和分析
│   # 内容：
│   # - 代理交互日志
│   # - 性能分析数据
│   # - 调试信息
│   # 注意：此目录已被 gitignore
│   # 未来文件：
│   # - trace_*.json: 单个追踪文件
│   # - profiles/: 性能配置文件
│
├── tests/                       # 🧪 测试套件
│   # 目的：全面的测试覆盖
│   # 结构：镜像 src/ 目录结构
│   # 未来文件：
│   # - conftest.py: pytest 夹具
│   # - test_orchestrator/
│   # - test_scanner/
│   # - test_classifier/
│   # - test_agents/
│   # - test_validators/
│   # - test_renderer/
│   # - test_models/
│   # - integration/
│   # - e2e/
│
├── docs/                        # 📖 文档
│   ├── design-docs/            # 设计文档和 RFC
│   │   # 未来文件：
│   │   # - ADR-001-architecture-decision.md
│   │   # - RFC-001-agent-system.md
│   │   # - design-specifications.md
│   │
│   └── ENVIRONMENT_SETUP.md    # 环境设置指南（已创建）
│       # 其他未来文档：
│       # - API_REFERENCE.md
│       # - CONTRIBUTING.md
│       # - DEPLOYMENT.md
│
├── main.py                      # 🚀 CLI 入口点（已创建）
│   # 目的：主应用程序入口点
│   # 功能：
│   # - 基于 Typer 的 CLI 界面
│   # - Rich 终端输出
│   # - Loguru 日志设置
│   # - 命令：analyze <repo_url>
│   # - 命令：version
│
├── pyproject.toml               # ⚙️ 项目配置（已创建）
│   # 目的：现代 Python 项目配置
│   # 包含：
│   # - 项目元数据
│   # - 依赖
│   # - 构建系统设置
│   # - 工具配置（black、ruff、mypy）
│
├── .gitignore                   # 🚫 Git 忽略规则（已创建）
│   # 目的：从 git 中排除不必要的文件
│   # 包括：
│   # - Python 缓存文件
│   # - 虚拟环境
│   # - IDE 设置
│   # - 日志和追踪
│   # - 环境文件
│
├── .env.example                 # 📝 环境变量模板（已创建）
│   # 目的：环境配置模板
│   # 用法：复制到 .env 并填写值
│
├── setup.ps1                    # ⚡ 快速设置脚本（已创建）
│   # 目的：Windows 的自动化环境设置
│   # 功能：
│   # - 检查前置要求
│   # - 创建 conda 环境
│   # - 安装依赖
│   # - 验证安装
│
├── README.md                    # 📘 项目概述（已创建）
│   # 目的：主项目文档
│   # 包含：
│   # - 项目描述
│   # - 特性列表
│   # - 安装说明
│   # - 使用示例
│   # - 项目结构
│   # - 开发指南
│
├── ARCHITECTURE.md              # 🏗️ 架构设计（已创建）
│   # 目的：详细的架构文档
│   # 包含：
│   # - 架构原则
│   # - 模块职责
│   # - 数据流图
│   # - 技术栈选择理由
│   # - 扩展点
│
├── AGENTS.md                    # 🤖 代理规范（已创建）
│   # 目的：AI 代理设计文档
│   # 包含：
│   # - 代理类型和目的
│   # - 输入/输出规范
│   # - 提示工程指南
│   # - 配置选项
│   # - 测试策略
│
└── LICENSE                      # 📄 许可证文件（待添加）
    # 目的：项目许可证（推荐 MIT）
```

---

## 模块通信流程

```
用户输入 (CLI)
    ↓
main.py (Typer CLI)
    ↓
协调器（协调工作流）
    ↓
扫描器 → ScanResult（Pydantic 模型）
    ↓
分类器 → ClassificationResult（Pydantic 模型）
    ↓
上下文构建器 → 丰富的上下文（Pydantic 模型）
    ↓
代理（并行执行）
    ├→ 架构代理 → ArchitectureAnalysis
    ├→ 质量代理 → QualityAnalysis
    ├→ 安全代理 → SecurityAnalysis
    ├→ 文档代理 → DocumentationAnalysis
    └→ 其他代理 → 它们的结果
    ↓
验证器 → 验证结果
    ↓
渲染器 → 格式化输出
    ↓
展示给用户（Rich 终端）
```

---

## 关键设计决策

### 1. 为什么使用 `src/` 布局？

**优势**：
- 防止开发期间的导入冲突
- 源代码和测试之间的清晰分离
- 标准的 Python 打包实践
- 使用隔离导入更容易测试
- 避免意外导入未安装的代码

**考虑的替代方案**：平面布局（已拒绝）
- 可能导致导入混淆
- 更难正确测试
- 现代 Python 打包指南不推荐

---

### 2. 为什么使用 Pydantic 模型进行通信？

**优势**：
- 模块边界的运行时验证
- 整个管道的类型安全
- 自文档化的数据契约
- 易于序列化/反序列化
- IDE 自动完成支持
- 自动生成 JSON 模式

**考虑的替代方案**：Dicts/dataclasses（已拒绝）
- 无运行时验证
- 契约不太清晰
- 更容易出错

---

### 3. 为什么单独的 Prompts 目录？

**优势**：
- 无需代码更改即可进行提示工程
- 提示的版本控制
- 易于 A/B 测试
- 非开发者可以修改提示
- 清晰的关注点分离

**考虑的替代方案**：内联提示（已拒绝）
- 难以维护
- 提示调整需要代码更改
- 难以测试不同版本

---

### 4. 为什么没有 ORM 或数据库？

**理由**：
- 第一版本专注于单次运行分析
- 最初不需要持久存储
- 保持架构轻量级
- 需要时可以稍后添加数据库
- 遵循"无过度工程"原则

**未来增强**：
- 添加 SQLite/PostgreSQL 用于分析历史
- 实现缓存层
- 存储比较数据

---

### 5. 为什么异步优先设计？

**优势**：
- 并行代理执行
- 高效的 I/O 操作（GitHub API、文件系统）
- 非阻塞操作
- 更好的资源利用
- 可扩展以处理大型仓库

**实现**：
- asyncio 用于并发
- 全程使用 async/await 语法
- 任务组用于并行执行

---

### 6. 为什么多个专业化代理？

**优势**：
- 每个代理单一职责
- 更容易测试和维护
- 可以独立启用/禁用代理
- 可以并行执行
- 清晰的关注点分离
- 易于添加新代理

**考虑的替代方案**：单一体代理（已拒绝）
- 太复杂
- 难以维护
- 无法并行化
- 难以测试

---

## 文件命名约定

### Python 文件
- **模块**：`snake_case.py`（例如 `file_analyzer.py`）
- **类**：`PascalCase`（例如 `FileAnalyzer`）
- **函数**：`snake_case`（例如 `analyze_file()`）
- **常量**：`UPPER_CASE`（例如 `MAX_FILE_SIZE`）
- **私有**：`_leading_underscore`（例如 `_internal_method()`）

### 测试文件
- 镜像源结构：`test_<module_name>.py`
- 示例：`src/scanner/file_analyzer.py` → `tests/test_scanner/test_file_analyzer.py`

### 文档文件
- 主文档使用 `UPPER_CASE.md`（README、ARCHITECTURE）
- 子文档使用 `kebab-case.md`（environment-setup.md）

### 提示文件
- `<agent_name>_prompt.txt`（例如 `architecture_agent_prompt.txt`）

---

## 导入指南

### 在 src/ 内部

```python
# ✅ 正确：从 src 绝对导入
from src.models.base_models import AnalysisConfig
from src.scanner.repo_scanner import RepositoryScanner

# ❌ 避免：相对导入（更难重构）
from ..models.base_models import AnalysisConfig
```

### 在测试中

```python
# ✅ 正确：从 src 包导入
from src.models.base_models import AnalysisConfig

# ❌ 避免：从本地路径导入
import sys
sys.path.insert(0, '../src')
```

---

## 依赖管理

### 当前依赖（pyproject.toml）

**核心**：
- `typer>=0.9.0`: CLI 框架
- `rich>=13.7.0`: 终端格式化
- `loguru>=0.7.0`: 日志记录
- `pydantic>=2.5.0`: 数据验证
- `pydantic-settings>=2.1.0`: 设置管理

**开发**（可选）：
- `pytest>=7.4.0`: 测试
- `pytest-asyncio>=0.21.0`: 异步测试
- `black>=23.0.0`: 代码格式化
- `ruff>=0.1.0`: 代码检查
- `mypy>=1.7.0`: 类型检查

### 未来依赖（按模块）

**扫描器**：
- `gitpython`: Git 操作
- `pathspec`: .gitignore 解析

**分类器**：
- `lingua-language-detector`: 语言检测

**代理**：
- `openai`: OpenAI API 客户端
- 或 `anthropic`: Anthropic API 客户端

**基础设施**：
- `aiohttp`: 异步 HTTP 客户端
- `python-dotenv`: 环境变量

---

## 测试策略

### 测试类型

1. **单元测试** (`tests/unit/`)
   - 测试单个函数/类
   - 模拟外部依赖
   - 快速执行

2. **集成测试** (`tests/integration/`)
   - 测试模块交互
   - 实际依赖（如果可行）
   - 中等执行时间

3. **端到端测试** (`tests/e2e/`)
   - 完整工作流执行
   - 真实仓库
   - 慢速执行

### 测试组织

```
tests/
├── conftest.py              # 共享夹具
├── unit/
│   ├── test_scanner/
│   ├── test_classifier/
│   ├── test_agents/
│   └── ...
├── integration/
│   ├── test_orchestrator.py
│   └── test_workflow.py
├── e2e/
│   ├── test_full_analysis.py
│   └── test_cli_commands.py
└── fixtures/
    ├── sample_repos/        # 测试仓库
    └── mock_data/           # 模拟响应
```

---

## 日志策略

### 日志级别

- **DEBUG**: 详细的诊断信息
- **INFO**: 一般操作消息
- **WARNING**: 意外但已处理的情况
- **ERROR**: 不停止执行的错误
- **CRITICAL**: 停止执行的致命错误

### 日志目标

1. **控制台**（stderr）：INFO 及以上级别，彩色
2. **文件**（logs/）：DEBUG 及以上级别，每天轮换
3. **追踪**（traces/）：代理交互，JSON 格式

### 日志格式

```
2026-05-14 10:30:45 | INFO     | src.scanner.repo_scanner:scan:42 - 正在扫描仓库...
2026-05-14 10:30:46 | DEBUG    | src.agents.quality_agent:analyze:87 - 正在分析 150 个文件
2026-05-14 10:30:47 | ERROR    | src.infrastructure.github_client:fetch:123 - API 速率限制超出
```

---

## 错误处理策略

### 异常层次结构

```python
# src/infrastructure/exceptions.py

class AnalyzerError(Exception):
    """所有分析器错误的基础异常。"""
    pass

class ScannerError(AnalyzerError):
    """仓库扫描期间的错误。"""
    pass

class ClassificationError(AnalyzerError):
    """技术分类期间的错误。"""
    pass

class AgentError(AnalyzerError):
    """代理执行期间的错误。"""
    pass

class ValidationError(AnalyzerError):
    """结果验证期间的错误。"""
    pass
```

### 错误处理模式

```python
try:
    result = await agent.analyze(context)
except AgentError as e:
    logger.error(f"代理失败：{e}")
    if config.retry_count > 0:
        result = await retry(agent.analyze, context)
    else:
        result = agent.get_fallback_result()
```

---

## 配置管理

### 优先级顺序

1. 命令行参数（最高优先级）
2. 环境变量
3. `.env` 文件
4. 默认值（最低优先级）

### 实现

```python
# src/infrastructure/config.py

from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    # CLI 参数覆盖这些
    repo_url: str
    output_format: str = "markdown"
    
    # 环境变量
    ai_provider: str = "openai"
    ai_model: str = "gpt-4-turbo"
    
    class Config:
        env_file = ".env"
        env_prefix = "ANALYZER_"
```

---

## 开发的下一步

### 第一阶段：核心基础设施（第 1-2 周）
- [ ] 实现扫描器模块
- [ ] 实现分类器模块
- [ ] 完成上下文构建器
- [ ] 添加 GitHub API 客户端

### 第二阶段：代理系统（第 3-4 周）
- [ ] 实现基础代理框架
- [ ] 创建提示模板
- [ ] 构建 2-3 个核心代理（质量、架构、安全）
- [ ] 实现代理协调

### 第三阶段：输出和验证（第 5 周）
- [ ] 实现渲染器模块
- [ ] 构建验证系统
- [ ] 创建 Markdown 和 JSON 渲染器
- [ ] 添加 Rich 终端输出

### 第四阶段：测试和完善（第 6 周）
- [ ] 编写全面的测试
- [ ] 性能优化
- [ ] 文档完成
- [ ] Beta 测试

---

*最后更新：2026-05-14*
