from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.models.test_case import TestStatus

class TestResult(BaseModel):
    test_name: str
    status: TestStatus
    duration: float
    error_message: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    assertions: Dict[str, bool] = {}

class TestSuiteResult(BaseModel):
    suite_name: str
    start_time: datetime
    end_time: datetime
    total_tests: int
    passed: int
    failed: int
    skipped: int
    results: List[TestResult] = []
    report_path: Optional[str] = None
