"""
技术栈规则定义

职责：
定义用于识别技术栈的规则和模式。

设计原则：
1. 配置驱动 - 禁止 if/else 硬编码
2. 高内聚低耦合 - 按功能分类组织规则
3. 可扩展性 - 新增语言只需添加规则，无需修改检测逻辑
4. 中文注释 - 所有注释使用中文

规则分类：
- LANGUAGE_RULES: 语言识别规则
- FRAMEWORK_RULES: 框架识别规则  
- BUILD_TOOL_RULES: 构建工具规则
- CI_CD_RULES: CI/CD 规则
- CONTAINER_RULES: 容器化规则
- CLOUD_NATIVE_RULES: 云原生规则
- TESTING_RULES: 测试框架规则

最终聚合为 TECH_STACK_RULES 供 detector 使用
"""

# ============================================================================
# 语言识别规则
# ============================================================================
# 通过项目中的特征文件识别编程语言
# key: 特征文件名或路径模式
# value: 对应的语言名称
LANGUAGE_RULES = {
    # Python 项目识别规则
    "requirements.txt": "Python",
    "pyproject.toml": "Python",
    "setup.py": "Python",
    "setup.cfg": "Python",
    "Pipfile": "Python",
    "*.py": "Python",  # Python 源文件
    
    # JavaScript/Node.js 项目识别规则
    "package.json": "JavaScript",
    "*.js": "JavaScript",
    "*.ts": "TypeScript",
    "*.jsx": "JavaScript",
    "*.tsx": "TypeScript",
    
    # Java 项目识别规则
    "pom.xml": "Java",
    "build.gradle": "Java",
    "build.gradle.kts": "Java",
    "*.java": "Java",
    
    # Go 项目识别规则
    "go.mod": "Go",
    "go.sum": "Go",
    "*.go": "Go",
}

# ============================================================================
# 框架识别规则
# ============================================================================
# 通过依赖包名称识别使用的框架
# key: 依赖包名称（支持模糊匹配）
# value: 框架信息字典 {"name": 框架名, "category": 分类, "confidence": 置信度}
FRAMEWORK_RULES = {
    # Python 框架
    "fastapi": {"name": "FastAPI", "category": "Web Framework", "confidence": 0.9},
    "django": {"name": "Django", "category": "Web Framework", "confidence": 0.95},
    "flask": {"name": "Flask", "category": "Web Framework", "confidence": 0.9},
    "typer": {"name": "Typer", "category": "CLI Framework", "confidence": 0.9},
    "streamlit": {"name": "Streamlit", "category": "Data App Framework", "confidence": 0.9},
    "celery": {"name": "Celery", "category": "Task Queue", "confidence": 0.85},
    "rich": {"name": "Rich", "category": "Terminal UI", "confidence": 0.85},
    "loguru": {"name": "Loguru", "category": "Logging", "confidence": 0.85},
    "pydantic": {"name": "Pydantic", "category": "Data Validation", "confidence": 0.9},
    
    # Node.js 框架
    "vue": {"name": "Vue.js", "category": "Frontend Framework", "confidence": 0.95},
    "react": {"name": "React", "category": "Frontend Framework", "confidence": 0.95},
    "next": {"name": "Next.js", "category": "Fullstack Framework", "confidence": 0.9},
    "nuxt": {"name": "Nuxt.js", "category": "Fullstack Framework", "confidence": 0.9},
    "express": {"name": "Express", "category": "Web Framework", "confidence": 0.9},
    "nestjs": {"name": "NestJS", "category": "Backend Framework", "confidence": 0.9},
    "angular": {"name": "Angular", "category": "Frontend Framework", "confidence": 0.95},
    "svelte": {"name": "Svelte", "category": "Frontend Framework", "confidence": 0.9},
    
    # Java 框架
    "spring-boot-starter": {"name": "Spring Boot", "category": "Backend Framework", "confidence": 0.95},
    "spring-boot": {"name": "Spring Boot", "category": "Backend Framework", "confidence": 0.95},
    "springframework": {"name": "Spring Framework", "category": "Backend Framework", "confidence": 0.9},
    "hibernate": {"name": "Hibernate", "category": "ORM", "confidence": 0.85},
    "mybatis": {"name": "MyBatis", "category": "ORM", "confidence": 0.85},
    
    # Go 框架
    "gin": {"name": "Gin", "category": "Web Framework", "confidence": 0.9},
    "fiber": {"name": "Fiber", "category": "Web Framework", "confidence": 0.9},
    "grpc": {"name": "gRPC", "category": "RPC Framework", "confidence": 0.85},
    "echo": {"name": "Echo", "category": "Web Framework", "confidence": 0.85},
    "beego": {"name": "Beego", "category": "Web Framework", "confidence": 0.85},
}

