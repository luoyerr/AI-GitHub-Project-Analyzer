# 技术栈分析 Prompt

## 任务描述

分析目标项目的技术栈信息。

## 输入变量

- `repo_name`: {{repo_name}}
- `directory_tree`: {{directory_tree}}
- `key_files`: {{key_files}}
- `detected_tech_stack`: {{detected_tech_stack}}
- `sampled_code`: {{sampled_code}}

## 输出要求

**必须严格按照以下 JSON 格式返回结果**：

```json
{
  "languages": ["Python 3.12", "TypeScript"],
  "frameworks": ["FastAPI", "React"],
  "libraries": ["pydantic", "loguru"],
  "build_tools": ["Poetry"],
  "package_managers": ["pip"],
  "databases": [],
  "ci_cd": [],
  "containers": ["Docker"],
  "cloud_native": [],
  "testing_tools": [],
  "confidence": 0.8,
  "evidence": {
    "languages": ["来自 pyproject.toml"],
    "frameworks": ["来自 requirements.txt"]
  }
}
```

识别以下内容：

- 编程语言及版本
- 核心框架
- 主要依赖库
- 构建工具
- 部署工具
- 数据库技术

## 约束条件

- 基于配置文件和依赖文件分析
- 避免猜测
- 标记不确定性
- 提供证据来源
- **重要**：必须基于实际的项目信息进行分析，不要返回“请提供xxx”之类的提示
- **如果某个字段没有信息，使用空数组 []，不要编造**
