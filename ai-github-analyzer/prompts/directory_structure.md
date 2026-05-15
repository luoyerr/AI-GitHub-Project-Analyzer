# 目录结构分析 Prompt

## 任务描述

分析项目的目录结构和各目录职责。

## 输入变量

- `repo_name`: {{repo_name}}
- `directory_tree`: {{directory_tree}}
- `key_files`: {{key_files}}
- `detected_tech_stack`: {{detected_tech_stack}}

## 输出要求

解释以下目录的职责：

- src/ 或源代码目录
- config/ 或配置目录
- tests/ 或测试目录
- docs/ 或文档目录
- 其他重要目录

## 约束条件

- 基于实际目录结构分析
- 说明每个目录的作用
- 识别架构模式（MVC、分层等）
- 标记不明确的目录
- **重要**：必须基于实际的项目信息进行分析，不要返回“请提供xxx”之类的提示