# ============================================================================
# 构建工具规则
# ============================================================================
# 通过特征文件识别构建工具
# key: 特征文件名
# value: 构建工具信息字典 {"name": 工具名, "category": 分类}
BUILD_TOOL_RULES = {
    # Python 构建工具
    "pyproject.toml": {"name": "Poetry/Pip", "category": "Package Manager"},
    "requirements.txt": {"name": "pip", "category": "Package Manager"},
    "Pipfile": {"name": "Pipenv", "category": "Package Manager"},
    "setup.py": {"name": "setuptools", "category": "Build Tool"},
    
    # Node.js 构建工具
    "package.json": {"name": "npm/yarn/pnpm", "category": "Package Manager"},
    "yarn.lock": {"name": "Yarn", "category": "Package Manager"},
    "pnpm-lock.yaml": {"name": "pnpm", "category": "Package Manager"},
    "package-lock.json": {"name": "npm", "category": "Package Manager"},
    "webpack.config.js": {"name": "Webpack", "category": "Bundler"},
    "vite.config.js": {"name": "Vite", "category": "Bundler"},
    "rollup.config.js": {"name": "Rollup", "category": "Bundler"},
    
    # Java 构建工具
    "pom.xml": {"name": "Maven", "category": "Build Tool"},
    "build.gradle": {"name": "Gradle", "category": "Build Tool"},
    "build.gradle.kts": {"name": "Gradle Kotlin", "category": "Build Tool"},
    "gradlew": {"name": "Gradle Wrapper", "category": "Build Tool"},
    
    # Go 构建工具
    "go.mod": {"name": "Go Modules", "category": "Package Manager"},
    "Makefile": {"name": "Make", "category": "Build Tool"},
}

# ============================================================================
# CI/CD 规则
# ============================================================================
# 通过配置文件识别 CI/CD 工具
# key: 配置文件路径或名称
# value: CI/CD 工具名称
CI_CD_RULES = {
    ".github/workflows": "GitHub Actions",
    ".github/workflows/*.yml": "GitHub Actions",
    ".github/workflows/*.yaml": "GitHub Actions",
    ".gitlab-ci.yml": "GitLab CI",
    ".gitlab-ci.yaml": "GitLab CI",
    "Jenkinsfile": "Jenkins",
    ".jenkinsfile": "Jenkins",
    ".circleci/config.yml": "CircleCI",
    ".travis.yml": "Travis CI",
    "azure-pipelines.yml": "Azure Pipelines",
    ".drone.yml": "Drone CI",
}

# ============================================================================
# 容器化规则
# ============================================================================
# 通过配置文件识别容器化工具
# key: 配置文件名称
# value: 容器化工具信息字典 {"name": 工具名, "category": 分类}
CONTAINER_RULES = {
    "Dockerfile": {"name": "Docker", "category": "Containerization"},
    "docker-compose.yml": {"name": "Docker Compose", "category": "Orchestration"},
    "docker-compose.yaml": {"name": "Docker Compose", "category": "Orchestration"},
    ".dockerignore": {"name": "Docker", "category": "Containerization"},
    "Containerfile": {"name": "Podman/Buildah", "category": "Containerization"},
}

# ============================================================================
# 云原生规则
# ============================================================================
# 通过目录结构和配置文件识别云原生工具
# key: 目录或文件路径模式
# value: 云原生工具信息字典 {"name": 工具名, "category": 分类}
CLOUD_NATIVE_RULES = {
    "charts/": {"name": "Helm", "category": "Package Manager"},
    "Chart.yaml": {"name": "Helm", "category": "Package Manager"},
    "helm/": {"name": "Helm", "category": "Package Manager"},
    "k8s/": {"name": "Kubernetes", "category": "Orchestration"},
    "kubernetes/": {"name": "Kubernetes", "category": "Orchestration"},
    "*.yaml": {"name": "Kubernetes Manifest", "category": "Orchestration"},  # 需要进一步判断
    "*.yml": {"name": "Kubernetes Manifest", "category": "Orchestration"},  # 需要进一步判断
    "terraform.tf": {"name": "Terraform", "category": "IaC"},
    "*.tf": {"name": "Terraform", "category": "IaC"},
    "Pulumi.yaml": {"name": "Pulumi", "category": "IaC"},
}

# ============================================================================
# 测试框架规则
# ============================================================================
# 通过依赖包或配置文件识别测试框架
# key: 依赖包名称或配置文件名
# value: 测试框架信息字典 {"name": 框架名, "category": 分类}
TESTING_RULES = {
    # Python 测试框架
    "pytest": {"name": "Pytest", "category": "Testing Framework"},
    "unittest": {"name": "Unittest", "category": "Testing Framework"},
    "nose": {"name": "Nose", "category": "Testing Framework"},
    "tox.ini": {"name": "Tox", "category": "Testing Environment"},
    
    # JavaScript/Node.js 测试框架
    "jest": {"name": "Jest", "category": "Testing Framework"},
    "vitest": {"name": "Vitest", "category": "Testing Framework"},
    "mocha": {"name": "Mocha", "category": "Testing Framework"},
    "jasmine": {"name": "Jasmine", "category": "Testing Framework"},
    "cypress": {"name": "Cypress", "category": "E2E Testing"},
    "playwright": {"name": "Playwright", "category": "E2E Testing"},
    
    # Java 测试框架
    "junit": {"name": "JUnit", "category": "Testing Framework"},
    "testng": {"name": "TestNG", "category": "Testing Framework"},
    "mockito": {"name": "Mockito", "category": "Mocking Framework"},
    
    # Go 测试框架
    "testing": {"name": "Go Testing", "category": "Testing Framework"},  # Go 内置测试包
    "ginkgo": {"name": "Ginkgo", "category": "Testing Framework"},
    "gomock": {"name": "GoMock", "category": "Mocking Framework"},
}

# ============================================================================
# 统一聚合：技术栈规则总表
# ============================================================================
# 将所有规则分类聚合为一个统一的规则字典
# 供 detector 模块统一调用和查询
TECH_STACK_RULES = {
    "language": LANGUAGE_RULES,
    "framework": FRAMEWORK_RULES,
    "build_tool": BUILD_TOOL_RULES,
    "ci_cd": CI_CD_RULES,
    "container": CONTAINER_RULES,
    "cloud_native": CLOUD_NATIVE_RULES,
    "testing": TESTING_RULES,
}
