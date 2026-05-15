# 核心模块分析 Prompt

## 任务描述

识别和分析项目的核心模块及其职责。

## 输入变量

- `repo_name`: {{repo_name}}
- `directory_tree`: {{directory_tree}}
- `key_files`: {{key_files}}
- `sampled_code`: {{sampled_code}}

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
- **重要**：必须基于实际的项目信息进行分析，不要返回“请提供xxx”之类的提示
