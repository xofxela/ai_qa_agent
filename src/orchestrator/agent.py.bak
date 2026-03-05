import os
from typing import Dict, Any, Optional
from src.parsers.base import SpecParser
from src.generators.base import TestGenerator
from src.executors.base import TestExecutor
from src.reporters.base import Reporter
from src.llm.base import LLMProvider
from src.utils.logger import logger

class QAAgent:
    def __init__(self,
                 spec_parser: SpecParser,
                 test_generator: TestGenerator,
                 test_executor: TestExecutor,
                 reporter: Reporter,
                 llm_provider: LLMProvider):
        self.spec_parser = spec_parser
        self.test_generator = test_generator
        self.test_executor = test_executor
        self.reporter = reporter
        self.llm = llm_provider
    
    async def run_pipeline(self,
                          spec_source: str,
                          base_url: str,
                          output_dir: str = "generated_tests",
                          report_dir: str = "reports") -> Dict[str, Any]:
        """Run full pipeline: parse spec, generate tests, execute, report."""
        logger.info(f"Starting pipeline for spec: {spec_source}")
        
        # Step 1: Parse specification
        endpoints = await self.spec_parser.parse(spec_source)
        logger.info(f"Parsed {len(endpoints)} endpoints")
        
        # Step 2: Generate test file
        test_filename = f"test_{os.path.basename(spec_source).split('.')[0]}.py"
        test_path = os.path.join(output_dir, test_filename)
        test_path = await self.test_generator.generate_test_file(
            endpoints=endpoints,
            output_path=test_path,
            base_url=base_url
        )
        
        # Step 3: Execute tests
        results = await self.test_executor.run_tests(
            test_path=test_path,
            report_dir=report_dir
        )
        
        # Step 4: Generate report
        report_url = await self.reporter.generate_report(
            results=results,
            output_dir=report_dir
        )
        
        return {
            "endpoints_count": len(endpoints),
            "test_file": test_path,
            "execution_results": results,
            "report_url": report_url
        }
