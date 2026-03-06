from typing import Dict, Any, Literal, Optional
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

class QAAgent:
    def __init__(self, protocol: Literal["rest", "graphql", "grpc"] = "rest"):
        self.protocol = protocol
        self.llm_provider = self._create_llm_provider()
        self.parser = self._create_parser()
        self.generator = self._create_generator()
        # Для REST и GraphQL используем pytest executor
        self.executor = PytestExecutor() if protocol != "grpc" else None
        self.reporter = AllureReporter()
        self.logger = logger

    def _create_llm_provider(self) -> LLMProvider:
        from src.llm.gemini_provider import GeminiProvider
        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.default_model
        )

    def _create_parser(self) -> Optional[SpecParser]:
        if self.protocol == "rest":
            return OpenApiParser()
        elif self.protocol == "graphql":
            return GraphQLParser()
        elif self.protocol == "grpc":
            # Для gRPC парсер не используется
            return None
        else:
            raise ValueError(f"Unsupported protocol: {self.protocol}")

    def _create_generator(self) -> Optional[TestGenerator]:
        if self.protocol == "rest":
            return PytestGenerator(llm_provider=self.llm_provider)
        elif self.protocol == "graphql":
            return GraphQLTestGenerator(llm_provider=self.llm_provider)
        elif self.protocol == "grpc":
            # Для gRPC генератор не используется
            return None
        else:
            raise ValueError(f"Unsupported protocol: {self.protocol}")

    async def run_pipeline(self, spec_source: str, base_url: str, output_dir: str) -> Dict[str, Any]:
        self.logger.info(f"Starting pipeline for protocol {self.protocol}, spec: {spec_source}")

        if self.protocol == "rest":
            if self.parser is None:
                raise RuntimeError("Parser not initialized for REST")
            endpoints = await self.parser.parse(spec_source)
            self.logger.info(f"Parsed {len(endpoints)} REST endpoints")
            if self.generator is None:
                raise RuntimeError("Generator not initialized for REST")
            test_file = await self.generator.generate_test_file(
                endpoints=endpoints,
                output_path=f"{output_dir}/test_{self.protocol}.py",
                base_url=base_url
            )
            results = await self.executor.run_tests(
                test_path=test_file,
                report_dir=settings.reports_dir
            )
        elif self.protocol == "graphql":
            if self.parser is None:
                raise RuntimeError("Parser not initialized for GraphQL")
            schema = await self.parser.parse(spec_source)
            self.logger.info(f"Parsed {len(schema.query_fields)} GraphQL queries")
            if self.generator is None:
                raise RuntimeError("Generator not initialized for GraphQL")
            test_file = await self.generator.generate_test_file(
                schema=schema,
                output_path=f"{output_dir}/test_{self.protocol}.py",
                endpoint_url=base_url
            )
            results = await self.executor.run_tests(
                test_path=test_file,
                report_dir=settings.reports_dir
            )
        elif self.protocol == "grpc":
            executor = GrpcurlExecutor(base_url, reports_dir=settings.reports_dir)
            results = await executor.run_tests()
            # Для gRPC у нас нет test_file и отчёт генерируется внутри executor
            return {
                "test_file": None,
                "results": results,
                "report": None,  # Можно будет добавить генерацию отчёта позже
                "protocol": self.protocol
            }
        else:
            raise ValueError(f"Unsupported protocol: {self.protocol}")

        report_url = None
        if results:
            report_url = await self.reporter.generate_report(
                results=results,
                output_dir=settings.reports_dir
            )

        return {
            "test_file": test_file if self.protocol != "grpc" else None,
            "results": results,
            "report": report_url,
            "protocol": self.protocol
        }