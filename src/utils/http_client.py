import httpx
from src.utils.logger import logger

class HttpClient:
    def __init__(self, timeout: int = 30):
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def get(self, url: str, **kwargs):
        try:
            response = await self.client.get(url, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"HTTP GET failed: {e}")
            raise
    
    async def post(self, url: str, **kwargs):
        try:
            response = await self.client.post(url, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"HTTP POST failed: {e}")
            raise
    
    async def close(self):
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
