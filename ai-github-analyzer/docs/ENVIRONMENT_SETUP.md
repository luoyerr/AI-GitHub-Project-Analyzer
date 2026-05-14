# 环境设置指南

## 使用 Anaconda 快速开始

本指南提供使用 Anaconda 设置开发环境的分步说明。

### 前置要求

1. **安装 Anaconda 或 Miniconda**
   - 下载地址：https://www.anaconda.com/download
   - Miniconda（轻量级）：https://docs.conda.io/en/latest/miniconda.html

2. **验证安装**
   ```bash
   conda --version
   python --version
   ```

---

## 步骤 1：克隆仓库

```bash
git clone <repository-url>
cd ai-github-analyzer
```

---

## 步骤 2：创建 Conda 环境

使用 Python 3.12 创建新环境：

```bash
conda create -n ai-github-analyzer python=3.12 -y
```

**解释**：
- `-n ai-github-analyzer`：命名环境
- `python=3.12`：指定 Python 版本
- `-y`：自动确认安装

---

## 步骤 3：激活环境

```bash
conda activate ai-github-analyzer
```

您应该在终端提示符中看到 `(ai-github-analyzer)`。

---

## 步骤 4：安装依赖

### 选项 A：从 pyproject.toml 安装（推荐）

```bash
pip install -e .
```

这将以**可编辑/开发模式**安装包，意味着：
- 源代码的更改会立即反映
- 修改后无需重新安装
- 安装 `pyproject.toml` 中的所有依赖

### 选项 B：安装开发依赖

```bash
pip install -e ".[dev]"
```

这包括额外的工具：
- `pytest`：测试框架
- `black`：代码格式化器
- `ruff`：快速代码检查器
- `mypy`：类型检查器

### 选项 C：手动安装（如需要）

```bash
pip install typer>=0.9.0 rich>=13.7.0 loguru>=0.7.0 pydantic>=2.5.0
```

---

## 步骤 5：验证安装

测试一切是否正常：

```bash
# 检查包安装
python main.py version

# 测试分析命令
python main.py analyze --help

# 验证导入正常工作
python -c "from src.models.base_models import AnalysisConfig; print('✓ 导入正常')"
```

预期输出：
```
AI GitHub Analyzer v0.1.0
```

---

## 步骤 6：配置环境变量（可选）

创建 `.env` 文件进行配置：

```bash
# 复制示例 env 文件
cp .env.example .env

# 使用您的设置编辑
nano .env  # 或使用您喜欢的编辑器
```

示例 `.env` 内容：
```env
# AI 提供商配置
AI_PROVIDER=openai
AI_MODEL=gpt-4-turbo
AI_API_KEY=your_api_key_here

# 代理设置
AGENT_TIMEOUT=60
AGENT_MAX_RETRIES=2
AGENT_PARALLEL_LIMIT=4

# 日志
LOG_LEVEL=INFO
```

**注意**：`.env` 文件已被 gitignore，绝不应提交。

---

## 开发工作流

### 运行应用程序

```bash
# 基本用法
python main.py analyze https://github.com/username/repo

# 带选项
python main.py analyze https://github.com/username/repo --format json --verbose
```

### 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行并生成覆盖率报告
pytest tests/ --cov=src --cov-report=html

# 运行特定测试文件
pytest tests/test_scanner.py -v
```

### 代码质量检查

```bash
# 格式化代码
black src/ main.py

# 检查代码
ruff check src/ main.py

# 自动修复代码检查问题
ruff check src/ main.py --fix

# 类型检查
mypy src/
```

### Pre-commit Hook 设置（可选）

```bash
# 安装 pre-commit
pip install pre-commit

# 初始化 hooks
pre-commit install

# 手动运行
pre-commit run --all-files
```

---

## 故障排除

### 问题：Conda 命令未找到

**解决方案**：将 conda 添加到 PATH
```bash
# Windows (PowerShell)
$env:Path += ";C:\Users\<YourUser>\Anaconda3\Scripts"

