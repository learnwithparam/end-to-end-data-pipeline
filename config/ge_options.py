"""Port of Options/GEOptions.cs."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GEOptions(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="GE_", env_file=".env", extra="ignore")

    cli_path: str = ""
    timeout_seconds: int = Field(default=300, ge=5, le=1800)
