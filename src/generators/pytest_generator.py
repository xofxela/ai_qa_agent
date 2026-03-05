import asyncio
import json
import os
from typing import List
from src.generators.base import TestGenerator
from src.models.endpoint import ApiEndpoint
from src.llm.base import LLMProvider
from src.utils.logger import logger

class PytestGenerator(TestGenerator):
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        self.logger = logger

    async def generate_test_file(self, endpoints: List[ApiEndpoint], output_path: str, base_url: str) -> str:
        """Генерирует файл с тестами, пропуская защищённые эндпоинты"""
        
        # Фильтруем эндпоинты, требующие авторизации
        public_endpoints = []
        auth_endpoints = []
        
        for endpoint in endpoints:
            # Проверяем наличие security требований
            if endpoint.security and len(endpoint.security) > 0:
                # Проверяем, есть ли среди них api_key или petstore_auth
                has_api_key = any('api_key' in sec for sec in endpoint.security)
                has_oauth = any('petstore_auth' in sec for sec in endpoint.security)
                
                if has_api_key or has_oauth:
                    auth_endpoints.append(endpoint)
                    continue
            
            public_endpoints.append(endpoint)
        
        self.logger.info(f"Public endpoints: {len(public_endpoints)}, Auth required: {len(auth_endpoints)}")
        
        # Если нет публичных эндпоинтов, генерируем заглушку с информацией
        if not public_endpoints:
            test_content = await self._generate_auth_test_file(auth_endpoints, base_url)
        else:
            # Генерируем тесты для публичных эндпоинтов
            prompt = self._build_prompt(public_endpoints, base_url)
            test_content = await self.llm.generate(prompt, temperature=0.1)
        
        # Очищаем ответ от возможных markdown-обёрток
        test_content = self._clean_code_block(test_content)
        
        # Создаём директорию, если нужно
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Сохраняем файл
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        self.logger.info(f"Test file generated: {output_path}")
        return output_path

    def _build_prompt(self, endpoints: List[ApiEndpoint], base_url: str) -> str:
        """Строит промпт с жёсткими требованиями к асинхронности и корректному закрытию клиента"""
        
        endpoints_json = json.dumps([endpoint.dict() for endpoint in endpoints], indent=2, default=str)
        
        prompt = f"""You are an expert QA engineer. Generate a COMPLETE pytest test file for the following API endpoints.

    BASE URL: {base_url}

    !!! ABSOLUTELY CRITICAL REQUIREMENTS - MUST FOLLOW EXACTLY !!!
    1. EVERY test function MUST be defined with 'async def' (NOT just 'def')
    2. EVERY test function MUST have '@pytest.mark.asyncio' decorator
    3. EVERY test function MUST accept 'async_client' as first parameter
    4. The 'async_client' fixture MUST be defined as an ASYNC fixture using 'async def' and MUST use 'async with' to ensure the client is properly closed.

    FIXTURE DEFINITION - COPY THIS EXACTLY:
    @pytest.fixture
    async def async_client():
        async with httpx.AsyncClient(base_url=BASE_URL) as client:
            yield client

    CORRECT TEST EXAMPLE:
    @pytest.mark.asyncio
    async def test_get_pet(async_client):
        response = await async_client.get("/pet/1")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data

    INCORRECT EXAMPLE (WILL FAIL):
    @pytest.fixture
    def async_client():  # WRONG - sync fixture
        client = httpx.AsyncClient(base_url=BASE_URL)
        yield client  # client will never be closed properly

    ENDPOINTS TO TEST:
    {endpoints_json}

    Generate the ENTIRE test file with:
    1. All necessary imports (pytest, httpx)
    2. The exact fixture shown above (async def with async with)
    3. ALL tests following the CORRECT async pattern
    4. NO synchronous fixtures or tests that use async_client"""
        
        return prompt

    async def _generate_auth_test_file(self, auth_endpoints: List[ApiEndpoint], base_url: str) -> str:
        """
        Генерирует тестовый файл-заглушку для эндпоинтов, требующих авторизации.
        Этот метод вызывается, когда все эндпоинты требуют аутентификации.
        """
        endpoints_json = json.dumps([{
            "path": e.path,
            "method": e.method,
            "operation_id": e.operation_id,
            "security": e.security
        } for e in auth_endpoints], indent=2)
        
        return f'''"""
            Тесты для эндпоинтов, требующих авторизации.
            Все перечисленные ниже эндпоинты требуют API key или OAuth2.
            Для их тестирования необходимо добавить заголовки авторизации.

            Эндпоинты, требующие авторизации:
            {endpoints_json}

            Как добавить авторизацию:
            1. Получите API key из настроек Petstore (special-key)
            2. Добавьте заголовок: {{"api_key": "special-key"}}
            3. Или настройте OAuth2 flow для petstore_auth
            """

            import pytest
            import httpx
            from typing import Dict, Any

            BASE_URL = "{base_url}"

            # Заглушки для будущих тестов с авторизацией
            @pytest.mark.skip(reason="Требуется авторизация")
            @pytest.mark.asyncio
            async def test_auth_endpoints_placeholder():
                """Заглушка для тестов, требующих авторизации."""
                assert True

            # Список эндпоинтов, которые нужно будет протестировать с авторизацией
            AUTH_ENDPOINTS = {json.dumps([{{
                "path": e.path,
                "method": e.method,
                "operation_id": e.operation_id
            }} for e in auth_endpoints], indent=2)}
            '''
    
    def _clean_code_block(self, content: str) -> str:
        """Удаляет markdown-обёртки кода из ответа LLM."""
        content = content.strip()
        
        # Удаляем ```python в начале и ``` в конце
        if content.startswith('```python'):
            content = content[9:]
        elif content.startswith('```'):
            content = content[3:]
        
        if content.endswith('```'):
            content = content[:-3]
        
        return content.strip()