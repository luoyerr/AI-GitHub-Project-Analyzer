# Architecture Design Document

## Overview

AI GitHub Analyzer follows a **Clean Architecture** pattern with clear separation of concerns. The system is designed around a modular, event-driven workflow where each module has a single responsibility and communicates through well-defined Pydantic models.

## Architectural Principles

1. **Separation of Concerns**: Each module handles one specific aspect of analysis
2. **Dependency Rule**: Dependencies point inward toward core business logic
3. **Model-Driven Communication**: All inter-module communication uses Pydantic models
4. **Async-First Design**: Built on asyncio for concurrent operations
5. **No Over-Engineering**: Lightweight, focused modules without unnecessary abstractions

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Layer (Typer)                       │
│                    main.py - Entry Point                     │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  Orchestrator Module                         │
│           Coordinates the analysis workflow                 │
└──┬──────────┬──────────┬──────────┬──────────┬─────────────┘
   │          │          │          │          │
┌──▼───┐  ┌──▼────┐  ┌──▼──────┐  │          │
│Scan  │  │Class  │  │Context  │  │          │
│ner   │──▶ifier  │──▶Builder  │  │          │
└──────┘  └───────┘  └────┬────┘  │          │
                          │       │          │
                   ┌──────▼───────▼──┐      │
                   │    Agents       │◀─────┘
                   │  (Specialized)  │
                   └──────┬──────────┘
                          │
                   ┌──────▼──────┐
                   │ Validators  │
                   └──────┬──────┘
                          │
                   ┌──────▼──────┐
                   │  Renderer   │
                   └─────────────┘
```

## Module Responsibilities

### 1. Orchestrator (`src/orchestrator/`)

**Purpose**: Central coordinator that manages the analysis workflow lifecycle.

**Responsibilities**:
- Initialize and configure the analysis pipeline
- Execute modules in the correct sequence
- Handle errors and retries
- Manage async task coordination
- Track overall progress

**Key Interfaces**:
- `AnalysisOrchestrator`: Main orchestrator class
- Accepts `AnalysisConfig`, returns `AnalysisResult`

---

### 2. Scanner (`src/scanner/`)

**Purpose**: Extracts raw repository structure and metadata.

**Responsibilities**:
- Clone or access repository (local/remote)
- Build file tree structure
- Count files, lines, and directories
- Detect programming languages
- Extract dependency information (package.json, requirements.txt, etc.)
- Identify configuration files

**Output**: `ScanResult` model

**Design Notes**:
- Should support both local paths and GitHub URLs
- Must handle large repositories efficiently
- Ignore common non-code directories (node_modules, .git, etc.)

---

### 3. Classifier (`src/classifier/`)

**Purpose**: Analyzes scanned data to identify technology stack and patterns.

**Responsibilities**:
- Determine primary programming language
- Detect frameworks and libraries
- Identify architectural patterns (MVC, microservices, etc.)
- Classify repository type (library, application, framework, etc.)
- Calculate confidence scores for classifications

**Input**: `ScanResult`  
**Output**: `ClassificationResult`

**Design Notes**:
- Use heuristics and pattern matching
- Consider file extensions, imports, and configurations
- Support extensible classification rules

---

### 4. Context Builder (`src/context_builder/`)

**Purpose**: Aggregates and enriches data from scanner and classifier.

**Responsibilities**:
- Merge scan results with classification data
- Build comprehensive repository context
- Extract key files (README, documentation, configs)
- Prepare context for AI agents
- Create structured representation for analysis

**Input**: `ScanResult`, `ClassificationResult`  
**Output**: Enriched context object (Pydantic model)

**Design Notes**:
- Should create a unified view of the repository
- Optimize context size for AI token limits
- Preserve important structural information

---

### 5. Agents (`src/agents/`)

**Purpose**: Specialized AI agents that perform deep analysis tasks.

**Responsibilities**:
- **Architecture Agent**: Analyze architectural decisions and patterns
- **Quality Agent**: Assess code quality and best practices
- **Security Agent**: Identify potential security issues
- **Documentation Agent**: Evaluate documentation completeness
- **Recommendation Agent**: Generate actionable improvements

**Input**: Enriched context from Context Builder  
**Output**: Agent-specific analysis results

**Design Notes**:
- Each agent should be independent and focused
- Support parallel execution where possible
- Agents communicate results back to orchestrator
- Use prompt templates from `prompts/` directory

---

### 6. Validators (`src/validators/`)

**Purpose**: Ensure analysis results meet quality standards.

**Responsibilities**:
- Validate completeness of analysis
- Check for consistency across modules
- Verify data integrity
- Flag potential issues or uncertainties
- Apply validation rules

**Input**: Raw analysis results  
**Output**: Validated results with quality metrics

**Design Notes**:
- Implement pluggable validation rules
- Provide detailed validation reports
- Support configurable strictness levels

---

### 7. Renderer (`src/renderer/`)

**Purpose**: Format and present analysis results.

**Responsibilities**:
- Convert results to various formats (Markdown, JSON, HTML)
- Apply formatting and styling
- Generate visualizations if needed
- Export to file or display in terminal
- Support custom templates

**Input**: Validated `AnalysisResult`  
**Output**: Formatted output in requested format

**Design Notes**:
- Support multiple output formats
- Rich terminal output using Rich library
- Template-based rendering for flexibility

---

### 8. Models (`src/models/`)

**Purpose**: Define all data structures for inter-module communication.

**Responsibilities**:
- Define Pydantic models for all data types
- Ensure type safety across modules
- Provide validation at data boundaries
- Document data contracts

**Key Models**:
- `AnalysisConfig`: Configuration parameters
- `RepositoryInfo`: Repository metadata
- `ScanResult`: Scanner output
- `ClassificationResult`: Classifier output
- `AnalysisResult`: Final analysis result

**Design Notes**:
- All models should be immutable where possible
- Include comprehensive field descriptions
- Use appropriate types and constraints

---

### 9. Infrastructure (`src/infrastructure/`)

**Purpose**: Core infrastructure components supporting the application.

**Responsibilities**:
- Configuration management (pydantic-settings)
- Logging setup (loguru)
- Error handling utilities
- Async helpers
- External service clients (GitHub API, AI providers)

**Design Notes**:
- Keep infrastructure concerns separate from business logic
- Support environment-based configuration
- Provide reusable utilities

---

### 10. Utils (`src/utils/`)

**Purpose**: General-purpose utility functions.

**Responsibilities**:
- File system operations
- String manipulation
- Date/time helpers
- Common algorithms
- Helper functions used across modules

**Design Notes**:
- Functions should be pure and stateless
- No module-specific logic
- Well-tested and documented

---

## Data Flow

```
1. User Input (CLI)
   ↓
