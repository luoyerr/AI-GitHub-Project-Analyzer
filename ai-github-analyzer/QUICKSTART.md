# 快速入门指南 - AI GitHub Analyzer

## 🚀 5 分钟快速设置

### 步骤 1：创建 Conda 环境

```powershell
# 导航到项目目录
cd E:\code\project\AI-GitHub-Project-Analyzer\ai-github-analyzer

# 使用 Python 3.12 创建环境
conda create -n ai-github-analyzer python=3.12 -y

# 激活环境
conda activate ai-github-analyzer
```

### 步骤 2：安装依赖

```powershell
# 以开发模式安装包
pip install -e .

# 或安装开发依赖（开发者推荐）
pip install -e ".[dev]"
```

### 步骤 3：验证安装

```powershell
# 检查安装是否成功
python main.py version

# 预期输出：AI GitHub Analyzer v0.1.0
```

### 步骤 4：测试 CLI

```powershell
# 显示帮助
python main.py --help

# 显示分析命令帮助
python main.py analyze --help
```

---

## 📖 基本用法

### 分析 GitHub 仓库

```powershell
# 基本分析
python main.py analyze https://github.com/username/repository

# 指定输出格式
python main.py analyze https://github.com/username/repository --format json

# 启用详细输出
python main.py analyze https://github.com/username/repository --verbose

# 组合选项
python main.py analyze https://github.com/username/repository -f markdown -v
```

### 分析本地仓库

```powershell
python main.py analyze C:\path\to\local\repository
```

---

## 🏗️ 项目结构概览

```
ai-github-analyzer/
├── src/                      # 所有源代码（src 布局）
│   ├── orchestrator/         # 工作流协调
│   ├── scanner/              # 仓库扫描
│   ├── classifier/           # 技术栈分类
│   ├── context_builder/      # 上下文聚合
│   ├── agents/               # AI 代理实现
│   ├── validators/           # 结果验证
│   ├── renderer/             # 输出渲染
│   ├── models/               # Pydantic 数据模型
│   ├── infrastructure/       # 核心基础设施
│   └── utils/                # 实用函数
├── prompts/                  # AI 提示模板
├── schemas/                  # JSON 模式
├── traces/                   # 执行追踪
├── tests/                    # 测试套件
├── docs/                     # 文档
├── main.py                   # CLI 入口点
├── pyproject.toml            # 项目配置
└── README.md                 # 项目概述
```

---

## 📚 文档

