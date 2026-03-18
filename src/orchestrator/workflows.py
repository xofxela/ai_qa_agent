"""
Advanced workflow definitions for OpenClaw orchestration.

This module provides reusable workflow patterns and configurations
for complex testing scenarios.
"""

from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
from src.orchestrator.openclaw_orchestrator import TaskResult, TaskStatus


@dataclass
class WorkflowConfig:
    """Configuration for a workflow."""
    name: str
    protocol: str
    description: str
    tasks: Dict[str, List[str]] = field(default_factory=dict)  # task_name -> dependencies
    retry_policy: Optional[Dict[str, int]] = None  # task_name -> max_retries
    timeout_policy: Optional[Dict[str, int]] = None  # task_name -> timeout_seconds
    parallel_tasks: Optional[List[List[str]]] = None  # Groups of tasks to run in parallel


# Predefined Workflows

# REST API Testing Workflow
REST_WORKFLOW = WorkflowConfig(
    name="rest_api_testing",
    protocol="rest",
    description="Complete REST API testing pipeline",
    tasks={
        "parse_spec": [],
        "validate_spec": ["parse_spec"],
        "generate_tests": ["validate_spec"],
        "lint_tests": ["generate_tests"],
        "run_tests": ["lint_tests"],
        "generate_report": ["run_tests"],
        "publish_report": ["generate_report"],
    },
    retry_policy={
        "parse_spec": 2,
        "run_tests": 1,
    },
    timeout_policy={
        "parse_spec": 30,
        "run_tests": 300,
        "generate_report": 60,
    },
    parallel_tasks=[
        ["parse_spec"],  # Get spec
        ["validate_spec", "lint_tests"],  # Can run in parallel after dependencies
    ]
)

# GraphQL Testing Workflow
GRAPHQL_WORKFLOW = WorkflowConfig(
    name="graphql_testing",
    protocol="graphql",
    description="Complete GraphQL testing pipeline",
    tasks={
        "fetch_schema": [],
        "validate_schema": ["fetch_schema"],
        "generate_tests": ["validate_schema"],
        "run_tests": ["generate_tests"],
        "generate_report": ["run_tests"],
    },
    retry_policy={
        "fetch_schema": 3,
        "run_tests": 1,
    },
    timeout_policy={
        "fetch_schema": 60,
        "run_tests": 300,
    }
)

# gRPC Testing Workflow
GRPC_WORKFLOW = WorkflowConfig(
    name="grpc_testing",
    protocol="grpc",
    description="Complete gRPC testing pipeline",
    tasks={
        "run_grpc_tests": [],
        "generate_report": ["run_grpc_tests"],
    },
    retry_policy={
        "run_grpc_tests": 2,
    },
    timeout_policy={
        "run_grpc_tests": 300,
    }
)

# Advanced Multi-Protocol Workflow
MULTI_PROTOCOL_WORKFLOW = WorkflowConfig(
    name="multi_protocol_testing",
    protocol="multi",
    description="Test multiple API protocols in sequence",
    tasks={
        # REST API phase
        "parse_rest_spec": [],
        "generate_rest_tests": ["parse_rest_spec"],
        "run_rest_tests": ["generate_rest_tests"],
        
        # GraphQL phase (can overlap with REST runs)
        "fetch_graphql_schema": [],
        "generate_graphql_tests": ["fetch_graphql_schema"],
        "run_graphql_tests": ["generate_graphql_tests"],
        
        # gRPC phase
        "run_grpc_tests": [],
        
        # Aggregation phase
        "aggregate_results": ["run_rest_tests", "run_graphql_tests", "run_grpc_tests"],
        "generate_combined_report": ["aggregate_results"],
    },
    parallel_tasks=[
        ["parse_rest_spec", "fetch_graphql_schema", "run_grpc_tests"],
        ["generate_rest_tests", "generate_graphql_tests"],
        ["run_rest_tests", "run_graphql_tests"],
    ]
)


