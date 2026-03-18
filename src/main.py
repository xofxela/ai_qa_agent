import asyncio
import argparse
import sys
from src.config import settings
from src.orchestrator.openclaw_orchestrator import OpenClawOrchestrator
from src.utils.logger import logger

async def main():
    """Main entry point for AI QA Agent using OpenClaw orchestration."""
    parser = argparse.ArgumentParser(
        description="AI QA Agent with OpenClaw Orchestration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # REST API testing
  python -m src.main --protocol rest --spec examples/openapi.json --base-url https://petstore.swagger.io/v2
  
  # GraphQL testing
  python -m src.main --protocol graphql --spec https://spacex-production.up.railway.app/ --base-url https://spacex-production.up.railway.app/
  
  # gRPC testing
  python -m src.main --protocol grpc --base-url grpcb.in:9000
        """
    )
    
    parser.add_argument(
        "--protocol",
        choices=["rest", "graphql", "grpc"],
        default="rest",
        help="API protocol to test (default: rest)"
    )
    parser.add_argument(
        "--spec",
        help="OpenAPI spec URL/file (for REST) or GraphQL endpoint URL (for GraphQL). "
             "For gRPC this argument is ignored (you can pass empty string)."
    )
    parser.add_argument(
        "--base-url",
        required=True,
        help="Base URL for API requests. For REST and GraphQL, this is the endpoint base. "
             "For gRPC, this is the server address (host:port)."
    )
    parser.add_argument(
        "--output",
        default=settings.tests_output_dir,
        help=f"Output directory for generated tests (default: {settings.tests_output_dir})"
    )
    parser.add_argument(
        "--orchestrator",
        choices=["openclaw", "legacy"],
        default="openclaw",
        help="Orchestrator to use for pipeline execution (default: openclaw)"
    )
    
    args = parser.parse_args()

    # Validate arguments
    if args.protocol != "grpc" and not args.spec:
        logger.error("--spec is required for REST and GraphQL protocols")
        sys.exit(1)

    logger.info("=" * 70)
    logger.info("AI QA Agent - Powered by OpenClaw Orchestrator")
    logger.info("=" * 70)
    logger.info(f"Protocol: {args.protocol}")
    logger.info(f"Spec: {args.spec if args.spec else '(not used for gRPC)'}")
    logger.info(f"Base URL: {args.base_url}")
    logger.info(f"Output Directory: {args.output}")
    logger.info(f"Orchestrator: {args.orchestrator}")
    logger.info("=" * 70)

    try:
        if args.orchestrator == "openclaw":
            # Use new OpenClaw orchestrator
            orchestrator = OpenClawOrchestrator(protocol=args.protocol)
            result = await orchestrator.execute_pipeline(
                spec_source=args.spec if args.spec else "",
                base_url=args.base_url,
                output_dir=args.output
            )
            
            # Print execution summary
            orchestrator.print_execution_summary()
        else:
            # Fall back to legacy agent
            from src.orchestrator.agent import QAAgent
            agent = QAAgent(protocol=args.protocol)
            result = await agent.run_pipeline(
                spec_source=args.spec if args.spec else "",
                base_url=args.base_url,
                output_dir=args.output
            )

        logger.info("=" * 70)
        logger.info("Pipeline Execution Completed")
        logger.info("=" * 70)
        logger.info(f"Test file: {result['test_file']}")
        logger.info(f"Protocol: {result['protocol']}")
        
        # Check if we have test results
        if result.get('results'):
            if result['results'].get('success'):
                logger.info("✓ All tests passed!")
            else:
                logger.warning("⚠ Some tests failed or had errors")
                if result['results'].get('stderr'):
                    error_msg = result['results']['stderr'][:200]
                    logger.warning(f"  Error: {error_msg}")
        
        if result.get('report'):
            logger.info(f"Report URL: {result['report']}")
        
        # Check overall success
        if result.get('overall_success', True):
            logger.info("✓ Overall: SUCCESS")
        else:
            logger.warning("⚠ Overall: SOME ISSUES DETECTED")
            # Show failed tasks
            task_results = result.get('task_results', {})
            failed = [name for name, info in task_results.items() if info['status'] == 'failed']
            if failed:
                logger.warning(f"  Failed tasks: {failed}")
        
        logger.info("=" * 70)

    except Exception as e:
        logger.error(f"Pipeline execution error: {e}", exc_info=True)
        logger.error("=" * 70)
        logger.error("Check your API configuration and try again.")
        logger.error("For help, see: https://github.com/your-repo/ai_qa_agent/wiki")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())