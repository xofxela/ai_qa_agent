"""
Example scripts demonstrating OpenClaw orchestrator usage.

These examples show various ways to use the OpenClaw orchestration engine
for API testing with different configurations and workflows.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.orchestrator.openclaw_orchestrator import OpenClawOrchestrator
from src.orchestrator.workflows import get_workflow, WorkflowBuilder, WorkflowExecutor
from src.orchestrator.task_utils import (
    TaskMonitor,
    TaskRetryHandler,
    RetryConfig,
    RetryStrategy,
    TaskScheduler,
)
from src.utils.logger import logger


async def example_1_basic_rest_testing():
    """
    Example 1: Basic REST API testing with OpenClaw orchestrator.
    
    This is the simplest example showing how to use the orchestrator
    for testing a REST API using an OpenAPI specification.
    """
    logger.info("\n" + "=" * 70)
    logger.info("Example 1: Basic REST API Testing")
    logger.info("=" * 70)
    
    orchestrator = OpenClawOrchestrator(protocol="rest")
    
    try:
        result = await orchestrator.execute_pipeline(
            spec_source="examples/openapi.json",
            base_url="https://petstore.swagger.io/v2",
            output_dir="generated_tests"
        )
        
        orchestrator.print_execution_summary()
        
        logger.info("\nFinal Results:")
        logger.info(f"  Test file: {result['test_file']}")
        logger.info(f"  Test results: {result['results'].get('success', False)}")
        if result.get('report'):
            logger.info(f"  Report: {result['report']}")
            
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")


async def example_2_detailed_task_inspection():
    """
    Example 2: Detailed inspection of task execution.
    
    Shows how to inspect individual task results and understand
    what each task accomplished.
    """
    logger.info("\n" + "=" * 70)
    logger.info("Example 2: Detailed Task Inspection")
    logger.info("=" * 70)
    
    orchestrator = OpenClawOrchestrator(protocol="graphql")
    
    try:
        result = await orchestrator.execute_pipeline(
            spec_source="https://spacex-production.up.railway.app/",
            base_url="https://spacex-production.up.railway.app/",
            output_dir="generated_tests"
        )
        
        # Get detailed task results
        task_results = orchestrator.get_task_results()
        
        logger.info("\nDetailed Task Execution Report:")
        logger.info("-" * 70)
        
        for task_name, task_result in task_results.items():
            logger.info(f"\n📋 Task: {task_name}")
            logger.info(f"   Status: {task_result.status.value}")
            
            if task_result.status.value == "completed":
                logger.info(f"   ✓ Completed successfully")
                
            elif task_result.status.value == "failed":
                logger.info(f"   ✗ Failed: {task_result.error}")
                
            elif task_result.status.value == "skipped":
                logger.info(f"   ⊘ Skipped: {task_result.metadata.get('reason', 'N/A')}")
            
            if task_result.metadata:
                logger.info(f"   Metadata:")
                for key, value in task_result.metadata.items():
                    logger.info(f"     - {key}: {value}")
        
        logger.info("\n" + "-" * 70)
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")


async def example_3_task_monitoring():
    """
    Example 3: Task execution monitoring and performance metrics.
    
    Shows how to monitor task execution and collect performance metrics.
    """
    logger.info("\n" + "=" * 70)
    logger.info("Example 3: Task Monitoring and Performance Metrics")
    logger.info("=" * 70)
    
    monitor = TaskMonitor()
    
    # Simulate task execution with monitoring
    tasks = [
        ("parse_spec", 0.5),
        ("generate_tests", 2.5),
        ("run_tests", 5.0),
        ("generate_report", 1.0),
    ]
    
    for task_name, duration in tasks:
        monitor.record_start(task_name)
        await asyncio.sleep(duration)
        monitor.record_end(task_name, "completed")
    
    # Get and display metrics
    logger.info("\n📊 Execution Metrics:")
    logger.info("-" * 70)
    
    all_metrics = monitor.get_all_metrics()
    total_duration = 0
    
    for task_name, metrics in sorted(all_metrics.items()):
        duration = metrics.get("duration", 0)
        total_duration += duration
        logger.info(f"  {task_name:<30} {duration:>8.2f}s")
    
    logger.info("-" * 70)
    logger.info(f"  {'TOTAL':<30} {total_duration:>8.2f}s")
    
    # Get slowest task
    slowest = monitor.get_slowest_task()
    if slowest:
        logger.info(f"\n⚠️  Slowest task: {slowest[0]} ({slowest[1]:.2f}s)")
    
    monitor.print_summary()


async def example_4_retry_strategy():
    """
    Example 4: Using retry strategies for resilience.
    
    Shows how to configure and use different retry strategies
    for handling transient failures.
    """
    logger.info("\n" + "=" * 70)
    logger.info("Example 4: Retry Strategy Configuration")
    logger.info("=" * 70)
    
    # Define a task that might fail
    attempt_count = 0
    
    async def unreliable_task():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise ConnectionError(f"Attempt {attempt_count}: Connection failed")
        return "Success!"
    
    # Configure exponential backoff retry
    retry_config = RetryConfig(
        max_retries=5,
        strategy=RetryStrategy.EXPONENTIAL,
        initial_delay=0.1,
        max_delay=1.0,
        backoff_factor=2.0
    )
    
    retry_handler = TaskRetryHandler(retry_config)
    
    logger.info("\n⚙️  Retry Configuration:")
    logger.info(f"  Strategy: {retry_config.strategy.value}")
    logger.info(f"  Max retries: {retry_config.max_retries}")
    logger.info(f"  Initial delay: {retry_config.initial_delay}s")
    logger.info(f"  Max delay: {retry_config.max_delay}s")
    
    try:
        result = await retry_handler.execute_with_retry(
            task_name="unreliable_api_call",
            task_func=unreliable_task
        )
        
        retries = retry_handler.get_retry_count("unreliable_api_call")
        logger.info(f"\n✓ Task succeeded after {retries} retries")
        logger.info(f"  Result: {result}")
        
    except Exception as e:
        logger.error(f"Task failed after max retries: {e}")


async def example_5_task_scheduling():
    """
    Example 5: Task scheduling with concurrency control.
    
    Shows how to schedule multiple tasks concurrently while
    controlling resource usage.
    """
    logger.info("\n" + "=" * 70)
    logger.info("Example 5: Task Scheduling and Concurrency")
    logger.info("=" * 70)
    
    async def sample_task(task_id: int, duration: float):
        """Sample async task."""
        await asyncio.sleep(duration)
        return f"Task {task_id} completed"
    
    # Create scheduler with max 3 concurrent tasks
    scheduler = TaskScheduler(max_concurrent=3)
    
    logger.info("\n⚙️  Scheduler Configuration:")
    logger.info(f"  Max concurrent tasks: {scheduler.max_concurrent}")
    
    # Submit tasks
    logger.info("\n📝 Submitting 5 tasks...")
    start_time = asyncio.get_event_loop().time()
    
    for i in range(5):
        duration = (i % 2) + 0.5
        await scheduler.submit(f"task_{i}", sample_task(i, duration))
    
    end_time = asyncio.get_event_loop().time()
    total_time = end_time - start_time
    
    logger.info(f"\n✓ All tasks completed in {total_time:.2f}s")
    logger.info(f"  Total tasks completed: {scheduler.get_completed_count()}")


async def example_6_custom_workflow():
    """
    Example 6: Creating and using custom workflows.
    
    Shows how to define custom workflows with specific task
    dependencies and retry policies.
    """
    logger.info("\n" + "=" * 70)
    logger.info("Example 6: Custom Workflow Definition")
    logger.info("=" * 70)
    
    # Create custom workflow
    workflow = (WorkflowBuilder("custom_rest_testing", "rest")
        .add_task("fetch_spec")
        .add_task("validate_spec", ["fetch_spec"])
        .add_task("generate_tests", ["validate_spec"])
        .add_task("lint_tests", ["generate_tests"])
        .add_task("run_tests", ["lint_tests"])
        .add_task("collect_metrics", ["run_tests"])
        .add_task("generate_report", ["collect_metrics"])
        .set_retry_policy("fetch_spec", max_retries=3)
        .set_retry_policy("run_tests", max_retries=2)
        .set_timeout("fetch_spec", timeout_seconds=30)
        .set_timeout("run_tests", timeout_seconds=300)
        .build())
    
    logger.info("\n📋 Workflow Configuration:")
    logger.info(f"  Name: {workflow.name}")
    logger.info(f"  Protocol: {workflow.protocol}")
    logger.info(f"  Tasks: {len(workflow.tasks)}")
    
    logger.info("\n🔗 Task Dependencies:")
    for task_name, dependencies in workflow.tasks.items():
        deps_str = " → ".join(dependencies) if dependencies else "None"
        logger.info(f"  {task_name}: [{deps_str}]")
    
    if workflow.retry_policy:
        logger.info("\n🔄 Retry Policies:")
        for task_name, max_retries in workflow.retry_policy.items():
            logger.info(f"  {task_name}: {max_retries} retries")
    
    if workflow.timeout_policy:
        logger.info("\n⏱️  Timeout Policies:")
        for task_name, timeout in workflow.timeout_policy.items():
            logger.info(f"  {task_name}: {timeout}s")


async def example_7_multi_protocol():
    """
    Example 7: Testing multiple API protocols.
    
    Shows how to test different API types (REST, GraphQL) in sequence.
    """
    logger.info("\n" + "=" * 70)
    logger.info("Example 7: Multi-Protocol API Testing")
    logger.info("=" * 70)
    
    protocols = [
        ("rest", "examples/openapi.json", "https://petstore.swagger.io/v2"),
        ("graphql", "https://spacex-production.up.railway.app/", "https://spacex-production.up.railway.app/"),
    ]
    
    results = {}
    
    for protocol, spec_source, base_url in protocols:
        logger.info(f"\n🧪 Testing {protocol.upper()} protocol...")
        
        orchestrator = OpenClawOrchestrator(protocol=protocol)
        
        try:
            result = await orchestrator.execute_pipeline(
                spec_source=spec_source,
                base_url=base_url,
                output_dir=f"generated_tests_{protocol}"
            )
            
            results[protocol] = {
                "success": result.get("results", {}).get("success", False),
                "test_file": result.get("test_file"),
                "report": result.get("report"),
            }
            
            logger.info(f"✓ {protocol.upper()} testing completed")
            
        except Exception as e:
            logger.error(f"✗ {protocol.upper()} testing failed: {e}")
            results[protocol] = {"success": False, "error": str(e)}
    
    logger.info("\n" + "=" * 70)
    logger.info("Multi-Protocol Test Summary:")
    logger.info("-" * 70)
    
    for protocol, result in results.items():
        status = "✓" if result.get("success") else "✗"
        logger.info(f"  {status} {protocol.upper()}: {result}")


async def main():
    """Run all examples."""
    examples = [
        ("1", "Basic REST Testing", example_1_basic_rest_testing),
        ("2", "Detailed Task Inspection", example_2_detailed_task_inspection),
        ("3", "Task Monitoring", example_3_task_monitoring),
        ("4", "Retry Strategy", example_4_retry_strategy),
        ("5", "Task Scheduling", example_5_task_scheduling),
        ("6", "Custom Workflow", example_6_custom_workflow),
        ("7", "Multi-Protocol Testing", example_7_multi_protocol),
    ]
    
    if len(sys.argv) > 1:
        # Run specific example
        example_num = sys.argv[1]
        for num, name, func in examples:
            if num == example_num:
                await func()
                return
        logger.error(f"Unknown example: {example_num}")
    else:
        # Show menu
        logger.info("\nAvailable OpenClaw Examples:")
        for num, name, _ in examples:
            logger.info(f"  {num}. {name}")
        
        logger.info("\nRun examples with:")
        logger.info("  python examples/openclaw_examples.py <number>")
        logger.info("\nExample:")
        logger.info("  python examples/openclaw_examples.py 1")


if __name__ == "__main__":
    asyncio.run(main())
