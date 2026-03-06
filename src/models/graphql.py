from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class GraphQLArgument(BaseModel):
    name: str
    type: str
    required: bool
    description: Optional[str] = None

class GraphQLField(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    args: List[GraphQLArgument] = []
    fields: List[Dict[str, Any]] = []  # вложенные поля для объектных типов

class GraphQLSchema(BaseModel):
    query_fields: List[GraphQLField]
