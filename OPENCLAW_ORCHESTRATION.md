# OpenClaw Orchestration Integration

This document describes the OpenClaw-based orchestration system for the AI QA Agent.

## Overview

OpenClaw is a workflow orchestration framework that manages complex task dependencies and execution. The AI QA Agent now uses OpenClaw to orchestrate the API testing pipeline, providing:

- **Task Dependency Management**: Automatic execution ordering based on task dependencies
- **Error Handling**: Graceful failure handling and status tracking
- **Progress Monitoring**: Detailed execution status and metrics
- **Scalability**: Support for parallel task execution when dependencies allow
- **Extensibility**: Easy addition of new workflow tasks

## Architecture

### Task Workflow

The OpenClaw orchestrator manages the following tasks:

#### For REST APIs:
1. **parse_spec** → Parse OpenAPI specification
2. **generate_tests** → Generate pytest test file (depends on: parse_spec)
3. **run_tests** → Execute tests with pytest (depends on: generate_tests)
4. **generate_report** → Generate Allure report (depends on: run_tests)

#### For GraphQL:
1. **fetch_schema** → Fetch and parse GraphQL schema
2. **generate_tests** → Generate GraphQL tests (depends on: fetch_schema)
3. **run_tests** → Execute tests (depends on: generate_tests)
4. **generate_report** → Generate report (depends on: run_tests)

#### For gRPC:
1. **run_grpc_tests** → Run gRPC tests
2. **generate_report** → Generate report (depends on: run_grpc_tests)

### Task Execution Model

```
┌─────────────────┐
│  parse_spec     │  (or fetch_schema for GraphQL / run_grpc_tests for gRPC)
└────────┬────────┘
         │
┌────────▼──────────┐
│ generate_tests    │
└────────┬──────────┘
         │
┌────────▼──────────┐
│  run_tests        │
└────────┬──────────┘
         │
┌────────▼──────────────┐
│ generate_report       │
└──────────────────────┘
```

## Task Status Tracking

Each task execution produces a `TaskResult` with:
- **task_name**: Name of the task
- **status**: Current status (PENDING, RUNNING, COMPLETED, FAILED, SKIPPED)
- **data**: Result data if successful
- **error**: Error message if failed
- **metadata**: Additional execution metadata

## Usage Examples

### Using OpenClaw Orchestrator (Default)

```bash
# REST API with OpenClaw
python -m src.main --protocol rest \
  --spec examples/openapi.json \
  --base-url https://petstore.swagger.io/v2 \
  --orchestrator openclaw

# GraphQL with OpenClaw
python -m src.main --protocol graphql \
  --spec https://spacex-production.up.railway.app/ \
  --base-url https://spacex-production.up.railway.app/ \
  --orchestrator openclaw

# gRPC with OpenClaw
python -m src.main --protocol grpc \
  --base-url grpcb.in:9000 \
  --orchestrator openclaw
```

### Programmatic Usage

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

# Get detailed task results
task_results = orchestrator.get_task_results()
for task_name, task_result in task_results.items():
    print(f"{task_name}: {task_result.status}")
    if task_result.error:
        print(f"  Error: {task_result.error}")

# Print execution summary
orchestrator.print_execution_summary()
```

## Error Handling

The OpenClaw orchestrator handles errors gracefully:

1. **Task Failure**: If a task fails, dependent tasks are skipped
2. **Dependency Chain Failure**: Pipeline stops if critical tasks fail
3. **Error Logging**: All errors are logged with full details
4. **Graceful Rollback**: Results remain consistent even if pipeline fails

Example:
```python
try:
    result = await orchestrator.execute_pipeline(...)
    if result.get("task_results"):
        for task_name, task_info in result["task_results"].items():
            if task_info["status"] == "failed":
                print(f"Task {task_name} failed: {task_info['error']}")
except Exception as e:
    print(f"Pipeline failed: {e}")
```

## Configuration

Configure OpenClaw behavior via environment variables or `settings`:

```python
# In src/config.py or .env
MAX_CONCURRENT_TASKS=5  # Maximum parallel task execution
LOG_LEVEL=INFO          # Logging verbosity
```

## Fallback to Legacy Agent

If you need to use the legacy agent-based orchestration, use:

```bash
python -m src.main --protocol rest \
  --spec examples/openapi.json \
  --base-url https://petstore.swagger.io/v2 \
  --orchestrator legacy
```

## Task Execution Details

### parse_spec Task (REST)

Parses OpenAPI specification and extracts endpoints.

**Input**: REST API spec URL or file path  
**Output**: List of API endpoints  
**Metadata**: spec_source, endpoint count

### fetch_schema Task (GraphQL)

Fetches GraphQL schema from endpoint.

**Input**: GraphQL endpoint URL  
**Output**: GraphQL schema  
**Metadata**: endpoint, query field count

### generate_tests Task

Generates test file using LLM-powered test generation.

**Input**: Parsed spec/schema, base URL  
**Output**: Test file path  
**Metadata**: base_url, endpoint_count (REST) or endpoint_url (GraphQL)

### run_tests Task

Executes generated tests using pytest.

**Input**: Test file path  
**Output**: Test execution results (success, stdout, stderr)  
**Metadata**: test_file, report_dir

### run_grpc_tests Task

Executes gRPC tests using grpcurl.

**Input**: gRPC server address  
**Output**: Test execution results  
**Metadata**: server address

### generate_report Task

Generates Allure test report.

**Input**: Test execution results  
**Output**: Report URL  
**Metadata**: output_dir

## Extending OpenClaw Orchestrator

To add new tasks to the workflow:

1. **Add task to dependency graph** in `_build_task_graph()`
2. **Create task method** following `async def _task_*()` pattern
3. **Execute task** in `_execute_task()` method
4. **Return TaskResult** with status and data

Example:

```python
async def _task_custom_task(self) -> TaskResult:
    """Custom task implementation."""
    try:
        # Task logic
        result_data = await self.perform_operation()
        
        return TaskResult(
            task_name="custom_task",
            status=TaskStatus.COMPLETED,
            data=result_data,
            metadata={"custom": "metadata"}
        )
    except Exception as e:
        return TaskResult(
            task_name="custom_task",
            status=TaskStatus.FAILED,
            error=str(e)
        )
```

## Monitoring and Debugging

### Enable Detailed Logging

```bash
LOG_LEVEL=DEBUG python -m src.main --protocol rest \
  --spec examples/openapi.json \
  --base-url https://api.example.com
```

### Inspect Task Results

```python
# After pipeline execution
result = await orchestrator.execute_pipeline(...)

# View detailed task information
for task_name, task_info in result["task_results"].items():
    print(f"\nTask: {task_name}")
    print(f"  Status: {task_info['status']}")
    if task_info.get('error'):
        print(f"  Error: {task_info['error']}")
    print(f"  Metadata: {task_info.get('metadata', {})}")
```

## Performance Considerations

- **Task Parallelization**: Tasks with no dependency chain are executed sequentially in current implementation. Future versions can enable parallel execution.
- **Caching**: Schema/spec parsing results are cached in task results
- **Memory**: Large result datasets are stored in-memory; for very large tests, consider streaming

## Version History

- **v1.0**: Initial OpenClaw integration with REST, GraphQL, and gRPC support
