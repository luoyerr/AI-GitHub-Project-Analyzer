# Project Structure Guide

## Complete Directory Structure

```
ai-github-analyzer/
│
├── src/                          # Source code (src layout pattern)
│   ├── __init__.py              # Package initialization, version info
│   │
│   ├── orchestrator/            # 🎯 Workflow Orchestration
│   │   └── __init__.py
│   │   # Responsibilities:
│   │   # - Coordinate analysis pipeline execution
│   │   # - Manage module lifecycle
│   │   # - Handle errors and retries
│   │   # - Track progress and status
│   │   # Future files:
│   │   # - orchestrator.py: Main orchestrator class
│   │   # - workflow.py: Workflow definitions
│   │   # - task_manager.py: Async task management
│   │
│   ├── scanner/                 # 🔍 Repository Scanning
│   │   └── __init__.py
│   │   # Responsibilities:
│   │   # - Clone/access repositories (local/remote)
│   │   # - Build file tree structure
│   │   # - Count files, lines, directories
│   │   # - Detect programming languages
│   │   # - Extract dependency information
│   │   # Future files:
│   │   # - repo_scanner.py: Core scanning logic
│   │   # - file_analyzer.py: File-level analysis
│   │   # - language_detector.py: Language identification
│   │   # - dependency_extractor.py: Dependency parsing
│   │
│   ├── classifier/              # 🏷️ Technology Classification
│   │   └── __init__.py
│   │   # Responsibilities:
│   │   # - Identify primary programming language
│   │   # - Detect frameworks and libraries
│   │   # - Classify repository type
│   │   # - Identify architectural patterns
│   │   # - Calculate confidence scores
│   │   # Future files:
│   │   # - tech_classifier.py: Technology detection
│   │   # - pattern_recognizer.py: Pattern matching
│   │   # - repo_categorizer.py: Repository classification
│   │   # - rules_engine.py: Classification rules
│   │
│   ├── context_builder/         # 📚 Context Aggregation
│   │   └── __init__.py
│   │   # Responsibilities:
│   │   # - Merge scan and classification results
│   │   # - Build comprehensive repository context
│   │   # - Extract key files (README, configs)
│   │   # - Prepare context for AI agents
│   │   # - Optimize context size for token limits
│   │   # Future files:
│   │   # - context_assembler.py: Context building
│   │   # - file_extractor.py: Key file extraction
│   │   # - context_optimizer.py: Size optimization
│   │
│   ├── agents/                  # 🤖 AI Agent Implementations
│   │   └── __init__.py
│   │   # Responsibilities:
│   │   # - Architecture analysis agent
│   │   # - Code quality assessment agent
│   │   # - Security vulnerability detection agent
│   │   # - Documentation evaluation agent
│   │   # - Recommendation generation agent
│   │   # - Dependency health analysis agent
│   │   # - Performance bottleneck detection agent
│   │   # Future files:
│   │   # - base_agent.py: Base agent class
│   │   # - architecture_agent.py
│   │   # - quality_agent.py
│   │   # - security_agent.py
│   │   # - documentation_agent.py
│   │   # - recommendation_agent.py
│   │   # - dependency_agent.py
│   │   # - performance_agent.py
│   │   # - agent_registry.py: Agent management
│   │
│   ├── validators/              # ✅ Result Validation
│   │   └── __init__.py
│   │   # Responsibilities:
│   │   # - Validate analysis completeness
│   │   # - Check data consistency
│   │   # - Verify result integrity
│   │   # - Apply validation rules
│   │   # - Generate validation reports
│   │   # Future files:
│   │   # - result_validator.py: Main validator
│   │   # - rule_engine.py: Validation rules
│   │   # - quality_checker.py: Quality checks
│   │
│   ├── renderer/                # 📊 Output Rendering
│   │   └── __init__.py
│   │   # Responsibilities:
│   │   # - Format results (Markdown, JSON, HTML)
│   │   # - Apply styling and formatting
│   │   # - Generate terminal output with Rich
│   │   # - Export to files
│   │   # - Support custom templates
│   │   # Future files:
│   │   # - markdown_renderer.py
│   │   # - json_renderer.py
│   │   # - html_renderer.py
│   │   # - terminal_renderer.py: Rich-based output
│   │   # - template_engine.py: Template processing
│   │
│   ├── models/                  # 📦 Pydantic Data Models
│   │   ├── __init__.py
│   │   └── base_models.py      # Core data models (already created)
│   │   # Responsibilities:
│   │   # - Define all data structures
│   │   # - Ensure type safety
│   │   # - Provide validation
│   │   # - Document data contracts
│   │   # Future files:
│   │   # - agent_models.py: Agent-specific models
│   │   # - config_models.py: Configuration models
│   │   # - result_models.py: Result models
│   │
│   ├── infrastructure/          # 🔧 Core Infrastructure
│   │   └── __init__.py
│   │   # Responsibilities:
│   │   # - Configuration management
│   │   # - Logging setup
│   │   # - Error handling utilities
│   │   # - Async helpers
│   │   # - External service clients
│   │   # Future files:
│   │   # - config.py: Settings management
│   │   # - logging_config.py: Loguru configuration
│   │   # - github_client.py: GitHub API client
│   │   # - ai_client.py: AI provider client
│   │   # - exceptions.py: Custom exceptions
│   │   # - async_utils.py: Async utilities
│   │
│   └── utils/                   # 🛠️ Utility Functions
│       └── __init__.py
│       # Responsibilities:
│       # - File system operations
│       # - String manipulation
│       # - Date/time helpers
│       # - Common algorithms
│       # - Helper functions
│       # Future files:
│       # - file_utils.py: File operations
│       # - string_utils.py: String helpers
│       # - git_utils.py: Git operations
│       # - path_utils.py: Path manipulation
│       # - time_utils.py: Time utilities
│
├── prompts/                     # 💬 AI Prompt Templates
│   # Purpose: Store AI prompt templates separately from code
│   # Benefits:
│   # - Easy to modify without code changes
│   # - Version control for prompts
│   # - A/B testing different prompts
│   # Future files:
│   # - architecture_agent_prompt.txt
│   # - quality_agent_prompt.txt
│   # - security_agent_prompt.txt
│   # - documentation_agent_prompt.txt
│   # - recommendation_agent_prompt.txt
│   # - system_prompt.txt
│
├── schemas/                     # 📋 JSON Schemas
│   # Purpose: JSON schema definitions for external integrations
│   # Benefits:
│   # - API contract validation
│   # - External tool integration
│   # - Data exchange standards
│   # Future files:
│   # - analysis_result_schema.json
│   # - agent_input_schema.json
│   # - agent_output_schema.json
│
├── traces/                      # 🔎 Execution Traces
│   # Purpose: Store execution traces for debugging and analysis
│   # Contents:
│   # - Agent interaction logs
│   # - Performance profiling data
│   # - Debug information
│   # Note: This directory is gitignored
│   # Future files:
│   # - trace_*.json: Individual trace files
│   # - profiles/: Performance profiles
│
├── tests/                       # 🧪 Test Suite
│   # Purpose: Comprehensive test coverage
│   # Structure: Mirror src/ directory structure
│   # Future files:
│   # - conftest.py: pytest fixtures
│   # - test_orchestrator/
│   # - test_scanner/
│   # - test_classifier/
│   # - test_agents/
│   # - test_validators/
│   # - test_renderer/
│   # - test_models/
│   # - integration/
│   # - e2e/
│
├── docs/                        # 📖 Documentation
│   ├── design-docs/            # Design documents and RFCs
│   │   # Future files:
│   │   # - ADR-001-architecture-decision.md
│   │   # - RFC-001-agent-system.md
│   │   # - design-specifications.md
│   │
│   └── ENVIRONMENT_SETUP.md    # Environment setup guide (created)
│       # Additional future docs:
│       # - API_REFERENCE.md
│       # - CONTRIBUTING.md
│       # - DEPLOYMENT.md
│
├── main.py                      # 🚀 CLI Entry Point (created)
│   # Purpose: Main application entry point
│   # Features:
│   # - Typer-based CLI interface
│   # - Rich terminal output
│   # - Loguru logging setup
│   # - Command: analyze <repo_url>
│   # - Command: version
│
├── pyproject.toml               # ⚙️ Project Configuration (created)
│   # Purpose: Modern Python project configuration
│   # Contains:
│   # - Project metadata
│   # - Dependencies
│   # - Build system settings
│   # - Tool configurations (black, ruff, mypy)
│
├── .gitignore                   # 🚫 Git Ignore Rules (created)
│   # Purpose: Exclude unnecessary files from git
│   # Includes:
│   # - Python cache files
│   # - Virtual environments
│   # - IDE settings
│   # - Logs and traces
│   # - Environment files
│
├── .env.example                 # 📝 Environment Variables Template (created)
│   # Purpose: Template for environment configuration
│   # Usage: Copy to .env and fill in values
│
├── setup.ps1                    # ⚡ Quick Setup Script (created)
│   # Purpose: Automated environment setup for Windows
│   # Features:
│   # - Check prerequisites
│   # - Create conda environment
│   # - Install dependencies
│   # - Verify installation
│
├── README.md                    # 📘 Project Overview (created)
│   # Purpose: Main project documentation
│   # Contains:
│   # - Project description
│   # - Features list
│   # - Installation instructions
│   # - Usage examples
│   # - Project structure
│   # - Development guide
│
├── ARCHITECTURE.md              # 🏗️ Architecture Design (created)
│   # Purpose: Detailed architecture documentation
│   # Contains:
│   # - Architectural principles
│   # - Module responsibilities
│   # - Data flow diagrams
│   # - Technology stack rationale
│   # - Extension points
│
├── AGENTS.md                    # 🤖 Agent Specifications (created)
│   # Purpose: AI agent design documentation
│   # Contains:
│   # - Agent types and purposes
│   # - Input/output specifications
│   # - Prompt engineering guidelines
│   # - Configuration options
│   # - Testing strategies
│
└── LICENSE                      # 📄 License File (to be added)
    # Purpose: Project license (MIT recommended)
```

