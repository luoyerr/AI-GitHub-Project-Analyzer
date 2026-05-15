# 配置分析 Prompt

## 任务描述

分析项目的配置文件和配置策略。

## 输入变量

- `repo_name`: 仓库名称
- `context`: 项目上下文信息
- `config_files`: 配置文件内容
- `env_example`: .env.example 内容

## 输出要求

分析以下配置：

- YAML/JSON/Properties 配置
- 环境变量配置
- Docker 配置
- CI/CD 配置
- 日志配置
- 数据库配置

## 约束条件

- 脱敏敏感信息
- 说明配置项含义
- 识别配置最佳实践
- 标记不合理的配置
