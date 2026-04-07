from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # GitHub OAuth
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    
    # Anthropic API
    ANTHROPIC_API_KEY: str
    
    # Analysis Settings
    ANALYSIS_MODE: Literal["ast", "full_code"] = "ast"
    # ast: Send only AST summaries (~15k tokens, ~$0.08/analysis)
    # full_code: Send complete file contents (~200k tokens, ~$0.63/analysis)
    
    MAX_FILE_SIZE_BYTES: int = 100_000  # Skip files larger than 100KB in full_code mode
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton pattern
_settings: Settings = None


def get_settings() -> Settings:
    """Get application settings (singleton)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings