# OpenClaw Quick Reference

## Installation

```bash
pip install -r requirements.txt
```

## Command Line Usage

### Basic Commands

```bash
# REST API Testing (OpenClaw is default)
python -m src.main --protocol rest \
  --spec examples/openapi.json \
  --base-url https://petstore.swagger.io/v2

# GraphQL Testing
python -m src.main --protocol graphql \
  --spec https://spacex-production.up.railway.app/ \
  --base-url https://spacex-production.up.railway.app/

# gRPC Testing
python -m src.main --protocol grpc \
  --base-url grpcb.in:9000

# With custom output directory
python -m src.main --protocol rest \
  --spec examples/openapi.json \
  --base-url https://petstore.swagger.io/v2 \
  --output my_tests

# Using legacy agent (fallback)
python -m src.main --protocol rest \
  --spec examples/openapi.json \
  --base-url https://petstore.swagger.io/v2 \
  --orchestrator legacy
```

## Python Usage

### Basic Usage

```python
import asyncio
from src.orchestrator.openclaw_orchestrator import OpenClawOrchestrator

async def main():
    orchestrator = OpenClawOrchestrator(protocol="rest")
    result = await orchestrator.execute_pipeline(
        spec_source="examples/openapi.json",
        base_url="https://petstore.swagger.io/v2",
        output_dir="generated_tests"
    )
    print(f"Test file: {result['test_file']}")
    print(f"Report: {result['report']}")

asyncio.run(main())
```

### With Monitoring

```python
async def main():
    orchestrator = OpenClawOrchestrator(protocol="rest")
    result = await orchestrator.execute_pipeline(...)
    
    # Print execution summary
    orchestrator.print_execution_summary()
    
    # Get task results
    task_results = orchestrator.get_task_results()
    for task_name, result in task_results.items():
        print(f"{task_name}: {result.status.value}")
```

### With Retry Configuration

```python
from src.orchestrator.task_utils import TaskRetryHandler, RetryConfig, RetryStrategy

async def main():
    retry_config = RetryConfig(
        max_retries=3,
        strategy=RetryStrategy.EXPONENTIAL
    )
    
    handler = TaskRetryHandler(retry_config)
    result = await handler.execute_with_retry(
        "fetch_spec",
        fetch_spec_async,
        spec_url="https://api.example.com/spec"
    )
```

### With Task Monitoring

```python
from src.orchestrator.task_utils import TaskMonitor

async def main():
    monitor = TaskMonitor()
    
    monitor.record_start("task_1")
    # ... do work ...
    monitor.record_end("task_1", "completed")
    
    # Print metrics
    monitor.print_summary()
```

### Custom Workflow

```python
from src.orchestrator.workflows import WorkflowBuilder

workflow = (WorkflowBuilder("my_test", "rest")
    .add_task("parse_spec")
    .add_task("generate_tests", ["parse_spec"])
    .add_task("run_tests", ["generate_tests"])
    .set_retry_policy("run_tests", max_retries=2)
    .set_timeout("run_tests", timeout_seconds=300)
    .build())
```

## Task Status Values

- `pending` - Waiting to execute
- `running` - Currently executing
- `completed` - Executed successfully
- `failed` - Execution failed
- `skipped` - Skipped (dependency failed or condition not met)

## Retry Strategies

- `exponential` - Delay grows exponentially (2^attempt)
- `linear` - Delay grows linearly (initial_delay * attempt)
- `immediate` - No delay between retries

## Configuration

### Via `.env` File

```env
# Logging
LOG_LEVEL=INFO

# Orchestrator
DEFAULT_ORCHESTRATOR=openclaw
ORCHESTRATOR_ENABLE_MONITORING=true
ORCHESTRATOR_MAX_RETRIES=3
ORCHESTRATOR_RETRY_STRATEGY=exponential
ORCHESTRATOR_TASK_TIMEOUT=300

# Output
TESTS_OUTPUT_DIR=generated_tests
REPORTS_DIR=reports

# Concurrency
MAX_CONCURRENT_TASKS=5

# LLM
GEMINI_API_KEY=your_key_here
```

### Via Code

```python
from src.config import settings

settings.log_level = "DEBUG"
settings.max_concurrent_tasks = 10
settings.orchestrator_max_retries = 5
```

## Common Patterns

### Execute and Check Results

```python
result = await orchestrator.execute_pipeline(...)

if result['results']['success']:
    print("✓ Tests passed!")
else:
    print("✗ Tests failed!")
    print(result['results']['stderr'])
```

### Handle Failures

```python
try:
    result = await orchestrator.execute_pipeline(...)
except Exception as e:
    print(f"Pipeline failed: {e}")
    
    # Check which tasks failed
    for task_name, task_result in orchestrator.get_task_results().items():
        if task_result.status.value == "failed":
            print(f"Failed: {task_name} - {task_result.error}")
```

### Execute Multiple Protocols

```python
for protocol in ["rest", "graphql", "grpc"]:
    orchestrator = OpenClawOrchestrator(protocol=protocol)
    result = await orchestrator.execute_pipeline(...)
    print(f"{protocol}: {'✓' if result['results']['success'] else '✗'}")
```

