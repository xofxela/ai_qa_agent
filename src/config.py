from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # LLM
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    default_llm_provider: str = "gemini"
    default_model: str = "gemini-2.5-flash-lite"
    
    # Добавьте это поле!
    gemini_model_name: Optional[str] = None
    
    # API тестирования
    default_base_url: str = "https://petstore.swagger.io/v2"
    
    # Пути
    tests_output_dir: str = "generated_tests"
    reports_dir: str = "reports"
    
    # Логирование
    log_level: str = "INFO"
    
    # Прочее
    max_concurrent_tasks: int = 5
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Можно добавить эту строку, чтобы разрешить дополнительные поля,
        # но лучше явно объявить все используемые переменные
        # extra = "ignore"  

settings = Settings()