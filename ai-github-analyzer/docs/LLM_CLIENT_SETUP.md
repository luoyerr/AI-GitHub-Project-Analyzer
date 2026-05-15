# LLM 客户端调整说明文档

## 一、修改文件

### 1. 新增文件

#### `src/models/llm_response.py`
- **用途**：定义 LLM 响应数据模型
- **包含字段**：
  - `success`: 请求是否成功
  - `content`: AI 返回的内容
  - `model`: 使用的模型名称
  - `token_usage`: Token 使用统计（字典类型）
  - `elapsed_time`: 请求耗时（秒）
  - `error_message`: 错误信息（失败时）

#### `src/models/__init__.py`（已更新）
- 导出新的 `LLMResponse` 模型

### 2. 修改文件

#### `src/ai_engine/llm_client.py`
- **完全重写**，实现以下功能：
  - 支持通过 OpenRouter 调用 Qwen 免费模型
  - 使用 OpenAI SDK 兼容模式
  - 从环境变量读取配置
  - 实现 `generate()` 方法
  - 实现 `validate_connection()` 方法
  - 统一异常处理（不抛出异常，返回失败响应）
  - 使用 loguru 记录日志

#### `pyproject.toml`（已更新）
- 添加依赖：
  - `openai>=2.0.0`
  - `python-dotenv>=1.0.0`

---

## 二、Qwen Free 接入说明

### 核心特性

1. **单一 Provider 支持**
   - 当前阶段仅支持 `openai_compatible` 模式
   - 通过 OpenRouter 调用 Qwen 免费模型
   - 不使用多 provider 架构，避免过度设计

2. **OpenAI Compatible API**
   - 使用 OpenAI SDK 的兼容模式
   - 代码简洁，易于维护
   - 未来可扩展其他兼容 API 的服务商

3. **环境变量驱动**
   - 所有配置通过环境变量管理
   - 支持 `.env` 文件
   - 便于不同环境切换

### 技术实现

```python
from openai import OpenAI

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

response = client.chat.completions.create(
    model=model,
    messages=messages,
    temperature=temperature,
    max_tokens=max_tokens,
    timeout=timeout
)
```

---

## 三、OpenRouter 配置说明

### 环境变量配置

在项目根目录创建 `.env` 文件（参考 `.env.example`）：

```bash
# AI Provider 配置
AI_PROVIDER=openai_compatible
AI_MODEL=qwen/qwen3-coder:free
AI_API_KEY=sk-or-v1-xxx
AI_BASE_URL=https://openrouter.ai/api/v1

# Agent 配置
AGENT_TIMEOUT=60
```

### 环境变量说明

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `AI_PROVIDER` | AI 提供商 | `openai_compatible` | 否 |
| `AI_MODEL` | 模型名称 | `qwen/qwen3-coder:free` | 否 |
| `AI_API_KEY` | API 密钥 | 空字符串 | **是** |
| `AI_BASE_URL` | API 基础 URL | `https://openrouter.ai/api/v1` | 否 |
| `AGENT_TIMEOUT` | 请求超时时间（秒） | `60` | 否 |

### 获取 OpenRouter API Key

