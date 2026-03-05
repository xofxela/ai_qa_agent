import subprocess
import asyncio
import os
from typing import Dict, Any
from src.reporters.base import Reporter
from src.utils.logger import logger

class AllureReporter(Reporter):
    async def generate_report(self, results: Dict[str, Any], output_dir: str) -> str:
        """Generate Allure HTML report from results directory."""
        # Check if allure command is available
        try:
            subprocess.run(["allure", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Allure command not found. Skipping report generation.")
            return "Allure not installed"
        
        report_path = os.path.join(output_dir, "html")
        os.makedirs(report_path, exist_ok=True)
        
        cmd = [
            "allure", "generate",
            results.get("report_dir", output_dir),
            "-o", report_path,
            "--clean"
        ]
        
        try:
            process = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if process.returncode == 0:
                logger.info(f"Allure report generated at {report_path}")
                return report_path
            else:
                logger.error(f"Allure generation failed: {process.stderr}")
                return ""
        except Exception as e:
            logger.error(f"Allure generation error: {e}")
            return ""