### Task Scheduler for Parallel Tasks

```python
from src.orchestrator.task_utils import TaskScheduler

scheduler = TaskScheduler(max_concurrent=5)

for i in range(10):
    await scheduler.submit(f"task_{i}", async_function(i))

print(f"Completed: {scheduler.get_completed_count()}")
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | INFO | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |
| `DEFAULT_ORCHESTRATOR` | openclaw | Default orchestrator (openclaw, legacy) |
| `ORCHESTRATOR_MAX_RETRIES` | 3 | Maximum retry attempts |
| `ORCHESTRATOR_RETRY_STRATEGY` | exponential | Retry strategy (exponential, linear, immediate) |
| `ORCHESTRATOR_TASK_TIMEOUT` | 300 | Task timeout in seconds |
| `MAX_CONCURRENT_TASKS` | 5 | Maximum concurrent tasks |
| `TESTS_OUTPUT_DIR` | generated_tests | Output directory for tests |
| `REPORTS_DIR` | reports | Output directory for reports |

## Useful Commands

```bash
# Run with debug logging
LOG_LEVEL=DEBUG python -m src.main --protocol rest \
  --spec examples/openapi.json \
  --base-url https://petstore.swagger.io/v2

# Run examples
python examples/openclaw_examples.py 1  # Basic REST
python examples/openclaw_examples.py 3  # Monitoring
python examples/openclaw_examples.py 4  # Retry
python examples/openclaw_examples.py 6  # Custom workflow

# Run tests
pytest tests/test_orchestrator.py -v
pytest tests/ --cov=src.orchestrator

# Generate report
allure generate --clean -o allure-report reports/
allure open allure-report/

# Clean up
rm -rf generated_tests* reports/* __pycache__
```

## API Reference

### OpenClawOrchestrator

```python
# Create
orchestrator = OpenClawOrchestrator(protocol="rest")

# Execute
result = await orchestrator.execute_pipeline(
    spec_source: str,
    base_url: str,
    output_dir: str
) -> Dict

# Get results
task_results = orchestrator.get_task_results() -> Dict[str, TaskResult]

# Print summary
orchestrator.print_execution_summary() -> None
```

### TaskResult

```python
class TaskResult:
    task_name: str
    status: TaskStatus
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def is_success() -> bool
    def is_failed() -> bool
```

### Task Status

```python
class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
```

### TaskRetryHandler

```python
handler = TaskRetryHandler(config: RetryConfig)

result = await handler.execute_with_retry(
    task_name: str,
    task_func: Callable,
    *args,
    **kwargs
) -> Any

retry_count = handler.get_retry_count(task_name: str) -> int
```

### TaskMonitor

```python
monitor = TaskMonitor()

monitor.record_start(task_name: str) -> None
monitor.record_end(task_name: str, status: str, error: str = None) -> None
monitor.get_metrics(task_name: str) -> Dict
monitor.get_all_metrics() -> Dict
monitor.get_total_duration() -> float
monitor.get_slowest_task() -> Optional[tuple]
monitor.print_summary() -> None
```

### WorkflowBuilder

```python
workflow = WorkflowBuilder(name: str, protocol: str)

workflow.add_task(task_name: str, dependencies: List[str] = None) -> WorkflowBuilder
workflow.set_retry_policy(task_name: str, max_retries: int) -> WorkflowBuilder
workflow.set_timeout(task_name: str, timeout_seconds: int) -> WorkflowBuilder

final_workflow = workflow.build() -> WorkflowConfig
```

## Documentation Files

- `OPENCLAW_ORCHESTRATION.md` - Architecture and task management
- `OPENCLAW_GUIDE.md` - Comprehensive usage guide
- `OPENCLAW_TESTING.md` - Testing strategies
- `OPENCLAW_IMPLEMENTATION.md` - Implementation details
- `README.md` - Project overview

## Troubleshooting

### OpenClaw Not Working

```bash
# Check installation
python -c "from src.orchestrator.openclaw_orchestrator import OpenClawOrchestrator; print('✓ OpenClaw installed')"

# Enable debug logging
LOG_LEVEL=DEBUG python -m src.main --protocol rest ...

# Use legacy agent as fallback
python -m src.main --protocol rest ... --orchestrator legacy
```

### Tasks Failing

```python
# Check task results
for task_name, task_result in orchestrator.get_task_results().items():
    if task_result.status.value == "failed":
        print(f"Failed: {task_name}")
        print(f"Error: {task_result.error}")
        print(f"Metadata: {task_result.metadata}")
```

### Performance Issues

```bash
# Increase concurrency
MAX_CONCURRENT_TASKS=20 python -m src.main ...

# Check task timing
python examples/openclaw_examples.py 3
```

## Need Help?

1. Check documentation files
2. Run examples: `python examples/openclaw_examples.py`
3. Enable debug logging: `LOG_LEVEL=DEBUG`
4. Review error messages and task results
5. Check GitHub issues or documentation