---

## Module Communication Flow

```
User Input (CLI)
    ↓
main.py (Typer CLI)
    ↓
Orchestrator (coordinates workflow)
    ↓
Scanner → ScanResult (Pydantic model)
    ↓
Classifier → ClassificationResult (Pydantic model)
    ↓
Context Builder → Enriched Context (Pydantic model)
    ↓
Agents (parallel execution)
    ├→ Architecture Agent → ArchitectureAnalysis
    ├→ Quality Agent → QualityAnalysis
    ├→ Security Agent → SecurityAnalysis
    ├→ Documentation Agent → DocumentationAnalysis
    └→ Other Agents → Their Results
    ↓
Validator → Validated Results
    ↓
Renderer → Formatted Output
    ↓
Display to User (Rich terminal)
```

---

## Key Design Decisions

### 1. Why `src/` Layout?

**Benefits**:
- Prevents import conflicts during development
- Clear separation between source and tests
- Standard Python packaging practice
- Easier to test with isolated imports
- Avoids accidental imports of uninstalled code

**Alternative Considered**: Flat layout (rejected)
- Can cause import confusion
- Harder to test properly
- Not recommended by modern Python packaging guides

---

### 2. Why Pydantic Models for Communication?

**Benefits**:
- Runtime validation at module boundaries
- Type safety across the entire pipeline
- Self-documenting data contracts
- Easy serialization/deserialization
- IDE autocomplete support
- Automatic JSON schema generation

