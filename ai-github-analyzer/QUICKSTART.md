# Quick Start Guide - AI GitHub Analyzer

## 🚀 5-Minute Setup

### Step 1: Create Conda Environment

```powershell
# Navigate to project directory
cd E:\code\project\AI-GitHub-Project-Analyzer\ai-github-analyzer

# Create environment with Python 3.12
conda create -n ai-github-analyzer python=3.12 -y

# Activate the environment
conda activate ai-github-analyzer
```

### Step 2: Install Dependencies

```powershell
# Install package in development mode
pip install -e .

# Or install with dev dependencies (recommended for developers)
pip install -e ".[dev]"
```

### Step 3: Verify Installation

```powershell
# Check if installation was successful
python main.py version

# Expected output: AI GitHub Analyzer v0.1.0
```

### Step 4: Test the CLI

```powershell
# Show help
python main.py --help

# Show analyze command help
python main.py analyze --help
```

---

## 📖 Basic Usage

### Analyze a GitHub Repository

```powershell
# Basic analysis
python main.py analyze https://github.com/username/repository

# Specify output format
python main.py analyze https://github.com/username/repository --format json

# Enable verbose output
python main.py analyze https://github.com/username/repository --verbose

# Combine options
python main.py analyze https://github.com/username/repository -f markdown -v
```

### Analyze a Local Repository

```powershell
python main.py analyze C:\path\to\local\repository
```

---

## 🏗️ Project Structure Overview

```
ai-github-analyzer/
├── src/                      # All source code (src layout)
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
├── main.py                   # CLI entry point
├── pyproject.toml            # Project configuration
└── README.md                 # Project overview
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Project overview, features, basic usage |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Detailed architecture design and module responsibilities |
| [AGENTS.md](AGENTS.md) | AI agent specifications and design |
| [docs/ENVIRONMENT_SETUP.md](docs/ENVIRONMENT_SETUP.md) | Complete environment setup guide |
| [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md) | Comprehensive project structure guide |

---

## 🔧 Development Commands

### Code Quality

```powershell
# Format code with Black
black src/ main.py

# Lint with Ruff
ruff check src/ main.py

# Auto-fix linting issues
ruff check src/ main.py --fix

# Type checking with MyPy
mypy src/
```

### Testing

```powershell
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_scanner/ -v
```

---

## 🎯 Current Status: Phase 1 Skeleton

### ✅ Completed

- [x] Project directory structure created
- [x] All module packages initialized with `__init__.py`
- [x] `pyproject.toml` configured with dependencies
- [x] `.gitignore` with comprehensive rules
- [x] Base Pydantic models defined
- [x] CLI entry point with Typer
- [x] Rich terminal output integration
- [x] Loguru logging configuration
- [x] Documentation (README, ARCHITECTURE, AGENTS)
- [x] Environment setup guide
- [x] Quick setup script (`setup.ps1`)

### 🚧 Next Steps (Implementation)

1. **Scanner Module** - Implement repository scanning logic
2. **Classifier Module** - Build technology detection
3. **Context Builder** - Create context aggregation
4. **Agents** - Implement AI agents
5. **Validators** - Add result validation
6. **Renderer** - Build output formatting
7. **Tests** - Write comprehensive test suite

---

## 🛠️ Technology Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| Python | Programming language | >= 3.12 |
| Typer | CLI framework | >= 0.9.0 |
| Rich | Terminal formatting | >= 13.7.0 |
| Loguru | Logging | >= 0.7.0 |
| Pydantic | Data validation | >= 2.5.0 |
| Pydantic Settings | Configuration | >= 2.1.0 |

### Development Tools

| Tool | Purpose | Version |
|------|---------|---------|
| pytest | Testing | >= 7.4.0 |
| pytest-asyncio | Async testing | >= 0.21.0 |
| black | Code formatting | >= 23.0.0 |
| ruff | Linting | >= 0.1.0 |
| mypy | Type checking | >= 1.7.0 |

---

## 📝 Key Design Principles

1. **Clean Architecture**: Clear separation of concerns
2. **Model-Driven**: All modules communicate via Pydantic models
3. **Async-First**: Built on asyncio for concurrency
4. **No Over-Engineering**: Lightweight, focused modules
5. **Extensible**: Easy to add new agents and features
6. **Type-Safe**: Full type hints and runtime validation

---

## 🔍 Module Responsibilities

| Module | Responsibility | Input | Output |
|--------|---------------|-------|--------|
| **Orchestrator** | Coordinate workflow | AnalysisConfig | AnalysisResult |
| **Scanner** | Extract repo structure | Repo URL/path | ScanResult |
| **Classifier** | Identify tech stack | ScanResult | ClassificationResult |
| **Context Builder** | Build context | Scan + Classify results | Enriched Context |
| **Agents** | Specialized analysis | Context | Agent Results |
| **Validators** | Validate results | Raw results | Validated results |
| **Renderer** | Format output | Validated results | Formatted output |

---

## ⚙️ Configuration

### Environment Variables (Optional)

Create a `.env` file from the template:

```powershell
copy .env.example .env
```

Edit `.env` with your settings:

```env
AI_PROVIDER=openai
AI_MODEL=gpt-4-turbo
AI_API_KEY=your_api_key_here
AGENT_TIMEOUT=60
LOG_LEVEL=INFO
```

### Command-Line Options

All settings can be overridden via CLI:

```powershell
python main.py analyze <repo_url> \
  --format markdown \
  --verbose
```

---

## 🐛 Troubleshooting

### Issue: "Module not found"

**Solution**: Ensure you're in the project root directory
```powershell
cd E:\code\project\AI-GitHub-Project-Analyzer\ai-github-analyzer
python main.py version
```

### Issue: "Conda not recognized"

**Solution**: Add conda to PATH or use Anaconda Prompt

### Issue: Dependency conflicts

**Solution**: Recreate environment
```powershell
conda deactivate
conda env remove -n ai-github-analyzer
conda create -n ai-github-analyzer python=3.12 -y
conda activate ai-github-analyzer
pip install -e .
```

---

## 📞 Getting Help

1. Check documentation in `docs/` folder
2. Review error messages carefully
3. Check logs in `logs/` directory (after running)
4. Search existing issues on GitHub
5. Create a new issue with details

---

## 🎓 Learning Resources

- **Typer**: https://typer.tiangolo.com/
- **Rich**: https://rich.readthedocs.io/
- **Loguru**: https://loguru.readthedocs.io/
- **Pydantic**: https://docs.pydantic.dev/
- **asyncio**: https://docs.python.org/3/library/asyncio.html

---

## ✨ Quick Test

Try analyzing this repository as a test:

```powershell
# Analyze a simple Python project
python main.py analyze https://github.com/pallets/flask

# Or analyze locally (if you have a repo)
python main.py analyze .
```

---

**Ready to start developing!** 🚀

Next: Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the design, then start implementing modules.

*Last Updated: 2026-05-14*
