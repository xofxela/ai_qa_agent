from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class ParameterLocation(str, Enum):
    PATH = "path"
    QUERY = "query"
    HEADER = "header"
    BODY = "body"
    FORM = "formData"

class EndpointParameter(BaseModel):
    name: str
    location: ParameterLocation
    required: bool
    param_schema: Dict[str, Any] = Field(default_factory=dict)  # ← добавили default_factory
    description: Optional[str] = None

class ApiEndpoint(BaseModel):
    path: str
    method: HttpMethod
    operation_id: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: List[EndpointParameter] = []
    request_body_schema: Optional[Dict[str, Any]] = None
    responses: Dict[str, Dict[str, Any]] = {}  # status code -> schema
    security: List[Dict[str, List[str]]] = []
    tags: List[str] = []