**Alternative Considered**: Dicts/dataclasses (rejected)
- No runtime validation
- Less clear contracts
- More error-prone

---

### 3. Why Separate Prompts Directory?

**Benefits**:
- Prompt engineering without code changes
- Version control for prompts
- Easy A/B testing
- Non-developers can modify prompts
- Clear separation of concerns

**Alternative Considered**: Inline prompts (rejected)
- Hard to maintain
- Requires code changes for prompt tweaks
- Difficult to test different versions

---

### 4. Why No ORM or Database?

**Rationale**:
- First version focuses on single-run analysis
- No need for persistent storage initially
- Keeps architecture lightweight
- Can add database later when needed
- Follows "no over-engineering" principle

**Future Enhancement**:
- Add SQLite/PostgreSQL for analysis history
- Implement caching layer
- Store comparison data

---

### 5. Why Async-First Design?

**Benefits**:
- Parallel agent execution
- Efficient I/O operations (GitHub API, file system)
- Non-blocking operations
- Better resource utilization
- Scalable for large repositories

**Implementation**:
- asyncio for concurrency
- Async/await syntax throughout
- Task groups for parallel execution

---

### 6. Why Multiple Specialized Agents?

**Benefits**:
- Single responsibility per agent
- Easier to test and maintain
- Can enable/disable agents independently
- Parallel execution possible
- Clear separation of concerns
- Easy to add new agents