1. 访问 [OpenRouter 官网](https://openrouter.ai/)
2. 注册/登录账号
3. 进入 Settings → Keys
4. 创建新的 API Key
5. 复制 Key 到 `.env` 文件的 `AI_API_KEY` 字段

### 可用免费模型

- `qwen/qwen3-coder:free` - 千问代码模型（免费）
- 更多免费模型请参考 OpenRouter 文档

---

## 四、验证方式

### 1. 代码质量检查

```bash
# MyPy 类型检查
mypy src/ai_engine/llm_client.py src/models/llm_response.py

# Ruff 代码规范检查
ruff check src/ai_engine/llm_client.py src/models/llm_response.py
```

**预期结果**：
- MyPy: `Success: no issues found`
- Ruff: `All checks passed!`

### 2. 单元测试

创建测试脚本验证功能：

```python
from src.ai_engine.llm_client import LLMClient

# 创建客户端
client = LLMClient()

# 验证连接
response = client.validate_connection()

if response.success:
    print(f"✓ 连接成功！")
    print(f"  响应: {response.content}")
    print(f"  耗时: {response.elapsed_time:.2f}s")
else:
    print(f"✗ 连接失败: {response.error_message}")
```

### 3. 实际调用测试

```python
from src.ai_engine.llm_client import LLMClient

client = LLMClient()

# 生成响应
response = client.generate(
    prompt="请简单介绍你自己",
    temperature=0.7
)

if response.success:
    print(f"模型: {response.model}")
    print(f"响应: {response.content}")
    print(f"Token 使用: {response.token_usage}")
    print(f"耗时: {response.elapsed_time:.2f}s")
else:
    print(f"错误: {response.error_message}")
```

### 4. 日志验证

运行后查看日志输出，应包含：

```
INFO | LLM 客户端初始化完成 - 模型: qwen/qwen3-coder:free, 提供商: openai_compatible
INFO | 开始验证 LLM 连接...
INFO | LLM 调用成功 - 模型: qwen/qwen3-coder:free, 耗时: X.XXs, Token: XX
INFO | LLM 连接验证成功 - 响应: hello
```

### 5. 常见错误处理

#### 429 错误（速率限制）
```
Error code: 429 - Provider returned error
qwen/qwen3-coder:free is temporarily rate-limited upstream
```

**解决方案**：
- 等待一段时间后重试
- 添加自己的 API Key 以累积速率限制
- 参考：https://openrouter.ai/settings/integrations

#### 401 错误（认证失败）
```
Error code: 401 - Invalid API key
```

**解决方案**：
- 检查 `AI_API_KEY` 是否正确
- 确认 API Key 未过期
- 验证 OpenRouter 账户状态

---

## 五、Git Commit

### 提交命令

```bash
git add .
git commit -m "feat(ai-engine): 接入免费千问模型支持

- 新增 LLMResponse 响应模型
- 实现 LLMClient.generate() 方法
- 实现 LLMClient.validate_connection() 方法
- 支持通过 OpenRouter 调用 Qwen 免费模型
- 使用 OpenAI SDK 兼容模式
- 添加环境变量配置支持
- 统一异常处理，不抛出异常
- 使用 loguru 记录详细日志
- 通过 mypy 和 ruff 检查"
```

### 提交说明

**类型**: `feat` - 新功能

**范围**: `ai-engine` - AI 引擎模块

**描述**:
- 接入免费千问模型支持
- 实现基础的 LLM 调用链路
- 为后续扩展打下基础

**技术细节**:
- 使用 OpenAI Compatible API
- 通过 OpenRouter 调用
- 环境变量驱动配置
- 完整的错误处理和日志记录

---

## 六、后续扩展方向

### 短期优化
1. 添加重试机制（RetryHandler 集成）
2. 添加请求缓存
3. 支持流式响应
4. 添加 Token 计数工具

### 中期扩展
1. 支持多个模型切换
2. 添加模型性能监控
3. 实现请求队列管理
4. 支持批量请求

### 长期规划
1. 支持多 Provider（OpenAI、Ollama 等）
2. 实现智能路由（根据成本、速度选择模型）
3. 添加 A/B 测试框架
4. 实现模型微调支持

---

## 七、注意事项

1. **API Key 安全**
   - 不要将 `.env` 文件提交到 Git
   - 确保 `.gitignore` 包含 `.env`
   - 定期轮换 API Key

2. **速率限制**
   - 免费模型有速率限制
   - 生产环境建议使用付费模型
   - 实现指数退避重试

3. **成本控制**
   - 监控 Token 使用情况
   - 设置预算告警
   - 优化 Prompt 长度

4. **错误处理**
   - 所有异常都被捕获并返回失败响应
   - 不会抛出异常中断程序
   - 通过日志记录详细错误信息

5. **日志管理**
   - 使用 loguru 记录所有调用
   - 包含模型、耗时、Token 等关键指标
   - 便于问题排查和性能分析

---

## 八、相关文件清单

```
ai-github-analyzer/
├── src/
│   ├── ai_engine/
│   │   └── llm_client.py          # LLM 客户端（已修改）
│   └── models/
│       ├── llm_response.py         # LLM 响应模型（新增）
│       └── __init__.py             # 模型导出（已更新）
├── .env.example                    # 环境变量示例
├── pyproject.toml                  # 项目依赖（已更新）
└── docs/
    └── LLM_CLIENT_SETUP.md        # 本文档（新增）
```

---

**文档版本**: 1.0  
**最后更新**: 2026-05-15  
**作者**: AI Assistant
