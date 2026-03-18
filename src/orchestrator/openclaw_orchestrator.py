"""
OpenClaw-based orchestrator for AI QA Agent pipeline.
Manages the complete workflow for API testing including parsing, generation, execution, and reporting.
"""

import asyncio
from typing import Dict, Any, Literal, Optional, List
from dataclasses import dataclass
from enum import Enum

from src.parsers.base import SpecParser
from src.parsers.openapi_parser import OpenApiParser
from src.parsers.graphql_parser import GraphQLParser
from src.generators.base import TestGenerator
from src.generators.pytest_generator import PytestGenerator
from src.generators.graphql_generator import GraphQLTestGenerator
from src.executors.base import TestExecutor
from src.executors.pytest_executor import PytestExecutor
from src.executors.grpcurl_executor import GrpcurlExecutor
from src.reporters.base import Reporter
from src.reporters.allure_reporter import AllureReporter
from src.llm.base import LLMProvider
from src.llm.gemini_provider import GeminiProvider
from src.config import settings
from src.utils.logger import logger


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TaskResult:
    """Result of a task execution."""
    task_name: str
    status: TaskStatus
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def is_success(self) -> bool:
        return self.status == TaskStatus.COMPLETED

    def is_failed(self) -> bool:
        return self.status == TaskStatus.FAILED


