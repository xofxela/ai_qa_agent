# Testing OpenClaw Integration

This guide provides comprehensive instructions for testing the OpenClaw orchestration system in the AI QA Agent.

## Prerequisites

Ensure you have installed all dependencies:

```bash
pip install -r requirements.txt
```

## Quick Test

Run a quick test to verify OpenClaw is working:

```bash
python -m src.main --protocol rest \
  --spec examples/openapi.json \
  --base-url https://petstore.swagger.io/v2 \
  --orchestrator openclaw
```

Expected output:
```
OpenClaw Orchestrator Execution Summary
============================================================
parse_spec: [COMPLETED]
generate_tests: [COMPLETED]
run_tests: [COMPLETED]
generate_report: [COMPLETED]
============================================================
```

## Unit Tests

### Running Orchestrator Tests

```bash
pytest tests/test_orchestrator.py -v
```

### Test Coverage

```bash
pytest tests/ --cov=src.orchestrator --cov-report=html
```

## Integration Tests

### Test REST API Integration

```bash
# Test with local OpenAPI spec
python -m src.main --protocol rest \
  --spec examples/openapi.json \
  --base-url https://petstore.swagger.io/v2 \
  --orchestrator openclaw \
  --output generated_tests_rest
```

### Test GraphQL Integration

```bash
# Test with SpaceX GraphQL API
python -m src.main --protocol graphql \
  --spec https://spacex-production.up.railway.app/ \
  --base-url https://spacex-production.up.railway.app/ \
  --orchestrator openclaw \
  --output generated_tests_graphql
```

### Test gRPC Integration

```bash
# Test with gRPC service
python -m src.main --protocol grpc \
  --base-url grpcb.in:9000 \
  --orchestrator openclaw \
  --output generated_tests_grpc
```

## Example Scripts

### Run OpenClaw Examples

```bash
# Basic REST testing
python examples/openclaw_examples.py 1

# Detailed task inspection
python examples/openclaw_examples.py 2

# Task monitoring
python examples/openclaw_examples.py 3

# Retry strategy
python examples/openclaw_examples.py 4

# Task scheduling
python examples/openclaw_examples.py 5

# Custom workflow
python examples/openclaw_examples.py 6

# Multi-protocol testing
python examples/openclaw_examples.py 7
```

## Performance Testing

### Measure Pipeline Execution Time

```bash
import asyncio
import time
from src.orchestrator.openclaw_orchestrator import OpenClawOrchestrator

async def benchmark():
    orchestrator = OpenClawOrchestrator(protocol="rest")
    
    start_time = time.time()
    result = await orchestrator.execute_pipeline(
        spec_source="examples/openapi.json",
        base_url="https://petstore.swagger.io/v2",
        output_dir="generated_tests"
    )
    end_time = time.time()
    
    print(f"Total execution time: {end_time - start_time:.2f}s")
    
    # Get per-task timing
    task_results = orchestrator.get_task_results()
    for task_name, task_result in task_results.items():
        print(f"  {task_name}: {task_result.metadata}")

asyncio.run(benchmark())
```

## Debugging Tests

### Enable Debug Logging

```bash
LOG_LEVEL=DEBUG python -m src.main --protocol rest \
  --spec examples/openapi.json \
  --base-url https://petstore.swagger.io/v2 \
  --orchestrator openclaw
```

### Inspect Task Results

```python
import asyncio
from src.orchestrator.openclaw_orchestrator import OpenClawOrchestrator

async def debug_pipeline():
    orchestrator = OpenClawOrchestrator(protocol="rest")
    
    result = await orchestrator.execute_pipeline(
        spec_source="examples/openapi.json",
        base_url="https://petstore.swagger.io/v2",
        output_dir="generated_tests"
    )
    
    # Print task results
    for task_name, task_result in orchestrator.get_task_results().items():
        print(f"\n{task_name}:")
        print(f"  Status: {task_result.status.value}")
        if task_result.error:
            print(f"  Error: {task_result.error}")
        if task_result.data:
            print(f"  Data: {task_result.data}")
        if task_result.metadata:
            print(f"  Metadata: {task_result.metadata}")

asyncio.run(debug_pipeline())
```

### Check Task Dependencies

```python
from src.orchestrator.openclaw_orchestrator import OpenClawOrchestrator

orchestrator = OpenClawOrchestrator(protocol="rest")
task_graph = orchestrator._build_task_graph()

print("Task Dependency Graph:")
for task, dependencies in task_graph.items():
    print(f"  {task}: {dependencies}")
```

## Error Handling Tests

### Test Task Failure Handling

```python
import asyncio
from src.orchestrator.openclaw_orchestrator import OpenClawOrchestrator

async def test_failure_handling():
    orchestrator = OpenClawOrchestrator(protocol="rest")
    
    try:
        # Use invalid spec to trigger failure
        result = await orchestrator.execute_pipeline(
            spec_source="invalid_spec.json",
            base_url="https://api.example.com",
            output_dir="generated_tests"
        )
    except Exception as e:
        print(f"Expected failure: {e}")
    
    # Check task results for failures
    for task_name, task_result in orchestrator.get_task_results().items():
        if task_result.status.value == "failed":
            print(f"✓ Task {task_name} correctly failed: {task_result.error}")

asyncio.run(test_failure_handling())
```

### Test Retry Logic

