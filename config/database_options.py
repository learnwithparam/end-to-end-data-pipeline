"""Port of Options/DatabaseOptions.cs."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseOptions(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mysql: str = Field(default="", alias="DB_MYSQL")
    postgres: str = Field(default="", alias="DB_POSTGRES")
    command_timeout_seconds: int = Field(default=30, ge=5, le=300, alias="DB_COMMAND_TIMEOUT_SECONDS")
