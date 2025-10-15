import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Application
    app_name: str = "Digestarr"
    app_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 5667
    
    # Plex Configuration
    plex_url: str = "http://plex:32400"  # Default to Docker service name
    plex_token: Optional[str] = None
    
    # Discord Configuration (can be empty at startup, configured via Web UI)
    discord_webhook_url: Optional[str] = None
    discord_username: str = "Digestarr"
    discord_avatar_url: Optional[str] = None
    
    # Scheduling Configuration
    digest_schedule: str = "0 */6 * * *"  # Cron format: every 6 hours
    digest_threshold: int = 0  # Auto-send if N items queued (0 = disabled)
    timezone: str = "America/New_York"
    
    # Feature Flags
    enable_movies: bool = True
    enable_tv_shows: bool = True
    enable_music: bool = True
    
    # Data Persistence
    data_dir: str = "/data"
    db_path: str = "/data/digestarr.db"
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