2. AnalysisConfig created
   ↓
3. Orchestrator initializes workflow
   ↓
4. Scanner → ScanResult
   ↓
5. Classifier → ClassificationResult
   ↓
6. Context Builder → Enriched Context
   ↓
7. Agents → Agent Results (parallel)
   ↓
8. Validators → Validated Results
   ↓
9. Renderer → Formatted Output
   ↓
10. Display to User
```

## Technology Stack Rationale

### Python 3.12+
- Latest performance improvements
- Better type hints and error messages
- Modern async/await syntax

### Typer
- Type-safe CLI framework
- Automatic help generation
- Easy command definition
- Built on Pydantic

### Rich
- Beautiful terminal output
- Progress bars and spinners
- Tables, panels, and formatting
- Color and styling support

### Loguru
- Zero-config logging
- Structured log output
- Easy rotation and retention
- Exception handling

### Pydantic
- Runtime data validation
- Type safety
- Clean model definitions
- Settings management

### asyncio
- Concurrent execution
- Efficient I/O operations
- Parallel agent execution
- Non-blocking operations

## Directory Structure Rationale

### `src/` Layout
- Prevents import conflicts during development
- Clear separation between source and tests
- Standard Python packaging practice
- Easier testing with isolated imports

### `prompts/`
- Separate AI prompt templates from code
- Easy to version and modify prompts
- Support prompt engineering workflows

### `schemas/`
- JSON schemas for external integrations
- API contract definitions
- Validation schemas

### `traces/`
- Store execution traces for debugging
- Performance profiling data
- Agent interaction logs

### `tests/`
- Comprehensive test suite
- Mirror src/ structure
- Unit, integration, and E2E tests

### `docs/design-docs/`
- Detailed design documents
- RFCs and proposals
- Architecture decision records (ADRs)

## Extension Points

The architecture supports easy extension:

1. **New Agents**: Add agent classes in `src/agents/`
2. **New Validators**: Implement validation rules in `src/validators/`
3. **New Renderers**: Add output formats in `src/renderer/`
4. **Custom Classifiers**: Extend classification logic in `src/classifier/`
5. **Prompt Templates**: Add/modify prompts in `prompts/`

## Error Handling Strategy

- Each module handles its own errors
- Orchestrator catches and aggregates errors
- Graceful degradation when optional modules fail
- Detailed error messages with context
- Logging at appropriate levels

## Performance Considerations

- Async I/O for network operations
- Parallel agent execution where possible
- Caching of expensive operations
- Lazy loading of large datasets
- Token optimization for AI calls

## Security Considerations

- Never execute arbitrary code from repositories
- Sanitize all inputs
- Rate limit external API calls
- Secure storage of API keys
- Validate repository URLs

## Testing Strategy

- **Unit Tests**: Each module independently tested
- **Integration Tests**: Module interactions
- **E2E Tests**: Full workflow execution
- **Mock External Services**: GitHub API, AI providers
- **Fixture Repositories**: Test against known repos

## Future Enhancements

- Plugin system for custom agents
- Web UI interface
- Database for storing analysis history
- Comparison between repository versions
- Integration with CI/CD pipelines
- Custom rule engine for validators

---

*Last Updated: 2026-05-14*