# macOS/Linux
export PATH="$HOME/anaconda3/bin:$PATH"
```

添加到您的 shell 配置文件（`~/.bashrc`、`~/.zshrc` 或 PowerShell profile）以持久化。

---

### 问题：安装期间权限错误

**解决方案**：确保您在激活的环境中
```bash
conda activate ai-github-analyzer
pip install -e .
```

在 conda 环境中不要对 pip 使用 `sudo`。

---

### 问题：依赖冲突

**解决方案**：创建新环境
```bash
# 删除旧环境
conda deactivate
conda env remove -n ai-github-analyzer

# 重新创建
conda create -n ai-github-analyzer python=3.12 -y
conda activate ai-github-analyzer
pip install -e .
```

---

### 问题：模块未找到错误

**解决方案**：确保您在项目根目录
```bash
# 导航到项目根目录
cd path/to/ai-github-analyzer

# 验证结构
ls src/
# 应显示：orchestrator/ scanner/ classifier/ 等

# 从项目根目录运行
python main.py version
```

---

### 问题：Python 版本不匹配

**解决方案**：验证 Python 版本
```bash
python --version
# 应显示：Python 3.12.x

# 如果版本错误，重新创建环境
conda env remove -n ai-github-analyzer
conda create -n ai-github-analyzer python=3.12 -y
```

---

## 环境管理命令

### 有用的 Conda 命令

```bash
# 列出所有环境
conda env list

# 激活环境
conda activate ai-github-analyzer

# 停用环境
conda deactivate

# 更新包
conda update --all

# 导出环境
conda env export > environment.yml

# 从导出的文件创建
conda env create -f environment.yml

# 删除环境
conda env remove -n ai-github-analyzer
```

### 有用的 Pip 命令

```bash
# 列出已安装的包
pip list

# 显示过时的包
pip list --outdated

# 更新特定包
pip install --upgrade package_name

# 卸载包
pip uninstall package_name

# 显示包信息
pip show package_name
```

---

## IDE 配置

### Visual Studio Code

1. **安装扩展**：
   - Python (Microsoft)
   - Pylance
   - Black Formatter
   - Ruff

2. **选择解释器**：
   - 按 `Ctrl+Shift+P`（Mac 上为 `Cmd+Shift+P`）
   - 输入 "Python: Select Interpreter"
   - 选择 conda 环境：`ai-github-analyzer`

3. **配置设置**（`.vscode/settings.json`）：
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

1. **添加 Conda 环境**：
   - 转到 `File → Settings → Project → Python Interpreter`
   - 点击齿轮图标 → `Add`
   - 选择 `Conda Environment` → `Existing Environment`
   - 浏览到：`<conda_path>/envs/ai-github-analyzer/bin/python`

2. **配置测试运行器**：
   - 转到 `File → Settings → Tools → Python Integrated Tools`
   - 将 `Default test runner` 设置为 `pytest`

---

## Docker 设置（可选）

用于容器化开发：

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

构建和运行：
```bash
docker build -t ai-github-analyzer .
docker run ai-github-analyzer analyze https://github.com/username/repo
```

---

## 持续集成

### GitHub Actions 示例

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

## 性能提示

### 加速 Conda

使用 `mamba` 进行更快的依赖解析：
```bash
conda install mamba -n base -c conda-forge
mamba create -n ai-github-analyzer python=3.12 -y
```

### 虚拟环境位置

默认情况下，conda 将环境存储在：
- **Windows**: `C:\Users\<User>\anaconda3\envs\`
- **macOS/Linux**: `~/anaconda3/envs/`

更改位置：
```bash
conda config --add envs_dirs /path/to/custom/envs
```

---

## 下一步

设置环境后：

1. ✅ 阅读 [README.md](README.md) 了解使用说明
2. ✅ 查看 [ARCHITECTURE.md](ARCHITECTURE.md) 了解设计概览
3. ✅ 检查 [AGENTS.md](AGENTS.md) 了解代理规范
4. 📝 根据架构开始实现模块
5. 🧪 开发时编写测试
6. 📊 在示例仓库上运行分析器

---

## 支持

如果遇到问题：

1. 检查上面的故障排除部分
2. 仔细查看错误消息
3. 在 GitHub 上搜索现有问题
4. 创建新问题，包含：
   - 您的操作系统和 Python 版本
   - 完整错误消息
   - 重现步骤
   - 环境详细信息（`conda list`）

---

*最后更新：2026-05-14*
