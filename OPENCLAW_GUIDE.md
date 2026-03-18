# OpenClaw Integration Guide

This guide provides comprehensive examples and best practices for using OpenClaw orchestration in the AI QA Agent.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Advanced Features](#advanced-features)
3. [Task Management](#task-management)
4. [Error Handling](#error-handling)
5. [Monitoring and Debugging](#monitoring-and-debugging)
6. [Custom Workflows](#custom-workflows)
7. [Performance Optimization](#performance-optimization)
8. [Troubleshooting](#troubleshooting)

## Basic Usage

### Command Line

#### REST API Testing

```bash
# Simple REST API test
python -m src.main --protocol rest \
  --spec examples/openapi.json \
  --base-url https://petstore.swagger.io/v2
```

#### GraphQL Testing

```bash
# GraphQL endpoint testing
python -m src.main --protocol graphql \
  --spec https://spacex-production.up.railway.app/ \
  --base-url https://spacex-production.up.railway.app/
```

#### gRPC Testing

```bash
# gRPC service testing
python -m src.main --protocol grpc \
  --base-url grpcb.in:9000
```

### Programmatic Usage

#### Basic Orchestrator Setup

```python
import asyncio
from src.orchestrator.openclaw_orchestrator import OpenClawOrchestrator

async def main():
    # Create orchestrator for REST API
    orchestrator = OpenClawOrchestrator(protocol="rest")
    
    # Execute pipeline
    result = await orchestrator.execute_pipeline(
        spec_source="examples/openapi.json",
        base_url="https://petstore.swagger.io/v2",
        output_dir="generated_tests"
    )
    
    # Print execution summary
    orchestrator.print_execution_summary()
    
    # Check results
    if result['results'].get('success'):
        print(f"✓ Tests passed!")
        print(f"Report: {result['report']}")
    else:
        print(f"✗ Tests failed!")

if __name__ == "__main__":
    asyncio.run(main())
```

## Advanced Features

### Task Status Monitoring

```python
from src.orchestrator.openclaw_orchestrator import TaskStatus

async def main():
    orchestrator = OpenClawOrchestrator(protocol="rest")
    result = await orchestrator.execute_pipeline(...)
    
    # Get detailed task results
    task_results = orchestrator.get_task_results()
    
    for task_name, task_result in task_results.items():
        print(f"\nTask: {task_name}")
        print(f"  Status: {task_result.status.value}")
        
        if task_result.status == TaskStatus.COMPLETED:
            print(f"  ✓ Completed successfully")
            if task_result.data:
                print(f"  Data: {task_result.data}")
        
        elif task_result.status == TaskStatus.FAILED:
            print(f"  ✗ Failed with error: {task_result.error}")
        
        elif task_result.status == TaskStatus.SKIPPED:
            print(f"  ⊘ Skipped: {task_result.metadata.get('reason')}")
        
        if task_result.metadata:
            print(f"  Metadata: {task_result.metadata}")
```

### Task Retry Configuration

```python
from src.orchestrator.task_utils import (
    TaskRetryHandler,
    RetryConfig,
    RetryStrategy
)

async def main():
    # Configure retry strategy
    retry_config = RetryConfig(
        max_retries=3,
        strategy=RetryStrategy.EXPONENTIAL,
        initial_delay=1.0,
        max_delay=60.0,
        backoff_factor=2.0
    )
    
    retry_handler = TaskRetryHandler(retry_config)
    
    # Execute task with automatic retries
    result = await retry_handler.execute_with_retry(
        task_name="fetch_api_spec",
        task_func=fetch_openapi_spec,
        spec_url="https://api.example.com/openapi.json"
    )
    
    # Check retry count
    retries = retry_handler.get_retry_count("fetch_api_spec")
    print(f"Task required {retries} retries")
```

### Task Scheduling

```python
from src.orchestrator.task_utils import TaskScheduler

async def main():
    # Create scheduler with max 5 concurrent tasks
    scheduler = TaskScheduler(max_concurrent=5)
    
    # Submit individual tasks
    result1 = await scheduler.submit("task_1", async_function_1())
    result2 = await scheduler.submit("task_2", async_function_2())
    
    # Submit batch of tasks
    tasks = {
        "parse_spec": parse_spec_async(),
        "validate_spec": validate_spec_async(),
        "generate_tests": generate_tests_async(),
    }
    results = await scheduler.submit_batch(tasks)
    
    # Get execution statistics
    completed = scheduler.get_completed_count()
    active = scheduler.get_active_tasks()
    print(f"Completed: {completed}, Active: {active}")
```

### Execution Monitoring

```python
from src.orchestrator.task_utils import TaskMonitor

async def main():
    monitor = TaskMonitor()
    
    # Record task execution
    monitor.record_start("parse_spec")
    # ... perform work ...
    monitor.record_end("parse_spec", "completed")
    
    # Get metrics for specific task
    metrics = monitor.get_metrics("parse_spec")
    print(f"Duration: {metrics['duration']:.2f}s")
    
    # Get all metrics
    all_metrics = monitor.get_all_metrics()
    for task_name, metrics in all_metrics.items():
        print(f"{task_name}: {metrics['duration']:.2f}s")
    
    # Print summary
    monitor.print_summary()
    
    # Get total execution time
    total_time = monitor.get_total_duration()
    print(f"Total execution time: {total_time:.2f}s")
```

## Task Management

### Task Dependencies

```python
from src.orchestrator.workflows import WorkflowBuilder

# Create workflow with task dependencies
workflow = (WorkflowBuilder("rest_api_test", "rest")
    .add_task("parse_spec")
    .add_task("validate_spec", ["parse_spec"])
    .add_task("generate_tests", ["validate_spec"])
    .add_task("lint_tests", ["generate_tests"])
    .add_task("run_tests", ["lint_tests"])
    .add_task("generate_report", ["run_tests"])
    .build())

# The orchestrator will execute tasks in order:
# parse_spec → validate_spec → generate_tests → lint_tests → run_tests → generate_report
```

### Parallel Task Execution

```python
# When adding multiple independent tasks
workflow = (WorkflowBuilder("parallel_test", "rest")
    .add_task("parse_spec")
    .add_task("validate_schema")  # No dependency - can run in parallel
    .add_task("generate_tests", ["parse_spec", "validate_schema"])
    .build())
```

### Retry on Specific Tasks

```python
workflow = (WorkflowBuilder("resilient_test", "rest")
    .add_task("parse_spec")
    .add_task("generate_tests", ["parse_spec"])
    .add_task("run_tests", ["generate_tests"])
    .set_retry_policy("parse_spec", max_retries=3)
    .set_retry_policy("run_tests", max_retries=2)
    .build())
```

### Task Timeouts

```python
workflow = (WorkflowBuilder("timeout_test", "rest")
    .add_task("parse_spec")
    .add_task("run_tests", ["parse_spec"])
    .set_timeout("parse_spec", timeout_seconds=30)
    .set_timeout("run_tests", timeout_seconds=300)
    .build())
```

## Error Handling

### Graceful Failure Handling

```python
async def main():
    orchestrator = OpenClawOrchestrator(protocol="rest")
    
    try:
        result = await orchestrator.execute_pipeline(
            spec_source="examples/openapi.json",
            base_url="https://api.example.com",
            output_dir="generated_tests"
        )
        
        # Check for task failures
        task_results = result.get("task_results", {})
        failed_tasks = [
            name for name, info in task_results.items()
            if info["status"] == "failed"
        ]
        
        if failed_tasks:
            print(f"Failed tasks: {failed_tasks}")
            for task_name in failed_tasks:
                error = task_results[task_name].get("error")
                print(f"  {task_name}: {error}")
        else:
            print("All tasks completed successfully!")
    
    except Exception as e:
        print(f"Pipeline failed: {e}")
        # Handle pipeline failure
```

### Task-Level Error Recovery

```python
from src.orchestrator.task_utils import TaskRetryHandler, RetryConfig

async def execute_with_fallback():
    retry_handler = TaskRetryHandler(
        RetryConfig(max_retries=3, strategy="exponential")
    )
    
    try:
        # Try primary method with retries
        result = await retry_handler.execute_with_retry(
            "fetch_spec",
            fetch_spec_primary,
            spec_url="https://api.example.com/spec"
        )
    except Exception as e:
        # Fallback to alternative method
        print(f"Primary method failed: {e}")
        result = await fetch_spec_fallback()
    
    return result
```

### Error Logging and Reporting

```python
async def main():
    orchestrator = OpenClawOrchestrator(protocol="rest")
    result = await orchestrator.execute_pipeline(...)
    
    # Log all errors
    import logging
    logger = logging.getLogger(__name__)
    
    for task_name, task_result in orchestrator.get_task_results().items():
        if task_result.error:
            logger.error(f"Task {task_name} failed: {task_result.error}")
            if task_result.metadata:
                logger.error(f"  Metadata: {task_result.metadata}")
```

## Monitoring and Debugging

### Detailed Logging

```bash
# Enable debug logging
DEBUG=1 LOG_LEVEL=DEBUG python -m src.main --protocol rest \
  --spec examples/openapi.json \
  --base-url https://petstore.swagger.io/v2
```

### Task Metrics

```python
from src.orchestrator.task_utils import TaskMonitor

async def main():
    monitor = TaskMonitor()
    
    # Simulate task execution with monitoring
    monitor.record_start("parse_spec")
    # ... work ...
    monitor.record_end("parse_spec", "completed")
    
    monitor.record_start("generate_tests")
    # ... work ...
    monitor.record_end("generate_tests", "completed")
    
    # Get slowest task
    slowest = monitor.get_slowest_task()
    if slowest:
        task_name, duration = slowest
        print(f"Slowest task: {task_name} ({duration:.2f}s)")
    
    # Print full summary
    monitor.print_summary()
```

### Real-Time Monitoring

```python
async def main():
    orchestrator = OpenClawOrchestrator(protocol="rest")
    
    # Create monitoring task that runs alongside pipeline
    async def monitor_pipeline():
        while True:
            task_results = orchestrator.get_task_results()
            active_tasks = [name for name, result in task_results.items()
                          if result.status.value == "running"]
            print(f"Active tasks: {active_tasks}")
            await asyncio.sleep(1)
    
    # Run pipeline with monitoring
    pipeline_task = asyncio.create_task(
        orchestrator.execute_pipeline(...)
    )
    monitor_task = asyncio.create_task(monitor_pipeline())
    
    result = await pipeline_task
    monitor_task.cancel()
```

## Custom Workflows

### Creating Custom Workflow

```python
from src.orchestrator.workflows import WorkflowBuilder, WorkflowExecutor

# Build custom workflow
workflow = (WorkflowBuilder("custom_api_test", "rest")
    .add_task("fetch_openapi_spec")
    .add_task("validate_spec", ["fetch_openapi_spec"])
    .add_task("generate_test_cases", ["validate_spec"])
    .add_task("lint_generated_code", ["generate_test_cases"])
    .add_task("run_tests", ["lint_generated_code"])
    .add_task("collect_coverage", ["run_tests"])
    .add_task("generate_report", ["collect_coverage"])
    .set_retry_policy("fetch_openapi_spec", 2)
    .set_timeout("run_tests", 600)
    .build())

# Execute with executor
executor = WorkflowExecutor(workflow)
# ... execute tasks ...
executor.print_workflow_metrics()
```

### Reusing Workflow Patterns

```python
from src.orchestrator.workflows import get_workflow

# Get predefined REST workflow
rest_workflow = get_workflow("rest")

# Get predefined GraphQL workflow
graphql_workflow = get_workflow("graphql")

# Get predefined gRPC workflow
grpc_workflow = get_workflow("grpc")
```

## Performance Optimization

### Parallel Task Execution

```python
# Design workflow to maximize parallelization
workflow = (WorkflowBuilder("optimized_test", "rest")
    .add_task("fetch_spec")
    .add_task("fetch_schema")  # Can run parallel to fetch_spec
    .add_task("validate_spec", ["fetch_spec"])  # Depends on fetch_spec
    .add_task("analyze_schema", ["fetch_schema"])  # Depends on fetch_schema
    .add_task("generate_tests", ["validate_spec", "analyze_schema"])
    .build())
```

### Efficient Resource Usage

```python
from src.orchestrator.task_utils import TaskScheduler

async def main():
    # Limit concurrent tasks to avoid resource exhaustion
    scheduler = TaskScheduler(max_concurrent=3)
    
    # Process tasks efficiently
    for task_name, task_func in large_task_list.items():
        await scheduler.submit(task_name, task_func())
```

### Caching Task Results

```python
# Results are automatically cached in orchestrator
task_results = orchestrator.get_task_results()

# Reuse results in subsequent operations
parse_result = task_results["parse_spec"]
if parse_result.is_success():
    endpoints = parse_result.data["endpoints"]
    # Use cached endpoints without re-parsing
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: Tasks Not Executing

```python
# Check task dependencies
orchestrator = OpenClawOrchestrator("rest")
task_graph = orchestrator._build_task_graph()

for task, deps in task_graph.items():
    print(f"{task}: depends on {deps}")

# Verify dependency chain is valid
```

#### Issue: Slow Execution

```python
# Analyze performance
monitor = TaskMonitor()
slowest = monitor.get_slowest_task()
print(f"Optimize this task: {slowest[0]} ({slowest[1]:.2f}s)")

# Check task concurrency
scheduler = TaskScheduler(max_concurrent=10)  # Increase concurrency
```

#### Issue: Retry Not Working

```python
from src.orchestrator.task_utils import RetryConfig, RetryStrategy

# Verify retry configuration
config = RetryConfig(
    max_retries=5,
    strategy=RetryStrategy.EXPONENTIAL,
    initial_delay=1.0,
    max_delay=120.0
)

handler = TaskRetryHandler(config)
print(f"Retry config: max_retries={config.max_retries}, strategy={config.strategy.value}")
```

### Debug Mode

```bash
# Run with detailed output
DEBUG=1 LOG_LEVEL=DEBUG python -m src.main --protocol rest \
  --spec examples/openapi.json \
  --base-url https://petstore.swagger.io/v2 \
  --orchestrator openclaw
```

### Getting Help

For detailed information:
- See [OPENCLAW_ORCHESTRATION.md](OPENCLAW_ORCHESTRATION.md) for architecture overview
- Check logs with `LOG_LEVEL=DEBUG`
- Review task metrics with `monitor.print_summary()`
