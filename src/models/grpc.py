from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class GrpcField(BaseModel):
    name: str
    type: str
    number: int
    repeated: bool = False

class GrpcMessage(BaseModel):
    name: str
    fields: List[GrpcField] = []

class GrpcMethod(BaseModel):
    name: str
    input_type: str
    output_type: str
    client_streaming: bool = False
    server_streaming: bool = False
    # Для унарных оба false

class GrpcService(BaseModel):
    name: str
    methods: List[GrpcMethod] = []

class GrpcProto(BaseModel):
    package: str
    services: List[GrpcService] = []
    messages: Dict[str, GrpcMessage] = {}
