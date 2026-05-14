# 代理规范

## 概述

本文档定义了 AI GitHub Analyzer 的 AI 代理规范。每个代理负责一个专门的分析任务，并在协调框架内独立运行。

## 代理架构

所有代理遵循通用接口：

```python
class BaseAgent:
    def analyze(self, context: AnalysisContext) -> AgentResult:
        """执行分析并返回结果。"""
        pass
    
    def validate_input(self, context: AnalysisContext) -> bool:
        """验证输入上下文是否充分。"""
        pass
```

## 代理类型

### 1. 架构代理

**目的**：分析仓库架构和设计模式。

**职责**：
- 识别架构风格（单体、微服务、分层等）
- 检测设计模式（MVC、MVVM、Repository、Factory 等）
- 评估模块组织和边界
- 评估关注点分离
- 识别耦合和 cohesion 问题

**输入上下文**：
- 文件结构和组织
- 模块依赖关系
- 配置文件
- 入口点和主模块

**输出**：
```python
class ArchitectureAnalysis(AgentResult):
    architectural_style: str
    design_patterns: List[str]
    module_structure: ModuleAnalysis
    coupling_score: float
    cohesion_score: float
    recommendations: List[str]
```

**提示策略**：
- 分析目录结构以获取架构线索
- 检查导入模式和依赖关系
- 审查配置文件以获取框架提示
- 评估代码组织原则

---

### 2. 质量代理

**目的**：评估代码质量和对最佳实践的遵守情况。

**职责**：
- 评估代码复杂度（圈复杂度、认知复杂度）
- 检查命名约定一致性
- 评估文档覆盖率
- 识别代码异味和反模式
- 评估测试覆盖率和质量
- 检查错误处理实践

**输入上下文**：
- 源代码文件
- 测试文件和结构
- 文档文件
- Lint 配置

**输出**：
```python
class QualityAnalysis(AgentResult):
    overall_score: float
    complexity_metrics: ComplexityMetrics
    documentation_score: float
    test_coverage_estimate: float
    code_smells: List[CodeSmell]
    best_practices_violations: List[str]
    improvement_suggestions: List[str]
```

**提示策略**：
- 从不同模块采样代表性文件
- 分析函数和类的复杂度
- 审查注释与代码的比例
- 检查常见反模式
- 评估错误处理策略

---

### 3. 安全代理

**目的**：识别潜在的安全漏洞和风险。

**职责**：
- 检测硬编码的秘密和凭据
- 识别不安全的依赖
- 检查常见漏洞模式
- 评估输入验证实践
- 审查身份验证/授权实现
- 标记危险操作（eval、exec 等）

**输入上下文**：
- 依赖文件（requirements.txt、package.json 等）
- 配置文件
- 身份验证相关代码
- API 端点实现

**输出**：
```python
class SecurityAnalysis(AgentResult):
    risk_level: RiskLevel  # LOW, MEDIUM, HIGH, CRITICAL
    vulnerabilities: List[Vulnerability]
    insecure_dependencies: List[DependencyIssue]
    security_recommendations: List[str]
    compliance_issues: List[str]
```

**提示策略**：
- 扫描已知漏洞模式
- 根据 CVE 数据库审查依赖版本
- 检查安全编码实践
- 分析身份验证流程
- 检查数据处理和清理

---

### 4. 文档代理

**目的**：评估文档完整性和质量。

**职责**：
- 评估 README 质量和完整性
- 检查 API 文档覆盖率
- 评估内联代码注释
- 审查文档结构
- 识别缺失的文档区域
- 检查过时的文档

**输入上下文**：
- README.md 和其他 Markdown 文件
- Docstring 和内联注释
- API 规范文件（OpenAPI、GraphQL schema）
- 文档目录

**输出**：
```python
class DocumentationAnalysis(AgentResult):
    completeness_score: float
    readme_quality: float
    api_documentation_coverage: float
    code_comment_ratio: float
    missing_documentation: List[str]
    documentation_issues: List[str]
    improvement_priorities: List[str]
```

