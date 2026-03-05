import json
import os
from src.generators.base import TestGenerator
from src.llm.base import LLMProvider
from src.models.graphql import GraphQLSchema
from src.utils.logger import logger

class GraphQLTestGenerator(TestGenerator):
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        self.logger = logger

    async def generate_test_file(self, schema: GraphQLSchema, output_path: str, endpoint_url: str) -> str:
        """Генерирует pytest файл с тестами для GraphQL запросов"""
        prompt = self._build_prompt(schema, endpoint_url)
        test_content = await self.llm.generate(prompt, temperature=0.1)
        test_content = self._clean_code_block(test_content)

        # Создаём директорию, если нужно
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        self.logger.info(f"GraphQL test file generated: {output_path}")
        return output_path

    def _build_prompt(self, schema: GraphQLSchema, endpoint_url: str) -> str:
        fields_json = json.dumps([f.dict() for f in schema.query_fields], indent=2, default=str)

        prompt = f'''"""You are an expert QA engineer. Generate a pytest test file for the following GraphQL queries.

GRAPHQL ENDPOINT: {endpoint_url}

AVAILABLE QUERIES (with arguments and return types):
{fields_json}

REQUIREMENTS (MUST FOLLOW EXACTLY):
1. Use the 'gql' library with async transport: from gql import Client, gql
2. Use HTTPXAsyncTransport from gql.transport.httpx
3. Create an async fixture 'graphql_client' that provides a Client instance
4. All tests must be async and decorated with @pytest.mark.asyncio
5. For each query, create a separate test function
6. For queries with arguments, generate realistic test data based on argument types
7. Verify response structure: assert that expected fields exist and have correct types (use isinstance where appropriate)
8. Handle potential GraphQL errors gracefully (e.g., if response contains 'errors' key)

FIXTURE EXAMPLE:
@pytest.fixture
async def graphql_client():
    transport = HTTPXAsyncTransport(url="{endpoint_url}")
    async with Client(transport=transport, fetch_schema_from_transport=False) as client:
        yield client

TEST EXAMPLE (for a query without arguments):
@pytest.mark.asyncio
async def test_company_query(graphql_client):
    query = gql("""
        query {{
            company {{
                name
                ceo
            }}
        }}
    """)
    result = await graphql_client.execute(query)
    assert "company" in result
    assert "name" in result["company"]
    assert "ceo" in result["company"]

TEST EXAMPLE (for a query with arguments):
@pytest.mark.asyncio
async def test_launch_query(graphql_client):
    query = gql("""
        query {{
            launch(id: "1") {{
                mission_name
                launch_date_utc
            }}
        }}
    """)
    result = await graphql_client.execute(query)
    assert "launch" in result
    assert "mission_name" in result["launch"]

Generate the COMPLETE test file with all necessary imports, fixture, and one test for each query. Use realistic field names from the provided schema. Ensure tests are independent.
"""'''
        return prompt

    def _clean_code_block(self, content: str) -> str:
        content = content.strip()
        if content.startswith('```python'):
            content = content[9:]
        elif content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        return content.strip()
