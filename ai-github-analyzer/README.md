# AI GitHub Analyzer

<div align="center">

**Enterprise-grade AI-powered GitHub repository analyzer with multi-agent orchestration**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

## 🚀 Overview

AI GitHub Analyzer is a sophisticated tool that leverages AI agents to perform comprehensive analysis of GitHub repositories. It automatically detects technology stacks, identifies architecture patterns, assesses code quality, and provides actionable recommendations.

## ✨ Features

- **Multi-Agent Orchestration**: Coordinated AI agents for specialized analysis tasks
- **Technology Stack Detection**: Automatic identification of frameworks, libraries, and tools
- **Architecture Pattern Recognition**: Detects common architectural patterns and design principles
- **Code Quality Assessment**: Evaluates code structure, maintainability, and best practices
- **Rich CLI Interface**: Beautiful terminal output with progress indicators
- **Structured Logging**: Comprehensive logging with loguru for debugging and tracing
- **Extensible Architecture**: Modular design for easy customization and extension

## 📋 Prerequisites

- Python 3.12 or higher
- Anaconda (recommended for environment management)
- Git

## 🛠️ Installation

### Using Anaconda (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd ai-github-analyzer

# Create conda environment
conda create -n ai-github-analyzer python=3.12 -y

# Activate environment
conda activate ai-github-analyzer

# Install in development mode
pip install -e .

# Install development dependencies (optional)
pip install -e ".[dev]"
```

### Using pip only

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e .
```

## 💻 Usage

### Basic Analysis

```bash
# Analyze a GitHub repository
python main.py analyze https://github.com/username/repository

# Analyze a local repository
python main.py analyze /path/to/local/repo

# Specify output format
python main.py analyze https://github.com/username/repository --format json

# Enable verbose output
python main.py analyze https://github.com/username/repository --verbose
```

### Available Commands

```bash
# Show help
python main.py --help

# Analyze command help
python main.py analyze --help

# Show version
python main.py version
```

## 🏗️ Project Structure

```
ai-github-analyzer/
├── src/                      # Source code (src layout)
│   ├── orchestrator/         # Workflow coordination
│   ├── scanner/              # Repository scanning
│   ├── classifier/           # Tech stack classification
│   ├── context_builder/      # Context aggregation
│   ├── agents/               # AI agent implementations
│   ├── validators/           # Result validation
│   ├── renderer/             # Output rendering
│   ├── models/               # Pydantic data models
│   ├── infrastructure/       # Core infrastructure
│   └── utils/                # Utility functions
├── prompts/                  # AI prompt templates
├── schemas/                  # JSON schemas
├── traces/                   # Execution traces
├── tests/                    # Test suite
├── docs/                     # Documentation
│   └── design-docs/          # Design documents
├── main.py                   # CLI entry point
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

## 🔧 Development

### Running Tests

```bash
pytest tests/ -v
```

### Code Formatting

```bash
# Format code with black
black src/ main.py

# Lint with ruff
ruff check src/ main.py

# Type checking with mypy
mypy src/
```

## 📖 Documentation

- [Architecture Design](ARCHITECTURE.md)
- [Agent Specifications](AGENTS.md)
- [Design Documents](docs/design-docs/)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) for CLI
- Styled with [Rich](https://rich.readthedocs.io/) for beautiful terminal output
- Logged with [Loguru](https://loguru.readthedocs.io/) for structured logging
- Validated with [Pydantic](https://docs.pydantic.dev/) for data modeling

---

<div align="center">
Made with ❤️ for the developer community
</div>
