# 核心模块分析 Prompt

## 任务描述

识别和分析项目的核心模块及其职责。

## 输入变量

- `repo_name`: 仓库名称
- `context`: 项目上下文信息
- `module_files`: 模块相关文件
- `import_graph`: 导入关系图

## 输出要求

分析以下模块：

- Controller/API 层
- Service/业务逻辑层
- Repository/数据访问层
- Domain/领域模型层
- Middleware/中间件层
- Utils/工具类

## 约束条件

- 识别模块间依赖关系
- 说明每个模块的核心职责
- 评估模块设计合理性
- 标记耦合度高的模块