```python
import asyncio
from src.orchestrator.task_utils import (
    TaskRetryHandler,
    RetryConfig,
    RetryStrategy
)

async def test_retry():
    counter = {"attempts": 0}
    
    async def failing_task():
        counter["attempts"] += 1
        if counter["attempts"] < 3:
            raise Exception(f"Attempt {counter['attempts']} failed")
        return "Success"
    
    config = RetryConfig(
        max_retries=5,
        strategy=RetryStrategy.EXPONENTIAL
    )
    
    handler = TaskRetryHandler(config)
    result = await handler.execute_with_retry(
        "test_task",
        failing_task
    )
    
    print(f"✓ Task succeeded after {handler.get_retry_count('test_task')} retries")
    print(f"  Result: {result}")

asyncio.run(test_retry())
```

## Monitoring Tests

### Test Task Monitoring

```python
import asyncio
from src.orchestrator.task_utils import TaskMonitor

async def test_monitoring():
    monitor = TaskMonitor()
    
    # Simulate tasks
    monitor.record_start("task_1")
    await asyncio.sleep(0.5)
    monitor.record_end("task_1", "completed")
    
    monitor.record_start("task_2")
    await asyncio.sleep(1.0)
    monitor.record_end("task_2", "completed")
    
    # Get metrics
    metrics = monitor.get_all_metrics()
    
    print("✓ Task Monitoring Results:")
    for task_name, metrics in metrics.items():
        print(f"  {task_name}: {metrics['duration']:.2f}s")
    
    # Check slowest task
    slowest = monitor.get_slowest_task()
    print(f"\n✓ Slowest task: {slowest[0]} ({slowest[1]:.2f}s)")
    
    # Print summary
    monitor.print_summary()

asyncio.run(test_monitoring())
```

## Comparison Tests

### OpenClaw vs Legacy Agent

```bash
# Test with OpenClaw (new)
time python -m src.main --protocol rest \
  --spec examples/openapi.json \
  --base-url https://petstore.swagger.io/v2 \
  --orchestrator openclaw

# Test with Legacy Agent
time python -m src.main --protocol rest \
  --spec examples/openapi.json \
  --base-url https://petstore.swagger.io/v2 \
  --orchestrator legacy
```

Compare execution times and output quality.

## Stress Testing

### Test with High Concurrency

```python
import asyncio
from src.orchestrator.task_utils import TaskScheduler

async def stress_test():
    scheduler = TaskScheduler(max_concurrent=50)
    
    async def dummy_task(task_id):
        await asyncio.sleep(0.1)
        return f"Task {task_id} done"
    
    # Submit 100 tasks
    for i in range(100):
        await scheduler.submit(f"task_{i}", dummy_task(i))
    
    print(f"✓ Completed {scheduler.get_completed_count()} tasks")

asyncio.run(stress_test())
```

### Test with Large Workflows

```python
from src.orchestrator.workflows import WorkflowBuilder

# Create workflow with many tasks
workflow = WorkflowBuilder("large_workflow", "rest")

# Add 50 interdependent tasks
for i in range(50):
    deps = [f"task_{i-1}"] if i > 0 else []
    workflow.add_task(f"task_{i}", deps)

final_workflow = workflow.build()
print(f"✓ Created workflow with {len(final_workflow.tasks)} tasks")
```

## Documentation Tests

### Verify Documentation Examples

```bash
# Test example from OPENCLAW_ORCHESTRATION.md
python -c "
import asyncio
from src.orchestrator.openclaw_orchestrator import OpenClawOrchestrator

async def example():
    orchestrator = OpenClawOrchestrator(protocol='rest')
    result = await orchestrator.execute_pipeline(
        spec_source='examples/openapi.json',
        base_url='https://petstore.swagger.io/v2',
        output_dir='generated_tests'
    )
    print('✓ Documentation example works')

asyncio.run(example())
"
```

## Test Results Validation

### Validate Generated Tests

```bash
# Run generated tests
pytest generated_tests/test_rest.py -v --alluredir=reports

# Check test results
python -c "
import json
import glob

report_files = glob.glob('reports/*-result.json')
for report_file in report_files:
    with open(report_file) as f:
        result = json.load(f)
        print(f'Test: {result.get(\"name\", \"unknown\")}')
        print(f'  Status: {result.get(\"status\", \"unknown\")}')
"
```

## CI/CD Testing

### GitHub Actions Example

```yaml
name: OpenClaw Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Test OpenClaw REST
        run: |
          python -m src.main --protocol rest \
            --spec examples/openapi.json \
            --base-url https://petstore.swagger.io/v2 \
            --orchestrator openclaw
      
      - name: Test OpenClaw Examples
        run: |
          python examples/openclaw_examples.py 3
          python examples/openclaw_examples.py 4
      
      - name: Run Pytest
        run: pytest tests/ --cov=src.orchestrator
```

## Troubleshooting Test Failures

### Test Timeouts

If tests timeout:

```bash
# Increase timeout
pytest tests/ --timeout=600
```

### Import Errors

If you see import errors:

```bash
# Verify Python path
python -c "import sys; print(sys.path)"

# Install in development mode
pip install -e .
```

### API Connectivity

If API tests fail:

```bash
# Test connectivity
curl -I https://petstore.swagger.io/v2

# Use offline mode with cached specs
python -m src.main --protocol rest \
  --spec examples/openapi.json \
  --base-url http://localhost:8000
```

## Reporting

Generate test report:

```bash
# Generate Allure report
allure generate --clean -o allure-report reports/

# Open in browser
allure open allure-report/
```

## Cleanup

Clean up test artifacts:

```bash
# Remove generated tests
rm -rf generated_tests generated_tests_*

# Remove reports
rm -rf reports/*

# Remove Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```
