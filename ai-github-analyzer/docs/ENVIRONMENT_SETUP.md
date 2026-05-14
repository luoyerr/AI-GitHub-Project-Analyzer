# Environment Setup Guide

## Quick Start with Anaconda

This guide provides step-by-step instructions for setting up the development environment using Anaconda.

### Prerequisites

1. **Install Anaconda or Miniconda**
   - Download from: https://www.anaconda.com/download
   - Miniconda (lightweight): https://docs.conda.io/en/latest/miniconda.html

2. **Verify Installation**
   ```bash
   conda --version
   python --version
   ```

---

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd ai-github-analyzer
```

---

## Step 2: Create Conda Environment

Create a new environment with Python 3.12:

```bash
conda create -n ai-github-analyzer python=3.12 -y
```

**Explanation**:
- `-n ai-github-analyzer`: Names the environment
- `python=3.12`: Specifies Python version
- `-y`: Automatically confirms installation

---

## Step 3: Activate Environment

```bash
conda activate ai-github-analyzer
```

You should see `(ai-github-analyzer)` in your terminal prompt.

---

## Step 4: Install Dependencies

### Option A: Install from pyproject.toml (Recommended)

```bash
pip install -e .
```

This installs the package in **editable/development mode**, meaning:
- Changes to source code are immediately reflected
- No need to reinstall after modifications
- All dependencies from `pyproject.toml` are installed

### Option B: Install with Development Dependencies

```bash
pip install -e ".[dev]"
```

This includes additional tools:
- `pytest`: Testing framework
- `black`: Code formatter
- `ruff`: Fast linter
- `mypy`: Type checker

### Option C: Manual Installation (if needed)

```bash
pip install typer>=0.9.0 rich>=13.7.0 loguru>=0.7.0 pydantic>=2.5.0
```

---

## Step 5: Verify Installation

Test that everything is working:

```bash
# Check package installation
python main.py version

# Test analyze command
python main.py analyze --help

# Verify imports work
python -c "from src.models.base_models import AnalysisConfig; print('✓ Imports OK')"
```

Expected output:
```
AI GitHub Analyzer v0.1.0
```

---

## Step 6: Configure Environment Variables (Optional)

Create a `.env` file for configuration:

```bash
# Copy example env file
cp .env.example .env

# Edit with your settings
nano .env  # or use your preferred editor
```

Example `.env` content:
```env
# AI Provider Configuration
AI_PROVIDER=openai
AI_MODEL=gpt-4-turbo
AI_API_KEY=your_api_key_here

# Agent Settings
AGENT_TIMEOUT=60
AGENT_MAX_RETRIES=2
AGENT_PARALLEL_LIMIT=4

# Logging
LOG_LEVEL=INFO
```

**Note**: The `.env` file is gitignored and should never be committed.

---

## Development Workflow

### Running the Application

```bash
# Basic usage
python main.py analyze https://github.com/username/repo

# With options
python main.py analyze https://github.com/username/repo --format json --verbose
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_scanner.py -v
```

### Code Quality Checks

```bash
# Format code
black src/ main.py

# Lint code
ruff check src/ main.py

# Auto-fix linting issues
ruff check src/ main.py --fix

# Type checking
mypy src/
```

### Pre-commit Hook Setup (Optional)

```bash
# Install pre-commit
pip install pre-commit

# Initialize hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Troubleshooting

### Issue: Conda command not found

**Solution**: Add conda to PATH
```bash
# Windows (PowerShell)
$env:Path += ";C:\Users\<YourUser>\Anaconda3\Scripts"

# macOS/Linux
export PATH="$HOME/anaconda3/bin:$PATH"
```

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, or PowerShell profile) for persistence.

---

### Issue: Permission errors during installation

**Solution**: Ensure you're in the activated environment
```bash
conda activate ai-github-analyzer
pip install -e .
```

Do NOT use `sudo` with pip in conda environments.

---

### Issue: Dependency conflicts

