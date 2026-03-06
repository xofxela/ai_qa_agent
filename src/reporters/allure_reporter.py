import subprocess
import shutil
import os
from typing import Dict, Any
from src.reporters.base import Reporter
from src.utils.logger import logger

class AllureReporter(Reporter):
    async def generate_report(self, results: Dict[str, Any], output_dir: str) -> str:
        """Генерирует отчёт Allure из результатов в output_dir."""
        # Проверяем, есть ли файлы результатов
        if not os.path.exists(output_dir) or not os.listdir(output_dir):
            logger.warning(f"No allure results found in {output_dir}")
            return "No results to generate report"

        # Ищем allure в PATH
        allure_path = shutil.which("allure")
        if allure_path is None:
            logger.warning("Allure CLI not found in PATH. Please install Allure and ensure it's in PATH.")
            logger.info("You can still view raw results in %s", output_dir)
            return f"Allure not installed. Raw results in {output_dir}"

        # Генерируем отчёт
        report_dir = os.path.join(os.path.dirname(output_dir), "allure-report")
        try:
            # Удаляем старый отчёт, если есть
            if os.path.exists(report_dir):
                shutil.rmtree(report_dir)
            
            # Запускаем allure generate
            cmd = [allure_path, "generate", output_dir, "-o", report_dir, "--clean"]
            logger.info(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            
            if result.returncode != 0:
                logger.error(f"Allure generate failed: {result.stderr}")
                return f"Report generation failed. Raw results in {output_dir}"
            
            logger.info(f"Allure report generated at {report_dir}")
            return report_dir
        except Exception as e:
            logger.error(f"Failed to generate Allure report: {e}")
            return f"Error: {e}. Raw results in {output_dir}"
