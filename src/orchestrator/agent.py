from typing import Dict, Any, Literal
from src.parsers.base import SpecParser
from src.parsers.openapi_parser import OpenApiParser
from src.parsers.graphql_parser import GraphQLParser
from src.generators.base import TestGenerator
from src.generators.pytest_generator import PytestGenerator
from src.generators.graphql_generator import GraphQLTestGenerator
from src.executors.base import TestExecutor
from src.executors.pytest_executor import PytestExecutor
from src.reporters.base import Reporter
from src.reporters.allure_reporter import AllureReporter
from src.llm.base import LLMProvider
from src.llm.gemini_provider import GeminiProvider
from src.config import settings
from src.utils.logger import logger

class QAAgent:
    def __init__(self, protocol: Literal["rest", "graphql"] = "rest"):
        self.protocol = protocol
        self.llm_provider = self._create_llm_provider()
        self.parser = self._create_parser()
        self.generator = self._create_generator()
        self.executor = PytestExecutor()  # для всех протоколов пока один
        self.reporter = AllureReporter()
        self.logger = logger

    def _create_llm_provider(self) -> LLMProvider:
        # Используем Gemini как основной
        from src.llm.gemini_provider import GeminiProvider
        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.default_model
        )

    def _create_parser(self) -> SpecParser:
        if self.protocol == "rest":
            return OpenApiParser()
        elif self.protocol == "graphql":
            return GraphQLParser()
        else:
            raise ValueError(f"Unsupported protocol: {self.protocol}")

    def _create_generator(self) -> TestGenerator:
        if self.protocol == "rest":
            return PytestGenerator(llm_provider=self.llm_provider)
        elif self.protocol == "graphql":
            return GraphQLTestGenerator(llm_provider=self.llm_provider)
        else:
            raise ValueError(f"Unsupported protocol: {self.protocol}")

    async def run_pipeline(self, spec_source: str, base_url: str, output_dir: str) -> Dict[str, Any]:
        """Запускает полный пайплайн: парсинг -> генерация -> выполнение -> отчёт"""
        self.logger.info(f"Starting pipeline for protocol {self.protocol}, spec: {spec_source}")

        # Парсинг спецификации
        if self.protocol == "rest":
            endpoints = await self.parser.parse(spec_source)
            self.logger.info(f"Parsed {len(endpoints)} REST endpoints")
        else:  # graphql
            schema = await self.parser.parse(spec_source)
            self.logger.info(f"Parsed {len(schema.query_fields)} GraphQL queries")
            # Для единообразия передаём схему в генератор напрямую

        # Генерация тестов
        if self.protocol == "rest":
            test_file = await self.generator.generate_test_file(
                endpoints=endpoints,
                output_path=f"{output_dir}/test_{self.protocol}.py",
                base_url=base_url
            )
        else:
            test_file = await self.generator.generate_test_file(
                schema=schema,
                output_path=f"{output_dir}/test_{self.protocol}.py",
                endpoint_url=base_url
            )

        # Выполнение тестов
        results = await self.executor.run_tests(
            test_path=test_file,
            report_dir=settings.reports_dir
        )

        # Генерация отчёта (если есть результаты)
        report_url = None
        if results:
            report_url = await self.reporter.generate_report(
                results=results,
                output_dir=settings.reports_dir
            )

        return {
            "test_file": test_file,
            "results": results,
            "report": report_url,
            "protocol": self.protocol
        }
