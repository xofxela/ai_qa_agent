import asyncio
import argparse
import sys
from src.config import settings
from src.llm.gemini_provider import GeminiProvider
from src.parsers.openapi_parser import OpenApiParser
from src.generators.pytest_generator import PytestGenerator
from src.executors.pytest_executor import PytestExecutor
from src.reporters.allure_reporter import AllureReporter
from src.orchestrator.agent import QAAgent
from src.utils.logger import logger

async def main():
    parser = argparse.ArgumentParser(description="AI QA Agent")
    parser.add_argument("--spec", required=True, help="URL or path to OpenAPI spec (JSON)")
    parser.add_argument("--base-url", default=settings.default_base_url, help="Base URL for API (default from config)")
    parser.add_argument("--output-dir", default=settings.tests_output_dir, help="Directory to store generated tests")
    parser.add_argument("--report-dir", default=settings.reports_dir, help="Directory to store Allure reports")
    args = parser.parse_args()
    
    # Initialize components
    try:
        llm = GeminiProvider()
    except ValueError as e:
        logger.error(f"Failed to initialize LLM: {e}")
        logger.error("Please set GEMINI_API_KEY in .env file")
        sys.exit(1)
    
    agent = QAAgent(
        spec_parser=OpenApiParser(),
        test_generator=PytestGenerator(llm_provider=llm),
        test_executor=PytestExecutor(),
        reporter=AllureReporter(),
        llm_provider=llm
    )
    
    # Run pipeline
    result = await agent.run_pipeline(
        spec_source=args.spec,
        base_url=args.base_url,
        output_dir=args.output_dir,
        report_dir=args.report_dir
    )
    
    # Print summary
    print("\n" + "="*50)
    print("AI QA Agent - Pipeline Summary")
    print("="*50)
    print(f"Endpoints parsed: {result['endpoints_count']}")
    print(f"Test file: {result['test_file']}")
    print(f"Execution success: {result['execution_results'].get('success', False)}")
    if result['execution_results'].get('returncode') is not None:
        print(f"Pytest return code: {result['execution_results']['returncode']}")
    if result['report_url']:
        print(f"Allure report: {result['report_url']}")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
