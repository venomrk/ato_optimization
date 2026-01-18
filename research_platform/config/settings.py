from functools import lru_cache
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    openai_api_keys: List[str] = Field(default_factory=list)
    anthropic_api_keys: List[str] = Field(default_factory=list)
    google_api_keys: List[str] = Field(default_factory=list)
    deepseek_api_key: Optional[str] = None
    qwen_api_key: Optional[str] = None
    xai_api_key: Optional[str] = None
    yi_api_key: Optional[str] = None
    
    semantic_scholar_api_key: Optional[str] = None
    springer_api_key: Optional[str] = None
    elsevier_api_key: Optional[str] = None
    
    database_url: str = "sqlite:///./research_platform.db"
    redis_url: str = "redis://localhost:6379/0"
    
    vector_db_type: str = "chroma"
    pinecone_api_key: Optional[str] = None
    pinecone_environment: Optional[str] = None
    pinecone_index_name: str = "research-papers"
    weaviate_url: str = "http://localhost:8080"
    qdrant_url: str = "http://localhost:6333"
    
    paper_storage_path: str = "./data/papers"
    model_storage_path: str = "./data/models"
    cache_dir: str = "./data/cache"
    
    max_agents: int = 15
    agent_timeout: int = 300
    consensus_threshold: float = 0.7
    min_confidence_score: float = 0.6
    
    max_api_calls_per_minute: int = 60
    rate_limit_window: int = 60
    
    enable_fine_tuning: bool = True
    fine_tune_batch_size: int = 8
    fine_tune_epochs: int = 3
    lora_rank: int = 8
    lora_alpha: int = 16
    
    auto_update_models: bool = True
    model_check_interval: int = 86400
    paper_ingestion_interval: int = 3600
    max_papers_per_query: int = 50
    
    log_level: str = "INFO"
    enable_metrics: bool = True
    prometheus_port: int = 9090
    
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    enable_cors: bool = True
    
    secret_key: str = "change-this-to-a-random-secret-key"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name.endswith('_api_keys'):
                return [k.strip() for k in raw_val.split(',') if k.strip()]
            return raw_val

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        openai_keys = []
        for i in range(1, 10):
            key_name = f'openai_api_key{"" if i == 1 else f"_{i}"}'
            key = kwargs.get(key_name) or getattr(self, key_name.upper(), None)
            if key:
                openai_keys.append(key)
        if openai_keys:
            self.openai_api_keys = openai_keys
            
        anthropic_keys = []
        for i in range(1, 10):
            key_name = f'anthropic_api_key{"" if i == 1 else f"_{i}"}'
            key = kwargs.get(key_name) or getattr(self, key_name.upper(), None)
            if key:
                anthropic_keys.append(key)
        if anthropic_keys:
            self.anthropic_api_keys = anthropic_keys
            
        google_keys = []
        for i in range(1, 10):
            key_name = f'google_api_key{"" if i == 1 else f"_{i}"}'
            key = kwargs.get(key_name) or getattr(self, key_name.upper(), None)
            if key:
                google_keys.append(key)
        if google_keys:
            self.google_api_keys = google_keys


@lru_cache()
def get_settings() -> Settings:
    return Settings()
