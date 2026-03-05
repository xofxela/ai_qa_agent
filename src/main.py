import asyncio
import argparse
from src.config import settings
from src.orchestrator.agent import QAAgent
from src.utils.logger import logger

async def main():
    parser = argparse.ArgumentParser(description="AI QA Agent")
    parser.add_argument("--protocol", choices=["rest", "graphql"], default="rest",
                        help="API protocol to test")
    parser.add_argument("--spec", required=True,
                        help="OpenAPI spec URL/file (for REST) or GraphQL endpoint URL (for GraphQL)")
    parser.add_argument("--base-url", default=settings.default_base_url,
                        help="Base URL for API requests (for REST) or GraphQL endpoint (for GraphQL)")
    parser.add_argument("--output", default=settings.tests_output_dir,
                        help="Output directory for generated tests")
    args = parser.parse_args()

    logger.info(f"Starting AI QA Agent with protocol: {args.protocol}")
    logger.info(f"Spec: {args.spec}")
    logger.info(f"Base URL: {args.base_url}")

    agent = QAAgent(protocol=args.protocol)
    result = await agent.run_pipeline(
        spec_source=args.spec,
        base_url=args.base_url,
        output_dir=args.output
    )

    logger.info("Pipeline completed")
    logger.info(f"Test file: {result['test_file']}")
    logger.info(f"Protocol: {result['protocol']}")
    if result.get('report'):
        logger.info(f"Report: {result['report']}")

if __name__ == "__main__":
    asyncio.run(main())
