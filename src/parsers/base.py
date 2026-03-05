from abc import ABC, abstractmethod
from typing import List
from src.models.endpoint import ApiEndpoint

class SpecParser(ABC):
    @abstractmethod
    async def parse(self, source: str) -> List[ApiEndpoint]:
        """Parse API specification from source (URL or file) and return list of endpoints."""
        pass
