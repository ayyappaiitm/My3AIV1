from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Database
    database_url: str
    
    # OpenAI
    openai_api_key: str
    
    # Address Validation (optional)
    google_maps_api_key: Optional[str] = None
    smartystreets_api_key: Optional[str] = None
    enable_address_validation: bool = True
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7 days (7 * 24 * 60)
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:3001"
    
    # Environment
    environment: str = "development"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

