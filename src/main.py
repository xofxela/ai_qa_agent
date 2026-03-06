import asyncio
import argparse
import sys
from src.config import settings
from src.orchestrator.agent import QAAgent
from src.utils.logger import logger

async def main():
    parser = argparse.ArgumentParser(description="AI QA Agent")
    parser.add_argument("--protocol", choices=["rest", "graphql", "grpc"], default="rest",
                        help="API protocol to test")
    parser.add_argument("--spec", help="OpenAPI spec URL/file (for REST) or GraphQL endpoint URL (for GraphQL). "
                                       "For gRPC this argument is ignored (you can pass empty string).")
    parser.add_argument("--base-url", required=True,
                        help="Base URL for API requests. For REST and GraphQL, this is the endpoint base. "
                             "For gRPC, this is the server address (host:port).")
    parser.add_argument("--output", default=settings.tests_output_dir,
                        help="Output directory for generated tests")
    args = parser.parse_args()

    # For gRPC, spec is not required
    if args.protocol != "grpc" and not args.spec:
        logger.error("--spec is required for REST and GraphQL protocols")
        sys.exit(1)

    logger.info(f"Starting AI QA Agent with protocol: {args.protocol}")
    logger.info(f"Spec: {args.spec if args.spec else '(not used for gRPC)'}")
    logger.info(f"Base URL: {args.base_url}")

    agent = QAAgent(protocol=args.protocol)
    result = await agent.run_pipeline(
        spec_source=args.spec if args.spec else "",
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