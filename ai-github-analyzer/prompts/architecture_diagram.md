# 架构图生成 Prompt

## 任务描述

生成项目的 Mermaid 架构图。

## 输入变量

- `repo_name`: 仓库名称
- `context`: 项目上下文信息
- `module_structure`: 模块结构
- `dependency_graph`: 依赖关系图

## 输出要求

生成 Mermaid 格式的架构图，包含：

- 系统整体架构
- 模块间调用关系
- 数据流向
- 外部依赖
- 部署拓扑（如适用）

## 约束条件

- 仅使用 Mermaid 语法
- 保持图表简洁清晰
- 标注关键组件
- 避免过度复杂
