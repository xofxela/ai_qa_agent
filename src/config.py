from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # LLM configuration
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    default_llm_provider: str = "gemini"
    default_model: str = "gemini-2.5-flash-lite"
    
    # Specific Gemini model name (optional, can override default_model)
    gemini_model_name: Optional[str] = None
    
    # Directories
    tests_output_dir: str = "generated_tests"
    reports_dir: str = "reports"
    
    # Logging
    log_level: str = "INFO"
    
    # Concurrency
    max_concurrent_tasks: int = 5
    
    # OpenClaw Orchestrator configuration
    default_orchestrator: str = "openclaw"  # openclaw or legacy
    orchestrator_enable_monitoring: bool = True
    orchestrator_enable_retries: bool = True
    orchestrator_max_retries: int = 3
    orchestrator_retry_strategy: str = "exponential"  # exponential, linear, immediate
    orchestrator_task_timeout: int = 300  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # To allow extra fields from .env not defined above, uncomment:
        # extra = "ignore"

settings = Settings()