**Solution**: Create fresh environment
```bash
# Remove old environment
conda deactivate
conda env remove -n ai-github-analyzer

# Recreate
conda create -n ai-github-analyzer python=3.12 -y
conda activate ai-github-analyzer
pip install -e .
```

---

### Issue: Module not found errors

**Solution**: Ensure you're in the project root directory
```bash
# Navigate to project root
cd path/to/ai-github-analyzer

# Verify structure
ls src/
# Should show: orchestrator/ scanner/ classifier/ etc.

# Run from project root
python main.py version
```

---

### Issue: Python version mismatch

**Solution**: Verify Python version
```bash
python --version
# Should show: Python 3.12.x

# If wrong version, recreate environment
conda env remove -n ai-github-analyzer
conda create -n ai-github-analyzer python=3.12 -y
```

---

## Environment Management Commands

### Useful Conda Commands

```bash
# List all environments
conda env list

# Activate environment
conda activate ai-github-analyzer

# Deactivate environment
conda deactivate

# Update packages
conda update --all

# Export environment
conda env export > environment.yml

# Create from exported file
conda env create -f environment.yml

# Remove environment
conda env remove -n ai-github-analyzer
```

### Useful Pip Commands

```bash
# List installed packages
pip list

# Show outdated packages
pip list --outdated

# Update specific package
pip install --upgrade package_name

# Uninstall package
pip uninstall package_name

# Show package info
pip show package_name
```

---

## IDE Configuration

### Visual Studio Code

1. **Install Extensions**:
   - Python (Microsoft)
   - Pylance
   - Black Formatter
   - Ruff

2. **Select Interpreter**:
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Python: Select Interpreter"
   - Choose the conda environment: `ai-github-analyzer`

3. **Configure Settings** (`.vscode/settings.json`):
   ```json
   {
     "python.defaultInterpreterPath": "${workspaceFolder}/.conda/envs/ai-github-analyzer/bin/python",
     "editor.formatOnSave": true,
     "python.formatting.provider": "black",
     "python.linting.enabled": true,
     "python.linting.ruffEnabled": true,
     "python.testing.pytestEnabled": true
   }
   ```

### PyCharm

1. **Add Conda Environment**:
   - Go to `File → Settings → Project → Python Interpreter`
   - Click gear icon → `Add`
   - Select `Conda Environment` → `Existing Environment`
   - Browse to: `<conda_path>/envs/ai-github-analyzer/bin/python`

2. **Configure Test Runner**:
   - Go to `File → Settings → Tools → Python Integrated Tools`
   - Set `Default test runner` to `pytest`

---

## Docker Setup (Optional)

For containerized development:

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY src/ src/
COPY main.py .

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t ai-github-analyzer .
docker run ai-github-analyzer analyze https://github.com/username/repo
```

---

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        pip install -e ".[dev]"
    
    - name: Run tests
      run: pytest tests/ -v
    
    - name: Lint
      run: ruff check src/
    
    - name: Type check
      run: mypy src/
```

---

## Performance Tips

### Speed Up Conda

Use `mamba` for faster dependency resolution:
```bash
conda install mamba -n base -c conda-forge
mamba create -n ai-github-analyzer python=3.12 -y
```

### Virtual Environment Location

By default, conda stores environments in:
- **Windows**: `C:\Users\<User>\anaconda3\envs\`
- **macOS/Linux**: `~/anaconda3/envs/`

To change location:
```bash
conda config --add envs_dirs /path/to/custom/envs
```

---

## Next Steps

After setting up the environment:

1. ✅ Read the [README.md](README.md) for usage instructions
2. ✅ Review the [ARCHITECTURE.md](ARCHITECTURE.md) for design overview
3. ✅ Check [AGENTS.md](AGENTS.md) for agent specifications
4. 📝 Start implementing modules according to architecture
5. 🧪 Write tests as you develop
6. 📊 Run the analyzer on sample repositories

---

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review error messages carefully
3. Search existing issues on GitHub
4. Create a new issue with:
   - Your OS and Python version
   - Full error message
   - Steps to reproduce
   - Environment details (`conda list`)

---

*Last Updated: 2026-05-14*
