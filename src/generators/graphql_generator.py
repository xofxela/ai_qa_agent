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
        prompt = self._build_prompt(schema, endpoint_url)
        test_content = await self.llm.generate(prompt, temperature=0.1)
        test_content = self._clean_code_block(test_content)

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        self.logger.info(f"GraphQL test file generated: {output_path}")
        return output_path

    def _build_prompt(self, schema: GraphQLSchema, endpoint_url: str) -> str:
        # Получаем список имён запросов с аргументами
        queries = []
        for field in schema.query_fields:
            args = []
            for arg in field.args:
                if arg.required:
                    args.append(f"{arg.name}: ${arg.name}")
            if args:
                query_def = f"{field.name}({', '.join(args)})"
            else:
                query_def = field.name
            queries.append(query_def)

        # Словарь с примерами значений аргументов
        arg_examples = {
            "id": '"falcon9"',
            "launch_id": '"108"',
            "rocket_id": '"falcon9"',
            "ship_id": '"5ea6ed2d080df4000697c901"',
            "capsule_id": '"C101"',
            "core_id": '"B1051"',
            "landpad_id": '"ksc_lc_39a"',
            "payload_id": '"60d21b866762410026a70902"',
            "limit": "5",
            "offset": "1",
            "sort": '"name"',
            "order": '"asc"',
            "find": "{}",
            "mission_name": '"Starlink"',
            "launch_year": '"2020"',
        }

        queries_str = "\n".join(queries)

        prompt = f'''You are an expert QA engineer. Generate a pytest test file for the following GraphQL queries against the SpaceX API.

GRAPHQL ENDPOINT: {endpoint_url}

AVAILABLE QUERIES:
{queries_str}

CRITICAL REQUIREMENTS (MUST FOLLOW EXACTLY):

1. USE HTTPX (NOT gql) - we only need to verify HTTP status code 200.
2. Create a fixture 'graphql_client' that returns an httpx.AsyncClient with base_url set to the endpoint.
3. All tests must be async and decorated with @pytest.mark.asyncio.
4. For each query, create a separate test function.
5. In each test, send a POST request with JSON body: {{"query": "..."}}.
6. **FOR EVERY QUERY, REQUEST ONLY THE `__typename` FIELD** – this field is guaranteed to exist in GraphQL for any object. It returns the name of the object type, and ensures the query is valid without depending on specific fields.
   - If the query returns a list, select `__typename` on the list items, e.g., `rockets {{ __typename }}`.
   - If the query returns an object with nested objects, you may need to drill down, but for simplicity, request `__typename` at the level of the returned object.
7. For queries with required arguments, use the following example values:
   - id arguments: {arg_examples['id']}
   - limit: {arg_examples['limit']}
   - offset: {arg_examples['offset']}
   - find filters: {arg_examples['find']}
   - sort/order: {arg_examples['sort']}, {arg_examples['order']}
8. Assert that response.status_code == 200. Do NOT validate response body.
9. Include error handling: if status != 200, print response text for debugging.

FIXTURE EXAMPLE:
@pytest.fixture
async def graphql_client():
    async with httpx.AsyncClient(base_url="{endpoint_url}") as client:
        yield client

TEST EXAMPLE (for rocket query):
@pytest.mark.asyncio
async def test_rocket_query(graphql_client):
    query = \"\"\"
        query {{
            rocket(id: "falcon9") {{
                __typename
            }}
        }}
    \"\"\"
    response = await graphql_client.post("", json={{"query": query}})
    assert response.status_code == 200, f"Expected 200, got {{response.status_code}}. Response: {{response.text}}"

TEST EXAMPLE (for list query):
@pytest.mark.asyncio
async def test_rockets_query(graphql_client):
    query = \"\"\"
        query {{
            rockets(limit: 5) {{
                __typename
            }}
        }}
    \"\"\"
    response = await graphql_client.post("", json={{"query": query}})
    assert response.status_code == 200, f"Expected 200, got {{response.status_code}}. Response: {{response.text}}"

TEST EXAMPLE (for result wrapper):
@pytest.mark.asyncio
async def test_rockets_result_query(graphql_client):
    query = \"\"\"
        query {{
            rocketsResult(limit: 5) {{
                data {{
                    __typename
                }}
            }}
        }}
    \"\"\"
    response = await graphql_client.post("", json={{"query": query}})
    assert response.status_code == 200, f"Expected 200, got {{response.status_code}}. Response: {{response.text}}"

Generate the COMPLETE test file with all necessary imports, the fixture, and one test for each query. Use __typename for all selections.
'''
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
