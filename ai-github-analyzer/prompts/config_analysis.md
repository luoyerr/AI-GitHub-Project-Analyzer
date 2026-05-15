# 配置分析 Prompt

## 任务描述

分析项目的配置文件和配置策略。

## 输入变量

- `repo_name`: {{repo_name}}
- `directory_tree`: {{directory_tree}}
- `key_files`: {{key_files}}
- `sampled_code`: {{sampled_code}}

## 输出要求

分析以下配置：

- YAML/JSON/Properties 配置
- 环境变量配置
- Docker 配置
- CI/CD 配置
- 日志配置
- 数据库配置

## 分析步骤（重要）

1. **首先检查 `sampled_code` 中的以下内容**：
   - 查找文件名包含 `pyproject.toml`、`package.json`、`.env.example`、`requirements.txt`、`setup.py`、`application.yml`、`config.yaml` 等配置文件
   - 提取这些文件的完整内容
   - 如果没有找到明确的配置文件，从代码中推断配置需求

2. **配置文件分析**：
   - 列出所有检测到的配置文件及其路径
   - 说明每个配置文件的作用和关键配置项
   - 识别配置的最佳实践和潜在问题

3. **环境变量分析**：
   - 从 `.env.example` 或代码中提取环境变量名
   - 说明每个环境变量的用途和默认值
   - 标记必需的变量和可选的变量

4. **Docker/CI-CD 配置**：
   - 检查是否有 `Dockerfile`、`docker-compose.yml`、`.github/workflows/` 等
   - 说明构建和部署流程

## 约束条件

- **禁止返回"未检测到明确的配置文件信息"之类的空洞回答**
- **必须从 `sampled_code` 中实际提取配置内容**
- 如果确实没有找到配置文件，请说明："根据项目结构推断，该项目可能使用XXX方式管理配置"
- 脱敏敏感信息（如密码、密钥、token）
- 说明配置项含义
- 识别配置最佳实践
- 标记不合理的配置
