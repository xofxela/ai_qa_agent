from abc import ABC, abstractmethod
from typing import Dict, Any

class Reporter(ABC):
    @abstractmethod
    async def generate_report(self, results: Dict[str, Any], output_dir: str) -> str:
        """Generate report and return path or URL."""
        pass
