from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class GraphQLArgument(BaseModel):
    name: str
    type: str
    required: bool
    description: Optional[str] = None

class GraphQLField(BaseModel):
    name: str
    description: Optional[str] = None
    args: List[GraphQLArgument] = []
    type: str
    is_deprecated: bool = False

class GraphQLSchema(BaseModel):
    query_fields: List[GraphQLField]
    # mutation_fields и subscription_fields можно добавить позже
