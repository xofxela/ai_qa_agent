from abc import ABC, abstractmethod
from typing import Dict, Any

class TestExecutor(ABC):
    @abstractmethod
    async def run_tests(self, test_path: str, report_dir: str) -> Dict[str, Any]:
        """Run tests and return statistics."""
        pass
