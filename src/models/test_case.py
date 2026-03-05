from pydantic import BaseModel
from typing import Dict, Any, Optional
from enum import Enum

class TestStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"

class TestCase(BaseModel):
    name: str
    endpoint_path: str
    method: str
    status_code: int
    request_data: Optional[Dict[str, Any]] = None
    expected_schema: Optional[Dict[str, Any]] = None
