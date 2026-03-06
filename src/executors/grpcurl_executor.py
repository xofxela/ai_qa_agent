import subprocess
from src.utils.logger import logger
from typing import Dict, Any, List

class GrpcurlExecutor:
    def __init__(self, server_address: str):
        self.server_address = server_address

    async def run_tests(self) -> Dict[str, Any]:
        logger.info(f"Running gRPC tests via grpcurl against {self.server_address}")

        services = self._list_services()
        if not services:
            return {"total": 0, "passed": 0, "failed": 0, "details": [], "error": "No services found"}

        results = {"total": 0, "passed": 0, "failed": 0, "details": []}
        for service in services:
            # Пропускаем служебный reflection сервис
            if service == "grpc.reflection.v1alpha.ServerReflection":
                continue

            methods = self._list_methods(service)
            for method_full in methods:
                # Извлекаем короткое имя метода (последняя часть после точки)
                method_short = method_full.split('.')[-1]
                success, error = self._call_method(service, method_short)
                results["total"] += 1
                if success:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                results["details"].append({
                    "service": service,
                    "method": method_short,
                    "success": success,
                    "error": error if not success else None
                })

        logger.info(f"grpcurl tests completed: {results['passed']}/{results['total']} passed")
        return results

    def _list_services(self) -> List[str]:
        """Получает список сервисов через grpcurl."""
        cmd = ["grpcurl", "-plaintext", self.server_address, "list"]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.PIPE, text=True)
            services = [s.strip() for s in output.splitlines() if s.strip()]
            logger.info(f"Found services: {services}")
            return services
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list services: {e.stderr}")
            return []

    def _list_methods(self, service: str) -> List[str]:
        """Получает список методов для сервиса (полные имена с точками)."""
        cmd = ["grpcurl", "-plaintext", self.server_address, "list", service]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.PIPE, text=True)
            methods = [s.strip() for s in output.splitlines() if s.strip()]
            logger.debug(f"Service {service} methods: {methods}")
            return methods
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list methods for {service}: {e.stderr}")
            return []

    def _call_method(self, service: str, method: str) -> tuple[bool, str]:
        """Вызывает метод с пустым JSON-запросом {}.
        method должно быть коротким именем метода (без префикса сервиса)."""
        full_method = f"{service}/{method}"
        cmd = ["grpcurl", "-plaintext", "-d", "{}", self.server_address, full_method]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.PIPE, text=True)
            logger.debug(f"Method {full_method} succeeded: {output[:100]}")
            return True, ""
        except subprocess.CalledProcessError as e:
            logger.debug(f"Method {full_method} failed: {e.stderr}")
            return False, e.stderr