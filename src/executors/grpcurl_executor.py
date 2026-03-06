import subprocess
import json
import os
import time
import uuid
from src.utils.logger import logger
from typing import Dict, Any, List

class GrpcurlExecutor:
    def __init__(self, server_address: str, reports_dir: str = "reports"):
        self.server_address = server_address
        self.reports_dir = reports_dir
        os.makedirs(self.reports_dir, exist_ok=True)
        logger.info(f"grpcurl executor initialized. Reports will be saved to {os.path.abspath(self.reports_dir)}")

    async def run_tests(self) -> Dict[str, Any]:
        logger.info(f"Running gRPC tests via grpcurl against {self.server_address}")

        services = self._list_services()
        if not services:
            logger.error("No services found")
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
                    "output": output[:500] if output else None,
                    "full_output": output if output else None
                }
                results["details"].append(details)
                self._save_allure_result(service, method_short, details)

        saved_files = [f for f in os.listdir(self.reports_dir) if f.startswith("grpc_") and f.endswith(".json")]
        logger.info(f"Saved {len(saved_files)} Allure result files in {self.reports_dir}")
        logger.info(f"grpcurl tests completed: {results['passed']}/{results['total']} passed")
        return results

    def _list_services(self) -> List[str]:
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
        cmd = ["grpcurl", "-plaintext", self.server_address, "list", service]
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.PIPE, text=True)
            methods = [s.strip() for s in output.splitlines() if s.strip()]
            logger.debug(f"Service {service} methods: {methods}")
            return methods
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list methods for {service}: {e.stderr}")
            return []

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
        """Save test result in Allure-compatible JSON format."""
        try:
            result_id = str(uuid.uuid4())
            timestamp = int(time.time() * 1000)
            # Важно: имя файла должно заканчиваться на -result.json
            filename = f"grpc_{service.replace('.', '_')}_{method}_{timestamp}-result.json"
            filepath = os.path.join(self.reports_dir, filename)

            attachments = []
            if details.get("full_output"):
                output_file = f"grpc_{service.replace('.', '_')}_{method}_{timestamp}-output.txt"
                output_path = os.path.join(self.reports_dir, output_file)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(details["full_output"])
                attachments.append({
                    "name": "Output",
                    "type": "text/plain",
                    "source": output_file
                })

            result = {
                "uuid": result_id,
                "name": f"{service}.{method}",
                "status": "passed" if details["success"] else "failed",
                "statusDetails": {
                    "message": details["error"] if details["error"] else "",
                    "trace": ""
                },
                "stage": "finished",
                "start": timestamp,
                "stop": timestamp,
                "attachments": attachments,
                "labels": [
                    {"name": "protocol", "value": "grpc"},
                    {"name": "service", "value": service},
                    {"name": "method", "value": method}
                ]
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            logger.info(f"Allure result saved: {filepath}")
        except Exception as e:
            logger.error(f"Failed to save allure result for {service}.{method}: {e}")