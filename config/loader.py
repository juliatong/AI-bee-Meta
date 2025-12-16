"""Configuration loader for application settings."""
import os
from typing import Optional
from pydantic_settings import BaseSettings
import yaml


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Meta API Configuration
    meta_access_token: str
    meta_business_manager_id: str

    # Development Settings
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Directory Paths
    data_dir: str = "data"
    creatives_dir: str = "creatives"
    configs_dir: str = "configs"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def load_campaign_config(config_path: str) -> dict:
    """Load campaign configuration from YAML file.

    Args:
        config_path: Path to YAML config file (relative to project root)

    Returns:
        dict: Campaign configuration

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML is invalid
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Campaign config not found: {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    return config


# Global settings instance
settings = Settings()
