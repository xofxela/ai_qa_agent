import subprocess
import json
import os
import time
from src.utils.logger import logger
from typing import Dict, Any, List

class GrpcurlExecutor:
    def __init__(self, server_address: str, reports_dir: str = "reports"):
        self.server_address = server_address
        self.reports_dir = reports_dir
        os.makedirs(self.reports_dir, exist_ok=True)

    async def run_tests(self) -> Dict[str, Any]:
        logger.info(f"Running gRPC tests via grpcurl against {self.server_address}")

        services = self._list_services()
        if not services:
            return {"total": 0, "passed": 0, "failed": 0, "details": [], "error": "No services found"}

        results = {"total": 0, "passed": 0, "failed": 0, "details": []}
        for service in services:
            if service == "grpc.reflection.v1alpha.ServerReflection":
                continue

            methods = self._list_methods(service)
            for method_full in methods:
                method_short = method_full.split('.')[-1]
                success, error, output = self._call_method(service, method_short)
                results["total"] += 1
                if success:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                details = {
                    "service": service,
                    "method": method_short,
                    "success": success,
                    "error": error if not success else None,
                    "output": output[:500] if output else None
                }
                results["details"].append(details)
                # Сохраняем результат в Allure-совместимом формате
                self._save_allure_result(service, method_short, details)

        logger.info(f"grpcurl tests completed: {results['passed']}/{results['total']} passed")
        return results

    def _list_services(self) -> List[str]:
        # ... (без изменений)

    def _list_methods(self, service: str) -> List[str]:
        # ... (без изменений)

    def _call_method(self, service: str, method: str) -> tuple[bool, str, str]:
        full_method = f"{service}/{method}"
        cmd = ["grpcurl", "-plaintext", "-d", "{}", self.server_address, full_method]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.PIPE, text=True)
            logger.debug(f"Method {full_method} succeeded: {output[:100]}")
            return True, "", output
        except subprocess.CalledProcessError as e:
            logger.debug(f"Method {full_method} failed: {e.stderr}")
            return False, e.stderr, ""

    def _save_allure_result(self, service: str, method: str, details: Dict):
        """Сохраняет результат теста в формате, совместимом с Allure."""
        # Формируем структуру allure-результата
        result = {
            "name": f"{service}.{method}",
            "status": "passed" if details["success"] else "failed",
            "statusDetails": {
                "message": details["error"] if details["error"] else "",
                "trace": ""
            },
            "stage": "finished",
            "start": int(time.time() * 1000),
            "stop": int(time.time() * 1000),
            "attachments": [
                {
                    "name": "Output",
                    "type": "text/plain",
                    "source": details.get("output", "")
                }
            ] if details.get("output") else [],
            "labels": [
                {"name": "protocol", "value": "grpc"},
                {"name": "service", "value": service},
                {"name": "method", "value": method}
            ]
        }
        # Генерируем уникальное имя файла
        filename = f"grpc_{service.replace('.', '_')}_{method}_{int(time.time() * 1000)}.json"
        filepath = os.path.join(self.reports_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)