**Alternative Considered**: Single monolithic agent (rejected)
- Too complex
- Hard to maintain
- Cannot parallelize
- Difficult to test

---

## File Naming Conventions

### Python Files
- **Modules**: `snake_case.py` (e.g., `file_analyzer.py`)
- **Classes**: `PascalCase` (e.g., `FileAnalyzer`)
- **Functions**: `snake_case` (e.g., `analyze_file()`)
- **Constants**: `UPPER_CASE` (e.g., `MAX_FILE_SIZE`)
- **Private**: `_leading_underscore` (e.g., `_internal_method()`)

### Test Files
- Mirror source structure: `test_<module_name>.py`
- Example: `src/scanner/file_analyzer.py` → `tests/test_scanner/test_file_analyzer.py`

### Documentation Files
- `UPPER_CASE.md` for main docs (README, ARCHITECTURE)
- `kebab-case.md` for sub-docs (environment-setup.md)

### Prompt Files
- `<agent_name>_prompt.txt` (e.g., `architecture_agent_prompt.txt`)

---

## Import Guidelines

### Within src/

```python
# ✅ Correct: Absolute imports from src
from src.models.base_models import AnalysisConfig
from src.scanner.repo_scanner import RepositoryScanner

# ❌ Avoid: Relative imports (harder to refactor)
from ..models.base_models import AnalysisConfig
```

### In Tests

```python
# ✅ Correct: Import from src package
from src.models.base_models import AnalysisConfig

# ❌ Avoid: Import from local path
import sys
sys.path.insert(0, '../src')
```

---

## Dependency Management

### Current Dependencies (pyproject.toml)

**Core**:
- `typer>=0.9.0`: CLI framework
- `rich>=13.7.0`: Terminal formatting
- `loguru>=0.7.0`: Logging
- `pydantic>=2.5.0`: Data validation
- `pydantic-settings>=2.1.0`: Settings management

**Development** (optional):
- `pytest>=7.4.0`: Testing
- `pytest-asyncio>=0.21.0`: Async testing
- `black>=23.0.0`: Code formatting
- `ruff>=0.1.0`: Linting
- `mypy>=1.7.0`: Type checking

### Future Dependencies (by module)

**Scanner**:
- `gitpython`: Git operations
- `pathspec`: .gitignore parsing

**Classifier**:
- `lingua-language-detector`: Language detection

**Agents**:
- `openai`: OpenAI API client
- OR `anthropic`: Anthropic API client

