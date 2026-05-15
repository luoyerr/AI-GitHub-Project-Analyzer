# 风险分析 Prompt

## 任务描述

识别项目的潜在风险和待改进点。

## 输入变量

- `repo_name`: {{repo_name}}
- `directory_tree`: {{directory_tree}}
- `key_files`: {{key_files}}
- `sampled_code`: {{sampled_code}}
- `detected_tech_stack`: {{detected_tech_stack}}

## 输出要求

分析以下风险维度：

- 安全风险（硬编码密钥、注入漏洞等）
- 性能风险（N+1 查询、内存泄漏等）
- 可维护性风险（代码重复、复杂度过高等）
- 扩展性风险（紧耦合、缺乏接口等）
- 技术债（过时依赖、废弃 API 等）
- 文档风险（缺少文档、文档过时等）

## 约束条件

- 基于代码证据分析
- 按严重程度排序
- 提供改进建议
- 避免过度批评
- **重要**：必须基于实际的项目信息进行分析，不要返回“请提供xxx”之类的提示