| 文档 | 用途 |
|----------|---------|
| [README.md](README.md) | 项目概述、特性、基本用法 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 详细的架构设计和模块职责 |
| [AGENTS.md](AGENTS.md) | AI 代理规范和设计 |
| [docs/ENVIRONMENT_SETUP.md](docs/ENVIRONMENT_SETUP.md) | 完整的环境设置指南 |
| [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | 全面的项目结构指南 |

---

## 🔧 开发命令

### 代码质量

```powershell
# 使用 Black 格式化代码
black src/ main.py

# 使用 Ruff 进行代码检查
ruff check src/ main.py

# 自动修复代码检查问题
ruff check src/ main.py --fix

# 使用 MyPy 进行类型检查
mypy src/
```

### 测试

```powershell
# 运行所有测试
pytest tests/ -v

# 运行并生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 运行特定测试文件
pytest tests/test_scanner/ -v
```

---

## 🎯 当前状态：第一阶段骨架

### ✅ 已完成

- [x] 项目目录结构已创建
- [x] 所有模块包已使用 `__init__.py` 初始化
- [x] `pyproject.toml` 已配置依赖
- [x] `.gitignore` 包含全面的规则
- [x] 基础 Pydantic 模型已定义
- [x] 使用 Typer 的 CLI 入口点
- [x] Rich 终端输出集成
- [x] Loguru 日志配置
- [x] 文档（README、ARCHITECTURE、AGENTS）
- [x] 环境设置指南
- [x] 快速设置脚本（`setup.ps1`）

### 🚧 下一步（实现阶段）

1. **扫描器模块** - 实现仓库扫描逻辑
2. **分类器模块** - 构建技术检测
3. **上下文构建器** - 创建上下文聚合
4. **代理** - 实现 AI 代理
5. **验证器** - 添加结果验证
6. **渲染器** - 构建输出格式化
7. **测试** - 编写全面的测试套件

---

## 🛠️ 技术栈

| 技术 | 用途 | 版本 |
|------------|---------|---------|
| Python | 编程语言 | >= 3.12 |
| Typer | CLI 框架 | >= 0.9.0 |
| Rich | 终端格式化 | >= 13.7.0 |
| Loguru | 日志记录 | >= 0.7.0 |
| Pydantic | 数据验证 | >= 2.5.0 |
| Pydantic Settings | 配置管理 | >= 2.1.0 |

### 开发工具

| 工具 | 用途 | 版本 |
|------|---------|---------|
| pytest | 测试框架 | >= 7.4.0 |
| pytest-asyncio | 异步测试 | >= 0.21.0 |
| black | 代码格式化 | >= 23.0.0 |
| ruff | 代码检查 | >= 0.1.0 |
| mypy | 类型检查 | >= 1.7.0 |

---

## 📝 关键设计原则

1. **整洁架构**：清晰的关注点分离
2. **模型驱动**：所有模块通过 Pydantic 模型通信
3. **异步优先**：基于 asyncio 构建并发
4. **拒绝过度工程**：轻量级、专注的模块
5. **可扩展**：易于添加新代理和功能
6. **类型安全**：完整的类型提示和运行时验证

---

## 🔍 模块职责

| 模块 | 职责 | 输入 | 输出 |
|--------|---------------|-------|--------|
| **协调器** | 协调工作流 | AnalysisConfig | AnalysisResult |
| **扫描器** | 提取仓库结构 | 仓库 URL/路径 | ScanResult |
| **分类器** | 识别技术栈 | ScanResult | ClassificationResult |
| **上下文构建器** | 构建上下文 | 扫描 + 分类结果 |  enriched Context |
| **代理** | 专门分析 | 上下文 | 代理结果 |
| **验证器** | 验证结果 | 原始结果 | 验证后的结果 |
| **渲染器** | 格式化输出 | 验证后的结果 | 格式化输出 |

---

## ⚙️ 配置

### 环境变量（可选）

从模板创建 `.env` 文件：

```powershell
copy .env.example .env
```

编辑 `.env` 填入您的设置：

```env
AI_PROVIDER=openai
AI_MODEL=gpt-4-turbo
AI_API_KEY=your_api_key_here
AGENT_TIMEOUT=60
LOG_LEVEL=INFO
```

### 命令行选项

所有设置都可以通过 CLI 覆盖：

```powershell
python main.py analyze <repo_url> \
  --format markdown \
  --verbose
```

---

## 🐛 故障排除

### 问题："Module not found"

**解决方案**：确保您在项目根目录
```powershell
cd E:\code\project\AI-GitHub-Project-Analyzer\ai-github-analyzer
python main.py version
```

### 问题："Conda not recognized"

**解决方案**：将 conda 添加到 PATH 或使用 Anaconda Prompt

### 问题：依赖冲突

**解决方案**：重新创建环境
```powershell
conda deactivate
conda env remove -n ai-github-analyzer
conda create -n ai-github-analyzer python=3.12 -y
conda activate ai-github-analyzer
pip install -e .
```

---

## 📞 获取帮助

1. 检查 `docs/` 文件夹中的文档
2. 仔细查看错误消息
3. 检查 `logs/` 目录中的日志（运行后）
4. 在 GitHub 上搜索现有问题
5. 创建包含详细信息的新问题

---

## 🎓 学习资源

- **Typer**: https://typer.tiangolo.com/
- **Rich**: https://rich.readthedocs.io/
- **Loguru**: https://loguru.readthedocs.io/
- **Pydantic**: https://docs.pydantic.dev/
- **asyncio**: https://docs.python.org/3/library/asyncio.html

---

## ✨ 快速测试

尝试分析此仓库作为测试：

```powershell
# 分析一个简单的 Python 项目
python main.py analyze https://github.com/pallets/flask

# 或在本地分析（如果您有仓库）
python main.py analyze .
```

---

**准备好开始开发了！** 🚀

下一步：阅读 [ARCHITECTURE.md](ARCHITECTURE.md) 了解设计，然后开始实现模块。

*最后更新：2026-05-14*