**Infrastructure**:
- `aiohttp`: Async HTTP client
- `python-dotenv`: Environment variables

---

## Testing Strategy

### Test Types

1. **Unit Tests** (`tests/unit/`)
   - Test individual functions/classes
   - Mock external dependencies
   - Fast execution

2. **Integration Tests** (`tests/integration/`)
   - Test module interactions
   - Real dependencies where practical
   - Medium execution time

3. **E2E Tests** (`tests/e2e/`)
   - Full workflow execution
   - Real repositories
   - Slow execution

### Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_scanner/
│   ├── test_classifier/
│   ├── test_agents/
│   └── ...
├── integration/
│   ├── test_orchestrator.py
│   └── test_workflow.py
├── e2e/
│   ├── test_full_analysis.py
│   └── test_cli_commands.py
└── fixtures/
    ├── sample_repos/        # Test repositories
    └── mock_data/           # Mock responses
```

---

## Logging Strategy

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational messages
- **WARNING**: Unexpected but handled situations
- **ERROR**: Errors that don't stop execution
- **CRITICAL**: Fatal errors that stop execution

### Log Destinations

1. **Console** (stderr): INFO and above, colorized
2. **File** (logs/): DEBUG and above, rotated daily
3. **Traces** (traces/): Agent interactions, JSON format

### Log Format

```
2026-05-14 10:30:45 | INFO     | src.scanner.repo_scanner:scan:42 - Scanning repository...
2026-05-14 10:30:46 | DEBUG    | src.agents.quality_agent:analyze:87 - Analyzing 150 files
2026-05-14 10:30:47 | ERROR    | src.infrastructure.github_client:fetch:123 - API rate limit exceeded
```

---

## Error Handling Strategy

### Exception Hierarchy

```python
# src/infrastructure/exceptions.py

class AnalyzerError(Exception):
    """Base exception for all analyzer errors."""
    pass

class ScannerError(AnalyzerError):
    """Errors during repository scanning."""
    pass

class ClassificationError(AnalyzerError):
    """Errors during technology classification."""
    pass

class AgentError(AnalyzerError):
    """Errors during agent execution."""
    pass

class ValidationError(AnalyzerError):
    """Errors during result validation."""
    pass
```

### Error Handling Pattern

```python
try:
    result = await agent.analyze(context)
except AgentError as e:
    logger.error(f"Agent failed: {e}")
    if config.retry_count > 0:
        result = await retry(agent.analyze, context)
    else:
        result = agent.get_fallback_result()
```

---

## Configuration Management

### Priority Order

1. Command-line arguments (highest priority)
2. Environment variables
3. `.env` file
4. Default values (lowest priority)

### Implementation

```python
# src/infrastructure/config.py

from pydantic_settings import BaseSettings

class AppSettings(BaseSettings):
    # CLI args override these
    repo_url: str
    output_format: str = "markdown"
    
    # Environment variables
    ai_provider: str = "openai"
    ai_model: str = "gpt-4-turbo"
    
    class Config:
        env_file = ".env"
        env_prefix = "ANALYZER_"
```

---

## Next Steps for Development

### Phase 1: Core Infrastructure (Week 1-2)
- [ ] Implement Scanner module
- [ ] Implement Classifier module
- [ ] Complete Context Builder
- [ ] Add GitHub API client

### Phase 2: Agent System (Week 3-4)
- [ ] Implement base agent framework
- [ ] Create prompt templates
- [ ] Build 2-3 core agents (Quality, Architecture, Security)
- [ ] Implement agent orchestration

### Phase 3: Output & Validation (Week 5)
- [ ] Implement Renderer module
- [ ] Build validation system
- [ ] Create Markdown and JSON renderers
- [ ] Add Rich terminal output

### Phase 4: Testing & Polish (Week 6)
- [ ] Write comprehensive tests
- [ ] Performance optimization
- [ ] Documentation completion
- [ ] Beta testing

---

*Last Updated: 2026-05-14*
