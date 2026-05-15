# AI GitHub Project Analyzer - 环境配置指南

**版本**: v2.0
 **适用系统**: AI-GitHub-Project-Analyzer
 **架构**: Five-Layer Pipeline (LLM-based)

------

# 1. 系统要求

## 1.1 基础环境

| 项目   | 要求                    |
| ------ | ----------------------- |
| Python | 3.10+                   |
| Git    | 2.0+                    |
| OS     | Windows / macOS / Linux |
| 内存   | ≥ 4GB                   |
| 网络   | 可访问 OpenRouter API   |

------

## 1.2 推荐环境

- Python 3.11
- VSCode
- Git Bash（Windows）
- Conda（可选）

------

# 2. 项目安装

## 2.1 克隆项目

```
git clone https://github.com/your-repo/ai-github-analyzer.git
cd ai-github-analyzer
```

------

## 2.2 创建虚拟环境

### Mac / Linux

```
python3 -m venv venv
source venv/bin/activate
```

### Windows

```
python -m venv venv
venv\Scripts\activate
```

------

## 2.3 安装依赖

```
pip install -r requirements.txt
```

或（如果你用的是 pyproject）

```
pip install -e .
```

------

# 3. 环境变量配置（核心）

创建 `.env` 文件：

```
# ========== LLM CONFIG ==========
AI_PROVIDER=openai_compatible
AI_MODEL=qwen/qwen3-coder:free
AI_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx
AI_BASE_URL=https://openrouter.ai/api/v1

# ========== PIPELINE CONFIG ==========
AGENT_TIMEOUT=60
TOKEN_BUDGET=50000

# ========== DEBUG ==========
DEBUG=true
LOG_LEVEL=INFO

# ========== CACHE (future) ==========
ENABLE_CACHE=false
```

------

# 4. OpenRouter 配置（必须）

## 4.1 获取 API Key

1. 打开 OpenRouter
2. 创建 API Key
3. 复制 `sk-or-v1-xxxx`

------

## 4.2 模型推荐

### 免费模型（推荐）

- `qwen/qwen3-coder:free` ⭐（当前默认）
- `meta-llama/llama-3.1-8b-instruct`
- `mistralai/mistral-7b-instruct`

------

### 高质量模型（可选）

- GPT-4o
- Claude 3.5 Sonnet

------

# 5. 项目启动方式

## 5.1 基础运行

```
python main.py analyze https://github.com/user/repo
```

------

## 5.2 本地路径分析

```
python main.py analyze ./my-project
```

------

## 5.3 Debug 模式

```
DEBUG=true python main.py analyze ./repo
```

------

# 6. 系统运行流程验证

启动成功后，你应该看到：

```
[Scanner] RepositorySnapshot created
[TechStack] Detected: Python, FastAPI
[Context] AIContext built (50 files)
[AI Engine] Executing 8 tasks...
[Report] PROJECT_ANALYSIS.md generated
```

------

# 7. 常见问题（非常重要）

------

## ❌ 问题 1：LLM 调用失败

### 原因

- API Key 错误
- Base URL 错误
- 网络问题

### 解决

```
echo $AI_API_KEY
```

检查：

- 是否是 `sk-or-v1-`
- 是否有额度

------

## ❌ 问题 2：模块 import error

### 解决

```
pip install -e .
```

或：

```
pip install -r requirements.txt
```

------

## ❌ 问题 3：GitHub clone 失败

### 原因

- 网络问题
- repo 不存在

### 解决

```
git clone https://github.com/user/repo --depth 1
```

------

## ❌ 问题 4：报告没生成

检查：

- Layer 4 是否执行完成
- AnalysisResult 是否为空
- logs/

------

## ❌ 问题 5：Mermaid 不显示

原因：

- Markdown 渲染器不支持 Mermaid

解决：

- 用 GitHub
- 或 Typora
- 或 Obsidian

------

# 8. 性能建议（非常关键）

## 当前瓶颈

- 8 次 LLM 串行调用
- 每次 5–15 秒

## 优化建议

### 开启缓存（未来）

```
ENABLE_CACHE=true
```

### 使用更快模型

- qwen3-coder:free（推荐）
- mistral-7b（更快）

------

# 9. 目录结构检查

确保项目结构如下：

```
ai-github-analyzer/
├── scanner/
├── analyzer/
├── context_builder/
├── ai_engine/
├── report/
├── prompts/
├── main.py
├── .env
└── ARCHITECTURE.md
```

------

# 10. 验证系统是否正常（Health Check）

运行：

```
python main.py health
```

预期输出：

```
Scanner: OK
TechStack: OK
ContextBuilder: OK
AI Engine: OK
LLM: OK
Report: OK

SYSTEM STATUS: HEALTHY
```

------

# 11. 推荐开发模式（强烈建议）

## Debug 模式开发

```
DEBUG=true
LOG_LEVEL=DEBUG
```

------

## 推荐流程

1. 跑 scanner
2. 看 context
3. 看 prompt
4. 看 llm response
5. 再改 prompt

------

# 12. 安全说明

- ❌ 不要上传 `.env`
- ❌ 不要 commit API key
- ❌ 不要扫描 production 服务器代码

------

# 13. 一句话总结

> 这个系统本质是：**LLM-driven Code Analysis Pipeline**