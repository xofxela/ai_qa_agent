import subprocess
import asyncio
import json
import os
from typing import Dict, Any
from src.executors.base import TestExecutor
from src.utils.logger import logger

class PytestExecutor(TestExecutor):
    async def run_tests(self, test_path: str, report_dir: str) -> Dict[str, Any]:
        """Run pytest with Allure and return results."""
        # Ensure report directory exists
        os.makedirs(report_dir, exist_ok=True)
        
        # Run pytest
        cmd = [
            "pytest",
            test_path,
            f"--alluredir={report_dir}",
            "-v",
            "--tb=short"
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        try:
            # Run in subprocess
            process = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            # Parse results
            return {
                "success": process.returncode == 0,
                "returncode": process.returncode,
                "stdout": process.stdout,
                "stderr": process.stderr,
                "report_dir": report_dir
            }
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "report_dir": report_dir
            }
