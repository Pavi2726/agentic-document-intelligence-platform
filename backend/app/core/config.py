import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Agentic Document Intelligence Platform"
    
    # API Keys
    GROQ_API_KEY: str
    
    # Database URIs
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    
    POSTGRES_URL: str
    
    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # MongoDB Configuration
    MONGO_URI: str = "mongodb://localhost:27017/"
    
    # Local Storage Folders
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
    VECTOR_STORE_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "vector_store")
    
    model_config = SettingsConfigDict(
        # Read from .env file inside backend/ directory
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