class OpenClawOrchestrator:
    """
    OpenClaw-based orchestrator for coordinating API testing pipeline.
    Manages task execution, dependencies, and error handling.
    """

    def __init__(self, protocol: Literal["rest", "graphql", "grpc"] = "rest"):
        self.protocol = protocol
        self.llm_provider = self._create_llm_provider()
        self.reporter = AllureReporter()
        self.logger = logger
        self.task_results: Dict[str, TaskResult] = {}
        self.task_graph = self._build_task_graph()

    def _create_llm_provider(self) -> LLMProvider:
        """Create LLM provider instance."""
        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.default_model
        )

    def _build_task_graph(self) -> Dict[str, List[str]]:
        """
        Build task dependency graph.
        Returns dict where keys are task names and values are their dependencies.
        """
        if self.protocol == "rest":
            return {
                "parse_spec": [],
                "generate_tests": ["parse_spec"],
                "run_tests": ["generate_tests"],
                "generate_report": ["run_tests"],
            }
        elif self.protocol == "graphql":
            return {
                "fetch_schema": [],
                "generate_tests": ["fetch_schema"],
                "run_tests": ["generate_tests"],
                "generate_report": ["run_tests"],
            }
        elif self.protocol == "grpc":
            return {
                "run_grpc_tests": [],
                "generate_report": ["run_grpc_tests"],
            }
        else:
            raise ValueError(f"Unsupported protocol: {self.protocol}")

    async def execute_pipeline(self, spec_source: str, base_url: str, output_dir: str) -> Dict[str, Any]:
        """
        Execute the complete testing pipeline using OpenClaw orchestration.
        
        Args:
            spec_source: API spec URL/file or GraphQL endpoint
            base_url: Base URL for API requests
            output_dir: Output directory for generated tests
            
        Returns:
            Pipeline execution result
        """
        self.logger.info(f"Starting OpenClaw orchestration for protocol: {self.protocol}")
        
        try:
            # Execute tasks in dependency order
            await self._execute_tasks(spec_source, base_url, output_dir)
            
            # Check for critical failures (only tasks that prevent pipeline from continuing)
            critical_failures = [name for name, result in self.task_results.items() 
                               if result.is_failed() and name not in ['run_tests', 'run_grpc_tests', 'generate_report']]
            
            if critical_failures:
                self.logger.error(f"Pipeline failed in critical tasks: {critical_failures}")
                for task_name in critical_failures:
                    error = self.task_results[task_name].error
                    self.logger.error(f"  - {task_name}: {error}")
                # For critical failures, we still return results but mark overall failure
            
            # Return final results (even if some non-critical tasks failed)
            return self._compile_results()
            
        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}")
            # Still return compiled results even on exception
            return self._compile_results()

    async def _execute_tasks(self, spec_source: str, base_url: str, output_dir: str) -> None:
        """Execute all tasks in dependency order."""
        executed = set()
        
        while len(executed) < len(self.task_graph):
            # Find tasks ready to execute (all dependencies completed)
            ready_tasks = [
                name for name, deps in self.task_graph.items()
                if name not in executed and all(dep in executed for dep in deps)
            ]
            
            if not ready_tasks:
                # Cycle detected or all tasks executed
                break
            
            # Execute ready tasks
            for task_name in ready_tasks:
                await self._execute_task(task_name, spec_source, base_url, output_dir)
                executed.add(task_name)

    async def _execute_task(self, task_name: str, spec_source: str, base_url: str, output_dir: str) -> None:
        """Execute a single task and record result."""
        self.logger.info(f"Executing task: {task_name}")
        
        try:
            if task_name == "parse_spec":
                result = await self._task_parse_spec(spec_source)
            elif task_name == "fetch_schema":
                result = await self._task_fetch_graphql_schema(spec_source)
            elif task_name == "generate_tests":
                result = await self._task_generate_tests(base_url, output_dir)
            elif task_name == "run_tests":
                result = await self._task_run_tests(output_dir)
            elif task_name == "run_grpc_tests":
                result = await self._task_run_grpc_tests(base_url, output_dir)
            elif task_name == "generate_report":
                result = await self._task_generate_report(output_dir)
            else:
                raise ValueError(f"Unknown task: {task_name}")
            
            self.task_results[task_name] = result
            self.logger.info(f"Task {task_name} completed with status: {result.status}")
            
        except Exception as e:
            self.logger.error(f"Task {task_name} failed: {e}")
            self.task_results[task_name] = TaskResult(
                task_name=task_name,
                status=TaskStatus.FAILED,
                error=str(e)
            )

    async def _task_parse_spec(self, spec_source: str) -> TaskResult:
        """Task: Parse OpenAPI specification."""
        try:
            parser = OpenApiParser()
            endpoints = await parser.parse(spec_source)
            self.logger.info(f"Parsed {len(endpoints)} endpoints")
            
            return TaskResult(
                task_name="parse_spec",
                status=TaskStatus.COMPLETED,
                data={"endpoints": endpoints, "count": len(endpoints)},
                metadata={"spec_source": spec_source}
            )
        except Exception as e:
            return TaskResult(
                task_name="parse_spec",
                status=TaskStatus.FAILED,
                error=str(e)
            )

    async def _task_fetch_graphql_schema(self, spec_source: str) -> TaskResult:
        """Task: Fetch and parse GraphQL schema."""
        try:
            parser = GraphQLParser()
            schema = await parser.parse(spec_source)
            query_fields = len(schema.query_fields) if hasattr(schema, 'query_fields') else 0
            self.logger.info(f"Fetched GraphQL schema with {query_fields} query fields")
            
            return TaskResult(
                task_name="fetch_schema",
                status=TaskStatus.COMPLETED,
                data={"schema": schema, "query_fields": query_fields},
                metadata={"endpoint": spec_source}
            )
        except Exception as e:
            return TaskResult(
                task_name="fetch_schema",
                status=TaskStatus.FAILED,
                error=str(e)
            )

    async def _task_generate_tests(self, base_url: str, output_dir: str) -> TaskResult:
        """Task: Generate test file."""
        try:
            if self.protocol == "rest":
                endpoints_result = self.task_results.get("parse_spec")
                if not endpoints_result or not endpoints_result.is_success():
                    raise RuntimeError("Cannot generate tests: parse_spec task failed")
                
                endpoints = endpoints_result.data["endpoints"]
                generator = PytestGenerator(llm_provider=self.llm_provider)
                test_file = await generator.generate_test_file(
                    endpoints=endpoints,
                    output_path=f"{output_dir}/test_api.py",
                    base_url=base_url
                )
                
                return TaskResult(
                    task_name="generate_tests",
                    status=TaskStatus.COMPLETED,
                    data={"test_file": test_file},
                    metadata={"base_url": base_url, "endpoint_count": len(endpoints)}
                )
                
            elif self.protocol == "graphql":
                schema_result = self.task_results.get("fetch_schema")
                if not schema_result or not schema_result.is_success():
                    raise RuntimeError("Cannot generate tests: fetch_schema task failed")
                
                schema = schema_result.data["schema"]
                generator = GraphQLTestGenerator(llm_provider=self.llm_provider)
                test_file = await generator.generate_test_file(
                    schema=schema,
                    output_path=f"{output_dir}/test_graphql.py",
                    endpoint_url=base_url
                )
                
                return TaskResult(
                    task_name="generate_tests",
                    status=TaskStatus.COMPLETED,
                    data={"test_file": test_file},
                    metadata={"endpoint_url": base_url}
                )
                
        except Exception as e:
            return TaskResult(
                task_name="generate_tests",
                status=TaskStatus.FAILED,
                error=str(e)
            )

    async def _task_run_tests(self, output_dir: str) -> TaskResult:
        """Task: Run generated tests."""
        try:
            generate_result = self.task_results.get("generate_tests")
            if not generate_result or not generate_result.is_success():
                raise RuntimeError("Cannot run tests: generate_tests task failed")
            
            test_file = generate_result.data["test_file"]
            executor = PytestExecutor()
            results = await executor.run_tests(
                test_path=test_file,
                report_dir=settings.reports_dir
            )
            
            # Mark as COMPLETED even if tests failed
            # The test success/failure is in the data, not the task status
            success = results.get("success", False)
            
            if success:
                self.logger.info(f"✓ All tests passed")
            else:
                self.logger.warning(f"⚠ Some tests failed or had errors: {results.get('returncode', 'unknown')}")
                if results.get('stderr'):
                    self.logger.warning(f"Errors: {results.get('stderr')[:500]}")
            
            return TaskResult(
                task_name="run_tests",
                status=TaskStatus.COMPLETED,  # Always mark as completed, not failed
                data=results,
                metadata={
                    "test_file": test_file,
                    "tests_passed": success,
                    "return_code": results.get("returncode", -1)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Test execution error: {e}")
            return TaskResult(
                task_name="run_tests",
                status=TaskStatus.COMPLETED,  # Mark as completed even with error
                data={"success": False, "error": str(e)},
                error=str(e),
                metadata={"tests_passed": False}
            )

    async def _task_run_grpc_tests(self, base_url: str, output_dir: str) -> TaskResult:
        """Task: Run gRPC tests."""
        try:
            executor = GrpcurlExecutor(base_url, reports_dir=settings.reports_dir)
            results = await executor.run_tests()
            
            # Mark as COMPLETED even if tests failed (consistent with REST/GraphQL)
            # The test success/failure is in the data, not the task status
            success = results.get("success", False)
            
            if success:
                self.logger.info(f"✓ gRPC tests passed")
            else:
                self.logger.warning(f"⚠ gRPC tests failed or had errors")
                if results.get('stderr'):
                    self.logger.warning(f"Errors: {results.get('stderr')[:500]}")
            
            return TaskResult(
                task_name="run_grpc_tests",
                status=TaskStatus.COMPLETED,  # Always mark as completed, not failed
                data=results,
                metadata={
                    "server": base_url,
                    "tests_passed": success,
                    "return_code": results.get("returncode", -1)
                }
            )
            
        except Exception as e:
            self.logger.error(f"gRPC test execution error: {e}")
            return TaskResult(
                task_name="run_grpc_tests",
                status=TaskStatus.COMPLETED,  # Mark as completed even with error
                data={"success": False, "error": str(e)},
                error=str(e),
                metadata={"tests_passed": False}
            )

    async def _task_generate_report(self, output_dir: str) -> TaskResult:
        """Task: Generate test report."""
        try:
            if self.protocol == "grpc":
                # gRPC doesn't use pytest, so no report generation
                self.logger.info("Skipping report generation for gRPC")
                return TaskResult(
                    task_name="generate_report",
                    status=TaskStatus.SKIPPED,
                    data=None,
                    metadata={"reason": "gRPC protocol"}
                )
            
            tests_result = self.task_results.get("run_tests")
            if not tests_result:
                return TaskResult(
                    task_name="generate_report",
                    status=TaskStatus.SKIPPED,
                    metadata={"reason": "No test results"}
                )
            
            results = tests_result.data
            report_url = await self.reporter.generate_report(
                results=results,
                output_dir=settings.reports_dir
            )
            
            return TaskResult(
                task_name="generate_report",
                status=TaskStatus.COMPLETED,
                data={"report_url": report_url},
                metadata={"output_dir": settings.reports_dir}
            )
            
        except Exception as e:
            self.logger.warning(f"Report generation failed: {e}")
            return TaskResult(
                task_name="generate_report",
                status=TaskStatus.FAILED,
                error=str(e)
            )

    def _compile_results(self) -> Dict[str, Any]:
        """Compile final pipeline results."""
        test_file = None
        results = None
        report_url = None
        overall_success = True
        
        if "generate_tests" in self.task_results:
            gen_result = self.task_results["generate_tests"]
            if gen_result.is_success():
                test_file = gen_result.data.get("test_file")
            else:
                overall_success = False
        
        if "run_tests" in self.task_results:
            run_result = self.task_results["run_tests"]
            # Always get results, even if tests failed
            results = run_result.data
            # Check if tests actually passed
            if not run_result.data.get("success", False):
                overall_success = False
        
        if "run_grpc_tests" in self.task_results:
            grpc_result = self.task_results["run_grpc_tests"]
            results = grpc_result.data
            if not grpc_result.data.get("success", False):
                overall_success = False
        
        if "generate_report" in self.task_results:
            report_result = self.task_results["generate_report"]
            if report_result.is_success() or report_result.data:
                report_url = report_result.data.get("report_url") if report_result.data else None
        
        return {
            "test_file": test_file,
            "results": results,
            "report": report_url,
            "protocol": self.protocol,
            "overall_success": overall_success,
            "task_results": {name: {
                "status": result.status.value,
                "error": result.error,
                "metadata": result.metadata
            } for name, result in self.task_results.items()}
        }

    def get_task_results(self) -> Dict[str, TaskResult]:
        """Get all task execution results."""
        return self.task_results

    def print_execution_summary(self) -> None:
        """Print execution summary."""
        self.logger.info("=" * 60)
        self.logger.info("OpenClaw Orchestrator Execution Summary")
        self.logger.info("=" * 60)
        
        for task_name, result in self.task_results.items():
            status_str = f"[{result.status.value.upper()}]"
            message = f"  {task_name}: {status_str}"
            
            if result.error:
                message += f" - Error: {result.error}"
            if result.metadata:
                message += f" - {result.metadata}"
            
            self.logger.info(message)
        
        self.logger.info("=" * 60)
