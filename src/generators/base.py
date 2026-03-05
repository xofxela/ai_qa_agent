from abc import ABC, abstractmethod
from typing import List
from src.models.endpoint import ApiEndpoint

class TestGenerator(ABC):
    @abstractmethod
    async def generate_test_file(self, endpoints: List[ApiEndpoint], output_path: str, base_url: str) -> str:
        """Generate test file and return its path."""
        pass
