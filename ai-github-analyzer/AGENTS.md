# AI GitHub Project Analyzer - Agent 行为规范

**版本**: v2.0
 **适用系统**: AI-GitHub-Project-Analyzer
 **架构类型**: Five-Layer Pipeline (Harness-inspired)

------

# 1. Agent 总目标

所有参与本项目的 AI / 自动化 Agent 必须遵循以下目标：

> 将任意 GitHub / 本地代码仓库 → 转换为结构化企业级分析报告

输出必须是：

- 可读
- 可扩展
- 可验证
- 可复现

------

# 2. 系统本质（必须理解）

本系统不是：

- ❌ Multi-Agent System
- ❌ AutoGen / CrewAI
- ❌ LangGraph DAG runtime

本系统是：

> ✅ Five-Layer Pipeline + Task Executor Architecture

核心特征：

- 串行执行（8 Tasks）
- 静态 DAG
- Prompt 驱动 LLM
- 无 Agent 自主决策

------

# 3. Five-Layer 架构约束

所有 Agent 行为必须严格遵循：

## Layer 1 - Scanner

职责：

- 仓库解析
- GitHub clone
- 文件树生成

禁止：

- ❌ 解析业务逻辑
- ❌ 做 AI 判断

------

## Layer 2 - Tech Stack Analyzer

职责：

- 规则识别技术栈
- 基于文件名 / 配置文件判断

禁止：

- ❌ 使用 LLM
- ❌ 推测业务架构

------

## Layer 3 - Context Builder

职责：

- 文件筛选
- 优先级排序
- token 控制

禁止：

- ❌ 修改文件内容
- ❌ 推理业务逻辑

------

## Layer 4 - AI Engine（核心）

职责：

- 执行 8 个 Task
- 调用 LLM
- 生成结构化分析

关键约束：

- 必须使用 PromptManager
- 必须使用 BaseTask 模板
- 必须按 DAG 顺序执行
- 不允许跳过 Task

------

## Layer 5 - Report Generator

职责：

- Markdown 生成
- 格式化输出
- 写入 PROJECT_ANALYSIS.md

禁止：

- ❌ 修改分析逻辑
- ❌ 重新解释 LLM 输出

------

# 4. 8 Task 执行规范

必须严格执行顺序：

```
1. tech_stack
2. directory_structure
3. core_modules
4. startup_flow
5. config_analysis
6. risks
7. architecture_diagram
8. learning_path
```

## Task 行为规则

每个 Task 必须：

### 必须

- 使用 PromptManager
- 使用 AIContext
- 输出结构化 JSON
- 通过 validate_result()

### 禁止

- ❌ return raw text
- ❌ skip LLM
- ❌ hardcode result
- ❌ cross-task mutation

------

# 5. Prompt 规范（非常关键）

所有 Prompt 必须满足：

## 规则

- 必须在 `prompts/*.md`
- 必须使用 `{{variable}}`
- 必须 UTF-8
- 必须模块化

## 禁止

- ❌ Prompt 写在 Python 代码中
- ❌ 动态拼接业务逻辑
- ❌ 隐式 prompt injection

------

# 6. LLM 调用规范

所有 LLM 调用必须：

## 使用统一接口

```
LLMClient.generate()
```

## 必须包含：

- system_prompt
- user_prompt
- temperature = 0.7
- max_tokens ≤ 4000

------

## 禁止

- ❌ 直接调用 OpenAI SDK（绕过 LLMClient）
- ❌ 多 provider 混用未统一
- ❌ 无 system prompt

------

# 7. 数据流约束

必须遵循：

```
Repo
 → RepositorySnapshot
 → ProjectTechStack
 → AIContext
 → TaskContext
 → PromptResult[8]
 → AnalysisResult
 → Markdown
```

## 禁止

- ❌ 跳过 AIContext
- ❌ Task 直接访问文件系统
- ❌ Task 之间直接通信

------

# 8. DAG 执行规则

当前系统：

> Static DAG (Serial Execution)

## 规则

- 必须顺序执行
- 不允许乱序 Task
- 不允许并行（当前版本）

## 未来扩展（禁止当前实现）

- ❌ Parallel execution
- ❌ Dynamic DAG
- ❌ Agent-based scheduling

------

# 9. 代码修改规范（非常重要）

## 修改优先级

1. Prompt（优先）
2. Task Parser
3. Context Builder
4. LLM Client
5. Scanner（最后）

------

## 禁止行为

- ❌ 修改 Layer 顺序
- ❌ 跳过 Context Builder
- ❌ 直接修改 AnalysisResult 结构

------

# 10. 错误处理规范

## 必须行为

- 捕获 LLM 异常
- 记录失败 Task
- 允许 Task fail but continue

## 禁止

- ❌ crash entire pipeline
- ❌ silent failure
- ❌ ignore LLM error

------

# 11. 输出规范

最终必须生成：

```
PROJECT_ANALYSIS.md
```

必须包含：

- 8 个章节
- Mermaid 图
- 技术栈总结
- 风险分析
- 学习路径

------

# 12. 扩展规则（未来演进）

允许扩展：

- 新 Task（必须注册到 TaskRegistry）
- 新 Prompt
- 新 Parser

禁止：

- ❌ 修改核心 Pipeline
- ❌ 改变 5 Layer 架构
- ❌ 破坏 DAG 顺序

------

# 13. Agent 行为总结（最重要）

所有 Agent 必须遵守一句话原则：

> “只做本层该做的事，不跨层，不越权，不自作主张”

------

# 14. 一句话架构认知

> Scanner → Structure → Context → LLM Tasks → Report