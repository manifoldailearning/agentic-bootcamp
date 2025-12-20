"""Application configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    app_name: str = "enterprise-delivery-command-center"
    environment: str = "development"
    log_level: str = "INFO"
    
    # API Keys
    openai_api_key: str
    langchain_api_key: Optional[str] = None
    langchain_tracing_v2: bool = True
    langchain_project: str = "delivery-command-center"
    
    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "delivery_center"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    vector_db_schema: str = "vector_store"
    chat_db_schema: str = "chat_store"
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    
    # JIRA
    jira_server: str
    jira_email: str
    jira_api_token: str
        
    # Security
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # LLM Settings
    default_model: str = "gpt-4.1-nano"
    embedding_model: str = "text-embedding-3-small"
    max_tokens: int = 4000
    temperature: float = 0.3
    
    # Evaluation Thresholds
    eval_groundedness_threshold: float = 0.8
    eval_completeness_threshold: float = 0.85
    eval_policy_compliance_threshold: float = 0.95
    eval_action_accuracy_threshold: float = 0.9
    eval_communication_quality_threshold: float = 0.85
    
    # Monitoring
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    prometheus_port: int = 8000
    
    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def redis_url(self) -> str:
        """Get Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}"
        return f"redis://{self.redis_host}:{self.redis_port}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env


settings = Settings()

