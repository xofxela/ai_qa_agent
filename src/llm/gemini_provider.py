import asyncio
from google import genai
from google.genai import types
from src.llm.base import LLMProvider
from src.config import settings
from src.utils.logger import logger

class GeminiProvider(LLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        self.client = genai.Client(api_key=self.api_key)
        self.model = model or settings.default_model
    
    async def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.2) -> str:
        contents = [prompt]
        system_instruction = system_prompt if system_prompt else None
        
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=self.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    system_instruction=system_instruction,
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise
    
    async def generate_with_retry(self, prompt: str, system_prompt: str = None, retries: int = 3) -> str:
        for attempt in range(retries):
            try:
                return await self.generate(prompt, system_prompt)
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed: {e}")
                if attempt == retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
