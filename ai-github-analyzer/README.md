# AI GitHub Analyzer

<div align="center">

**企业级 AI 驱动的 GitHub 仓库分析器，支持多代理协调**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

## 🚀 概述

AI GitHub Analyzer 是一款精密的工具，利用 AI 代理对 GitHub 仓库进行全面分析。它能自动检测技术栈、识别架构模式、评估代码质量，并提供可操作的建议。

## ✨ 特性

- **多代理协调**：协调的 AI 代理执行专门的分析任务
- **技术栈检测**：自动识别框架、库和工具
- **架构模式识别**：检测常见的架构模式和设计原则
- **代码质量评估**：评估代码结构、可维护性和最佳实践
- **丰富的 CLI 界面**：带有进度指示器的精美终端输出
- **结构化日志**：使用 loguru 进行全面的日志记录，便于调试和追踪
- **可扩展架构**：模块化设计，易于定制和扩展

## 📋 前置要求

- Python 3.12 或更高版本
- Anaconda（推荐用于环境管理）
- Git

## 🛠️ 安装方式

### 使用 Anaconda（推荐）

```bash
# 克隆仓库
git clone <repository-url>
cd ai-github-analyzer

# 创建 conda 环境
conda create -n ai-github-analyzer python=3.12 -y

# 激活环境
conda activate ai-github-analyzer

# 以开发模式安装
pip install -e .

# 安装开发依赖（可选）
pip install -e ".[dev]"
```

### 仅使用 pip

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装包
pip install -e .
```

## 💻 使用方法

### 基本分析

```bash
# 分析 GitHub 仓库
python main.py analyze https://github.com/username/repository

# 分析本地仓库
python main.py analyze /path/to/local/repo

# 指定输出格式
python main.py analyze https://github.com/username/repository --format json

# 启用详细输出
python main.py analyze https://github.com/username/repository --verbose
```

### 可用命令

```bash
# 显示帮助
python main.py --help

# 分析命令帮助
python main.py analyze --help

# 显示版本
python main.py version
```

## 🏗️ 项目结构

```
ai-github-analyzer/
├── src/                      # 源代码（src 布局）
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
│   └── design-docs/          # 设计文档
├── main.py                   # CLI 入口点
├── pyproject.toml            # 项目配置
└── README.md                 # 本文件
```

## 🔧 开发

### 运行测试

```bash
pytest tests/ -v
```

### 代码格式化

```bash
# 使用 black 格式化代码
black src/ main.py

# 使用 ruff 进行代码检查
ruff check src/ main.py

# 使用 mypy 进行类型检查
mypy src/
```

## 📖 文档

- [架构设计](ARCHITECTURE.md)
- [代理规范](AGENTS.md)
- [设计文档](docs/design-docs/)

## 🤝 贡献

欢迎贡献！请随时提交 Pull Request。

1. Fork 仓库
2. 创建功能分支（`git checkout -b feature/amazing-feature`）
3. 提交更改（`git commit -m 'Add amazing feature'`）
4. 推送到分支（`git push origin feature/amazing-feature`）
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件。

## 👥 作者

- Your Name - 初始工作

## 🙏 致谢

- 使用 [Typer](https://typer.tiangolo.com/) 构建 CLI
- 使用 [Rich](https://rich.readthedocs.io/) 美化终端输出
- 使用 [Loguru](https://loguru.readthedocs.io/) 进行结构化日志记录
- 使用 [Pydantic](https://docs.pydantic.dev/) 进行数据建模

---

<div align="center">
为开发者社区用心打造 ❤️
</div>
