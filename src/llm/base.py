from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.2) -> str:
        """Generate text from prompt."""
        pass

    @abstractmethod
    async def generate_with_retry(self, prompt: str, system_prompt: str = None, retries: int = 3) -> str:
        """Generate with automatic retries."""
        pass
