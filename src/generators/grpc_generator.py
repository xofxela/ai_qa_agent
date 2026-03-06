import json
import os
from src.generators.base import TestGenerator
from src.llm.base import LLMProvider
from src.models.grpc import GrpcProto, GrpcService, GrpcMethod, GrpcMessage
from src.utils.logger import logger

class GrpcTestGenerator(TestGenerator):
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
        self.logger = logger

    async def generate_test_file(self, proto: GrpcProto, output_path: str, server_address: str) -> str:
        prompt = self._build_prompt(proto, server_address)
        test_content = await self.llm.generate(prompt, temperature=0.1)
        test_content = self._clean_code_block(test_content)

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        self.logger.info(f"gRPC test file generated: {output_path}")
        return output_path

    def _build_prompt(self, proto: GrpcProto, server_address: str) -> str:
        # Строим описание сервисов и методов с типами
        services_desc = []
        for service in proto.services:
            methods_desc = []
            for method in service.methods:
                if method.client_streaming or method.server_streaming:
                    continue  # только унарные
                input_msg = proto.messages.get(method.input_type)
                output_msg = proto.messages.get(method.output_type)
                input_fields = []
                if input_msg:
                    for f in input_msg.fields:
                        input_fields.append(f"{f.name}: {f.type}")
                output_fields = []
                if output_msg:
                    for f in output_msg.fields:
                        output_fields.append(f"{f.name}: {f.type}")
                methods_desc.append(f"""
Method: {method.name}
  Input: {method.input_type} ({', '.join(input_fields)})
  Output: {method.output_type} ({', '.join(output_fields)})
""")
            services_desc.append(f"Service {service.name}:\n" + "\n".join(methods_desc))

        services_str = "\n".join(services_desc)

        prompt = f'''You are an expert QA engineer. Generate a pytest test file for the following gRPC services (unary methods only) against the server at "{server_address}".

AVAILABLE SERVICES AND METHODS:
{services_str}

REQUIREMENTS (MUST FOLLOW EXACTLY):

1. Use grpcio library: import grpc, and import the generated stubs (assume they are generated and available as <service>_pb2 and <service>_pb2_grpc).
2. Create a fixture 'grpc_channel' that returns an insecure channel to the server.
3. All tests must be regular functions (not async) because gRPC is synchronous by default, but you may use async if needed (keep simple).
4. For each unary method, create a separate test function.
5. For each test:
   - Create a stub using the channel.
   - Construct a request message with sample data based on the input message fields.
   - Use realistic sample values (e.g., strings, numbers, booleans).
   - Call the method and get response.
   - Assert that the call succeeds (no exception).
   - Optionally, assert that response contains expected fields (basic sanity check).
6. For grpcb.in example:
   - Service: grpcbin.GRPCBin
   - Unary method: Unary (input: UnaryRequest, output: UnaryResponse)
   - Request fields: 
     - message: string
     - name: string
     - delay: int32
     - code: int32
   - You can use values: message="Hello", name="Test", delay=0, code=200

FIXTURE EXAMPLE:
@pytest.fixture
def grpc_channel():
    channel = grpc.insecure_channel("{server_address}")
    yield channel
    channel.close()

TEST EXAMPLE (for Unary method):
def test_unary(grpc_channel):
    import grpcbin_pb2
    import grpcbin_pb2_grpc
    stub = grpcbin_pb2_grpc.GRPCBinStub(grpc_channel)
    request = grpcbin_pb2.UnaryRequest(
        message="Hello",
        name="Test",
        delay=0,
        code=200
    )
    response = stub.Unary(request)
    assert response is not None
    assert response.message == request.message
    # add more assertions as needed

Generate the COMPLETE test file with all imports, the fixture, and one test for each unary method. Assume that the necessary _pb2 and _pb2_grpc modules will be generated separately (e.g., using grpcio-tools). The test file should include appropriate try/except for error handling.
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
