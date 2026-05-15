# 启动流程分析 Prompt

## 任务描述

分析项目的启动流程和运行方式。

## 输入变量

- `repo_name`: {{repo_name}}
- `directory_tree`: {{directory_tree}}
- `key_files`: {{key_files}}
- `sampled_code`: {{sampled_code}}

## 输出要求

说明以下内容：

- 环境准备步骤
- 依赖安装命令
- 数据库初始化
- 启动命令
- 构建命令
- 测试命令
- 常见配置项

## 分析步骤（重要）

1. **从 `sampled_code` 中提取关键文件内容**：
   - 查找 `pyproject.toml`、`package.json`、`requirements.txt`、`pom.xml`、`go.mod` 等依赖管理文件
   - 提取其中的 scripts/commands 部分（如 package.json 中的 "scripts"）
   - 查找 `main.py`、`app.py`、`index.js` 等入口文件，分析其启动逻辑
   - 检查 `.env.example` 了解环境变量需求

2. **环境准备**：
   - 根据技术栈推断需要的运行时环境（Python版本、Node版本、JDK版本等）
   - 从配置文件中提取环境要求

3. **依赖安装**：
   - Python: `pip install -r requirements.txt` 或 `poetry install`
   - Node.js: `npm install` 或 `pnpm install`
   - Java: `mvn install` 或 `gradle build`
   - Go: `go mod download`
   - **必须从实际配置文件中提取准确的命令**

4. **启动命令**：
   - 从入口文件分析启动方式（如 `python main.py`、`npm start`）
   - 检查是否有 Docker 启动方式
   - 说明是否需要先构建

5. **数据库初始化**：
   - 检查是否有 migration 文件或 schema 定义
   - 说明数据库类型和初始化步骤

## 约束条件

- **禁止返回"未检测到明确的启动命令"之类的空洞回答**
- **必须从 `sampled_code` 中实际提取命令和步骤**
- 如果确实没有找到明确命令，请根据技术栈和项目结构推断最可能的命令
- 基于实际配置文件分析
- 提供完整命令示例
- 说明环境变量需求
- 标记缺失的配置说明