@dataclass
class TaskMetrics:
    """Metrics for a task execution."""
    task_name: str
    start_time: float
    end_time: float
    duration_seconds: float
    status: TaskStatus
    retry_count: int = 0
    
    def get_duration_ms(self) -> int:
        """Get duration in milliseconds."""
        return int(self.duration_seconds * 1000)


class WorkflowExecutor:
    """Executes workflows with advanced orchestration features."""
    
    def __init__(self, workflow: WorkflowConfig):
        self.workflow = workflow
        self.task_metrics: Dict[str, TaskMetrics] = {}
        self.task_results: Dict[str, TaskResult] = {}
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get summary of workflow execution."""
        total_tasks = len(self.workflow.tasks)
        completed_tasks = sum(1 for r in self.task_results.values() if r.status == TaskStatus.COMPLETED)
        failed_tasks = sum(1 for r in self.task_results.values() if r.status == TaskStatus.FAILED)
        skipped_tasks = sum(1 for r in self.task_results.values() if r.status == TaskStatus.SKIPPED)
        
        total_duration = sum(m.duration_seconds for m in self.task_metrics.values())
        
        return {
            "workflow_name": self.workflow.name,
            "protocol": self.workflow.protocol,
            "total_tasks": total_tasks,
            "completed": completed_tasks,
            "failed": failed_tasks,
            "skipped": skipped_tasks,
            "success_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "total_duration_seconds": total_duration,
        }
    
    def print_workflow_metrics(self) -> None:
        """Print detailed workflow metrics."""
        summary = self.get_workflow_summary()
        
        print("\n" + "=" * 70)
        print(f"Workflow: {summary['workflow_name']}")
        print(f"Protocol: {summary['protocol']}")
        print("=" * 70)
        print(f"Total Tasks: {summary['total_tasks']}")
        print(f"  ✓ Completed: {summary['completed']}")
        print(f"  ✗ Failed: {summary['failed']}")
        print(f"  ⊘ Skipped: {summary['skipped']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Total Duration: {summary['total_duration_seconds']:.2f}s")
        print("=" * 70)
        
        if self.task_metrics:
            print("\nTask Metrics:")
            print(f"{'Task Name':<30} {'Status':<12} {'Duration (ms)':<15}")
            print("-" * 60)
            for task_name, metrics in sorted(self.task_metrics.items()):
                print(f"{task_name:<30} {metrics.status.value:<12} {metrics.get_duration_ms():<15}")
        
        print("=" * 70 + "\n")


class WorkflowBuilder:
    """Builder for creating custom workflows."""
    
    def __init__(self, name: str, protocol: str):
        self.config = WorkflowConfig(
            name=name,
            protocol=protocol,
            description=f"Custom workflow for {protocol}"
        )
    
    def add_task(self, task_name: str, dependencies: Optional[List[str]] = None) -> "WorkflowBuilder":
        """Add task to workflow."""
        self.config.tasks[task_name] = dependencies or []
        return self
    
    def set_retry_policy(self, task_name: str, max_retries: int) -> "WorkflowBuilder":
        """Set retry policy for task."""
        if self.config.retry_policy is None:
            self.config.retry_policy = {}
        self.config.retry_policy[task_name] = max_retries
        return self
    
    def set_timeout(self, task_name: str, timeout_seconds: int) -> "WorkflowBuilder":
        """Set timeout for task."""
        if self.config.timeout_policy is None:
            self.config.timeout_policy = {}
        self.config.timeout_policy[task_name] = timeout_seconds
        return self
    
    def build(self) -> WorkflowConfig:
        """Build workflow configuration."""
        return self.config


def get_workflow(protocol: str) -> WorkflowConfig:
    """Get predefined workflow for protocol."""
    if protocol == "rest":
        return REST_WORKFLOW
    elif protocol == "graphql":
        return GRAPHQL_WORKFLOW
    elif protocol == "grpc":
        return GRPC_WORKFLOW
    else:
        raise ValueError(f"Unknown protocol: {protocol}")


def create_custom_workflow(protocol: str) -> WorkflowBuilder:
    """Create custom workflow using builder pattern."""
    return WorkflowBuilder(f"custom_{protocol}", protocol)