**提示策略**：
- 根据最佳实践清单评估 README
- 检查入门指南
- 评估 API 文档完整性
- 审查代码示例和教程
- 识别文档覆盖率的空白

---

### 5. 建议代理

**目的**：生成可操作的改进建议。

**职责**：
- 综合所有其他代理的发现
- 按影响优先级排序建议
- 提供具体、可操作的步骤
- 建议工具和资源
- 创建改进路线图
- 估算每个建议的工作量

**输入上下文**：
- 所有其他代理的结果
- 仓库目标（如果指定）
- 行业最佳实践
- 类似仓库模式

**输出**：
```python
class RecommendationAnalysis(AgentResult):
    quick_wins: List[Recommendation]
    high_impact: List[Recommendation]
    long_term_improvements: List[Recommendation]
    priority_matrix: PriorityMatrix
    estimated_effort: EffortEstimate
    resource_links: List[str]
```

**提示策略**：
- 聚合所有分析的见解
- 应用优先级框架（影响 vs. 工作量）
- 参考行业标准和基准
- 提供具体示例和资源
- 考虑仓库上下文和目标

---

### 6. 依赖代理

**目的**：分析项目依赖及其健康状况。

**职责**：
- 映射完整的依赖树
- 识别过时的包
- 检测未使用的依赖
- 评估依赖健康状况（维护、社区）
- 检查许可证兼容性
- 识别依赖冲突

**输入上下文**：
- 依赖清单文件
- 锁定文件（如果可用）
- 导入语句
- 包元数据

**输出**：
```python
class DependencyAnalysis(AgentResult):
    total_dependencies: int
    direct_dependencies: int
    transitive_dependencies: int
    outdated_packages: List[PackageInfo]
    unused_dependencies: List[str]
    license_issues: List[LicenseIssue]
    health_scores: Dict[str, float]
    update_recommendations: List[str]
```

**提示策略**：
- 准确解析依赖文件
- 与包注册表交叉引用
- 检查最后更新日期和维护活动
- 分析下载统计数据和社区采用情况
- 审查许可证兼容性

---

### 7. 性能代理

**目的**：识别性能瓶颈和优化机会。

**职责**：
- 检测低效算法
- 识别 N+1 查询模式
- 检查适当的缓存策略
- 评估数据库查询效率
- 审查异步/并发代码使用
- 标记内存密集型操作

**输入上下文**：
- 数据库交互代码
- API 端点实现
- 循环和迭代模式
- 缓存配置
- async/await 使用

**输出**：
```python
class PerformanceAnalysis(AgentResult):
    bottlenecks: List[PerformanceIssue]
    optimization_opportunities: List[Optimization]
    complexity_warnings: List[str]
    caching_recommendations: List[str]
    database_optimization_tips: List[str]
```

**提示策略**：
- 分析算法复杂度指标
- 审查数据库访问模式
- 检查正确的 async 使用
- 识别冗余计算
- 评估资源利用模式

---

## 代理执行模型

### 顺序执行 vs 并行执行

**顺序执行**（存在依赖关系时）：
```
扫描器 → 分类器 → 上下文构建器 → 代理
```

**并行执行**（独立代理）：
```
架构代理 ──┐
质量代理   ────┼→ 聚合器
安全代理   ────┤
文档代理 ──┘
```

### 超时处理

每个代理具有可配置的超时：
```python
config = AgentConfig(
    timeout=60,  # 秒
    retry_count=2,
    fallback_result=FallbackResult(...)
)
```

### 错误恢复

如果代理失败：
1. 记录详细的错误信息
2. 尝试重试（如果配置）
3. 使用回退/默认结果
4. 继续执行剩余代理
5. 报告部分结果并附带警告

---

## 提示工程指南

### 提示结构

每个代理提示应包括：

