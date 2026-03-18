# AI QA Agent

AI-powered agent for API testing with OpenClaw orchestration.

## Features

- 🚀 **OpenClaw Orchestration**: Advanced task orchestration with dependency management
- 🧪 **Multi-Protocol Support**: REST, GraphQL, and gRPC API testing
- 🤖 **LLM-Powered Test Generation**: Uses Google Gemini for intelligent test case creation
- 📊 **Allure Reports**: Beautiful test execution reports
- 📈 **Task Monitoring**: Comprehensive execution metrics and monitoring
- 🔄 **Retry Logic**: Configurable retry strategies with exponential backoff
- ⚡ **Parallel Execution**: Supports parallel task execution when dependencies allow
- 📚 **Extensible**: Easy to extend with custom tasks and workflows

## Test reports

[Github Pages](https://xofxela.github.io/ai_qa_agent/)

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### API Testing Examples

#### REST API Testing (with OpenClaw)
```bash
python -m src.main --protocol rest --spec examples/openapi.json --base-url https://petstore.swagger.io/v2 --orchestrator openclaw
```

#### GraphQL Testing (with OpenClaw)
```bash
python -m src.main --protocol graphql \
  --spec https://spacex-production.up.railway.app/ \
  --base-url https://spacex-production.up.railway.app/ \
  --orchestrator openclaw
```

#### gRPC Testing (with OpenClaw)
```bash
python -m src.main --protocol grpc \
  --base-url grpcb.in:9000 \
  --orchestrator openclaw
```

#### Using Legacy Agent (Backward Compatibility)
```bash
python -m src.main --protocol rest \
  --spec examples/openapi.json \
  --base-url https://petstore.swagger.io/v2 \
  --orchestrator legacy
```

## OpenClaw Orchestration

This project uses OpenClaw as the default orchestration engine for managing complex API testing workflows.

### Key Components

- **Task Dependency Graph**: Automatically manages task execution order
- **Status Tracking**: Real-time tracking of task status (PENDING, RUNNING, COMPLETED, FAILED, SKIPPED)
- **Error Handling**: Graceful failure handling with comprehensive error reporting
- **Execution Monitoring**: Detailed metrics and performance monitoring

### Workflow Structure

```
parse_spec/fetch_schema → generate_tests → run_tests → generate_report
```

For detailed information about OpenClaw orchestration, see [OPENCLAW_ORCHESTRATION.md](OPENCLAW_ORCHESTRATION.md).

### Configuration

Configure orchestration behavior through environment variables:

```bash
# Set logging level
LOG_LEVEL=INFO

# Set maximum concurrent tasks
MAX_CONCURRENT_TASKS=5

# Set output directories
TESTS_OUTPUT_DIR=generated_tests
REPORTS_DIR=reports
```

## Advanced Usage

### Programmatic API

```python
from src.orchestrator.openclaw_orchestrator import OpenClawOrchestrator

# Create orchestrator
orchestrator = OpenClawOrchestrator(protocol="rest")

# Execute pipeline
result = await orchestrator.execute_pipeline(
    spec_source="examples/openapi.json",
    base_url="https://api.example.com",
    output_dir="generated_tests"
)

# Get execution results
print(f"Status: {result['results']['success']}")
print(f"Test file: {result['test_file']}")
print(f"Report: {result['report']}")

# Print execution summary
orchestrator.print_execution_summary()
```

### Custom Workflows

```python
from src.orchestrator.workflows import WorkflowBuilder

# Create custom workflow
workflow = (WorkflowBuilder("custom_api_testing", "rest")
    .add_task("parse_spec")
    .add_task("validate_spec", ["parse_spec"])
    .add_task("generate_tests", ["validate_spec"])
    .add_task("run_tests", ["generate_tests"])
    .set_retry_policy("run_tests", max_retries=2)
    .set_timeout("run_tests", timeout_seconds=300)
    .build())
```

### Task Monitoring

```python
from src.orchestrator.task_utils import TaskMonitor

monitor = TaskMonitor()
# Use monitor with orchestrator
monitor.print_summary()
```

## Project Structure

```
src/
├── main.py                          # Entry point (with OpenClaw integration)
├── config.py                        # Configuration settings
├── orchestrator/
│   ├── agent.py                     # Legacy agent (for backward compatibility)
│   ├── openclaw_orchestrator.py     # OpenClaw-based orchestrator
│   ├── workflows.py                 # Workflow definitions
│   └── task_utils.py                # Task utilities and decorators
├── generators/                      # Test generators (REST, GraphQL)
├── executors/                       # Test executors (pytest, gRPC)
├── parsers/                         # Spec parsers (OpenAPI, GraphQL)
├── reporters/                       # Report generators (Allure)
├── llm/                             # LLM providers (Gemini, OpenAI)
├── models/                          # Data models
└── utils/                           # Utility modules
```

## Environment Setup

Create a `.env` file with your API keys:

```env
GEMINI_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
LOG_LEVEL=INFO
```

## Docker Support

Run tests in Docker:

```bash
docker-compose up
```

## GitHub Actions (CI/CD)

This project includes automated workflows for continuous integration and testing.

### Available Workflows

1. **AI QA Agent Pipeline** (`ai-qa-agent.yml`)
   - Main testing pipeline
   - Supports all protocols: REST, GraphQL, gRPC
   - Manual trigger with customizable inputs
   - Generates Allure reports
   - Deploys to GitHub Pages

2. **OpenClaw Tests** (`openclaw-tests.yml`)
   - Unit tests for orchestrator
   - Integration tests
   - Performance checks
   - Documentation validation
   - Code quality checks

3. **CI/CD Pipeline** (`ci-cd.yml`)
   - Linting and code formatting
   - Security checks
   - Build verification
   - Quality gates

### Trigger Workflows

#### Automatic Triggers
- Push to main/master/develop branches
- Pull requests to main/master/develop

#### Manual Triggers
Via GitHub UI: Actions → Select workflow → "Run workflow"

**Customize inputs:**
- Protocol: rest, graphql, grpc
- Spec URL: Path or URL
- Base URL: API endpoint
- Orchestrator: openclaw or legacy
- Debug: true/false

**Via GitHub CLI:**
```bash
gh workflow run ai-qa-agent.yml \
  -f protocol=rest \
  -f orchestrator=openclaw \
  -f debug=false
```

### View Results

1. Go to Actions tab
2. Select workflow run
3. View job logs and artifacts
4. Download test results and Allure reports

### GitHub Pages Reports

- Automatically deployed on master branch
- Available at: `https://{username}.github.io/{repo}/`
- Updated on each successful run

### Configuration

**Set required secrets:**
1. Settings → Secrets and variables → Actions
2. Add `GEMINI_API_KEY`
3. (Optional) Add `API_BASE_URL`

More details: See [.GITHUB_ACTIONS.md](.GITHUB_ACTIONS.md)

## Troubleshooting

### OpenClaw Integration Issues

If you encounter issues with OpenClaw:

1. Ensure dependencies are installed: `pip install -r requirements.txt`
2. Check logs: `LOG_LEVEL=DEBUG python -m src.main ...`
3. Use legacy orchestrator as fallback: `--orchestrator legacy`

### Common Issues

- **Test Generation Fails**: Check LLM API keys and quotas
- **Test Execution Fails**: Verify API endpoint accessibility
- **Report Generation Fails**: Check write permissions to reports directory

## Contributing

Contributions are welcome! Please ensure:

1. Code follows project style guidelines
2. Tests pass: `pytest`
3. Type hints are included
4. Documentation is updated