1. **角色定义**：清晰的代理人格和专业领域
2. **任务描述**：具体的分析目标
3. **输入格式**：预期的数据结构
4. **输出格式**：所需的响应结构
5. **示例**：输入和输出示例
6. **约束**：限制和边界
7. **评估标准**：如何评估质量

### 示例提示模板

```markdown
# 角色
您是专注于 {domain} 的专家软件架构师。

# 任务
分析提供的仓库上下文并识别 {specific_aspects}。

# 输入
仓库上下文包括：
- 文件结构：{file_tree}
- 关键文件：{file_contents}
- 元数据：{metadata}

# 输出格式
请按以下 JSON 结构提供您的分析：
{
  "findings": [...],
  "score": 0.0,
  "recommendations": [...]
}

# 约束
- 仅关注 {scope}
- 不要超出提供的数据做出假设
- 保持具体和可操作

# 示例
示例 1：
输入：...
输出：...
```

---

## 代理配置

### 环境变量

```bash
# AI 提供商配置
AI_PROVIDER=openai  # 或 anthropic, azure 等
AI_MODEL=gpt-4-turbo
AI_API_KEY=your_api_key

# 代理特定设置
AGENT_TIMEOUT=60
AGENT_MAX_RETRIES=2
AGENT_PARALLEL_LIMIT=4

# 功能标志
ENABLE_ARCHITECTURE_AGENT=true
ENABLE_QUALITY_AGENT=true
ENABLE_SECURITY_AGENT=true
ENABLE_DOCUMENTATION_AGENT=true
ENABLE_RECOMMENDATION_AGENT=true
ENABLE_DEPENDENCY_AGENT=true
ENABLE_PERFORMANCE_AGENT=true
```

### Pydantic 设置模型

```python
class AgentSettings(BaseSettings):
    provider: str = "openai"
    model: str = "gpt-4-turbo"
    api_key: SecretStr
    timeout: int = 60
    max_retries: int = 2
    parallel_limit: int = 4
    
    class Config:
        env_prefix = "AGENT_"
```

---

## 代理结果聚合

协调器聚合所有代理的结果：

```python
class AggregatedResult(BaseModel):
    architecture: Optional[ArchitectureAnalysis]
    quality: Optional[QualityAnalysis]
    security: Optional[SecurityAnalysis]
    documentation: Optional[DocumentationAnalysis]
    dependencies: Optional[DependencyAnalysis]
    performance: Optional[PerformanceAnalysis]
    recommendations: RecommendationAnalysis
    
    overall_score: float
    critical_issues: List[str]
    summary: str
```

聚合逻辑：
1. 收集所有成功的代理结果
2. 按重要性加权分数
3. 识别跨领域问题
4. 解决冲突的建议
5. 生成统一摘要

---

## 测试代理

### 单元测试

使用模拟上下文测试每个代理：
```python
def test_architecture_agent():
    agent = ArchitectureAgent()
    context = create_mock_context()
    result = agent.analyze(context)
    assert result.architectural_style is not None
```

### 集成测试

测试代理交互：
```python
async def test_agent_orchestration():
    orchestrator = AnalysisOrchestrator()
    result = await orchestrator.run(config)
    assert len(result.agents_executed) > 0
```

### 固定仓库

维护具有已知特征的测试仓库：
- 简单的 Flask 应用
- 复杂的微服务架构
- 低质量代码库
- 文档完善的库
- 存在安全漏洞的应用

---

## 未来代理想法

1. **可访问性代理**：检查 UI 可访问性合规性
2. **合规代理**：验证监管合规性（GDPR、HIPAA）
3. **本地化代理**：评估国际化准备情况
4. **DevOps 代理**：评估 CI/CD 和部署实践
5. **社区代理**：分析社区参与和贡献指南
6. **成本代理**：估算云基础设施成本
7. **迁移代理**：建议现代化路径

---

*最后更新：2026-05-14*
